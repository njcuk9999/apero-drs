Changelog
=========


0.7.288 (2023-08-30)
--------------------
- [NIRPS] remove AB from `file_Definitions` of nirps he and ha. [Neil
  Cook]
- [NIRPS] fix which definitions are used for `apero_postprocess` for
  nirps-he and nirps-ha. [Neil Cook]
- [APERO] `apero_get` - fix pid. [Neil Cook]
- `Error_html.py` - fix `pid_to_time` to allow no pid. [Neil Cook]
- [APERO] `error_html.py` - fix links in date table. [Neil Cook]
- [APERO] `error_html.py` - fix filtering. [Neil Cook]
- [APERO] `error_html.py` - fix filtering. [Neil Cook]
- [APERO] add roweven and rowodd. [Neil Cook]
- [APERO] `error_html.py` - fix html styling for recipe page. [Neil Cook]
- [APERO] `error_html.py` - fix problem with `from_outlist`. [Neil Cook]
- [APERO] `error_html.py` - fix problem with `from_outlist`. [Neil Cook]
- Start error html work. [Neil Cook]
- Start error html work. [Neil Cook]
- Start error html work. [Neil Cook]
- [APERO] add some error handling functions. [Neil Cook]
- [APERO] - add a `add_html` function to markdown functions. [Neil Cook]
- Start error html work. [Neil Cook]
- [APERO] - add a `add_html` function to markdown functions. [Neil Cook]
- [APERO] add some error handling functions. [Neil Cook]
- [APERO] correct making a tar with no files. [Neil Cook]
- [APERO] `apero_get.py` - make tars actually a tar.gz. [Neil Cook]
- [APERO] correct dprtype for LBL NIRPS + make default run.ini files set
  lbl steps skip=False. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- [APERO] `apero_get` - fix arguments. [Neil Cook]
- `Listing.drs_get.py` - change `DRS_DATE_OBS` to `KW_MJDATE` (for matching on
  observed time) [Neil Cook]
- [APERO] `apero_get` - add a timekey to switch between processed and
  observed. [Neil Cook]
- [APERO] `apero_get` - add indict and outdict (for return analysis) [Neil
  Cook]
- [APERO] `apero_get` - fix tar file addition. [Neil Cook]
- [APERO] `apero_get` - fix tar file addition. [Neil Cook]
- [APERO] `apero_get` - fix tar file addition. [Neil Cook]
- [APERO] reset - ask before reseting all databases. [Neil Cook]
- [APERO] reset - ask before reseting all databases. [Neil Cook]
- [APERO] update arg on `apero_database`. [Neil Cook]
- [APERO] Update `apero_get.py` (allow tar creation, filter by runid and
  get files up to a certain date) [Neil Cook]
- [APERO] `apero_lbl_ref_nirps_ha.py` - create directories before
  parallelisation. [Neil Cook]
- [APERO] `apero_lbl` - for FP do QC. [Neil Cook]
- [APERO] do `lbl_compute` qc before error reporting. [Neil Cook]
- [APERO] Add LBL to `apero_reset.py`. [Neil Cook]
- [APERO] add qc to lbl (for now they always pass) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- Merge branch 'v0.7.286-stable-test' into v0.7.287-live. [Neil Cook]
- [APERO] can no longer use append for dataframes use pd.concat instead
  (already implemented in v0.7.287) fixes issue #710. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- [APERO] fix to language database - if row is Nan skip. [Neil Cook]
- [APERO] remove EFFRON < `10*` RON as a QC parameter. [Neil Cook]
- [APERO] update QC limit to 10 `*` RON. [Neil Cook]
- [APERO] add noise combination method. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- Merge branch 'v0.7.287-live' of github.com:njcuk9999/apero-drs into
  v0.7.287-live. [Neil Cook]
- Fix broken links not being replaced. [Neil Cook]
- Deal with more copy paths existing (overwrite or remove before copy)
  [Neil Cook]
- [APERO] update requirements (downgrade mysql-connector-python) [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-live' into
  v0.7.287-live. [Neil Cook]
- [APERO] fix problem with `eff_ron`. [Neil Cook]
- [APERO] correct gain --> `EFF_GAIN`. [Neil Cook]
- `Apero.core.instruments.nirps_*` - update comments on `MJD_FLUX`, `RMS_POS`,
  `MED_POS`. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - revert forcing value to a string in
  `self.str_arg_list`. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - revert forcing value to a string in
  `self.str_arg_list`. [Neil Cook]
- [NIRPS] update `KW_IDENTIFIER`. [Neil Cook]
- Add keyword `EFF_RON` to headers. [Neil Cook]
- Add keyword `EFF_RON` to headers. [Neil Cook]
- `Setup/install.py` - update now we have lbl in the requirements. [Neil
  Cook]
- Add lbl + postprocess recipes to `nirps_he` and `nirps_ha`. [Neil Cook]
- Update run.ini files. [Neil Cook]
- Update run.ini files with LBL and and `post_procesing` file for nirps.
  [Neil Cook]
- [APERO/LBL] Deal with errors and skipping better. [Neil Cook]
- Make Gain a constant (do not use from header) [Neil Cook]
- Continue work on running lbl from APERO (test running) [Neil Cook]
- Continue work on running lbl from APERO (test running) [Neil Cook]
- Continue work on running lbl from APERO (add lbl files to file index
  database) [Neil Cook]
- Continue work on running lbl from APERO. [Neil Cook]
- Merge branch 'v0.7.287-stable-test' into v0.7.287-live. [Neil Cook]
- Add keyword `EFF_RON` to headers. [Neil Cook]
- Continue work on running lbl from APERO. [Neil Cook]
- Merge branch 'v0.7.287-stable-test' into v0.7.287-live. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.287-stable-test' into
  v0.7.287-stable-test. [Neil Cook]
- Measure effective readout noise in order to better calculate SNR. Add
  QC if effective readout noise > 2 `*` sigdet. [Neil Cook]
- Continue work on running lbl from APERO. [Neil Cook]
- Allow LBL to be run from APERO [UNFINISHED & UNTESTED] [Neil Cook]
- Update date/version/changelog/readme. [Neil Cook]


0.7.287 (2023-08-08)
--------------------
- [APERO] Correct that ribbon cannot load in raw file path. [Neil Cook]
- [APERO] Correct that ribbon cannot save in raw file path. [Neil Cook]
- [APERO] fix `apero_get` and null/nan `passed_all_qc` column. [Neil Cook]
- [APERO] `apero_get` if `PASSED_ALL_QC` is Null we should accept it as
  passed QC (as we don't know otherwise) [Neil Cook]
- [APERO] `drs_markdown.py` - if `csv_file` is None our table does not have
  rows. [Neil Cook]
- [SPRIOU] Correct the RUNID key (was QRUNID now RUNID) [Neil Cook]
- [APERO] `apero_processing.py` - fix issues with which objects go into
  templates (now only those that are in the obsdirs that are given), if
  none are given use all `obs_dir` (we cannot use the astrom list of
  targets as this contains many objects that don't exist for an
  instrument) [Neil Cook]
- Deal with processing obsdirs better [UNFINISHED, UNTESTED] [Neil Cook]
- [APERO] do not require params['INPUTS']['PARALLEL'] instead set it to
  False if not present. [Neil Cook]
- [APERO] `apero_ccf_spirou.py` - fix bug where `OBJ_DARK` and `POLAR_DARK`
  files crash CCF code. [Neil Cook]
- [APERO] `apero.core.core.drs_base_classes.py` - remove FutureWarning
  calling in on a single element (now get count and then force to int)
  [Neil Cook]
- Merge branch 'main' into v0.7.287-live. [Neil Cook]
- [APERO] update readme. [Neil Cook]
- Merge branch 'v0.7.285-live' into v0.7.286-live. [Neil Cook]
- `Apero.science.calib.background.py` - add in `local_background_correction`
  image even if not calculating. [Neil Cook]
- [NIRPS] Modify the `BKGR_BOXSIZE` and `BKGR_KER_AMP` (does not affect
  SPIROU) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.285-live' into
  v0.7.285-live. [Neil Cook]
- `Drs_precheck`, `drs_processing.py` - allow logging to be turned off (for
  `apero_checks)` [Neil Cook]
- [APERO] `find_objnames` can return an empty list, deal with each use
  case and report error if we do not want this to be empty. [Neil Cook]
- [APERO] `find_objnames` can return an empty list, deal with each use
  case and report error if we do not want this to be empty. [Neil Cook]
- [APERO] `find_objnames` can return an empty list, deal with each use
  case and report error if we do not want this to be empty. [Neil Cook]
- [APERO] `install.py` - in dev mode ask user to add all groups. [Neil
  Cook]
- [APERO] `install.py` - in dev mode ask user to add all groups. [Neil
  Cook]
- [APERO] `drs_astrometrics.py` - fix using dataframe.append (should be
  pd.concat) [Neil Cook]


0.7.286 (2023-07-12)
--------------------
- Merge remote-tracking branch 'origin/v0.7.286-live' into
  v0.7.286-live. [Neil Cook]
- Merge branch 'v0.7.285-live' into v0.7.286-live. [Neil Cook]
- `Drs_astrometrics.py` - make sure the user can't enter a blank name to
  replace the current name (and that name must be 3 characters long at
  least). [Neil Cook]
- [APERO] update date/version/changelog/notes. [Neil Cook]
- Merge branch 'v0.7.285-live' into v0.7.286-live. [Neil Cook]
- `Drs_processing.py` - add change to return of `_linear_generate_id`. [Neil
  Cook]
- Merge branch 'v0.7.285-live' into v0.7.286-live. [Neil Cook]
- [APERO] recode parallelisation of validation step. [Neil Cook]
- [APERO] push back recipemod. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.285-live' into
  v0.7.285-live. [Neil Cook]
- `Apero.tools.module.testing.drs_dev.py` - update
  self.mod-->self.recipemod. [Neil Cook]
- Move around `drs_precheck.py` functions + fix typo in `apero_astrometrics`
  `(apero_astrometric-->apero_astrometrics)` [Neil Cook]
- Move around `drs_precheck.py` functions + fix typo in `apero_astrometrics`
  `(apero_astrometric-->apero_astrometrics)` [Neil Cook]
- [APERO] upgrade validation multiprocessing [UNFINISHED, UNTESTED]
  [Neil Cook]
- [APERO] fix getting binned time. [Neil Cook]
- [APERO] update getting calibrations - now bin time to local midnight
  (all observations from the same day will use a calibration closest to
  the same point - local midnight) [UNFINISHED] [Neil Cook]
- [APERO] update getting calibrations - now bin time to local midnight
  (all observations from the same day will use a calibration closest to
  the same point - local midnight) [UNFINISHED] [Neil Cook]


0.7.285 (2023-07-05)
--------------------
- [APERO] update pool (to fix error) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.285-live' into
  v0.7.285-live. [Neil Cook]

  # Conflicts:
  #    `apero/core/instruments/default/default_constants.py`
  #    `apero/tools/module/processing/drs_processing.py`
- [APERO] add `REPROCESS_MP_TYPE_VAL` (multiprocess valid recipes) and
  allow linear/process/pool (now difference from multiprocess run
  recipes with  `REPROCESS_MP_TYPE)` [Neil Cook]
- [APERO] attempt to fix pickling issues (mac only problem) [Neil Cook]
- [APERO] `drs_processing.py` - try a fix for pickling on Mac (define
  recipemod inside parallel function = `generate_id)` [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.285-live' into
  v0.7.285-live. [Neil Cook]
- [APERO] fix pp QCC key order. [Neil Cook]
- [APERO] `drs_processing.py` - try a fix for pickling on Mac (define
  recipemod inside parallel function = `generate_id)` [Neil Cook]
- [APERO] attempt to fix pickling issues (mac only problem) [Neil Cook]
- [APERO] `drs_processing.py` - try a fix for pickling on Mac (define
  recipemod inside parallel function = `generate_id)` [Neil Cook]
- [APERO] fix pp QCC key order. [Neil Cook]
- [APERO] `drs_processing.py` - try a fix for pickling on Mac (define
  recipemod inside parallel function = `generate_id)` Issue #702. [Neil
  Cook]
- [APERO] update date/version/changelog. [Neil Cook]


0.7.284 (2023-06-14)
--------------------
- [APERO] update binary flags. [Neil Cook]
- [APERO] add fiber defintiions to recipe definitions. [Neil Cook]
- [APERO] add fiber defintiions to recipe definitions. [Neil Cook]
- [APERO] add fiber defintiions to recipe definitions. [Neil Cook]
- [NIRPS] `apero.science.preprocessing.detector.py` - fix `read_table`
  ext-->hdu. [Neil Cook]
- [APERO] `apero.tools.module.processing.drs_processing.py` - parallelize
  the validation. [Neil Cook]
- [APERO] remove use of np.int (depricated) [Neil Cook]
- Update date/version/changelog. [njcuk9999]


0.7.283 (2023-05-23)
--------------------
- Update python modules. [njcuk9999]
- [NIRPS] add posemeter values for nirps (mjd, rms, med) to header in
  preprocessing. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.282-live' into
  v0.7.282-live. [Neil Cook]
- [APERO] Lower limits for QC in `fit_tellu` (catch bad snr in template
  creation) [Neil Cook]
- [APERO] H20 to H2O. [Neil Cook]
- [NIRPS] Addd new CCF masks for NIRPS-HA and NIRPS-HE (based on
  `lbl_ccf_masks)` [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.282-stable-test' into
  v0.7.282-stable-test. [Neil Cook]
- Merge branch 'v0.7.279-live' into v0.7.282-stable-test. [Neil Cook]
- `Drs_markdown.py` - allow sectionname to be None. [Neil Cook]
- [APERO] only process the ccf for files that pass qc. [Neil Cook]
- [APERO] change the QCC for SNR preclean label. [Neil Cook]
- [APERO] update version. [Neil Cook]


0.7.282 (2023-04-27)
--------------------
- [APERO] `apero.core.utils.drs_utils.py` - fix ended=0 in rlog. [Neil
  Cook]
- [APERO] correct typo (median missing from methods) [Neil Cook]
- [APERO] fix logic when using mean (exptime should be a mean) [Neil
  Cook]
- [APERO] change all means for sums (for saturation flagging) [Neil
  Cook]
- [APERO] increase number of allowed flat files to 100 + add dprtypes
  before forcing dprtype. [Neil Cook]
- [APERO] Need first file to be a ref dprtype file (from file model)
  [Neil Cook]
- [APERO] cannot test type of file for flats (now we are combining)
  [Neil Cook]
- [APERO] FF HIGH PASS must be an integer. [Neil Cook]
- [APERO] do not reload the header or data if already loaded (otherwise
  we can't override header keys) [Neil Cook]
- [APERO] raise the limit on max number of files for `apero_loc` and
  `apero_flat`. [Neil Cook]
- [NIRPS] need to deal with multiple file definitions for `flat_dark` and
  `dark_flat`. [Neil Cook]
- [NIRPS] need to deal with multiple file definitions for `flat_dark` and
  `dark_flat`. [Neil Cook]
- [NIRPS] need to deal with multiple file definitions for `flat_dark` and
  `dark_flat`. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.279-live' into
  v0.7.279-live. [Neil Cook]
- [APERO] add source of `FF_HIGH_PASS_SIZE`. [Neil Cook]
- [APERO] flat field high pass - adjust the value to 501 pixels (for all
  instruments) [Neil Cook]
- [APERO] low pass the flat to remove low frequency components.
  [njcuk9999]
- [APERO] use the `dark_flats` and `flat_darks` in the flat recipe (combine
  with a sum) --> increased SNR. [Neil Cook]


0.7.281 (2023-04-21)
--------------------
- [APERO] replace `KW_DPRTYPES` spirou list with the nirps list (prevented
  ccfs for `OBJ_SKY` and `TELLU_SKY)` [Neil Cook]
- [APERO] `drs_markdown.py` - add custom cssclass to `add_csv_table`. [Neil
  Cook]
- `Drs_markdown.py` - deal with floating image vs one in a container.
  [Neil Cook]
- `Drs_markdown.py` - deal with floating image vs one in a container.
  [Neil Cook]
- `Drs_markdown.py` - deal with floating image vs one in a container.
  [Neil Cook]
- `Drs_markdown.py` - deal with floating image vs one in a container.
  [Neil Cook]
- `Drs_markdown.py` - deal with floating image vs one in a container.
  [Neil Cook]
- [APERO] `apero_get.py` - deal with removing hard and symlinks better.
  [Neil Cook]
- [APERO] `documentation.conf.py` - do not limit body to a max width of
  800. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.279-live' into
  v0.7.279-live. [Neil Cook]
- [APERO] `drs_markdown.py` - `add_divider` in markdown function. [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.279-live' into
  v0.7.279-live. [Neil Cook]
- [APERO] precheck: add runid/pi/obs-dir to objects with astrometric
  entry. [Neil Cook]
- [APERO] `drs_markdown` - properly format section and sub section and add
  sub sub section. [Neil Cook]
- [APERO] `ref_seq` `apero_loc` should have ref=True. [Neil Cook]


0.7.280 (2023-04-13)
--------------------
- [APERO] add extra `apero_preprocess` printouts to `nirps_he` and spirou.
  [Neil Cook]
- [APERO] add debug print out for trying to open via while loop. [Neil
  Cook]
- [APERO] `apero.recipes.*.apero_preprocess_*` - add more logging
  messages. [Neil Cook]
- [APERO] `apero.recipes.*.apero_preprocess_*` - add more logging
  messages. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.279-live' into
  v0.7.279-live. [Neil Cook]
- [NIRPS] add DRSOUTID for res file e2ds. [Neil Cook]
- [APERO] `pp_ref` add correct keys to `pp_ref` files for calib db (cannot
  update using database otherwise) [Neil Cook]
- [APERO] make `apero_database.py` --reset and --update more verbose + fix
  ended=0 in recipe log update. [Neil Cook]
- [APERO] change back to process. [Neil Cook]
- [APERO] `apero.tools.module.database.database_update.py` - add dbkind
  argument. [Neil Cook]
- [APERO] change how the --update and --rest work with
  `apero_database.py`. [Neil Cook]
- [APERO] change how the --update and --rest work with
  `apero_database.py`. [Neil Cook]
- [APERO] use pool instead of process. [Neil Cook]
- [APERO] update version and add run id to index database. [Neil Cook]


0.7.279 (2023-04-06)
--------------------
- [APERO] update run.ini scripts. [Neil Cook]
- [APERO] `apero.science.telluric.mk_tellu.py` - adjust for the slope.
  [Neil Cook]
- [APERO] `apero.science.telluric.mk_tellu.py` - change `frac_valid_min`.
  [Neil Cook]
- [APERO] `apero.science.mk_tellu` - only have the warning once per order.
  [Neil Cook]
- [APERO] `apero.science.mk_tellu` - correct typo 'warnings'-->'warning'
  [Neil Cook]
- [APERO] `apero.science.mk_tellu` - need to deal with bad orders (set to
  NaN) in SED. [Neil Cook]
- [APERO] `apero.science.mk_tellu` - need to deal with bad orders (set to
  NaN) in SED. [Neil Cook]
- [APERO] `apero.science.mk_tellu` - must have some valid points in order
  to correct image order. [Neil Cook]
- [APERO] `apero.science.mk_tellu` - `tapas_trans` needs to be per order
  (typo) [Neil Cook]
- [APERO] `apero.core.instruments.*.recipe_definitions.py` - fix order of
  the telluric correction. [Neil Cook]
- [APERO] `apero.science.telluric.mk_tellu` - add an additional step to
  use the tapas transmission to fit the sed residuals to the
  transmission (iteratively) [njcuk9999]
- [NIRPS] add ccf for `nirps_ha` and `nirps_he` with slope fit to ccf
  [SPIROU] add slope fit to ccf. [Neil Cook]
- [APERO] `apero.science.telluric.mk_tellu` - update lowpassfilter + trans
  file SED creation (filter 3 sigma outliers in hot star SED)
  [njcuk9999]
- [APERO] `apero.science.telluric.gen_tellu.py` - add `tapas_water` and
  `tapas_other` splines to preclean props. [Neil Cook]
- [APERO] `apero.tools.recipe.bin.apero_get.py` - copy if not doing
  symlink. [Neil Cook]
- [APERO] `apero.tools.recipe.bin.apero_get.py` - copy if not doing
  symlink. [Neil Cook]


0.7.278 (2023-03-29)
--------------------
- [APERO] `apero.tools.recipe.bin.apero_get.py` - add nosubdir argument
  and fix error when symlinks exist. [Neil Cook]
- [APERO] `apero.io.drs_image.py` - do not use removedirs use rmdir - do
  not remove block dirs. [Neil Cook]
- [APERO] `apero.io.drs_image.py` - do not use removedirs use rmdir. [Neil
  Cook]
- [APERO] `apero.io.drs_image.py` - do not use removedirs. [Neil Cook]
- [APERO] `apero.io.drs_image.py`: change mkdir --> makedirs. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.276-live' into
  v0.7.276-live. [Neil Cook]
- [APERO] `tools.recipes.bin.apero_get.py` - add --obsdir and `--pi_name` to
  arguments. [Neil Cook]
- [APERO] `tools.recipes.bin.apero_get.py` - add --obsdir and `--pi_name` to
  arguments. [Neil Cook]
- [APERO] `apero.io.drs_image.py`: change mkdir --> makedirs. [Neil Cook]
- [NIRPS] `apero.science.calib.dark.py` - fix typo `DRS_RAW_DIR` to
  `DRS_DATA_RAW`. [Neil Cook]
- [NIRPS] add new UNe catalogue for NIRPS-HA and `NIRPS_HE`. [Neil Cook]
- [NIRPS] add new UNe catalogue for NIRPS-HA and `NIRPS_HE`. [Neil Cook]
- [APERO] update apero astrometrics with a --check mode to check current
  database for duplicates (name, alias, ra+dec crossmatch) [njcuk9999]
- [APERO] update apero astrometrics to give aliases with and without
  spaces/underscores. [njcuk9999]
- [APERO] update apero astrometrics to give aliases with and without
  spaces/underscores. [njcuk9999]
- [APERO] update apero astrometrics to give aliases with and without
  spaces/underscores. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.276-live' into
  v0.7.276-live. [njcuk9999]
- [APERO] BUGFIX: bug when aliases end with "|" (matches "None" and
  "Null" thus when there is a null it matches the object with "|" at
  end. [njcuk9999]


0.7.277 (2023-03-14)
--------------------
- [APERO] apero.core.core - properly delete files from database. [Neil
  Cook]
- [APERO] apero.core.utils - deal with switch arguments in function call
  kwargs (return on True missing) [Neil Cook]
- [APERO] aupdate whitelists for nirps. [njcuk9999]
- [APERO] `apero.base.drs_db.py` - remove None's from list and get via a
  set (quicker than np.unique) [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.276-live' into
  v0.7.276-live. [njcuk9999]
- [APERO] `apero.science.telluric.gen_tellu.py` - Provide better error for
  tellu preclean CCF curve fit crash + add error to lang database. [Neil
  Cook]
- [APERO] `apero.science.calib.wave.py` - fix wave sol DV[AB-A] problem.
  [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.276-live' into
  v0.7.276-live. [njcuk9999]
- [APERO] `apero.recipes.*.apero_preprocess_*.py` - fix bug when `qc_params`
  fails. [Neil Cook]
- [APERO] cannot and should not write large median npy files into raw
  directory. [Neil Cook]
- [APERO] update run.ini files. [Neil Cook]
- [NIRPS] `psuedo_const.py` - need OBJECTNAME2 otherwise telluric,sky
  files fail. [Neil Cook]
- [APERO] `apero_preprocess_spirou.py` - error when qc fils in
  preprocessing. [njcuk9999]
- [NIRPS] `pseudo_const.py` - must have `KW_OBJECTNAME2` in the database.
  [njcuk9999]
- [NIRPS] `apero.science.velocity.gen_vel.py` - reduce number of decimials
  in DVRMS to get full comment. [njcuk9999]
- [NIRPS] update telluric hot star list. [njcuk9999]
- [APERO] do not update database if we are in parallel mode where we
  assume all files are in database and database has been updated
  externally. [Neil Cook]
- [APERO] fix MKFIT2 (should be AB not A --> use `sci_fiber)` [Neil Cook]


0.7.276 (2023-02-09)
--------------------
- Merge remote-tracking branch 'origin/v0.7.276-live' into
  v0.7.276-live. [njcuk9999]
- Allow creation of templates even if qc fails. [Neil Cook]
- [APERO] `apero.core.core.drs_database.py` - fix a problem with headers
  being of wrong type for s1d. [njcuk9999]
- [APERO] allow processing of LED tests (requires a switch to turn off
  input qc check) [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - allow `PP_EVERY`
  and `EXT_EVERY` for spirou. [Neil Cook]


0.8.001 (2023-01-30)
--------------------
- [APERO] update README.md (move developer and main to v0.7.275) [Neil
  Cook]
- [APERO] fix typo `apero.science.telluric.gen_tellu.py` - image.shape[0]
  --> range(image.shape[0]) [njcuk9999]
- [APERO] update date / version / documentation. [Neil Cook]


0.7.275 (2023-01-27)
--------------------
- [APERO] allow masking of bad wavelength regions in telluric correct +
  mask out bad tranmission. [Neil Cook]
- [APERO] `apero.science.telluric.template_tellu.py` - calculate the s1d
  template error and `n_valid`. [Neil Cook]
- [APERO] `apero.science.telluric.template_tellu.py` - calculate the s1d
  template error and `n_valid`. [Neil Cook]
- Merge branch 'v0.7.273-live' into v0.7.267-live. [Neil Cook]
- [APERO] recalculate template RMS + linearize template bcols between
  e2ds and s1d [NIRPS] change `MKTEMPLATE_SNR_ORDER` 33-->59. [Neil Cook]


0.7.274 (2023-01-25)
--------------------
- [APERO] fix not having a --since option. [njcuk9999]
- [APERO] `apero_go.py` - add --setup option. [njcuk9999]
- [APERO] check that --since argument is a valid date+ [njcuk9999]
- [APERO] add a --since argument to `drs_get.py`. [njcuk9999]
- [APERO] low-pass hot star template + deconv=median for hot stars
  (update `MKTEMPLATE_HOTSTAR_KER_VEL` dtype) [njcuk9999]
- [APERO] low-pass hot star template + deconv=median for hot stars
  (update imports) [njcuk9999]
- [APERO] low-pass hot star template + deconv=median for hot stars.
  [njcuk9999]
- [NIRPS] `apero.science.telluric.gen_tellu.py` - `finite_res_correction`
  now requires params (For threshold) [njcuk9999]
- [NIRPS] fix sky corr being applied twice for nirps and fix
  convergence. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.273-live' into
  v0.7.273-live. [njcuk9999]
- [APERO] update `install.py` `module_translation`. [Neil Cook]
- [NIRPS] `gen_tellu.py` - filter over bad finite res corrections.
  [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.273-live' into
  v0.7.273-live. [Neil Cook]
- [NIRPS] update skymodels (error in calculation) [njcuk9999]
- [APERO] `apero.science.calib.wave.py` - update key in table  to key in
  table.colnames. [Neil Cook]
- [APERO] update requirements. [Neil Cook]
- [APERO] update readme. [Neil Cook]
- Merge branch 'v0.7.273-live' into developer. [Neil Cook]

  # Conflicts:
  #    .gitignore
  #    README.md
  #    `apero/core/core/drs_database.py`
  #    `apero/core/core/drs_startup.py`
  #    `apero/core/instruments/default/default_config.py`
  #    `apero/core/instruments/default/default_constants.py`
  #    `apero/core/instruments/spirou/default_constants.py`
  #    `apero/core/instruments/spirou/file_definitions.py`
  #    `apero/core/instruments/spirou/recipe_definitions.py`
  #    apero/core/math/general.py
  #    `apero/data/spirou/reset/runs/calib_run.ini`
  #    `apero/data/spirou/reset/runs/complete_run.ini`
  #    `apero/data/spirou/reset/runs/mini_run.ini`
  #    `apero/data/spirou/reset/runs/other_run.ini`
  #    `apero/data/spirou/reset/runs/science_run.ini`
  #    `apero/data/spirou/reset/runs/trigger_night_calib_run.ini`
  #    apero/lang/backup/language.xls
  #    apero/lang/databases/language.xls
  #    `apero/recipes/spirou/apero_ccf_spirou.py`
  #    `apero/recipes/spirou/cal_thermal_spirou.py`
  #    apero/science/calib/localisation.py
  #    apero/science/calib/shape.py
  #    apero/science/calib/wave.py
  #    apero/science/extract/berv.py
  #    apero/science/polar/general.py
  #    `apero/science/telluric/gen_tellu.py`
  #    `apero/science/velocity/gen_vel.py`
  #    `apero/tools/module/setup/drs_processing.py`
  #    `apero/tools/recipes/bin/apero_processing.py`
  #    `apero/tools/recipes/spirou/apero_drift_spirou.py`
  #    `apero/tools/recipes/spirou/apero_expmeter_spirou.py`
  #    changelog.md
  #    documentation/working/conf.py
  #    documentation/working/index.rst
  #    documentation/working/main/misc/changelog.rst
  #    version.txt
- [APERO] update date/version/docs. [Neil Cook]
- Update `peak_number` rounding issue. [Neil Cook]
- Merge remote-tracking branch 'origin/developer' into developer. [Neil
  Cook]
- Merge branch 'master' into developer. [Neil Cook]
- `Science.extract.berv.py` - `get_berv` should warn when barycorrpy fails.
  [Neil Cook]
- Merge remote-tracking branch 'origin/developer' into developer. [Neil
  Cook]
- Merge remote-tracking branch 'origin/developer' into developer.
  [njcuk9999]
- `Apero.science.calib.shape.py` - Problem with shape when maximum
  correlation between FPs split between pixels (Issue #668) [njcuk9999]
- `Apero.core.instruments.spirou.file_definitions.py` - `RAW_LFC_FP` did not
  have outfunc - add outfunc=out.blank. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - `leak_master`
  should be after thermal master. [Neil Cook]
- `Apero.data.spirou.reset.runs.other_run.ini` - add LFCFP and FPLFC to
  other run.ini file. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` +
  `recipe_definitions.py` - add LFCFP and FPLFC to sequences. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` +
  `recipe_definitions.py` - add LFCFP and FPLFC to sequences. [Neil Cook]
- `Apero.tools.module.setup.drs_processing.py` - `_split_string_list` - if
  `allow_whitespace` must return a list not string. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - `_split_string_list` should
  not split by white space unless directly told to (allows spaces in
  filenames) [njcuk9999]
- `Apero.recipes.spirou.cal_ccf_spirou.py` - make sure A and B can be used
  as science fibers. [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - update
  `DRIFT_DPRTYPES` - (add `FP_DARK)` [Neil Cook]
- `Apero.recipes.spirou.cal_thermal_spirou.py` - `thermal_files` are not
  indexed - correct this. [Neil Cook]
- `Apero.science.calib.localisation.py` + `wave.py` - add `KW_PID` to writing
  functions. [Neil Cook]
- Merge remote-tracking branch 'origin/developer' into developer.
  [njcuk9999]
- Update README.md. [Neil Cook]

  correct typo
- `Apero.science.telluric.gen_tellu.py` - deal with Etienne using 0 as
  flag - bad bad bad. [njcuk9999]
- `Tools.recipe.spirou.cal_drift_spirou.py` - update output filename.
  [Neil Cook]
- `Tools.recipe.spirou.cal_drift_spirou.py` - allow `OBJ_FP` and `DARK_FP`
  files (and deal with fibers not containing FP) [Neil Cook]
- `Apero.science.calib.localisation.py` - fix qc logic for `MAX_RMPTS_POS`
  and `MAX_RMPTS_WID`. [Neil Cook]
- `Apero.core.core.drs_startup.py` - pep8 change. [Neil Cook]
- `Cal_expmeter_spirou.py` - update output filename based on input fibers.
  [Neil Cook]
- `Apero.core.core.drs_startup.py` - try to fix integer scalar bug. [Neil
  Cook]
- `Apero.tools.recipes.spirou.cal_expmeter_spirou.py` - add --fibers
  option. [Neil Cook]
- Update date/version/changelog/readme/documentation. [Neil Cook]


0.7.273 (2023-01-23)
--------------------
- [NIRPS] update telluric list. [njcuk9999]
- [APERO] `apero.science.telluric.gen_tellu.py` - correct typo for failing
  precleaned files. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.267-live' into
  v0.7.267-live. [njcuk9999]
- [APERO] correct params['INPUTS'] for FINITERES. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.267-live' into
  v0.7.267-live. [njcuk9999]
- [APERO] update date/version/docs. [Neil Cook]
- [NIRPS] update `sky_model` (ha and he) [njcuk9999]
- [APERO] `apero.science.telluric.gen_tellu.py` - fix spline in finite
  res. [njcuk9999]


0.7.272 (2023-01-19)
--------------------
- [APERO] allow switching on and off of finite res corr (via params and
  user input) + add header key that finite res was/wasn't done. [Neil
  Cook]
- [APERO] `ref_calib_run.ini` should not have `RUN_OBS_DIR` set to
  `DEFAULT_REF_OBSDIR` (we need `FP_FP` from all nights) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.267-live' into
  v0.7.267-live. [njcuk9999]
- [APERO] `apero.science.telluric.gen_tellu.py` - deal with edge effects
  in `wave_to_wave`. [Neil Cook]
- [APERO] `apero.science.calib.gen_calib.py` - fix typo in `check_fp`.
  [njcuk9999]
- [APERO] `apero.science.preprocessing.detector.py` - flag pixels that
  have inconsistent intercept in LED. [Neil Cook]
- [APERO] `apero.science.preprocessing.detector.py` - flag pixels that
  have inconsistent intercept in LED. [Neil Cook]
- [APERO] do not do science capacitive coupling correction for HC files.
  [Neil Cook]
- [NIRPS] apero.science.preprocessing.detector - do not sigma clip
  columns when we are creating a mask. [Neil Cook]
- [APERO] `apero.science.preprocessing.detector.py` - account for NaNs in
  butterfly maps. [Neil Cook]
- [APERO] `apero.science.telluric.gen_tellu.py` - correct (bad) changes
  for finite res. [Neil Cook]
- [APERO] `apero.science.telluric.gen_tellu.py` - correct (bad) changes
  for finite res. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.267-live' into
  v0.7.267-live. [Neil Cook]
- [NIRPS] correct `nirps_correction`. [Neil Cook]
- [NIRPS] `science.preprocessing.detector.py` - correct typos. [Neil Cook]
- [NIRPS] `science.preprocessing.detector.py` - correct of the first read
  of the amplifiers. [Neil Cook]
- [NIRPS] `science.preprocessing.detector.py` - correct of the first read
  of the amplifiers. [Neil Cook]
- [APERO]
  `apero.science.telluric.template_tellu.create_deconvolved_template` do
  not copy over flux (call flux0 as input) [Neil Cook]


0.7.271 (2023-01-17)
--------------------
- [APERO] `apero.core.math.gen_math.py` - add typing in `square_medbin`.
  [Neil Cook]
- [APERO] `science.telluric.gen_tellu.py` - fix that
  `qc_exit_tellu_preclean` fails without `image_e2ds_ini`
  `(PRE_SKYCORR_IMAGE)` [Neil Cook]
- [NIRPS] `science.preprocessing.detector.py` - fix nirps pp mask. [Neil
  Cook]
- [APERO] correct A and B telluric properly (sky + finite resolution)
  [Neil Cook]
- [APERO] correct A and B telluric properly (sky + finite resolution)
  [Neil Cook]
- [NIRPS] `apero.core.utils.drs_utils.py` - fix that times are a numpy
  array. [njcuk9999]
- [APERO] correct `post_t_file` (OHLINE, SKYCORR etc) [Neil Cook]
- [APERO] finish adjustments to finite resolution model. [Neil Cook]
- [APERO] add finite resolution effects code. [Neil Cook]
- [APERO] print progress on capacitive coupling. [Neil Cook]
- [NIRPS] add in the capacitive coupling from sci flux (for NIRPS) [Neil
  Cook]
- [APERO] add in the capacitive coupling from sci flux. [Neil Cook]


0.7.270 (2023-01-13)
--------------------
- [APERO] correct typo (bug) cavity[0] must have the pedestal added
  before updating by `mean_hc_vel` - all wave sols are wrong without this
  fix. [njcuk9999]
- [APERO] typo `correct_capacitive_coupling_pattern` -->
  `correct_capacitive_coupling`. [Neil Cook]
- [NIRPS] minor bug fixes for variable resolution. [njcuk9999]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [APERO] correct the capacitive coupling pattern using the amplifier
  bias model. [Neil Cook]
- [NIRPS] correct + speed variable resolution convolution, add `sky_model`
  for NIRPS HA. [njcuk9999]
- [APERO] add in variable resolution for the tellu convolution.
  [njcuk9999]
- [APERO] correct s1d res maps (needed blaze) [njcuk9999]
- [APERO] add s1d res amp/fwhm/expo files. [njcuk9999]
- Merge branch 'v0.7.261-live' into v0.7.267-live. [njcuk9999]
- [APERO] `apero.core.math.gen_math.py` - deal with nans for robust
  chebyshev. [njcuk9999]


0.7.269 (2023-01-10)
--------------------
- [APERO] create s1d res map [unfinished] [Neil Cook]
- [NIRPS] sky corr changes. [njcuk9999]
- [NIRPS] remove ravel from possible Nones. [Neil Cook]
- [NIRPS] remove ravel from possible Nones. [Neil Cook]
- [NIRPS] correct typo np.nqnwum --> np.nansum. [Neil Cook]
- Merge branch 'v0.7.261-live' into v0.7.267-live. [Neil Cook]
- [NIRPS] deal with not having the `KW_CAV_PEDESTAL` key. [Neil Cook]
- [NIRPS] add sky correction. [Neil Cook]
- [NIRPS] add sky correction. [Neil Cook]
- Merge branch 'v0.7.261-live' into v0.7.259-nirps-test. [Neil Cook]
- [NIRPS] add sky correction. [Neil Cook]
- [NIRPS] plan for res convolve change. [Neil Cook]
- [NIRPS] add `apero_skycorr_nirps_he.py` [UNFINISHED] [Neil Cook]
- [NIRPS] add sky model correction to telluric `mk_tellu` and `fit_tellu`
  codes. [Neil Cook]


0.7.268 (2022-12-23)
--------------------
- [APERO] update `apero_database.py` database names. [njcuk9999]
- [APERO] update date/version/docs/changelog. [njcuk9999]


0.7.267 (2022-12-22)
--------------------
- [APERO] change continuity for wave to chebyshev. [Neil Cook]
- [APERO] add sigma cut criteria on the CCF FWHM for the mean CCF
  profile. [Neil Cook]
- [APERO] add sigma cut criteria on the CCF FWHM for the mean CCF
  profile. [Neil Cook]
- [APERO] do not do nsig CCF cut for FP. [Neil Cook]
- [APERO] set a minimum value for allowed CCF fit (peak CCF < 5sigma)
  [Neil Cook]


0.7.266 (2022-12-21)
--------------------
- [APERO] fix key error with `CAVITY_PEDESTAL`. [Neil Cook]
- [APERO] add res e2ds to wave sol. [njcuk9999]
- [APERO] add a resolution e2ds map for amp/fwhm/expo. [Neil Cook]
- [APERO] improve wave solution with more cavity fit using chebyshev.
  [njcuk9999]
- [APERO] try making wave solution converge across machines. [Neil Cook]
- [APERO] `apero.core.math.gen_math.py` - update `robust_polyfit` and
  `robust_chebyfit` to be fuzzy at edges. [Neil Cook]
- [APERO] `apero.core.math.gen_math.py` - update `robust_polyfit` and
  `robust_chebyfit` to be fuzzy at edges. [Neil Cook]
- [APERO] `apero.core.math.gen_math.py` - update `robust_polyfit` and
  `robust_chebyfit` to be fuzzy at edges. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.261-live' into
  v0.7.261-live. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.261-live' into
  v0.7.261-live. [Neil Cook]
- [APERO] correct typo. [Neil Cook]
- [APERO] `apero.core.math.gen_math.py` - update `robust_polyfit` and
  `robust_chebyfit` to be fuzzy at edges. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.259-nirps-test' into
  v0.7.259-nirps-test. [njcuk9999]

  # Conflicts:
  #    `apero/data/spirou/telluric/sky_PCs.fits`
- [APERO] update `sky_PCs.fits`. [Neil Cook]
- [SPIROU] update `sky_PCs.fits` (needed to be flipped in shape)
  [njcuk9999]


0.7.265 (2022-12-13)
--------------------
- [APERO] storage for optimizing code. [Neil Cook]
- [APERO] storage for optimizing code. [Neil Cook]
- Merge branch 'v0.7.261-live' into v0.7.259-nirps-test. [Neil Cook]
- [APERO] implement a locking for orderps file so we don't try to write
  it and read it at the same time (should prevent an error we are
  getting in extraction) [Neil Cook]
- [APERO] fix ycents for AB,A,B spirou (change added for NIRPS) in order
  table. [Neil Cook]
- [APERO] fix ycents for AB,A,B spirou (change added for NIRPS) in order
  table. [Neil Cook]
- [APERO] fix ycents for AB,A,B spirou (change added for NIRPS) in order
  table. [Neil Cook]
- Merge branch 'v0.7.259-nirps-test' into v0.7.261-live. [Neil Cook]
- [APERO] update date/version/docs. [Neil Cook]
- [NIRPS] switch sequences for EFF,SKY,SKY and DARK,SKY. [njcuk9999]
- [NIRPS] add `calculate_dxmap_nirps` to both modes (rename from
  `calculate_dxmap_nirpshe)` [njcuk9999]
- [NIRPS] add `calculate_dxmap_nirps` to both modes (rename from
  `calculate_dxmap_nirpshe)` [njcuk9999]
- [APERO] `apero.science.extract.gen_ext.py` - better handle trying shapel
  file (when multiple files try to write it at once) [Neil Cook]
- [NIRPS] `apero.recipes.nirps_ha.apero_preprocess_nirps_ha.py` - fix
  loading of led lat. [Neil Cook]
- [APERO] add --plot=4 (select plots) and fix --fpref. [njcuk9999]
- [NIRPS] fix LED flat creation + update run.ini files. [Neil Cook]
- [NIRPS] fix LED flat creation + combine (for hash code) + save to
  calibDB. [Neil Cook]


0.7.264 (2022-12-08)
--------------------
- [NIRPS] update LED flat creation. [Neil Cook]
- [NIRPS] update preprocessing codes to use `LED_FLAT` from calibrations.
  [Neil Cook]
- [APERO] update `apero_get` + documentation. [Neil Cook]
- [APERO] update `apero_get.py`. [njcuk9999]
- [APERO] `apero_get.py` allow wildcard for --objnames. [Neil Cook]
- [NIRPS] Add LED flat creation to `PP_REF`. [Neil Cook]
- [APERO] update sky model. [njcuk9999]
- [APERO] require wavelength solution to be within 7 days if a night
  calibration. [njcuk9999]
- [APERO] try to fix problem with `shapel_orderps` FileNotFoundError.
  [Neil Cook]
- [APERO] add order table (for extracted files) + `WAVE_POLY_TYPE` +
  `LOC_POLY_TYPE`. [Neil Cook]
- [APERO] add order table (for extracted files) + `WAVE_POLY_TYPE` +
  `LOC_POLY_TYPE`. [Neil Cook]
- [APERO] add order table (for extracted files) + `WAVE_POLY_TYPE` +
  `LOC_POLY_TYPE`. [Neil Cook]
- [APERO] add poly type to loco keys loaded from locofile. [njcuk9999]
- [NIRPS] remove extraction bad pixel flagging for HA-A, HA-B, HE-B
  fibers [APERO] add loc and wave poly coeff type (Chebyshev)
  [njcuk9999]


0.7.263 (2022-11-30)
--------------------
- [NIRPS] change s1d max wavelength. [njcuk9999]
- [APERO] add `led_flat` code + allow forcing only telluric preclean.
  [njcuk9999]
- [APERO] add `led_flat`. [njcuk9999]
- [APERO] allow a constant to determine the min exptime for darks in the
  `dark_ref`. [njcuk9999]
- [APERO] must add to e2dsoutputs for leak correction to work.
  [njcuk9999]
- [NIRPS] update the list of telluric stars. [njcuk9999]
- [NIRPS] `apero.tools.module.processing.drs_processing.py` - fix skip
  list with `INCLUDE_OBS_DIRS` and `EXCLUDE_OBS_DIRS` (param--> param.listp)
  [njcuk9999]
- [NIRPS] `apero.science.gen_ext.py` - allow override of fibers for
  fplines calculation (for `FP_FP` tests) [njcuk9999]
- [NIRPS] `apero.science.calib.localisation.py` - change max to a
  percentile in the order loc label (avoids picking up pixels outside
  order for width measurement) [njcuk9999]
- [NIRPS] update `nirps_he` `recipe_definitions` (add `PP_EVERY` and
  `EXT_EVERY)` [Neil Cook]


0.7.262 (2022-11-15)
--------------------
- [APERO] Add `PP_EVERY` to `pp_seq_opt` and `EXTRACT_EVERY` to `eng_seq` (used
  in `other_run.ini)` to preprocess and extract everything (no calibs)
  [Neil Cook]
- [NIRPS] update HE and HA default wave solution. [Neil Cook]
- [NIRPS] updates for nirps HE wave solution. [Neil Cook]
- [APERO] update reset.calib.csv and `deafult_constants` for wave
  constants. [Neil Cook]
- [APERO] update nirps ref wave solutions. [Neil Cook]
- [APERO] nirps updates for wave sol. [Neil Cook]


0.7.261 (2022-11-10)
--------------------
- [APERO]doc string / typing /pcheck / pep8 update. [Neil Cook]
- Merge branch 'v0.7.259-working' into v0.7.259-nirps-test. [Neil Cook]
- Merge branch 'v0.7.259-nirps-test' into v0.7.259-working. [Neil Cook]
- [APERO] fix exposure meter. [Neil Cook]
- [APERO] doc string/ typing / pcheck / pep8 updates. [Neil Cook]
- [APERO] `localisation.py` - remove cross term between coefficients in
  the loco fit. [Neil Cook]
- [NIRPS] update orders and order position. [Neil Cook]


0.7.260 (2022-11-07)
--------------------
- [NIRPS] use chebyshev in the continuity fit. [Neil Cook]
- [NIRPS] use chebyshev in the continuity fit. [Neil Cook]
- [NIRPS] use chebyshev in the continuity fit. [Neil Cook]
- [NIRPS] use chebyshev in the continuity fit. [Neil Cook]
- [NIRPS] update number of orders (75--> 74) and `LOC_YDET_MIN`. [Neil
  Cook]
- [NIRPS] update number of orders (74--> 75) [Neil Cook]
- [NIRPS] update `LOC_YDET_MAX`, `LOC_YDET_MAX`. [Neil Cook]
- [NIRPS] back to 74 orders but move `LOC_YDET_MAX`. [Neil Cook]
- [NIRPS] back to 73 orders but move `LOC_YDET_MAX`. [Neil Cook]
- [NIRPS] update number of orders 73 --> 74. [Neil Cook]
- [NIRPS] update number of orders 73 --> 74. [Neil Cook]
- [APERO] `install.py` - fix git python version. [Neil Cook]
- [APERO] fix problem with `leak_ref` not being a hash code file (was just
  using first file) [Neil Cook]
- [APERO] `apero.plotting.plot_functions.py` - fix broken plot (type
  reference-->ref) [Neil Cook]
- [APERO] add paper to main page. [Neil Cook]
- [APERO] fix for badpix (bstatsb) [Neil Cook]
- [APERO] update version/date/changelog/docs. [Neil Cook]


0.7.259 (2022-11-04)
--------------------
- [APERO] add git branch + git hash + python modules + python version to
  `PARAM_TABLE`. [Neil Cook]
- [APERO] pep8 and warning fixes. [Neil Cook]
- Merge branch 'v0.7.254-working' into v0.7.254-cheby. [Neil Cook]

  # Conflicts:
  #    `apero/core/math/gen_math.py`
  #    `apero/plotting/plot_functions.py`
  #    apero/science/calib/shape.py
  #    apero/science/calib/wave.py
  #    apero/tools/module/utils/inverse.py
- [APERO] push chevyshev + clean hot pix lin mini fix into working
  branch. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.254-cheby' into
  v0.7.254-cheby. [Neil Cook]
- [APERO] `apero.tools.recipes.spirou.apero_expmeter_spirou.py`. [Neil
  Cook]
- [APERO] remove linear minimization from `clean_hotpix` function. [Neil
  Cook]
- [APERO] fixes for chebyshev. [Neil Cook]
- [APERO] force jit functions to not use fastmath mode. [Neil Cook]
- [APERO] fixes to EA chebyshev code. [Neil Cook]


0.7.258 (2022-10-31)
--------------------
- Adding cheby stuff all over the place. [eartigau]
- [APERO] make sure assets directory is reset (but copy all "new" files
  to a backup assets dir) [Neil Cook]
- [APERO] re-run template after best telluric correction. [Neil Cook]
- [APERO] add zsh profiles to setup dir. [Neil Cook]
- [APERO] update import order (pycharm Ctrl+Alt+O to sort) [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.7.257 (2022-10-25)
--------------------
- [APERO] correct columns in `apero_stats.py`. [Neil Cook]
- [APERO] add file index mode to `apero_stats.py` + write
  `apero_stats_static.txt` and `apero_stats_varying.txt` to msg/report
  directory. [Neil Cook]
- [APERO] remove cook@localhost.mysql.backup file from calib reset (it
  shouldn't be here) [Neil Cook]
- [APERO] start adding "all" mode to `apero_stats.py`. [Neil Cook]
- [APERO] fix `FORCE_REFWAVE` flag in `get_wavelength` function calls. [Neil
  Cook]
- [APERO] add conda and git documentation to other documentation. [Neil
  Cook]
- [APERO] add TODO re: hard coded value. [Neil Cook]
- [APERO] add a limit to `apero_stats` memory mode. [Neil Cook]
- [APERO] update `apero_stats` memory plot. [Neil Cook]
- [APERO] add to `apero_get` documentation. [Neil Cook]
- [APERO] test of wave [EXT] memory issue. [Neil Cook]
- [APERO] test of wave [EXT] memory issue. [Neil Cook]
- [APERO] fix problem with using `setup/install.py` --update mode. [Neil
  Cook]
- [APERO] update `apero_stats` plot. [Neil Cook]


0.7.256 (2022-10-13)
--------------------
- [APERO] pep8 fixes. [Neil Cook]
- [APERO] fixes for adding log start/log end + ccf `run_file`. [Neil Cook]
- [APERO] add `LOG_START` and `LOG_END` to log database (and fix `END_TIME)` -
  will require new log database. [Neil Cook]
- [APERO] improve memory stats plot. [Neil Cook]
- [APERO] add an exact requirements module to test all packages being
  the same. [Neil Cook]
- [APERO] fix custom arguments [INPUTS] coming from run.ini file and
  --mask argument not looking in the `assets/ccf_masks` directory. [Neil
  Cook]
- [APERO] add a printout to `wave_ref_spirou` + update `apero_overall_flow`
  graph. [Neil Cook]
- [APERO] update date/version/changelog/docs. [Neil Cook]


0.7.254 (2022-09-22)
--------------------
- [APERO] test fix for pickling PseudoConstants. [Neil Cook]
- [APERO] Apply fixes for pickling Run Class. [Neil Cook]
- [APERO] `apero.science.extract.extraction.py` - fix bug is cosmic check
  res = sx - fx/amp --> res = sx - `fx*amp`. [Neil Cook]
- [APERO] `apero.core.utils.drs_startup.py` - use np.genfromtxt instead of
  np.loadtxt as there is a bug in numpy 1.23. [Neil Cook]


0.7.255 (2022-09-30)
--------------------
- [APERO] doc + pep8 `[gen_calib.py]` [Neil Cook]
- [APERO] doc + pep8 `[flat_blaze.py]` [Neil Cook]
- [APERO] doc + pep8 [background.py, badpix.py, dark.py] [Neil Cook]
- [APERO] update docs. [Neil Cook]
- [APERO] update date/version/changelog/docs. [Neil Cook]


0.7.253 (2022-09-29)
--------------------
- [APERO] add `apero_stats` memory table to report directory. [Neil Cook]
- [APERO] correct documentation schematics not appearing. [Neil Cook]
- [APERO] correct documentation schematics not appearing. [Neil Cook]
- [APERO] update versionn/date/docs/changelog. [Neil Cook]


0.7.252 (2022-09-27)
--------------------
- [APERO] continue update doc string + pep8. [Neil Cook]
- [APERO] continue update doc string + pep8. [Neil Cook]
- [APERO] continue update doc string + pep8. [Neil Cook]
- [APERO] continue update doc string + pep8. [Neil Cook]
- [APERO] `apero.core.instruments.*.file_definitions.py` - fix typo
  `_WAVESOL_REF` --> `_wavesol_ref`. [Neil Cook]
- [APERO] update program descriptions and some doc strings + pep8. [Neil
  Cook]
- [APERO] `documentation.unused.v07_docstring_update.txt` - add more
  recipes to check. [Neil Cook]
- [APERO] `documentation.unused.v07_docstring_update.txt` - add more
  recipes to check. [Neil Cook]
- [APERO] `apero.science.calib.gen_calib.py` - if not required do not
  cause error. [Neil Cook]
- [APERO] correct flat codes - combine method should be "flat" [Neil
  Cook]
- [APERO] `apero.io.drs_path.py` - reset the listdir function. [njcuk9999]


0.7.251 (2022-09-19)
--------------------
- [APERO] update doc strings + pep8 (see `v07_docstring_update.txt)` [Neil
  Cook]
- [APERO] documentation - add to useful mysql commands. [Neil Cook]
- [APERO] update doc strings + pep8 (see progress in
  `v07_docstring_update.txt)` [Neil Cook]
- [APERO] `apero.tools.module.testing.drs_stats.py` - for sqlite need the
  LIKE parameter for recipe. [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_installation.py` - fix arg return
  of `get_sqlite_settings`. [Neil Cook]
- [APERO] update doc-string + deal with pep8. [Neil Cook]
- [APERO] update doc-string + deal with pep8. [Neil Cook]


0.7.250 (2022-09-13)
--------------------
- [APERO] update language database. [Neil Cook]
- [SPIROU] documentation: add schematics back to `recipe_definitions.py`.
  [Neil Cook]
- [APERO] update some todo messages. [Neil Cook]
- [APERO] update language database to replace some text (in TODO) [Neil
  Cook]
- [APERO] `apero.science.extract.gen_ext.py` - try to stop errors when
  order profile exists but cannot be read (parallelisation issue) [Neil
  Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- [APERO] `apero.recipes.*.apero_fit_tellu*.py` - recon must be multiplied
  by blaze before creating s1d (for proper weighting) [Neil Cook]
- [APERO] `apero.science.polar.gen_pol.py` - fix factor 2 in exponent
  (from Eder) [Neil Cook]


0.7.249 (2022-09-07)
--------------------
- [APERO] `setup.install.py` - make sure config path is still the full
  path. [Neil Cook]
- [APERO] `apero.base.base.py` - fix references to allparams. [Neil Cook]
- [NIRPS] correct typo `apero_PP_REF_nirps` --> `apero_pp_ref_nirps`. [Neil
  Cook]
- [NIRPS] correct typo `apero_PP_REF_nirps` --> `apero_pp_ref_nirps`. [Neil
  Cook]
- [APERO] `apero.tools.module.setup.drs_installation.py` - save install
  params to `DRS_UCONFIG` (for re-use / debug) in install.sh. [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_installation.py` -
  `all_params['MYSQL']` parameters should be uppercase (to match sqlite)
  [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_installation.py` -
  `all_params['MYSQL']` parameters should be uppercase (to match sqlite)
  [Neil Cook]
- [APERO] `apero.core.instruments.default.grouping.py` - fix problem where
  1 entry leads to a crash. [Neil Cook]
- [APERO] fix sqlite installation error (Issue #682) [Neil Cook]
- [APERO] apero.base.base.py: typo FILEINDEX --> FINDEX. [Neil Cook]
- [APERO] test recipe documentation. [Neil Cook]
- [APERO] correct `drs_db` change. [Neil Cook]
- [APERO] update version/date/changelog/documentation. [Neil Cook]


0.7.248 (2022-08-31)
--------------------
- [APERO] manage locking better (when no PID), manage databases better
  (from one place `pconst.GET_DB_COLS()`  + base) [Neil Cook]


0.7.247 (2022-08-29)
--------------------
- [APERO] Change object database to astrometric database. [Neil Cook]
- [APERO] Change object database to astrometric database. [Neil Cook]
- Merge branch 'v0.7.242-working' into v0.7.243-working. [Neil Cook]

  # Conflicts:
  #    `apero/core/core/drs_file.py`
  #    `apero/tools/module/listing/file_explorer.py`

  Conflicts fixed
- [APERO] update references to INDEX (and make all database lower case
  for SQL) [Neil Cook]
- [APERO] documentation - update files. [Neil Cook]
- [APERO] documentation - add sequence graphml/jpg/pdf files. [Neil
  Cook]
- `Apero.tools.module.database.database_gui.py` - save the hash col before
  removing it and add it back when saving. [Neil Cook]
- Put the readme files back in /bin/ and /tools/ [Neil Cook]
- [APERO] `apero.science.telluric.template_tellu.py` - fix s1d template
  (in similar way to s1d template) [Neil Cook]


0.7.246 (2022-08-17)
--------------------
- [APERO] add to sequence schematics + descriptions. [Neil Cook]
- [APERO] update file descriptions + update documentation with file
  descriptions. [Neil Cook]
- [APERO] update file descriptions. [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_reset.py` - correct temporary
  message. [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_reset.py` - correct file list.
  [Neil Cook]
- [APERO] `apero.tools.module.setup.drs_reset.py` - speed up reset (or at
  least display a message) [Neil Cook]
- [APERO] documentation - update overview schematics (yed) [Neil Cook]
- [APERO] `apero.tools.recipes.bin/apero_stats.py` - need recipe to be
  passed (for plotting) [Neil Cook]
- [APERO] `apero.tools.recipes.bin/apero_stats.py` - need recipe to be
  passed (for plotting) [Neil Cook]
- [APERO] `apero.science.telluric.gen_tellu.py` - change pre-cleaning SNR
  criteria to be median SNR (not max) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.243-working' into
  v0.7.243-working. [Neil Cook]
- [APERO] `apero.science.telluric.template_tellu.py` - [BAD BUG] fix for
  templates - binning was incorrect if N>50 files was using only the
  first sqrt(N) files, if N<50 was using only using the first. [Neil
  Cook]
- [APERO] paper - update `apero_overall_flow` diagram. [Neil Cook]


0.7.245 (2022-08-10)
--------------------
- Merge branch 'v0.7.242-working' into v0.7.243-working. [Neil Cook]
- [APERO] `apero.tools.recipes.bin.apero_stats.py` - add memory stats to
  `apero_stats.py`. [Neil Cook]
- Update filenames master-->ref. [Neil Cook]
- Update filenames master-->ref. [Neil Cook]
- Re-add run.ini files after master-->ref. [Neil Cook]
- Re-add run.ini files after master-->ref. [Neil Cook]
- Replace "master/MASTER" with "ref/reference"  (do not use "master" as
  a word) [UNTESTED] [Neil Cook]


0.7.244 (2022-08-02)
--------------------
- [APERO] `core.instruments.*.recipe_defintions.py` - missing
  `WAVEREF_EXPECTED` from plots. [Neil Cook]
- Update `mysql_database_commands.rst`. [Neil Cook]

  Add some extra useful MySQL commands
- Add files via upload. [Neil Cook]

  add overview for paper


0.7.243 (2022-06-30)
--------------------
- [APERO] `apero.base.drs_db.py` - up the wait time for database
  connection failure (5s--> 30s) [Neil Cook]
- Up the wait time for database connection failure. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.242-working' into
  v0.7.242-working. [Neil Cook]
- [APERO] deal with nan slices in transmission. [njcuk9999]
- Update paper schematics. [Neil Cook]


0.7.242 (2022-06-23)
--------------------
- [NIRPS] modify tapas to mask unusable regions. [njcuk9999]
- [APERO] `tools.module.processing.drs_processing.py` - make `KW_OBSTYPE`
  condition depend on instrument. [njcuk9999]
- [NIRPS] adjust some tellu parameters for nirps. [njcuk9999]
- [APERO] remove shortcut to `apero_flat_spirou.py` in bin dir. [Neil
  Cook]
- Update version/date/changelog/docs. [Neil Cook]


0.7.241 (2022-06-21)
--------------------
- [APERO] `apero.core.core.drs_file.py` - deal with nans better.
  [njcuk9999]
- [APERO] `apero.core.core.drs_file.py` - deal with nans better.
  [njcuk9999]
- [NIRPS] add a `test_fp_dark` file definition. [njcuk9999]


0.7.240 (2022-06-17)
--------------------
- [APERO] small changes for update to reject database. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- [APERO] change slightly how REJECTLIST works (to allow difference
  between spirou and nirps) [Neil Cook]
- [NIRPS] `default_constants.py` - update `GL_OBJ_COL_NAME`. [njcuk9999]


0.7.239 (2022-06-14)
--------------------
- [APERO] `drs_astrometrics.py` - ask user for Teff source. [Neil Cook]
- [NIRPS] add `TEST_DARK_DARK_SKY` from EFF,SKY,SKY files and add to
  engineering seqeuence. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- [NIRPS] update hot star list. [Neil Cook]
- [NIRPS] fix typo `LW_DRS_QC` --> `KW_DRS_QC`. [njcuk9999]
- [NIRPS] undo shape change for ha (from he) [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [Neil Cook]
- [NIRPS] B fiber should be `fit_cavity` + `fit_achromatic` = False.
  [njcuk9999]
- [APERO] save preprocessing files that fail qc to disk but check in all
  recipes that qc has passed (unless user forces `no_in_qc` check)
  [njcuk9999]
- [APERO] `apero.science.calib.background.py` - slightly change how
  background subtraction is done. [njcuk9999]
- [NIRPS] add raw test dark. [Neil Cook]


0.7.238 (2022-06-09)
--------------------
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [Neil Cook]
- [NIRPS] add `pp_test_eff_sky` file definition. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- [APERO] `tools.module.processing.drs_trigger.py` - put the
  `trigger_table.fits` in a standard location (not dependent on recipe run
  location) [Neil Cook]
- [NIRPS] fix for getting object name. [njcuk9999]
- [NIRPS] `science.extract.extraction.py` - remove an extra factor of gain
  (didn't matter for SPIRou as gain=1) [njcuk9999]
- [NIRPS] update `file_definitions.py` for `RAW_FLUXSTD_SKY`. [njcuk9999]
- [NIRPS] add `TELLU_SKY` file definition. [Neil Cook]
- [APERO] update date/version/doc/changelog. [Neil Cook]


0.7.237 (2022-06-08)
--------------------
- Add FLUX,STD,SKY file definition. [njcuk9999]
- [APERO] fixes for trigger + [NIRPS] gain header key change.
  [njcuk9999]
- [APERO] fix drsfile.nosave in `copy_header/copy_hdict`. [Neil Cook]
- [APERO] do not check non calib recipes for calib run. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- Deal with `store_true` action better (when called as an argument) [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- [APERO] add a nosave option for debug/plotting/information purposes
  (no writing of files) - bug fix. [Neil Cook]
- [APERO] add a nosave option for debug/plotting/information purposes
  (no writing of files) [Neil Cook]
- [APERO] add to trigger code (tested) [Neil Cook]
- [APERO] add new wave sol for `NIRPS_HA`. [njcuk9999]


0.7.236 (2022-06-04)
--------------------
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- [APERO] first commit of very basic trigger. [Neil Cook]
- [APERO] `apero.io.drs_fits.py` - fix `read_multi` extension being None
  (deepcopy instead of array) [njcuk9999]
- [APERO] fix memory leak with bottleneck + over copying of fits reader.
  [njcuk9999]
- [NIRPS] update `nirps_he` default wave sol. [njcuk9999]
- [APERO] `apero.core.instruments.default.deafult_constants.py` -
  `BADPIX_ERODE_SIZE` and `BADPIX_DILATE_SIZE` must be integers. [njcuk9999]
- [APERO] flat - better deal with bad flat pixels. [njcuk9999]
- [APERO] badpix - add erosion + dilution factors for large bad pixels.
  [njcuk9999]
- [APERO] `apero.science.extract.extraction.py` - fix flat (do not correct
  too small or too large values) [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [Neil Cook]

  # Conflicts:
  #    `bin/apero_flat_spirou.py`
- [NIRPS] add nirps to the documentation. [Neil Cook]
- [APERO] todo deal with small number division in the flat. [njcuk9999]
- [APERO] better patch edges of large bad pixel regions [NIRPS] update
  wave sols + catalogue. [njcuk9999]


0.7.235 (2022-05-31)
--------------------
- [NIRPS] add in telluric recipes. [njcuk9999]
- [NIRPS] `apero.tools.module.processing.drs_run_ini.py` - add to run.ini
  files the nirps helios sequence. [njcuk9999]
- Add changes to allow helios to be reduced. [njcuk9999]
- Pep8 changes. [njcuk9999]
- Update default nirps he wave solution + fix typo in
  `WAVE_FIBER_OFFSET_MOD` and `WAVE_FIBER_SCALE_MOD`. [njcuk9999]
- Update default nirps he wave solution. [njcuk9999]
- `WAVEREF_EXPECTED` to take diffvelo + allow offset/sclae of wave
  solution by N pixels. [njcuk9999]
- Update header keys for `nirps_he`. [Neil Cook]


0.7.234 (2022-05-20)
--------------------
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [njcuk9999]
- Add `mk_tellu` and `mk_model` to `nirps_ha` and `nirps_he` to sequences. [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.232-working' into
  v0.7.232-working. [Neil Cook]
- Add `mk_tellu` and `mk_model` to `nirps_ha` and `nirps_he`. [Neil Cook]
- Long and lat flipped for nirps (whoops) [njcuk9999]
- Update tellu white list and default master wave sol for `nirps_ha`.
  [njcuk9999]


0.7.233 (2022-05-18)
--------------------
- Deal with no pmra/pmde in headers. [njcuk9999]
- Update `nirps_ha` wave sol. [Neil Cook]
- Update `PP_OBJ_DPRTYPES` (add `OBJ_SKY)` [Neil Cook]
- For nirps we need to test whether OBJECT not in obstype (for SKY test)
  [Neil Cook]
- Object type different for nirps - add `REPROCESS_OBJECT_TYPES`. [Neil
  Cook]
- Add `fit_tellu` and `mk_template` for `nirps_he/nirps_ha`. [Neil Cook]
- Update gain header key for nirps. [Neil Cook]
- Update exptime for nirps. [Neil Cook]
- Some speed up tests. [Neil Cook]
- Update date/version/docs/changelog. [Neil Cook]


0.7.232 (2022-05-06)
--------------------
- Merge remote-tracking branch 'origin/v0.7.228-working' into
  v0.7.228-working. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.228-working' into
  v0.7.228-working. [njcuk9999]
- Replace PandasLikeDatabase with PandasLikeDatabaseDuckDB - speeds up
  post processing by factor of 5. [njcuk9999]
- Update date/version/docs/changelog. [Neil Cook]


0.7.231 (2022-05-06)
--------------------
- `Apero.science.polar.gen_pol.py` - shift correctly all parameters stored
  in headers of the wave solution. [Neil Cook]
- Create a `pol_calib` to store shifted blaze and wave + add `WAVE_AB` ad
  `BLAZE_AB` to p.fits from `pol_calib`. [Neil Cook]
- Add a binary flag for when wave master is forced. [Neil Cook]
- `Apero.tools.recipes.bin.apero_database.py` - add a reset database
  option. [Neil Cook]
- `Apero.io.drs_path.py` - sort directories and `valid_files`. [Neil Cook]


0.7.230 (2022-05-04)
--------------------
- `Apero.science.polar.gen_pol.py` - deal with polar failing on orders
  with all NaN. [njcuk9999]
- `Mk_template` now bins to avoid loading many images + correct berv
  coverage. [Neil Cook]


0.7.229 (2022-04-29)
--------------------
- Apero.data.spirou.databases.reset.calib.csv - uhash must be unique -
  generate hash for default values. [Neil Cook]
- `Apero.tools.module.database.manage_database.py` - update database
  creation with additional unique columns in calib/tellu database. [Neil
  Cook]
- Update reset calibration database (need UHASH column) [Neil Cook]
- `Apero.tools.recipes.bin.apero_explorer.py` - correct getting hash arg.
  [Neil Cook]
- `Apero.core.core.drs_misc.py` - do not use nan for doubles in stats.
  [Neil Cook]
- `Apero.core.utils.drs_utils.py` - do not use nan for doubles. [Neil
  Cook]
- Update date/version/docs/changelog. [Neil Cook]


0.7.228 (2022-04-28)
--------------------
- Add in PID, PDATE to calibration/telluric database add in RAM/SWAP/CPU
  column to log database. [Neil Cook]
- `Apero.recipes.spirou.apero_thermal_spirou.py` - for `DARK_DARK_INT` force
  wave solution to master. [Neil Cook]
- `Apero.recipes.*.apero_extract_*.py` - add way to force wave master in
  extraction + update `recipe_definitions.py`. [Neil Cook]


0.7.227 (2022-04-26)
--------------------
- `Documentation.working.resources.default.descriptions.apero_astrometric`
  s.rst - update the notes on `apero_astrometrics`. [Neil Cook]
- `Apero_astrometrics.py` - allow aliases to be added and deal with Teff
  objname better. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - link conditions to
  run.ini file supplied (for checking `obs_dir` etc) [Neil Cook]
- `Apero.tools.module.drs_processing.py` - add `UPDATE_IDATABASE_NAME`
  run.ini parameter (to allow turning off update certain databases)
  [Neil Cook]
- Update the default run.ini files. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.225-working' into
  v0.7.225-working. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - fix problem with MJDMID
  having a NaN (float) value. [njcuk9999]
- `Apero_extract_spirou.py` - add `EXP_FPLINE` flag. [Neil Cook]
- `Apero.recipes.spirou.apero_pol_spirou.py` - do not allow files that
  failed qc to be used in polar recipe (by default) flag and return
  failure. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - remove index database
  crossmatch for qc mode (not required?) [Neil Cook]


0.7.226 (2022-04-21)
--------------------
- `Apero.tools.resources.run_in.*` - update templates for run.ini files to
  have `UPDATE_INDEX_DATABASE` flag. [Neil Cook]
- `Apero.tools.recipes.bin.apero_processing.py` - add
  `UPDATE_INDEX_DATABASE` flag so user can not update the index database
  (needs big warning about doing this) [Neil Cook]
- `Apero.science.calib.leak.py` - add in a second log for fiber loop
  [untested] [Neil Cook]
- `Apero.recipes.spirou.apero_leak_master_spirou.py` - leak master has no
  qc - update recipe.log. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - `no_qc` must update children as well.
  [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add `UPDATE_INDEX_DATABASE` to allow
  not updating index database in `apero_processing` [UNTESTED] [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - update
  `WAVE_FP_DPRLIST` (missed `POLAR_FP)` [Neil Cook]
- Update some typos in `default_keywords.py`. [Neil Cook]
- Correct typo and change `NO_DB` = False. [Neil Cook]
- `Apero.base.base.py` - update `LOG_FLAGS` to include QCPASSED. [Neil Cook]
- `Apero.base.base.py` - update `LOG_FLAGS` to include OBJ. [Neil Cook]
- Update date/version/changelog/docs. [Neil Cook]


0.7.225 (2022-04-13)
--------------------
- `Apero.science.extract.other.py` - flag when extraction file has been
  found (require RecipeLog as input to `extract_*_files` functions) [Neil
  Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - add `INT_EXT` and
  `EXT_FOUND` flags to recipes that use `apero_extract` internally. [Neil
  Cook]
- `Apero.core.instruments.*.file_definitions.py` - `WAVEM_CAV` should only
  be the main science fiber. [Neil Cook]
- `Apero.base.base.py` - add log flag descriptions - can only add flags if
  the are here. [Neil Cook]


0.7.224 (2022-04-11)
--------------------
- `Apero.tools.processing.drs_processing.py` - update `skip_clean_arguments`
  to allow additional arguments. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` -
  `apero_water_master` should be a master recipe always. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - correct typo
  `"apero_loc.set_flags`" --> `"apero_extract.set_flags`" [Neil Cook]


0.7.223 (2022-04-09)
--------------------
- Merge branch 'v0.7.219-stable-test' into v0.7.221-working. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.219-stable-test' into
  v0.7.219-stable-test. [Neil Cook]
- Fix tellurics and thermal problems. [njcuk9999]


0.7.222 (2022-04-03)
--------------------
- Update documentation. [Neil Cook]
- Update documentation. [Neil Cook]
- Update date/version/docs. [Neil Cook]


0.7.221 (2022-04-02)
--------------------
- Fixes for outclass (telluric centric fixes) [Neil Cook]
- Fix problems with outclass + move `running/in_parallel/ended` to binary
  flag + add a flag mode in `apero_explorer.py`. [Neil Cook]


0.7.220 (2022-03-31)
--------------------
- Replace outfunc with outclass (a output file class) [Neil Cook]
- Update error for database not found (was ambiguous) [Neil Cook]
- Update date/version/docs/changelog. [Neil Cook]


0.7.219 (2022-03-27)
--------------------
- Bug fixes after nirps merge. [Neil Cook]
- Merge branch 'v0.7.213-nirps-he' into v0.7.213-working. [Neil Cook]
- `Apero.tools.moduile.processing.drs_grouping_functions.py` -
  `get_non_file_args()`: add an additional check on group being none
  before assigning `obs_dir` to group. [Neil Cook]
- Add back in `pp_master` for `nirps_he`. [Neil Cook]
- Re-run run.ini for nirps he. [Neil Cook]
- Merge branch 'v0.7.213-working' into v0.7.213-nirps-he. [Neil Cook]

  # Conflicts:
  #    `apero/core/core/drs_file.py`
- `Apero_shape_master_nirps_he.py` - update shape for nirps he + start
  preprocess changes. [Neil Cook]
- Add flags to log database and test with preprocessing and loc. [Neil
  Cook]


0.7.218 (2022-03-24)
--------------------
- `Apero.core.core.drs_base_classes.py` - add binary dictionary (to store
  flags) - eventually use for log. [Neil Cook]
- `Apero.core.core.drs_file.py` - switch axis in combined table - header
  keys are columns. [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - template header is now a
  combined header. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.7.215 (2022-03-21)
--------------------
- `Apero.core.*.recipe_definitions.py` - master night non master recipes
  should not have master=True, night cals should not have thermal
  master=True. [Neil Cook]
- `Drs_stats.py` - correct typo `LOG_FILE` --> LOGFILE. [Neil Cook]
- `Drs_stats.py` - add logfile and runstring to output timing stats. [Neil
  Cook]
- `Drs_stats.py` - add pid to log output. [Neil Cook]


0.7.214 (2022-03-15)
--------------------
- Update run.ini files and all negative number of cores (to mean
  N-abs(cores)) [Neil Cook]
- `Apero_flat_*.py` - remove e2ds saving. [Neil Cook]
- `Apero.core.constants.param_functions.py` + `apero.core.core.drs_file.py`
  - add iloc (index database entries) to `PARAM_TABLE`. [Neil Cook]
- `Apero.recipes.spirou.apero_flat_*.py` - write e2ds and e2dsll for flat
  files (as debug) [Neil Cook]
- `Apero.science.extract.gen_ext.py` - make sure orderps files are added
  to index database (and have `PARAM_TABLE)` [ID by DRS-TEST] [Neil Cook]
- `Apero.science.calib.dark.py` - fix bad naming of `dark_master` extensions
  [ID by DRS-TESTS] [Neil Cook]


0.7.216 (2022-03-11)
--------------------
- `Install.py` - fix `database_ask` criteria for reject database. [Neil
  Cook]
- `Install.py` - do not validate if --help in args. [Neil Cook]
- Update installer with reject database installation. [Neil Cook]
- `Apero_preprocessing.py` - correct `reject_infile()` [Neil Cook]
- Update `apero_go.py`. [Neil Cook]
- Update run.ini files and add reject database to `apero_database.py`.
  [Neil Cook]
- Update date, version, documentation, changelog. [Neil Cook]


0.7.213 (2022-03-09)
--------------------
- Merge branch 'v0.7.209-neil-test' into v0.7.208-working. [Neil Cook]
- `Apero.science.calib.shape.py` - try again to close file. [Neil Cook]
- `Apero.science.calib.shape.py` - must close file here. [Neil Cook]
- Merge branch 'v0.7.208-stable-test' into v0.7.208-working. [Neil Cook]
- `Apero.tools.recipes.bin.apero_astrometrics.py` - add an option to seach
  proper motion catalogues for the name even if it isn't found in
  SIMBAD. [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - get the file reject list from
  the reject database. [Neil Cook]
- Merge branch 'v0.7.208-stable-test' into v0.7.208-working. [Neil Cook]
- `Apero_astrometrics` - correct bug with multiple teff values.
  [njcuk9999]


0.7.212 (2022-03-05)
--------------------
- Update language database. [Neil Cook]
- Merge branch 'v0.7.208-stable-test' into v0.7.208-working. [Neil Cook]

  # Conflicts:
  #    apero/science/extract/extraction.py
- `Apero.science.extract.extraction.py` - correct typo in extraction.
  [Neil Cook]
- `Apero.science.extract.extraction.py` - correct typo in extraction.
  [Neil Cook]
- Merge branch 'v0.7.208-stable-test' into v0.7.208-working. [Neil Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - make teff selection
  more logical. [Neil Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - make teff selection
  more logical. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.208-stable-test' into
  v0.7.208-stable-test. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.208-stable-test' into
  v0.7.208-stable-test. [njcuk9999]
- `Apero_astrometrics` - correct bug with multiple teff values.
  [njcuk9999]
- Update a todo. [Neil Cook]
- Continue adding reject database. [Neil Cook]
- Merge branch 'v0.7.208-stable-test' into v0.7.208-working. [Neil Cook]
- `Apeor.plotting.plot_functions.py` - remove forced plot option. [Neil
  Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - deal better with
  masked rv value (no "--") [Neil Cook]
- Add reject database. [Neil Cook]
- Add reject database. [Neil Cook]


0.7.211 (2022-03-03)
--------------------
- `Apero.science.extraction.py` - rearrange equations for speed up. [Neil
  Cook]
- Replace np.nanfunc with mp.nanfunc (speed up) [Neil Cook]
- `Apero_precheck` - get time from sci data if no calibrations.
  [njcuk9999]
- Merge branch 'v0.7.208-working' into v0.7.208-stable-test. [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - update recipe
  definitions to add `calib_required` for those calibs that must be
  checked. [Neil Cook]
- `Apero.core.core.drs_database.py` - only use "USED=1" objects from
  object database. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - remove the todo line
  setting all objs to be refound. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - do not get the index
  database if in timing mode (we don't need it) [Neil Cook]
- Merge branch 'v0.7.208-working' into v0.7.208-stable-test. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - do not crossmatch with index
  for timing mode. [Neil Cook]
- Merge branch 'v0.7.208-working' into v0.7.208-stable-test. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - add dt vs start time plot.
  [Neil Cook]
- Merge branch 'v0.7.208-working' into v0.7.208-stable-test. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - use original names for
  use in astrometrics. [Neil Cook]
- Update requirements for `astro_visu`. [Neil Cook]
- Update requirements for `astro_visu`. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update requirements for LAM (downgrade bottleneck) [Neil Cook]


0.7.210 (2022-02-23)
--------------------
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Update visualisation test code. [Neil Cook]
- Test visualisations. [Neil Cook]


0.7.209 (2022-02-17)
--------------------
- `Apero.plotting.plot_functions.py.plot_stats_timing_plot` - deal with
  nrows=1 ncols=1. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - deal with None in `END_TIME`
  better. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - update timing error. [Neil
  Cook]
- `Apero.plotting.plot_functions.py` - deal with case where nrows = 1.
  [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - fix typo. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - only check obj names
  for science / hot star observations. [Neil Cook]
- Update date/version/docs. [Neil Cook]


0.7.208 (2022-02-11)
--------------------
- Copyraw and add version to setup codes, point README.md the
  documentation. [Neil Cook]
- Move the raw sym/copy in `apero_get` into setup (outside apero frame
  work) as it is probably only going to be used before installation.
  [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - correct typo
  `filepostfile.out_requiredd` --> `filepostfile.out_required`. [Neil Cook]
- Merge branch 'v0.7.205-stable-test' into v0.7.205-working. [Neil Cook]
- `Apero.science.calib.wave.py` - remove reference to NAXIS2 and NAXIS1.
  [Neil Cook]
- `Apero.tools.recipes.bin.apero_visu.py` - for later use. [Neil Cook]
- `Apero.recipes.*.apero_wave_master_*.py`. [Neil Cook]


0.7.207 (2022-02-07)
--------------------
- `Apero.tools.recipes.bin.apero_get.py` - create `user_outdir` path if it
  doesn't exist. [Neil Cook]
- `Apero.tools.recipes.bin.apero_get.py` - add in a raw copy/symlink
  option. [Neil Cook]
- `Apero.tools.recipes.bin.apero_get.py` - move functionality to module +
  finish changes to filter by qc failures. [njcuk9999]
- `Apero.tools.recipes.bin.apero_get.py` - only copy those with qc passed.
  [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.205-stable-test' into
  v0.7.205-stable-test. [Neil Cook]
- Update how null columns are handled. [njcuk9999]
- `Apero.science.calib.thermal.py` - fix ratio1 and ratio2 in Null case
  (should be ratio) [Neil Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - add way to not check
  pm (for dev only) [Neil Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - add way to attempt
  to update all missing teffs. [Neil Cook]
- `Apero.tools.module.database.drs_astrometrics.py` - add way to attempt
  to update all missing teffs. [Neil Cook]
- `Apero.tools.module.database.dsr_astrometrics.py` - work on updating
  teffs. [njcuk9999]
- `Apero.tools.module.database.manage_database.py` - separate update and
  get object database functions. [Neil Cook]
- `Apero_astrometrics.py` - add teff from disk if possible. [Neil Cook]
- Update run.ini files. [Neil Cook]
- `Apero.core.core.drs_database.py` - return only `OBS_NAMES[objname]`
  [njcuk9999]


0.7.206 (2022-02-03)
--------------------
- Update some documentation. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.7.205 (2022-02-01)
--------------------
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - deal with SKY and CALIB
  object names. [njcuk9999]
- `Apero.core.core.drs_database.py` - deal with special (calib/sky/test)
  better when trying to find aliases (don't check) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- `Apero.core.core.drs_fil.py` - update DrsInputFile children to have
  instrument input. [njcuk9999]
- Update `PP_OBJ_DPRTYPES`. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]

  # Conflicts:
  #    `apero/tools/recipes/bin/apero_get.py`
- Obj fix. [Neil Cook]
- `Find_objname` requires rawobjname not objname. [njcuk9999]
- `Apero.core.core.drs_database.py` - save a list of obs names so we don't
  do this multiple times per object. [Neil Cook]
- `Apero.tools.module.processing.drs_run_ini.py` - correct `pp_seq_opt` (set
  all `RUN_PP_XXX` to False except those we want as True by default) [Neil
  Cook]
- Continue dealing with aliases to object names. [Neil Cook]
- Update documentation. [Neil Cook]
- Update documentation. [Neil Cook]
- Update documentation. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- Update object database / index database / header fix to check object
  name aliases for raw data and in preprocessing (everything after this
  point uses preprocessing names) [Neil Cook]


0.7.204 (2022-01-29)
--------------------
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- Updates to `apero_astrometrics.py` to query pm catalogues for new
  coords/motions. [Neil Cook]
- `Apero_leak_master_nirps_he.py` - fix extract name (ha-->he) [Neil Cook]
- `Apero.plotting.plot_functions.py` - flip figure rows/cols + stokes
  parameter. [Neil Cook]
- `Apero.plotting.plot_functions.py` - LSD param typos. [Neil Cook]
- `Apero.plotting.plot_functions.py` - pprops and lprops --> props. [Neil
  Cook]
- `Apero.science.polar.lsd.py` - linevelo[jpos] --> linevelo[pix] [Neil
  Cook]
- `Apero.plotting.plot_functions.py` - typo tab:b -> tab:blue. [Neil Cook]
- Add labels to `plot_polar_fit_cont` graph. [Neil Cook]


0.7.203 (2022-01-28)
--------------------
- `Apero.plotting.plot_functions.py` - more plot fixes. [Neil Cook]
- `Apero.plotting.plot_functions.py` - more plot fixes. [Neil Cook]
- `Apero.plotting.plot_functions.py` - more plot fixes. [Neil Cook]
- `Apero.plotting.plot_functions.py` - correct more typos. [Neil Cook]
- `Apero.plotting.plot_functions.py` - correct typo NEXPOSURES -->
  `N_EXPOSURES`. [Neil Cook]
- `Apero.plotting.plot_functions.py` - deal with contx being None. [Neil
  Cook]
- `Apero.plotting.plot_functions.py` - `CONT_XBIN`, `CONT_YBIN` ->
  `CONT_POL_XBIN`, `CONT_POL_YBIN`. [Neil Cook]
- `Apero.plotting.plot_functions.py` - `FLAT_X` --> `FLAT_WLDATA`. [Neil Cook]
- `Apero.plotting.plot_functions.py` - `plot_polar_fit_cont` correct plot.
  [Neil Cook]
- `Apero.plotting.plot_functions.py` - `plot_polar_fit_cont` correct typo
  s-->ms. [Neil Cook]
- `Apero.science.polar.gen_pol.py` - typo `PLOT_POLAR_FIT_CONT` -->
  `POLAR_FIT_CONT`. [Neil Cook]
- `Apero.science.polar.gen_pol.py` - typo `POLAR_FIT_CONT` -->
  `PLOT_POLAR_FIT_CONT`. [Neil Cook]
- `Apero.insturments.spirou.recipe_definitions.py` - polar code
  --exposures should not be required. [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - remove
  `KW_THERM_RATIO_2`. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [njcuk9999]
- `Apero.core.core.drs_file.py` - deal better with exclude keys in post
  processing. [njcuk9999]
- `Apero.core.instruemnts.*.default_constants.py` - add LSD MAX LINEDEPTH.
  [Neil Cook]
- Add excess emissivity csv file (default file for the drs) [Neil Cook]
- Add excess emissivity changes. [Neil Cook]
- Add new lsd masks. [Neil Cook]
- Add polar changes (Eder update for 0.7) [Neil Cook]


0.7.202 (2022-01-26)
--------------------
- Move leak and thermal to own calib py files and start excess
  emissivity work. [Neil Cook]
- `[NIRPS_HE]` `apero.science.preprocessing.detector.py` - account for too
  much flux between pixels. [Neil Cook]
- Correct mini runs for `nirps_he` and `nirps_ha`. [Neil Cook]
- Update documentation (put examples for `apero_get` in correct place)
  [Neil Cook]


0.7.201 (2022-01-25)
--------------------
- Updates to get nirps-he working (currently on preprocessing) [Neil
  Cook]
- Update language database. [Neil Cook]
- `Apero.science.extract.gen_ext.py` - correct typo `THERMALFF_RATIO` to
  `THERMALFF_RATIO_USED`. [Neil Cook]
- Update lang messages that are warnings/errors to display error code.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - must copy exclude keys. [Neil Cook]
- `Apero.core.core.drs_file.py` - need to deal with
  `DrsOutFile.exclude_keys` = None. [Neil Cook]
- `Apero.tools.recipes.spirou.apero_postprocess_spirou.py` - allow polar
  code to skip certain files (i.e. if DRSMODE=SPECTROSCOPY or UNKNOWN
  there will not be any p files to product) [Neil Cook]
- `Apero.tools.recipes.bin.apero_astrometrics.py` - need to add old name
  to aliases. [Neil Cook]
- `Apero.tools.recipes.bin.apero_astrometrics.py` - need to update
  `astro_obj.objname`. [Neil Cook]
- Update `apero_astrometrics.py` and `apero_precheck.py` with new options.
  [Neil Cook]
- Update docs for dev tools + some optimization. [Neil Cook]


0.7.200 (2022-01-25)
--------------------
- Update docs for dev tools + some optimization. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [Neil Cook]
- Remove `_` = `display_func` and use of Constants = constants.load() where
  possible. [Neil Cook]
- Add a mode to thermal correction (tapas vs percentile) + add the
  thermal ratios to header. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [njcuk9999]
- `Recipe_definitions` for astrometric code wrong. [Neil Cook]
- `Recipe_definitions` for astrometric code wrong. [Neil Cook]
- Update requirements pillow + ipython. [Neil Cook]
- Apero.science.extract + telluric - fix magic grid (no divide by 1000)
  [njcuk9999]


0.7.199 (2022-01-21)
--------------------
- Update some recipe definitions for dev tools. [Neil Cook]
- `Apero.science.polar.gen_pol.py` - deal with full order having no good
  (all NaNs) pixels. [njcuk9999]


0.7.198 (2022-01-20)
--------------------
- Update documentation descriptions for user tools. [Neil Cook]
- Update documentation descriptions for user tools. [Neil Cook]
- Update documentation descriptions for user tools. [Neil Cook]
- Update documentation descriptions for user tools. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - deal with no unhandled
  errors found. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - check for PPLOG = None.
  [Neil Cook]
- `Apero.tools.recipes.bin.apero_stats.py` - error mode requires plog.
  [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - append after errors caught
  (otherwise x,y and m could be different lengths) [Neil Cook]
- `Apero.tools.module.drs_documentation.py` - fix capitalization (just
  first word) [Neil Cook]
- Only clean auto files if we are redoing all automatically created
  files. [Neil Cook]
- Rearrange doc structure + fix warnings + add tools and dev tools +
  clean auto files before restarting. [Neil Cook]
- Rearrange doc structure. [Neil Cook]
- Update documentation code + recipe definitions + file definitions +
  update docs. [Neil Cook]


0.7.197 (2022-01-13)
--------------------
- Merge remote-tracking branch 'origin/v0.7.194-working' into
  v0.7.194-working. [njcuk9999]
- `Apero.science.calib.flat_blaze.py` - add warning message that we are
  trying sinc fit again + update language database. [Neil Cook]
- `Apero.science.calib.flat_blaze.py` - sometimes does not fit (but not
  reproducible) try again 5 times and then report error. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - correct error
  reporting. [njcuk9999]
- `Apero.core.instruments.spirou.file_definitions.py` - cannot take tellu
  from telluric database (shouldn't be the closest - should match
  odometer `(KW_IDENTIFIER)` [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - TELLU A and B
  files not in telluric database (should they be?) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - tellurics from
  telluric database? [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - t.fits hlink for
  telluric files should be from database (shouldn't save if qc wasn't
  passed) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - fix typo `OBJ_HC2`
  --> `OBJ_HCTWO`. [Neil Cook]


0.7.196 (2022-01-12)
--------------------
- Update the language database. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - update pass message for calib delta
  time + language database. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - update pass message for calib delta
  time + language database. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - improve error for calib delta time.
  [Neil Cook]
- Problem with error code 09-002 and 09-003. [Neil Cook]
- Correction of magic grid function (from lbl changes) [Neil Cook]


0.7.195 (2021-12-27)
--------------------
- `Apero.tools.module.setup.drs_isntallation.py` - `user_instrument` must be
  a string. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - self.index is dataframe.
  [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - `PID-->KW_PID`. [Neil Cook]
- `Apero.tools.module.testing.drs_stats.py` - obtain the index database
  once and pass dataframe to classes. [Neil Cook]
- Update date/version/changelog/docs. [Neil Cook]


0.7.194 (2021-12-22)
--------------------
- Merge remote-tracking branch 'origin/v0.7.193-working' into
  v0.7.193-working. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - deal with masked
  columns and force str/float for all ftable row values (into tabledict)
  [njcuk9999]
- Deal with postprocess wave/blaze from calibration (may not be present
  in index database) [Neil Cook]
- Update language database for template skipped recipes. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` +
  `file_definitions.py` - for mini data pol + ccf should only include
  `science_targets`. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - move around errors.
  [njcuk9999]
- `Apero.core.core.drs_database.py` - correct column order in
  `update_header_fix()` [Neil Cook]
- `Apero.core.core.drs_database.py` - correct typos `OBS_KIND-->OBS_DIR`.
  [Neil Cook]
- Astropy (np>1.18) and numba (<1.12) conflict on numpy --> np=1.20.3.
  [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.7.193 (2021-12-20)
--------------------
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - move text to
  language database. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - combien textentry
  better. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - better handle error
  reporting. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - report error
  numbers. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - report error
  numbers. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.recipes.spirou.apero_postprocess_spirou.py` +
  `apero.core.core.drs_file.py` - add changes to report errors better in
  post processing. [Neil Cook]
- `Apero.science.calib.flat_blaze.py` - correct strlist for sinc fit
  (error reporting caused exception which hides actual error) [Neil
  Cook]


0.7.192 (2021-12-17)
--------------------
- Update language database. [Neil Cook]
- `Apero.science.extract.berv.py` - check whether both barycorrpy and
  pyasl are nan + deal better in pyasl with no distance (and give error
  when ra/dec are nan because of bad `apply_space_motion)` [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.182-working' into
  v0.7.182-working. [njcuk9999]
- Update DrsDatabaseErrors. [Neil Cook]
- Update the install module to work with command line args (see
  `install_script.sh)` [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.182-working' into
  v0.7.182-working. [njcuk9999]
- `Apero.core.instruemnts.spirou.pseudo_const.py` - get output type for
  header/hdict (otherwise drsfile is updated) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.182-working' into
  v0.7.182-working. [njcuk9999]
- Update `FILEDEF_HEADER_KEYS` (for spirou to include polar keys) [Neil
  Cook]
- Fixes for errors with full run 211018. [njcuk9999]


0.7.191 (2021-12-15)
--------------------
- `Apero.tools.module.testing.drs_stats.py` - update error mode. [Neil
  Cook]
- `Apero.tools.module.testing.drs_stats.py` - update error mode. [Neil
  Cook]
- `Apero.tools.module.testing.drs_stats.py` - update error mode. [Neil
  Cook]
- Add an error mode to the `apero_stats.py` module. [Neil Cook]
- `Apero.tools.moduile.recipes.bin.apero_astrometerics.py` - finalise
  design (move functionality to `drs_astrometrics.py`. [Neil Cook]
- `Apeor.science.velocity.gen_vel.py` - Fix CamelCase column names. [Neil
  Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - make S1D files
  have tag UniformWavelength/UniformVelocity. [Neil Cook]
- Remove auth keys for google sheet. [Neil Cook]
- `Tools.recipes.bin.apero_astrometrics.py` - add code to get/write to
  googlesheet. [Neil Cook]
- `Apero.tools.recipes.bin.apero_astrometrics.py` - add astrometrics code
  [unfinished] [Neil Cook]


0.7.190 (2021-12-08)
--------------------
- `Apero.tools.module.testing.drs_stats.py` - fix qc stat plot. [Neil
  Cook]
- Debug printout tables= [Neil Cook]
- Debug printout tables= [Neil Cook]
- Debug printout tables= [Neil Cook]
- `Apero.base.drs_db.py` - infer table name when getting columns. [Neil
  Cook]
- `Apero_stats.py` - add qc mode (unfinished) [Neil Cook]
- `Apero_stats.py` - add qc print outs [still need qc plots] [Neil Cook]
- `Apero_stats.py` - add qc mode (unfinished) [Neil Cook]
- `Setup.install.py` - add fix for Issue #676  - weird module version must
  be set in `module_translation`. [Neil Cook]


0.7.189 (2021-12-06)
--------------------
- Add timing to `apero_stats` (formly `apero_log_stats)` - still need QC and
  error checks. [Neil Cook]
- Remove ABSPATH (not indexed) in favour of `BLOCK_KIND` + `OBS_DIR` +
  FILENAME. [Neil Cook]
- Allow thermal correction for telescope dark to use internal dark if
  telescope dark is mising. [Neil Cook]
- Re-make run.ini files with changes to thermal code. [Neil Cook]
- Re-make run.ini files with changes to thermal code. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - update precheck to
  handle exclusive/inclusive drs file lists. [Neil Cook]
- Add quality control in preprocessing to catch `DARK_DARKs` that contain
  science data - these will not be preprocessed. [Neil Cook]
- Update run.ini files + typo in msg. [Neil Cook]
- Finish `apero_run_ini.py` code. [Neil Cook]


0.7.188 (2021-12-01)
--------------------
- Continue work on run.ini auto make. [Neil Cook]
- Continue work on `apero_run_ini.py`. [Neil Cook]
- Continue work on `apero_run_ini.py`. [Neil Cook]


0.7.187 (2021-11-24)
--------------------
- `Apero.tools.module.processing.drs_precheck.py` - must mask out other
  bad nights before comparing the 7 day rule. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - add a way to filter
  which nights are actually bad and which nights aren't. [Neil Cook]
- `Apero.base.drs_db.py` - must set number of tries after super call.
  [Neil Cook]
- Deal with language database trying to connect multiple times. [Neil
  Cook]
- `Apero.core.core.drs_argument.py` - don't load database until required.
  [Neil Cook]
- `Apero_get.py` - problem with AND when no object condition. [Neil Cook]
- `Apero.base.drs_db.py` - fix create index on multiple columns. [Neil
  Cook]
- `Apero.tools.module.drs_reset.py` - pep8 fixes. [Neil Cook]
- `Apero.tools.module.drs_reset.py` - add faster remove approach (when we
  have none or a few skip files) [Neil Cook]
- `Apero.tools.module.database.manage_database.py` +
  `apero.core.core.drs_database.py` - fix `idb_cols.get_index_groups`. [Neil
  Cook]
- Remove circular imports to PandasLikeDatabase (move to
  `drs_base_classes.py)` [Neil Cook]
- Remove requirement for database.tname when tname set in database.
  [Neil Cook]


0.7.186 (2021-11-23)
--------------------
- `Apero.core.core.drs_file.py` - pep8 move comment. [Neil Cook]
- `Apero.core.core.drs_argument.py` - remove pandas database store. [Neil
  Cook]
- `Apero.core.core.drs_database.py` + `drs_file.py` - load the whole
  database entry for that night. [Neil Cook]
- `Apero.tools.recipes.bin.apero_get.py` - allow no objname. [Neil Cook]


0.7.185 (2021-11-19)
--------------------
- Deal with loading. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.182-working' into
  v0.7.182-working. [Neil Cook]
- Option to turn off using database in arguments calls. [Neil Cook]
- `Apero.core.instruments.*.file_definitions.py` - `_wavesol_master_` -->
  `_wavesol_master` (removes double `__)` [Neil Cook]


0.7.184 (2021-11-17)
--------------------
- `Apero.tools.recipes.dev.apero_run_ini.py` - first commit and code for
  auto generating run.ini files [unfinished] [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.core.core.drs_log.py` - change recipe type when extract used
  inside another recipe. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - change recipe type when extract used
  inside another recipe. [Neil Cook]
- Update log dir for recipes calling extract recipe. [Neil Cook]
- Update log dir for recipes calling extract recipe. [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.core.utils.drs_startup.py` + `apero.core.core.drs_file` +
  `drs_log.py` - get the `obs_dir` (without path) for logging - log messages
  to subdir. [Neil Cook]


0.7.183 (2021-11-12)
--------------------
- `Apero.recipe.spirou.apero_extract_spirou.py` - add combine method
  argument. [Neil Cook]
- Update date/version/changelog/update notes/documentation. [Neil Cook]


0.7.182 (2021-11-10)
--------------------
- `Apero.core.core.drs_database.py` - do not log error in `read_header` -
  pass exception back to handler. [njcuk9999]
- `Apero.core.core.drs_database.py` - when updating index if we can't get
  header skip it - bad files should not crash the process here - but we
  should warn the user. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - update cleaning of
  object name now "+" goes to P and "-" goes to M by default. [Neil
  Cook]


0.7.181 (2021-11-09)
--------------------
- Update run.ini files for default skip parameters. [Neil Cook]
- `Apero.recipes.spirou.apero_ccf_spirou.py` - corrections for teff mask
  change. [Neil Cook]
- `Apero.core.instruments.default.recipe_definitions.py` - update precheck
  descriptions. [Neil Cook]
- `Apero.tools.module.processing.drs_precheck.py` - update name of
  precheck module. [Neil Cook]
- `Apero.tools.recipes.bin.apero_precheck.py` +
  `apero.tools.module.processing.drs_precheck.py` - add precheck code
  (check before running `apero_processing)` for checking raw calibration
  files, raw telluric files, raw science files and object names (from
  database vs header) [Neil Cook]
- `Apero.io.drs_fits.py` - correct typo fits.getdata --> fits.getheader.
  [Neil Cook]


0.7.180 (2021-11-06)
--------------------
- Make fure all FTELLU1 and FTELLU2 are FTFIT1 and FTFIT2. [Neil Cook]
- `Apero.io.drs_fits.py` - correct typo fits.getheader --> fits.getdata.
  [Neil Cook]
- Update date/version/changelog/docs/update notes. [Neil Cook]


0.7.179 (2021-11-04)
--------------------
- Merge branch 'v0.7.173-stable-test' into v0.7.173-obj-res-test. [Neil
  Cook]
- `Apero.science.calib.shape.py` - deal with shape master having more
  nights than the max number of shape files (means each group will only
  have one entry and all were skipped) change to single file groups
  being kept (just not combined) [njcuk9999]
- `Apero.io.drs_fits.py` - need to deal with getdata for bad files (maybe
  corrupted but don't always need all extensions) [Neil Cook]
- `Science.preprocessing.gen_pp.py` need to deal with converting
  astrometrics from header to required units (assume database is good)
  [Neil Cook]
- Update language database. [Neil Cook]
- Add readme to each `ccf_mask` directory. [Neil Cook]
- Default ccf mask now uses Teff (via `teff_mask.csv)` to assign masks -
  can still use old method with filename if desired. [Neil Cook]
- `Apero.science.extract.berv.py` - typo `set_sources-->set_source`. [Neil
  Cook]


0.7.178 (2021-11-03)
--------------------
- Force bad values of plx/rv. [Neil Cook]
- Preprocessing + berv correction - simplify to use gsheet(s) and do not
  match. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - only print about
  engineering nights once + remove "Removing filters" printout. [Neil
  Cook]


0.7.177 (2021-11-02)
--------------------
- Make sure FTFIT1 and FTFIT2 are in the run.ini files. [Neil Cook]
- `Apero.core.core.drs_database.py` - clear TLOG + typo in comment. [Neil
  Cook]
- Try to improve getting file list from disk (avoid glob due to max open
  file holders) [Neil Cook]
- Remove env files. [Neil Cook]


0.7.176 (2021-10-29)
--------------------
- `Apero.science.calib.wave.py` - deal with no cavity degree polynomial
  (i.e. from the default master wave sol) [Neil Cook]
- `Apero.science.calib.wave.py` - correct getting cavity polynomial from
  header. [Neil Cook]


0.7.175 (2021-10-22)
--------------------
- `Apero.core.math.fast.py` - fix weird typo np.array(guess) -->
  float(guess) [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.173-working' into
  v0.7.173-working. [Neil Cook]
- `Apero.core.math.fast.py` - update `odd_ratio_mean` function. [Neil Cook]


0.7.174 (2021-10-19)
--------------------
- Update schematics for paper. [Neil Cook]
- Update schematics for paper. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.7.173 (2021-10-18)
--------------------
- Update language database. [Neil Cook]
- `Apero.core.core.drs_log.py` - update log. [Neil Cook]
- Update warning messages to have sublevel. [Neil Cook]


0.7.172 (2021-10-13)
--------------------
- `Science.telluric.gen_tellu.py` - fix the width of the preclean ccf (now
  a low pass filter) [Neil Cook]
- `Apero.core.utils.drs_utils.py+` `apero.science.calib.dark.py` + shape.py
  - fix the down selection of master files (selected by time) [Neil
  Cook]
- Update the run.ini files + add the `fit_tellu` `res_plot` in the plotter
  functions. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.7.171 (2021-10-08)
--------------------
- `Apero.science.calib.dark.py` + `apero.science.calib.shape.py` - add
  limits for the dark master and shape master max number of files. [Neil
  Cook]
- `Apero.science.extract.gen_ext.py` - fix output for thermal files. [Neil
  Cook]
- Telluric update (EA-210923) - add `apero_mk_model_spirou.py` + add
  changes to `fit_tellu` + pre-cleaning. [Neil Cook]
- `Apero.recipes.*.apero_wave_*.py` - deal with and comment `fit_cavity` and
  `fit_achromatic` better. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.io.drs_fits.py` - read with multifits return better. [Neil Cook]
- Update run.ini files that use telluric recipes. [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - update telluric
  `recipe_definitions.py`. [Neil Cook]
- `Apero.core.instruments.*.file_definitions.py` - add `TELLU_MODEL` to
  `file_definitions.py`. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - update
  `tellup_ccf_scan_range` + `thermal_extract_type` (e2dsff-->e2ds) [Neil
  Cook]
- Continue work on transmission model update [EA 210923] [Neil Cook]
- Continue work on transmission model update [EA 210923] [Neil Cook]


0.7.170 (2021-10-04)
--------------------
- Start work on telluric update (EA-210923) [Neil Cook]
- Unbreak logging system (conflict with `OBS_DIR)` [Neil Cook]
- Conflict between `obs_dir` from params and `run_file`. [Neil Cook]
- Wave extraction needs to use master wave sol. [Neil Cook]
- Wave extraction needs to use master wave sol. [Neil Cook]
- Wave extraction needs to use master wave sol. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - deal with locking params better.
  [Neil Cook]
- Update date/version/docs/changelog. [Neil Cook]


0.7.169 (2021-10-01)
--------------------
- `Apero.science.extract.gen_ext.py` - leak correction must use reference
  fiber (not science fiber) to scale `dark_fp` correction. [Neil Cook]
- `Apero.science.wave.py` - add `cavity/cavity_deg/mean_hc_vel/err_hc_vel`
  to wprops (for storing in header) [Neil Cook]
- `Apero.recipes.*.apero_extract_*.py` - reference fiber must be extracted
  first - other fibers use reference fiber for leak correction. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add
  `CDBLEAKR/CDTLEAKR/WCAV/WCAV_DEG/WAVEMHC/WAVEEMHC` keywords. [Neil Cook]
- Add leakm (file and time) to the extracted header, do not filter
  master calibrations by dtime for calib vs obs (now use a CalibFile
  class to store info) [Neil Cook]
- Allow run file as an argument to recipes - (--crunfile) this allows
  passing a constant in the run.ini file when running
  `apero_processing.py`. [Neil Cook]


0.7.168 (2021-09-29)
--------------------
- `Apero.core.core.drs_database.py` - deal with unix time better (may be
  np.nan oir none time --> in these cases set to None) [njcuk9999]
- `Apero.recipes.*.apero_extract_nirps*.py` - correct position in foout
  3-->2 2-->1 1-->0. [njcuk9999]
- `Apero.science.extract.gen_ext.py` - `LEAK_CORRECTED` is in eprops not
  params. [njcuk9999]


0.7.167 (2021-09-28)
--------------------
- Merge branch 'v0.7.156-working' into v0.7.166-working. [njcuk9999]
- `Apero.core.instruments.default.grouping.py` - deal with no table
  (rawtab = None) [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.156-working' into
  v0.7.156-working. [njcuk9999]
- Merge remote-tracking branch 'origin/v0.7.156-working' into
  v0.7.156-working. [njcuk9999]
- Merge branch 'v0.7.156-working' of github.com:njcuk9999/apero-drs into
  v0.7.156-working. [njcuk9999]
- Merge branch 'v0.7.156-working' of github.com:njcuk9999/apero-drs into
  v0.7.156-working. [njcuk9999]
- `Apero.core.core.drs_database.py` - deal with removed files from the
  database. [njcuk9999]
- Update language database. [Neil Cook]
- Fix error in post products not adding wave files. [Neil Cook]
- Update language database. [Neil Cook]
- Update update notes. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `DO_CALIB_DTIME_CHECK` and `MAX_CALIB_DTIME`. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - add in a way to check delta time on
  observation vs calibration. [Neil Cook]
- Remove log.txt. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.7.166 (2021-09-27)
--------------------
- Update language database. [Neil Cook]
- `Apero.science.calib.wave.py` - replace mean rv fit diff with mean of
  difference of rvs in orders. [Neil Cook]
- `Apero.core.instruemnts.default.default_keywords.py` - the default
  key='' should be key='NULL' (otherwise get comments list) [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - correct `b_cols`. [Neil Cook]


0.7.165 (2021-09-25)
--------------------
- `Apero.science.calib.wave.py` - fix typo WLOG(params, msg) -->
  WLOG(params, '', msg) [Neil Cook]
- `Apero.science.calib.gen_calib.py` - deal with returning None (cannot
  case filename to string) [Neil Cook]
- `Apero.recipes.spirou.apero_extract_spirou.py` - correct indices on
  fbprops. [Neil Cook]
- `Apero.science.calib.gen_calib.py` + `apero.science.extract.gen_ext.py` -
  fix calib file being None in wave sol + orderp does n ot have CDTORDP
  (use MJDMID) [Neil Cook]
- `Apero.science.calib.shape.py` + `apero.science.extract.gen_ext.py` - use
  sprops. [Neil Cook]
- `Apero.recipes.*.apero_extract/flat*.py` - push sprops into
  `order_profiles`. [Neil Cook]
- `Apero.recipes.*.apero_shape_*.py` - poush sprops into write. [Neil
  Cook]
- `Apero.core.instruments.*.file_definitions.py` - change `orderp_straight`
  to DrsFitsFile. [Neil Cook]
- `Apero.core.core.drs_file.py` - allow coping of hdict / header without
  drsfile instance. [Neil Cook]
- `Apero.core.core.drs_database.py` - do not fix headers for non fits
  files. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - fix `load_calib_file` (add
  `return_time=True)` [Neil Cook]
- `Apero.core.core.drs_database.py` - fix ctable output. [Neil Cook]
- Add calibration MJDMID to all files that use CDBXXXX (as CBTXXXX)
  [Neil Cook]


0.7.164 (2021-09-23)
--------------------
- Apero.science.calib - `wave.py` - print out CCFRV as well as DV tests.
  [Neil Cook]
- `Apero.core.core.drs_database.py` - change message 40-001-00031 from
  general to debug print out ("Skipping search") [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - change cosmic intcut
  from 10-50 to 50-100. [Neil Cook]
- `Apero.data.spirou.calib.catalogue_UNe.csv` - add red most lines [EA]
  from large catalogue. [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - add back in order
  48 to wave solution. [Neil Cook]


0.7.163 (2021-09-22)
--------------------
- Update requirements (untested) [Neil Cook]
- `Apero.core.instruments.*` - make all instruments consistent (groups +
  other) [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - deal with non raw
  filter keys on raw files (ignore) [Neil Cook]
- Update catalogues from Etienne. [Neil Cook]
- Flat + wave - combine with sum not median. [Neil Cook]


0.7.162 (2021-09-22)
--------------------
- Need to deal with raw keys only. [Neil Cook]
- `Apero.recipes.spirou.apero_flat_spirou.py` - [REVERT] flats should be
  summed not medianed [EA] [Neil Cook]
- `Apero.recipes.spirou.apero_flat_spirou.py` - flats should be summed not
  medianed [EA] [Neil Cook]
- Update version/date/changelog/documentation. [Neil Cook]


0.7.161 (2021-09-15)
--------------------
- `Apero.base.base.py` + `apero.core.core.drs_loy.py` - make sure use of
  DPARAMS and IPARAMS give correct exception. [Neil Cook]
- `Apero.core.core.data.*.databases.reset*` - `WAVEM_D` --> `WAVESOL_DEFAULT`.
  [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.core.core.drs_database.py` - need to deal with forbidden keys
  better (comment, history and '' included) [Neil Cook]
- `Apero.data.*.reset.runs/master_calib_run.ini` - typo `calib_seq` -->
  `master_seq`. [Neil Cook]
- `Requirements_developer.txt` - ttkthemes required. [Neil Cook]
- `Apero.tools.module.database.database_update.py` - fix rlog values (now
  attributes are upper case) [Neil Cook]
- `Apero.science.extract.gen_ext.py` - add debug saving of e2ds
  uncorrected. [Neil Cook]
- `Apero.recipes.*.apero_extract_*.py` - add recipe to
  `manage_leak_correction` arguments. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - add '' and 'HISTORY' to
  forbidden keys. [Neil Cook]
- Remove `apero_leak` as recipe. [Neil Cook]
- `Apero.core.core.drs_file.py` - skip forbidden header keys. [Neil Cook]


0.7.160 (2021-09-14)
--------------------
- `Apero.recipe.spirou.apero_extract_spirou.py` - get leakcorr from
  `data_dict` (i.e. via `science.extract.other.py` `extract_files())` [Neil
  Cook]
- `Apero.science.calib.flat_blaze` and apero.science.extract.extraction +
  `gen_ext` + other  - fix blaze keys. [Neil Cook]
- Language database update. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - fix logging of DrsCodedException.
  [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - add argument
  --leakcorr to `apero_extract`. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - remove
  `ALLOWED_LEAK_TYPES` add `CORRECT_LEAKAGE` and `LEAKAGE_REF_TYPES`. [Neil
  Cook]
- `Apero.tools.module.processing.drs_processing.py` - must not update
  database in test run for Pool and Process. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - deal with runs not
  in ini files (now skips by default) [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - for nirps `KW_OBJNAME`
  not Calibration use `RAW_DPRCATG` as CALIB. [Neil Cook]
- `Apero.data.*.reset.runs.calib_run.ini` - add `PP_FF` to `RUN_` and `SKIP_`
  menus. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - add files to set. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - need to filter by files (why was this
  removed?) [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - do not update
  database in test run mode. [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - `pp_seq_opt` typo
  `add(apero_extract` --> `add(apero_preprocess`. [Neil Cook]
- `Apero.core.instruments.*.file_definitions.py` - make sure types have
  outfunc set. [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - `leak_master` should
  use E2DS not E2DSFF (change in where we do leak correction in
  extraction process) [Neil Cook]
- `Apero.core.instruments.nirps_ha.file_definitions.py` - remove
  `out_wave_hc` and `out_wave_fp` references. [Neil Cook]


0.7.159 (2021-09-10)
--------------------
- Add leak to extraction recipe (break up flat blaze corr) [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - add `DRS_DATE_NOW` (DRSPDATE)
  to index database. [Neil Cook]
- Revert UNe catalogue list. [Neil Cook]
- Wave - fix default and master wave solution names. [Neil Cook]


0.7.158 (2021-09-03)
--------------------
- Update indexing (index `KW_MID_OBS_TIME`, `KW_OBJNAME`, `KW_DPRTYPE`,
  `KW_OUTPUT`, `KW_PID`, `KW_IDENTIFIER)` [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` +
  `apero_postprocess_spirou.py` - change overwrite to skip - default is
  now to overwrite. [Neil Cook]
- `Apero.data.*.reset.runs.complete_run.ini` - `full_seq` should use EXTALL
  and LEAKALL. [Neil Cook]
- `Apero.data.spirou.reset.runs.*.ini` - update master nights. [Neil Cook]


0.7.157 (2021-08-30)
--------------------
- `Apero.recipes.spirou.apero_postprocess_spirou.py` - `set_infile` must
  take params (dealing with multiple possible DrsFitsFiles for single
  extension) [Neil Cook]
- `Apero.science.calib.wave.py` - remove references to `WAVE_FP` and `WAVE_HC`
  (use `WAVE_NIGHT)`   and `WAVEM_FP` and `WAVEM_HC` (use master wave sol)
  [Neil Cook]
- `Apero.core.instruments.*.file_definitions.py` + `recipe_definitions.py` -
  remove old definitions and make sure recipes use the new ones. [Neil
  Cook]
- `Apero.core.core.drs_file.py` - need to allow multiple drsfiles for some
  outfile extensions. [Neil Cook]
- Update version/date/changelog/documentation. [Neil Cook]


0.7.156 (2021-08-26)
--------------------
- `Apero.base.drs_db.py` - fix backup db directory. [Neil Cook]
- `Apero.science.telluric.fit_tellu.py` - correct scaling on tcorr A and B
  (needed blazeAB for reconAB not blazeA or blazeB) [Neil Cook]
- `Apero.science.calib.wave.py` - fix master wave. [Neil Cook]
- Update date/version/changelog/documents. [Neil Cook]


0.7.155 (2021-08-25)
--------------------
- `Apero.core.core.drs_database.py` - update reset + add key error for
  PandasDBStorage.get. [Neil Cook]
- `Apero.tools.recipes.bin.apero_processing.py` - move update index db
  stuff to function (for use elsewhere as well) + add indexdbm to args
  of `process_run_list`. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add an
  `update_index_db` function to deal with updates to block kinds (add it
  to multiprocesses so that after recipe finished all block kinds are
  updated) [Neil Cook]
- `Apero.database.database_update.py` - correct inputs for `index_update`.
  [Neil Cook]
- `A[erp/cpre/cpre/drs_database.py` - add subkey option to reset. [Neil
  Cook]
- `Apero.core.core.drs_database.py` - add classes PandasDBStorage (for
  storage) and PandasLikeDatabase (proxy pandas dataframe as database)
  to allow re-use of same databases / arrays instead of re-querying sql
  databases. [Neil Cook]
- `Apero.base.drs_db.py` - add to doc string. [Neil Cook]
- `Apero.core.core.drs_argument.py` - only read database once if in
  parallel mode and store in global way for other iterations. [Neil
  Cook]
- Update requirements - now require pandasql for efficiency. [Neil Cook]
- `Apero.science.calib.wave.py` - wave solution should use `WAVE_FP` and
  `WAVE_HC` not `WAVEM_FP` and `WAVEM_HC`. [Neil Cook]
- `Apero.science.calib.localisation.py` - `all_labels` --> `all_labels2`.
  [Neil Cook]


0.7.154 (2021-08-23)
--------------------
- `Apero.core.instruments.default.grouping.py` - better handle masked
  table: table.mask[colname]  not table[colname].mask. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Workflows.diagram.yml - avoid making new commit on push. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- `Apero.base.drs_db.py` - update path for sql to be in ~/.apero/ (for
  backups only) [Neil Cook]
- `Apero.plotting.plot_functions.py` - plots using fiber should have fiber
  in the suffix. [Neil Cook]
- README.md - update code diagram description. [Neil Cook]


0.7.153 (2021-08-20)
--------------------
- Repo visualizer: updated diagram. [repo-visualizer]
- Update readme and diagram.yml. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update readme and diagram.yml. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update readme and diagram.yml. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update readme and diagram.yml. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update diagram yaml. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update diagram yaml. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- Repo visualizer: updated diagram. [repo-visualizer]
- Update diagram yaml. [Neil Cook]
- Add diagram. [Neil Cook]

  add diagram
- Update diagram yaml. [Neil Cook]
- Try adding codebase diagram. [Neil Cook]
- `Apero.tools.recipes.bin.apero_get.py` - fix problems with blank fields.
  [Neil Cook]
- `Apero.tools.recipes.bin.apero_get.py` - deal with `filter_items` equal to
  None. [Neil Cook]
- Param func listp and listd need 'required' keyword argument. [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.151-working' into
  v0.7.151-working. [Neil Cook]
- `Apero.core.instruments.defualt.recipe_definitions.py` - name of
  `apero_get` typo anme --> name. [Neil Cook]


0.7.152 (2021-08-05)
--------------------
- Update loc regions text. [Neil Cook]
- `Apero.core.instruments.default.grouping.py` - pol group must remove
  masked rows. [Neil Cook]
- `Apero.core.core.drs_file.py` - deal with math = "None" (for polar
  combine --> return first header value) [Neil Cook]
- Update date/version/changelog/docs. [Neil Cook]
- Update date/version/changelog/docs. [Neil Cook]
- `Apero.science.calib.wave.py` - `wfp_target_rv` None --> 0.0 (so not Null
  in header) [Neil Cook]


0.7.151 (2021-07-29)
--------------------
- `Apero.science.calib.wave.py` - `wfp_target_rv` None --> 0.0 (so not Null
  in header) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - `remove_std_hkeys`
  True by default + add Recon/ReconErr to s.fits file + add tag for
  UniformWavelength and UniformVelocity. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - update `FORBIDDEN_KEYS`
  definitions. [Neil Cook]
- `Apero.core.instruments.default.grouping.py` - polar sequences must be
  for same object + correct `_is_numeric` function. [Neil Cook]
- `Apero.core.core.drs_file.py` - combine filename column names should not
  end in .fits + remove std hkeys by default. [Neil Cook]


0.7.150 (2021-07-24)
--------------------
- `Apero.science.preprocessing.detector.py` - fix issue with cosmic
  correction being slow - need to correct intercept + errslope. [Neil
  Cook]
- Remove databases and update gitignore. [Neil Cook]
- `Apero.science.calib.wave.py` - update wave qc (limit to 2 m/s between
  fibers) and add back in the ccf rv qc (again qc at 2 m/s) [Neil Cook]
- `Apero.core.math.gen_math.py` - add todo to fix this function (can take
  a long time) [Neil Cook]
- Add `start_time` and `end_time` to log database. [Neil Cook]
- `Apero.base.drs_db.py` - fix commit problem with sqlite3. [Neil Cook]
- `Apero.recipes.*.apero_preprocess_*.py` - move cosmic ray correction
  before shift. [Neil Cook]
- `Apero-drs-full.setup.install.py` + `setup_lang.py` - add way to get lang
  code without using apero (so we can check modules) otherwise if
  modules don't exist we can't import apero.base. [Neil Cook]


0.7.149 (2021-07-21)
--------------------
- `Apero.base.drs_db.py` - add changes to make sqlite work again. [Neil
  Cook]
- Sqlite3 no longer works - test it. [Neil Cook]
- `Apero.core.instruments.default.grouping.py` - need to deal with NUMEXP
  and CMPLTEXP being blank - remove them (adds 3 ms to polar grouping)
  [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.7.148 (2021-07-16)
--------------------
- Update .gitignore. [Neil Cook]
- Update language database. [Neil Cook]
- Update language database + add install text to language database
  (using langdb proxy) [Neil Cook]
- Add text to language database. [Neil Cook]
- `Apero.science.localisation.py` -  add loc im regions plot. [Neil Cook]
- `Setup.install.py` - scikit-image --> skimage in `module_translation`.
  [Neil Cook]
- Update language database. [Neil Cook]
- Add `pp_ff` and `ext_ff` to runs. [Neil Cook]
- `Apero.core.core.drs_database` + `apero.core.utils.drs_utils.py` +
  `apero.tools.module.processing.drs_processing.py` - fix problem with
  include/exclude list of `obs_dirs`. [Neil Cook]
- Update documentation, date, version, changelog. [Neil Cook]


0.7.147 (2021-07-14)
--------------------
- Update language database. [Neil Cook]
- `Apero.science.calib.wave.py` - update echelle orders calculation + up
  limits on `WAVE_CCF_RV_THRES_QC`. [Neil Cook]
- Force recipes that are master to give error on qc failure. [Neil Cook]


0.7.146 (2021-07-13)
--------------------
- `Apero.core.instruments.nirps_ha.default_constants.py` - up the nirps qc
  limit to 20 m/s. [Neil Cook]
- `Apero.science.calib.wave.py` - `match_fplines` to get dv from wave meas.
  [Neil Cook]


0.7.145 (2021-07-13)
--------------------
- `Apero.science.calib.wave.py` - need to sort both to the same length
  (assumes 1. they are sorted by peakn 2. there are no duplicates) [Neil
  Cook]
- `Apero.science.calib.flat_blaze.py` - deal with blaze failing even
  simple fix (remove cubic term) [Neil Cook]
- Update wave sol to fix problem with dv measurement between A,B and C
  rel to AB. [Neil Cook]


0.7.144 (2021-07-09)
--------------------
- Try to fix wave master solution. [Neil Cook]
- Try to fix wave master solution. [Neil Cook]
- Try to fix wave master solution. [Neil Cook]
- Update documentation + add recipe sequence auto doc. [Neil Cook]
- Update documentation + add recipe sequence auto doc. [Neil Cook]
- Update documentation. [Neil Cook]
- `Apero.science.calib.flat_blaze.py` - `load_calib_file` must use fiber
  argument!! [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` -
  `WAVE_CAVITY_FIT_DEGREE` too high, change from 11 --> 7. [Neil Cook]


0.7.143 (2021-07-06)
--------------------
- `Apero.science.extract.berv.py` - make sure berv warning is on by
  default. [Neil Cook]
- Update date / version / documentation. [Neil Cook]


0.7.142 (2021-07-05)
--------------------
- Update documentation. [Neil Cook]
- Change grouping to only allow a maximum number of files in a group.
  [Neil Cook]
- Update documentation. [Neil Cook]
- Add `nirps_he` mode. [Neil Cook]
- Update wave solution. [Neil Cook]


0.7.141 (2021-07-02)
--------------------
- Add auto-doc recipe definitions. [Neil Cook]
- `Apero.core.instruments.nirps_ha.pseudo_const.py` - correct typo remove
  filename from `get_drs_mode`. [Neil Cook]


0.7.140 (2021-06-30)
--------------------
- Apero.tools.module.documentation - add css + table formatting. [Neil
  Cook]
- Apero.tools.module.documentation - add to file definitions
  documentation nirps + spirou. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - expand `psuedo_consts`
  loading certain variables only once. [Neil Cook]
- `Apero.science.calib.shape.py` - correctiong for infiles for outfile3+
  (nirps hcfiles None) [Neil Cook]


0.7.139 (2021-06-29)
--------------------
- Update documentation based on `file_definitions` page. [Neil Cook]
- Add way to compile list of file definitions. [Neil Cook]
- `Apero.core.instruments.nirps_ha.default_constants.py` - change the
  localisation ydet max value limit from 4060-->4050. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add DrsCodedException as known error
  type (expected) [Neil Cook]
- `Apero.core.instruments.nirps_ha.file_definitions.py` - add `OBJ_SKY`,
  `OBJ_TUN`, `TEST_HCONE_HCONE`, `TEST_FP_HCONE`, `TEST_HCONE_FP`, `TEST_DARK_FP`.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - get id file error keys from psuedo
  const. [Neil Cook]
- `Apero.core.instruments.nirps_ha.file_definitions.py` - add FLAT,LED to
  known raw file types. [Neil Cook]
- Update reset.object.csv file based on current googlesheet (so we don't
  have to recheck we supply this as default) [Neil Cook]


0.7.138 (2021-06-29)
--------------------
- Database fixes - FLOAT-->DOUBLE, order file names for skipping, fix
  grouping for polar files (pol not running) [Neil Cook]
- Remove PPM from nirps run.ini files. [Neil Cook]
- Update requirements (no longer a test) [Neil Cook]
- Update master night for nirps. [Neil Cook]
- Update pseudo const for nirps. [Neil Cook]
- Update date/version/changelog/docs. [Neil Cook]


0.7.137 (2021-06-25)
--------------------
- Finish delete table app for `apero_database.py` (--delete) [Neil Cook]
- `Apero.tools.module.database.manage_db_gui.py` - work on app to delete /
  manage tables. [Neil Cook]
- Few fixes for database indexing. [Neil Cook]


0.7.136 (2021-06-23)
--------------------
- `Apero.core.utils.drs_utils.py` - forgot `param_kind` in log key loop.
  [Neil Cook]
- Continue database indexing overhaul. [Neil Cook]
- `Apero.base.drs_db.py` - add index column. [Neil Cook]
- Optimize database using index columns and define all sql data types
  properly (to aid speed up + indexing) [Neil Cook]
- `Apero.io.drs_path.py` - add listdirs, nofiles and listfiles functions
  (for quick directory/file listings) [Neil Cook]
- `Apero.core.math.gen_math.py` - rename 'slice' to 'imslace' (avoid using
  standard name) [Neil Cook]
- `Apero_wave_night_nirps_ha.py` - do not update `smart_fp_mask` here (only
  in master) [Neil Cook]
- `Apero_wave_night_spirou.py` - do not update `smart_fp_mask` here (only in
  master) [Neil Cook]
- Turn off cosmic correction for NIRPS - broken (Etienne will fix later)
  [Neil Cook]


0.7.135 (2021-06-21)
--------------------
- `Apero.core.core.drs_database` - add todo on how we deal with unique
  columns. [Neil Cook]
- Try to speed up processing pre-indexing. [Neil Cook]
- Try to speed up processing pre-indexing. [Neil Cook]
- Try to speed up processing pre-indexing. [Neil Cook]
- `Apero.core.core.drs_file.py` - self.abspath should be a string here.
  [Neil Cook]


0.7.134 (2021-06-18)
--------------------
- `Apero.core.core.drs_database.py` - last modified date a problem with
  many files. [Neil Cook]
- Update nirps preprocessing. [Neil Cook]
- `Apero_preprocess_nirps_ha.py` - need to add etiennes code for fixing
  first pixel in amp. [Neil Cook]
- Update version/date/changelog/update notes. [Neil Cook]
- Fix `apero_postprocess_spirou.py`  - fix db infiles. [Neil Cook]


0.7.133 (2021-06-17)
--------------------
- Keep adding drs output files with infiles (for the database) - brute
  force approach --> find blanks in database (we missed some) [Neil
  Cook]
- Keep adding drs output files with infiles (for the database) - brute
  force approach --> find blanks in database (we missed some) [Neil
  Cook]
- Add `KW_INSTRUMENT` + add infiles column to the index database. [Neil
  Cook]


0.7.132 (2021-06-15)
--------------------
- Update `requirements_test.txt`. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - fix `drs_mode`. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - add instrument to the
  keywords. [Neil Cook]
- `Apero.core.instruments.spirou.pseudo_const.py` - update DRSMODE -
  spectroscopy only for P16,P16   everything else with P2 or P4 or P14
  or P16 is POLAR (if valid in both channels) [Neil Cook]


0.7.131 (2021-06-14)
--------------------
- `Apero.core.instruments.*.file_definitions` + `default_keywords.py` - make
  sure raw files check instrument header key. [Neil Cook]
- `Apero.core.instruments.spirou.pseudo_const.py` - add polar rhomb
  positions that are valid for spectroscopy (P2,P4,P14,P16) unless
  specific polar combination. [Neil Cook]
- Add out directory to the reset code. [Neil Cook]


0.7.130 (2021-06-12)
--------------------
- Work on `apero_get.py`. [Neil Cook]
- Updates to echelle order numbers to wave solution - add to header.
  [Neil Cook]
- Add echelle order numbers to wave solution. [Neil Cook]


0.7.129 (2021-06-11)
--------------------
- Updates to localisation - now tested on mini data 1+2 spirou, + nirps
  20210218. [Neil Cook]
- Code space for echelle orders + change `wave_night` `__NAME__` to
  `wave_night` (was `wave_master)` [Neil Cook]
- `Apero_get.py` - new tool to get any file from the drs - currently code
  not copied see `apero-utils/general/apero_get/apero_get.py` for the
  draft code. [Neil Cook]


0.7.128 (2021-06-09)
--------------------
- Updates to localisation. [Neil Cook]
- `Apero.tools.recipes.bin.apero_database.py` - add a mode to update
  reset.object.csv using either a dfits text file or a read of all
  current raw files. [Neil Cook]
- Continue changes to update localisation for SPIRou and NIRPS. [Neil
  Cook]
- Upgrade the localisation using new recipe from EA (use blob finding)
  [Neil Cook]
- Fix installation bug (Issue #669) [Neil Cook]


0.7.127 (2021-06-02)
--------------------
- `Apero.core.utils.drs_startup.py` - must update recipe.inpudir and
  `recipe.in_block_str` when `in_block_str` is a block kind (and forced)
  [Neil Cook]
- `Apero.core.utils.drs_startup.py` - deal with `in_block_str` being a path
  as well as the current working directory containing block kind as a
  directory (would break here before) [Neil Cook]
- `Apero.science.calib.wave.py` - need a return to `res_fit_super_gauss`
  function. [Neil Cook]
- Merge branch 'master' into v0.7.126-working. [Neil Cook]

  # Conflicts:
  #    README.md
- Update README.md. [Neil Cook]

  correct typo
- Update version/date/changelog/update notes/documentation. [Neil Cook]


0.7.126 (2021-06-01)
--------------------
- `Apero.science.calib.wave.py` - fix res map to work for NIRPS (gaussian
  fit vs super-gaussian fit for spirou) [Neil Cook]


0.7.125 (2021-05-31)
--------------------
- `Apero.science.preprocessing.gen_pp.py` - handle request.get() exception
  or going to the wrong link (table inconsistent) [Neil Cook]
- Update wave codes for NIRPS and SPIRou - now can remove orders from
  any part of the detector. [Neil Cook]
- Update some doc strings + unused arguments in wave codes. [Neil Cook]
- Update nirps default wave grid (for cut 71) [Neil Cook]


0.7.124 (2021-05-27)
--------------------
- Update nirps default wave grid (for cut 71) [Neil Cook]
- Wave sol changes for `NIRPS_HA` full detector. [Neil Cook]


0.7.123 (2021-05-26)
--------------------
- `Apero.recipes.nirps_ha.apero_wave_master_nirps_ha.py` - add back in the
  FP file check. [Neil Cook]
- `Apero.recipes.science.calib.wave.py` - modify wave code for nirps.
  [Neil Cook]
- `Setup.newprofile.py` - (re)create yamls after updating them. [Neil
  Cook]
- `Apero.science.extract.extraction.py` - clean up
  `calculate_blaze_flat_sinc` args. [Neil Cook]
- `Apero.science.calib.flat_blaze.py` - make med filter size a constant
  (for each instrument) [Neil Cook]
- `Apero.recipes.*.apero_extract_*.py` - quicklook remove wavesol. [Neil
  Cook]
- `Apero.plotting.plot_funcitons.py` - type `frame1.set_ylim` -->
  `frame2.set_ylim`. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` + others - deal with `DRS_OBJ_NAME` +
  `DRS_OBJ_NAMES`. [Neil Cook]
- `Apero.instruments.nirps_ha.recipe_definitions.py` - `apero_pp_master`
  needed `group_func` + `group_column`. [Neil Cook]
- `Apero.core.instruments.default.grouping.py` - need to deal with
  rawtab=None. [Neil Cook]
- `Apero.instruments.*.pseudo_const.py` - sort out objname + null text.
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `FF_BLAZE_SINC_MED_SIZE`. [Neil Cook]
- `Apero.base.base.py` - `write_yaml` Path-->str + pep8. [Neil Cook]
- `Apero.core.instruments.spirou.default_keywords.py` - use OBJECT not
  OBJNAME (reversal of last weeks change) [Neil Cook]
- Update date / version / changelog / documentation. [Neil Cook]


0.7.122 (2021-05-25)
--------------------
- `Apero.recipes.nirps_ha.apero_wave_master_nirps_ha.py` - pep8 updates.
  [Neil Cook]
- `Apero.core.instruments.spirou.pseudo_const.py` - if OBJNAME is None use
  OBJECT header key. [njcuk9999]
- `Apero.core.core.drs_Database.py` +
  `apero.core.instruments.spirou.pseudo_const.py` - address Null vs None
  values in database. [njcuk9999]
- `Apero.core.instruments.spirou.pseudo_const.py` - need to add objectname
  and objectname2 for index database. [njcuk9999]


0.7.121 (2021-05-21)
--------------------
- `Apero.plotting.html.py` `latex.py` `plot_functions.py` - add typing doc
  strings and pep8. [Neil Cook]
- `Apero.plotting.html.py` `latex.py` `plot_functions.py` - add typing doc
  strings and pep8. [Neil Cook]
- `Apero.recipes.nirps_ha.apero_wave_master_nirps_ha.py` +
  `spirou/apero_wave_master_spirou.py` - remove debug hc + fp lines. [Neil
  Cook]
- `Apero.recipes.nirps_ha.apero_wave_master_nirps_ha.py` +
  `spirou/apero_wave_master_spirou.py` + `apero.science.calib.wave.py` -
  move offset code and apply to spirou and nirps. [Neil Cook]
- Update berv keys + remove HIERARCH keys + remove pp keys from post
  products (to be in-line with CADC) [Neil Cook]
- `Apero.core.core.drs_file.py` - make sure we copy all post file
  properties (explains why `header_add` were disappearing) [Neil Cook]
- `Apero.core.instruments.nirps_ha.default_constants.py` -
  `WAVEREF_HC_BOXSIZE` from 5-->13. [Neil Cook]
- `Apero.base.base.py` - remove future warning --> error. [Neil Cook]
- `Apero.plotting.core.py` - update typing/doc strings. [Neil Cook]
- `Apero.plotting.core.py` - update typing/doc strings. [Neil Cook]


0.7.120 (2021-05-19)
--------------------
- `Apero.science.preprocessing.gen_pp.py` - update `resolve_target` (python
  typing) [Neil Cook]
- `Apero.science.calib.gen_calib.py` - fix from logging issues in `check_fp`
  + add doc strings + typing. [Neil Cook]
- `Apero.core.core.drs_database.py` - `load_db` does not log by default.
  [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add database settings to the display
  print out. [Neil Cook]


0.7.119 (2021-05-19)
--------------------
- Test requirements + fix some warnings + add way to filter warnings (db
  mysql connection need func to ignore internal warnings as they are
  weird) [Neil Cook]
- Database - backup databases before deleting (in case I'm being stupid
  and delete them without realising) [Neil Cook]
- `Apero.setup.newprofile.py` - update error message for invalid path /
  apero profile name + change cprint sys.exit message to red. [Neil
  Cook]
- `Apero.setup.*.py` - update installation doc strings + pep8 + bring
  `newprofile.py` inline with changes to install.py. [Neil Cook]


0.7.118 (2021-05-17)
--------------------
- `Apero.setup.install.py` + `apero.tools.module.setup.drs_installation.py`
  - fix problem with database tables going to "MAIN" and problem with
  upper case vs lower case apero profile names (force lower) [Neil Cook]
- Apero.data.spirou.reset.calibdb - remove `master_calib_SPIROU.txt` (not
  longer used) [Neil Cook]
- `Apero.data.nirps_ha.databases.reset.calib.csv` - test 41 orders first
  for wave solution. [Neil Cook]
- `Apero.science.extract.berv.py` - add todo to check epoch for spirou.
  [Neil Cook]
- `Apero.science.calib.shape.py` - Problem with shape when maximum
  correlation between FPs split between pixels (Issue #668) [Neil Cook]
- Must deal with having no epoch - assume it is the observation time in
  this case. [Neil Cook]
- Update version to 0.7.117, update docs, date, changelog. [Neil Cook]


0.7.117 (2021-05-15)
--------------------
- `Apero.science.calib.gen_calib.py` - objname can be Null or None - deal
  with this. [Neil Cook]
- Make sure SKY is checked in OBJECT and OBJNAME even when `TRG_TYPE` is
  set. [Neil Cook]


0.7.116 (2021-05-13)
--------------------
- `Apero.science.calib.wave.py` - make sure qc failure prints to screen.
  [Neil Cook]
- `Apero.core.utils.drs_utils.py` - some rlog columns were still wrong -->
  correct humantime, groupname, levelcrit, `qc_values`, errormsgs. [Neil
  Cook]
- `Apero.recipes.spirou.apero_wave_master_spirou.py` - for master solution
  need an offset test after first HC lines calculation (this is because
  default wave solution can be off from master night if master night is
  far from when the default wave solution was made) [Neil Cook]
- Update `mini_run` files to have `SCIENCE_TARGETS` = All by default. [Neil
  Cook]
- Continue work on recreating databases from files on disk. [Neil Cook]


0.7.115 (2021-05-10)
--------------------
- Update language database. [Neil Cook]
- Add functionality to update databases from files on disk (index, log,
  calib, tellu) [Neil Cook]
- `Apero.data.spirou.reset.runs.*.ini` - correct run.ini with THI and THT.
  [Neil Cook]
- `Apero.core.core.drs_file.py` + `apero.io.drs_fits.py` - make sure headers
  are copied to extensions - was isinstance(header[it], Header) now
  isinstance(header[it], (Header, fits.Header)) [Neil Cook]


0.7.114 (2021-05-06)
--------------------
- CADC output fixes. [Neil Cook]
- More fixes for nirps into 0.7 (works up to `apero_flat)` [Neil Cook]
- Fixes for quicklook sequence. [Neil Cook]


0.7.113 (2021-05-04)
--------------------
- Update runs for NIRPS (LOC(M)AB --> LOC(M)A, LOC(M)C --> LOC(M)B)
  [Neil Cook]
- Update to code to bring NIRPS to 0.7. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - `leak_master` must
  be after thermal masters. [Neil Cook]
- `Apero.science.calib.wave.py` - add printouts for `calc_wave_lines`. [Neil
  Cook]
- `Apero.science.calib.flat_blaze.py` - correct problem with blaze in new
  mini data set (local minima) [Neil Cook]
- Update language database. [Neil Cook]
- Equalise nirps with spirou. [Neil Cook]
- Add program + parallel to log database + add switches for DEBUG files.
  [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]


0.7.112 (2021-04-30)
--------------------
- Make sure keys are added before argparse. [Neil Cook]
- Only update `drs_processing.py` Run runstring once. [Neil Cook]
- Correct typo '--parallel' --> ' --parallel' [Neil Cook]
- Deal with using --parallel argument (stops index database updating in
  a recipe run) [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.core.drs_argument.py` - add parallel argument. [Neil Cook]
- Update language database. [Neil Cook]


0.7.111 (2021-04-28)
--------------------
- `Apero.science.preprocessing.gen_pp.py` - add bad list checker. [Neil
  Cook]
- Update language database. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.tools.recipe.bin.apero_processing.py` - index certain block kinds
  to avoid indexing during recipe runs. [Neil Cook]
- `Apero.science.polar.gen_pol.py` - correct typo
  `STOKESI_CONTINUUM_DETECTION_ALGORITHM` --> `STOKESI_CONTINUUM_DET_ALG`.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.tools.recipe.bin.apero_processing.py` - try to stop re-indexing
  of the database occuring. [Neil Cook]
- `Get_wavesol` requires either 'infile' OR ('header' and 'nbpix') not
  both - correct. [Neil Cook]


0.7.110 (2021-04-27)
--------------------
- `Apero.core.utils.drs_utils.py` - add running to param table
  (rlog.running) [Neil Cook]
- `Apero.science.wave.py` - correct typo `*margs` --> args=margs. [Neil
  Cook]
- Move text to language database + update language database. [Neil Cook]
- Move text to language database and constants to instrument/default
  definitions. [Neil Cook]
- Fix mk tellu `add_wave_keys`. [Neil Cook]


0.7.109 (2021-04-23)
--------------------
- Move `wave.py` --> `wave_old.py`  and move `wave2.py` --> `wave.py`  (and move
  last required functions from `wave_old.py` --> wave.py) + move
  `wave_master_old` + `wave_night_old` to apero/tools/recipes/spirou/ [Neil
  Cook]
- Change recipe names `cal_` `obj_` --> `apero_` [Neil Cook]
- Update changelog + update notes. [Neil Cook]
- Update version/date/changelog/update notes. [Neil Cook]


0.7.108 (2021-04-22)
--------------------
- Fix grouping + fix emailing + fix run.ini files. [Neil Cook]
- Update run.ini files with LOCAB LOCC  (previously LOC)  and LOCMAB
  LOCMC (previously LOCM) [Neil Cook]
- `Apero.core.core.drs_database.py` - fix drsfile being NpyFile. [Neil
  Cook]
- `Apero.science.calib.wave2.py` - must read hc and fp e2ds files in
  `process_fibers`. [Neil Cook]
- Fix `plot_waveref_expected` with large outliers. [Neil Cook]
- Update wave sol with ea fixes. [Neil Cook]


0.7.107 (2021-04-20)
--------------------
- `Apero.tools.module.processing.py` +
  `apero.tools.recipes.bin.apero_processing.py` - remove reset from
  processing. [Neil Cook]
- Add NIRPS 0.6 changes. [Neil Cook]
- `Apero.core.core.drs_file.py` - make sure `obs_dir` is cleaned of
  `block_path` (via `block_kind)` [Neil Cook]
- Remove reset options from processing (do via `apero_reset.py` if
  required) [Neil Cook]
- Update nirps definitions with changes to 0.7 (note nirps still on 0.6
  and needs adding - this just changes 0.7 changes to code left over
  before 0.6 divergence) [Neil Cook]
- `Apero.science.calib.wave.py` - correct type (this is for wave2) -
  eventually move wave -> `wave_old`. [Neil Cook]
- Allow for recipe kind from input args + update recipe defintions with
  new recipe kinds for all sequences. [Neil Cook]
- Apero.recipes.spirou - move old wave sols to `_old` and new from `_ea` to
  main (no extra suffix) [Neil Cook]


0.7.106 (2021-04-20)
--------------------
- Fix grouping + shortnames + set running on construction `(__init__)`
  [Neil Cook]
- Catch warnings on astroquery import. [Neil Cook]
- `Apero.recipes.spirou.cal_wave_*_ea_spirou.py` - fix cavity file. [Neil
  Cook]
- `Apero.core.core.drs_database.py` - change rtype --> `recipe_type` + add
  `recipe_kind`. [Neil Cook]
- `Apero.core.core.drs_argument.py` - add recipe kind global argument.
  [Neil Cook]
- Fix grouping for polar code + change sequences arguments for polar
  code. [Neil Cook]
- `Apero.core.instruments.grouping.py` - work on the grouping for polar
  files. [Neil Cook]
- Fixes to `cal_wave_master_ea` and `cal_wave_night_ea`. [Neil Cook]


0.7.105 (2021-04-15)
--------------------
- Move ea wave functions from wave to wave2. [Neil Cook]
- `Apero.science.calib.wave2.py` - continue work on ea wave sol. [Neil
  Cook]
- `Apero.recipes.spirou.cal_wave_*_ea_spirou.py` - continue update to wave
  master + night ea. [Neil Cook]
- `Apero.plotting.plot_functions.py` - add `legend_no_alpha` +
  `plot_wave_hc_resmap` + `plot_wave_hc_resmap_old`. [Neil Cook]
- `Apero.core.math.py` - add `centered_super_gauss` function (for wave res
  map) [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add plot to
  `cal_wave_master_ea_spirou.py`. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - add WAVERES file
  (copy of WAVERESHC) [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add wave res keywords.
  [Neil Cook]
- `Apero.recipe.spirou.cal_wave_master_ea_spirou.py` - add WAVESOURCE to
  wprops. [Neil Cook]


0.7.104 (2021-04-13)
--------------------
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  `SUIM_CCF_RV_FIT` to summary plots. [Neil Cook]
- `Apero.recipe.spirou.cal_wave_master_ea_spirou.py` - continue work with
  EA on new wave sol. [Neil Cook]
- `Apero.science.gen_pol.py` - add more info to question. [Neil Cook]
- Make sure user can turn off saving to the database. [Neil Cook]
- Continue with polar update. [Neil Cook]
- Update sequence overview flow charts. [Neil Cook]
- `Apero.core.core.drs_file.py` + `apero.science.polar.gen_pol.py` -
  corrects to polar code. [Neil Cook]


0.7.103 (2021-04-10)
--------------------
- Fix ccf typo + `drs_file.DrsPath` distinguish between abspath and
  `obs_dir` and `block_kind`. [Neil Cook]
- `Apero.core.core.drs_file.py` - make block paths real paths (try to fix
  Issue #660) [Neil Cook]
- Remove references to `DRS_DS9_PATH` and `DRS_LATEX_PATH` - either get from
  shutil.which or don't use. [Neil Cook]
- Remove references to `DRS_DS9_PATH` and `DRS_LATEX_PATH` - either get from
  shutil.which or don't use. [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add lsd keywords + lsd
  file. [Neil Cook]
- `Apero.science.calib.gen_calib.py` - correct typo `block_ind` -->
  `block_kind`. [Neil Cook]
- `Apero.core.core.drs_file.py` - sort out length of data, header, names,
  datatype, dtype. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add polar to
  sequences and run.ini files [still requires grouping] [Neil Cook]
- Polar update - add writing polar files [unfinished - needs lsd files]
  [Neil Cook]
- Polar update - add writing polar files [unfinished - needs lsd files]
  [Neil Cook]
- Change return of `drs_file.combine`. [Neil Cook]


0.7.102 (2021-04-08)
--------------------
- Continue work on polar lsd code integration. [Neil Cook]
- Continue work on polar lsd code integration. [Neil Cook]
- Continue work on polar lsd code integration. [Neil Cook]
- Continue work on polar lsd code integration. [Neil Cook]
- Continue work on polar lsd code integration. [Neil Cook]


0.7.101 (2021-04-06)
--------------------
- Continue work on polar code integration. [Neil Cook]
- Continue work on polar code integration. [Neil Cook]
- Continue work on polar lsd integration. [Neil Cook]
- Continue work on polar code integration. [Neil Cook]
- Continue work on polar code integration. [Neil Cook]
- Merge pull request #666 from njcuk9999/v0.7-zsh. [Neil Cook]

  Add zsh support
- Add zsh to setup files. [Thomas Vandal]
- Add first version of zsh files. [Thomas Vandal]


0.7.100 (2021-04-02)
--------------------
- `Apero.recipes.spirou.obj_pol_spirou.py` + `science.polar.gen_pol.py` -
  continue work on polar code. [Neil Cook]
- `Apero.core.core.drs_file.py` - add to Block class (fileset) + move
  `get_file_definition` here + add `get_infile_infilename` function. [Neil
  Cook]
- Move `get_file_definition` to `drs_file.py`. [Neil Cook]
- Start work on polar code. [Neil Cook]
- `Apero.base.drs_db.py` - hide connection debug printout - use later to
  profile. [Neil Cook]


0.7.099 (2021-03-31)
--------------------
- `Apero.base.drs_db.py` - up the wait time to reconnect to 5+-1s `*` 20
  (max 120s) - brute force hack to try to make connections wait longer.
  [Neil Cook]
- `Apero.base.drs_db.py` - up the wait time to reconnect to 10+-2s (from
  0.1+-0.1) - brute force hack to try to make connections wait longer.
  [Neil Cook]
- `Apero.base.drs_db.py` - up the wait time to reconnect to 2+-1s (from
  0.1+-0.1) - brute force hack to try to make connections wait longer.
  [Neil Cook]
- `Apero.base.drs_db.py` - save error from exception. [Neil Cook]
- `Apero.base.drs_db.py` - and connection timing. [Neil Cook]
- `Apero.base.drs_db.py` - try again after connection failure. [Neil Cook]
- `Apero.core.core.drs_file.py` + `science.telluric.fit_tellu.py` - clear a
  possible back log of npy writing + do not populate output dictionary
  for npy files (not required - they shouldn't be in the index database)
  [Neil Cook]


0.7.098 (2021-03-29)
--------------------
- `Apero.base.drs_db.py` - add extra info to connection() error message.
  [Neil Cook]
- `Apero.recipes.spirou.obj_pol_spirou.py` - start integrating polar code.
  [Neil Cook]
- `Apero.base.drs_db.py` - allow dbname to be unset (dbname='NULL') [Neil
  Cook]
- `Apero.tools.module.setup.drs_reset.py` - try to remove files but give
  warning and continue if failed. [Neil Cook]
- `Apero.base.drs_db.py` - add table name to error. [Neil Cook]
- `Apero.base.drs_db.py` - make errors more explicit (database name) +
  close cursor and connections. [Neil Cook]


0.7.097 (2021-03-27)
--------------------
- `Apero.base.drs_db.py` - correct database exception error. [Neil Cook]
- `Apero.science.extract.berv.py` - `**bprops` should be props=bprops. [Neil
  Cook]
- `Apero.base.drs_db.py` - problem with shallow copy on values + need to
  deal with masked column in gtable (re: `input_gaiaid)` [Neil Cook]
- `Apero.base.drs_db.py` - continue integration of changes to the database
  connection + add "out" files to index database + fix `apero_explorer`
  `pandas.to_sql` erasing UNIQUE column. [Neil Cook]


0.7.096 (2021-03-25)
--------------------
- `Apero.base.drs_db.py` - continue work on `_conn_` replacement. [Neil
  Cook]
- `Apero.base.drs_db.py` - we cannot connect until we are going to do
  something --> move all `_conn_` inside places where we actually use the
  database - only connect (then importantly disconnect) each time we do
  something - do not keep connection open. [Neil Cook]
- `Apero.io.drs_fits.py` - deal with not being able to remove a file
  because it doesn't exist (try to test existence again) [Neil Cook]
- `Apero.recipes.*.cal_badpix_*.py` - combine `DARK_DARK` `same_type=False`
  (want to combine `DARK_DARK_TEL` and `DARK_DARK_INT)` [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.7.095 (2021-03-24)
--------------------
- Merge branch 'v0.7.090-test-stable' into v0.7.090-work. [Neil Cook]
- Merge pull request #662 from njcuk9999/v0.7.090-sql-reconnect. [Neil
  Cook]

  Update `drs_db` to reconnect upon cursor creation failure
- Add `KW_OUTPUT` for pp files + `KW_PID` for combined files + recipe in
  index database. [Neil Cook]
- Merge branch 'v0.7.090-test-stable' into v0.7.090-work. [Neil Cook]
- `Apero.base.drs_db.py` - add doc string for connect class and move all
  connections here. [Neil Cook]


0.7.094 (2021-03-19)
--------------------
- Undo unnecessary changes. [cusher]
- Update `drs_db` to reconnect upon cursor creation failure. [cusher]
- `Apero.base.drs_db.py` - add doc string for connect class and move all
  connections here. [Neil Cook]
- `Apero.base.drs_db.py` - add connection timeout for mwsql connection.
  [Neil Cook]
- `Apero.base.drs_db.py` - add connection timeout for mwsql connection.
  [Neil Cook]


0.7.093 (2021-03-17)
--------------------
- `Apero.core.core.drs_file.py` - `get_hkey_2d` dim1/dim2 should be
  integers. [Neil Cook]
- `Apero.data.spirou.reset.runs.other_run.ini` - add LFCFP and FPLFC to
  other run.ini file. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` +
  `recipe_definitions.py` - add LFCFP and FPLFC to sequences. [Neil Cook]


0.7.092 (2021-03-13)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - fix duplicate
  entries (pp + raw) and make badpix `dark_dark` inclusive (int + tel)
  [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - change using
  defaults from warning to normal message. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_defintiions.py` + `blank_run.ini` -
  add a blank sequence (for apero testing and maybe loading raw files to
  index database) [Neil Cook]
- `Apero.tools.module.setup.drs_processing.py` - `_split_string_list` should
  not split by white space unless directly told to (allows spaces in
  filenames) [Neil Cook]


0.7.091 (2021-03-11)
--------------------
- Update `spirou_map_sections.graphml`. [Neil Cook]
- Fix `display_func` + processing `obs_dir`. [Neil Cook]
- Add spirou map sections (for documenation and paper) [Neil Cook]
- `Params.snapshot_table` --> add recipe to args. [Neil Cook]
- Recipes - remove params from log functions. [Neil Cook]
- `Apero.io.drs_fits.py` - add `find_named_extensions` + `update_extension`.
  [Neil Cook]
- `Apero.core.utils.drs_utils.py` - rtype <--> `block_kind`. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - change rtype and `block_kind` for
  recipe.log. [Neil Cook]
- `Apero.core.core.drs_misc.py` - raise value error for non-string name in
  `display_func`. [Neil Cook]
- Remove RecipeLog from `drs_log.py`. [Neil Cook]
- `Apero.core.core.drs_file.py` - add `update_param_table` function. [Neil
  Cook]
- `Apero.core.core.drs_database.py` - add update param table to
  calib/tellu file update. [Neil Cook]
- `Apero.core.constants.param_functions.py` - update `snapshot_table` to
  have recipe.log parameters. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.7.090 (2021-03-09)
--------------------
- `Apero.core.core.drs_file.py` - catch `numpy_load` failure. [Neil Cook]


0.7.089 (2021-03-06)
--------------------
- Need gaiadr for AstroObject. [Neil Cook]
- `Apero.science.calib.wave.py` - correct typo. [Neil Cook]
- `Apero.core.instruments.*.deafult_keywords.py` - add `KW_GAIA_DR` (for
  future determining against dr2/dr3. [Neil Cook]
- Recipes: `.inputtype-->.in_block_str` `.outputtype-->.out_block_str`.
  [Neil Cook]
- `Apero.recipes.*.obj/out_postprocess_*.py` - `DIRNAME-->OBS_DIR`,
  `kind-->block_kind`. [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - add `POLAR_DARK`
  and `POLAR_FP` to DPRTYPES. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - `DIRNAME-->OBS_DIR`,
  `KIND-->BLOCK_KIND`. [Neil Cook]
- `Apero.core.core.drs_file.py` - `kind-->block_kind`. [Neil Cook]


0.7.088 (2021-03-04)
--------------------
- `Apero.core.core.drs_database.py` - deal with null values in index
  database hkeys. [Neil Cook]
- `General.py` --> `gen_xxx.py`, processing fixes. [Neil Cook]


0.7.087 (2021-03-03)
--------------------
- Rework directory/nightname (str --> DrsPath, `night-->obs_dir)`, remove
  whitelist (-->include list) and blacklist (-->exclude list) [Neil
  Cook]
- Rework directory (str --> DrsPath) - [unfinished] [Neil Cook]


0.7.086 (2021-02-27)
--------------------
- `Apero.science.calb.wave.py` - need to worry about updating e2ds files
  with multiple extensions. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - need to add `POLAR_FP`
  and `POLAR_DARK` to obj types. [Neil Cook]
- `Apero.io.drs_fits.py` - warnings for Table.read (with multiple tables)
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `REPROCESS_OBJ_DPRTYPES`. [Neil Cook]
- `Apero.core.core.drs_file.py` - correct `__log__` [Neil Cook]
- `Apero.tools.module.database.manage_databases.py` +
  `apero.recipes.bin.apero_database.py` - add kill switch for database
  stuck with processes `(apero_database.py` --kill) [Neil Cook]


0.7.085 (2021-02-26)
--------------------
- Need to be able to kill database connections. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - do not add nightname
  if already a master sequence. [Neil Cook]
- `Apero.science.calib.shape.py` - `lin_transform_vect` should be list.
  [Neil Cook]
- Correct typos with `snapshot_table` input. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - deal with directory separately from
  file/files (due to needing path between filename and raw/tmp/red path.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - fix headers + dout/hout. [Neil Cook]
- `Apero.core.core.drs_database.py` - condition now comes from uhash for
  index and object dbs. [Neil Cook]
- `Apero.base.drs_db.py` - get condition from uhash if `unique_cols` is
  populated + deal with unique exception text better (force lower case)
  [Neil Cook]
- `Apero.recipes.spirou.cal_ccf_spirou.py` - make sure A and B can be used
  as science fibers. [Neil Cook]


0.7.084 (2021-02-24)
--------------------
- `Apero.core.core.drs_database.py` - deal with unique keys in database.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.core.drs_database.py` - allow for unique columns (by using a
  hash column) in INDEX and HASH databases. [Neil Cook]
- `Apero.core.core.drs_database.py` - allow for unique columns (by using a
  hash column) in INDEX and HASH databases. [Neil Cook]
- Remove breakpoint/breakfunc (use debugger) + add hdict to snapshot
  table + replace most `write_file` with `write_multi` + snapshot tables.
  [Neil Cook]
- Change `display_func` (remove breakpoints/breakfuncs) + start adding
  parameter table to outputs `(write_multi` first) [Neil Cook]


0.7.083 (2021-02-20)
--------------------
- `Apero.core.constants.param_functions.py` - add used functionality to
  keep track of uses of parameters in a recipe (for output table) [Neil
  Cook]
- Continue work on new wave solution by EA [UNFINISHED - solution
  diverges on mean2error while loop) [Neil Cook]
- Continue work on new wave solution by EA [UNFINISHED - solution
  diverges on mean2error while loop) [Neil Cook]
- Continue work on new wave solution by EA [UNFINISHED - requires new
  `calc_wave_lines` func for HC and FP lines) [Neil Cook]


0.7.082 (2021-02-18)
--------------------
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- Apero.science.wave2 - add EA code for new wave solution. [Neil Cook]
- `Apero.core.core.drs_file.py` - drsfile can be 'table' therefore have to
  check if drsfile is DrsInputFile or else deepcopy. [Neil Cook]
- `Apero.core.constants.param_functions.py` - must check for INSTRUMENT
  (as this is used in installation when yaml may not exist) [Neil Cook]


0.7.081 (2021-02-12)
--------------------
- `Apero.science.calib.wave.py` - typing for `generate_res_files`. [Neil
  Cook]
- `Apero.science.calib.wave.py` - correct `generate_res_file` (should return
  names for extensions) [Neil Cook]
- `Apero.base.base.py` - add profile to all database tables - so you can
  change each table in settings. [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - change install message
  (to be more clear) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` +
  `apero.core.core.drs_file.py` - add a tag to `out_post` files + add NEXT
  to primary. [Neil Cook]


0.7.080 (2021-02-11)
--------------------
- Update `UPDATE_NODATE.txt`. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.insturments.spirou.pseudo_const.py` - `get_drs_mode()` - only
  set `DRS_MODE` for OBSTYPE="OBJECT" [Neil Cook]
- Add extension names to all extensions. [Neil Cook]
- `Apero.core.insturments.spirou.recipe_definitions.py` - add `quick_seq`
  (for trigger use) [Neil Cook]
- `Apero.core.utils.drs_startup.py` - setup() must load psuedo constants
  with an instrument (as FILEMOD/RECIPEMOD for recipes / files with no
  instrument come from here) [Neil Cook]
- `Apero.core.core.drs_log.py` - need to allow logger to have params as an
  input. [Neil Cook]
- `Apero.core.constants.param_functions.py` - `load_config` need a default
  option (instrument=None) [Neil Cook]
- Update constants.load, constants.pload (do not define instrument) +
  attempt a better way to read (get first ext automatrically) / write
  fits (do not write in primary) [Neil Cook]
- Get instrument from base.IPARAMS not from definition. [Neil Cook]


0.7.079 (2021-02-10)
--------------------
- Update extraction cosmic ray rejection [UNTESTED] [Neil Cook]
- `Apero.recipes.spirou.cal_thermal_spirou.py` - `thermal_files` are not
  indexed - correct this. [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.tools.module.error.find_error.py` +
  `apero.tools.recipes.dev.apero_langdb.py` - add --find option to
  `langdb.py` that launches `find_error` gui. [Neil Cook]
- `Apero.core.instruments.spirou.pseudo_const.py` - pep8 clean up. [Neil
  Cook]
- `Apero.base.drs_db.py` - surround all connections to cursor with the
  "with" statement to make sure connections are closed in all
  circumstances (i.e. Ctrl+C) [Neil Cook]


0.7.078 (2021-02-09)
--------------------
- Apero.core.instruments.spirou - add `POLAR_FP` and `POLAR_DARK` (similar
  to `OBJ_FP` and `OBJ_DARK)` for polar files with `SBRHB1_P` and `SBR2_P` keys
  used to distinguish between spectroscopy and polarimetry. [Neil Cook]
- `Apero.setup.newprofile.py` - fix code to copy profile files in 0.7
  format. [Neil Cook]
- Add switch between pool and process `(REPROCESS_MP_TYPE)` [Neil Cook]


0.7.077 (2021-02-08)
--------------------
- `Setup.install.py` - add mysql-connector to `module_translation`. [Neil
  Cook]
- Update requirements. [Neil Cook]
- `Apero-drs-spirou.recipe_definitions.py` - change grouping for
  `obj_pp_recipe`. [Neil Cook]
- `Apero.recipe.spirou.obj_postprocess_spirou.py` - remove unused imports.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - add clear file to postprocess. [Neil
  Cook]


0.7.076 (2021-02-04)
--------------------
- `Apero.core.core.drs_file.py` - allow `set_infile` to take a filename.
  [Neil Cook]
- `Apero.core.instruments.spirou.recipe_defintions.py` - add
  `obj_pp_recipe`. [Neil Cook]
- `Apero.recipes.spirou.obj_postprocess_spirou.py` - convert
  `out_postprocess` to a per file (for `apero_processing.py` and multiple
  cores) [Neil Cook]
- Apero.tools.recipes.spirou - move `tellu_db` files here. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - change `FWHM_PIXEL_PSF` -->
  `FWHM_PIXEL_LSF`. [Neil Cook]
- `Apero.ploting.plot_functions.py` - add `tellup_clean_oh` to definitions.
  [Neil Cook]
- `Apero.data.spirou.reset.runs.complete_run.ini` - remove commit() to
  database outside for loops (commit each entry) [Neil Cook]
- `Apero.core.instruments.spirou.recipe_defintions.py` - remove
  `obj_mk_tellu_db` and `obj_fit_tellu_db` from full sequence. [Neil Cook]
- Remvoe commit() to database outside for loops (commit each entry)
  [Neil Cook]
- `Apero.core.core.drs_database.py` - only check last modified for raw
  files. [Neil Cook]


0.7.075 (2021-02-03)
--------------------
- Add thermal flow diagram. [Neil Cook]
- Make sure PyQt5 is installed. [Neil Cook]
- `Apero.science.preprocessing.detector.py` - fix mask1+mask2 -->
  `xpand_mask` now data is fixed. [Neil Cook]
- `Apero.plotting.core.py` - remove Qt4Agg (not supported in matplotlib
  3.3+) [Neil Cook]
- `Apero.core.core.drs_file.py` - allow `read_data` to return data (and not
  set self.data) [Neil Cook]


0.7.074 (2021-02-02)
--------------------
- `Apero.tools.module.setup.drs_installation.py` - clean profile names.
  [Neil Cook]
- `Apero.science.preprocessing.detector.py` - do not do `expand_mask`. [Neil
  Cook]
- `Apero.core.instruments.default.default_constants.py` -
  `PP_COSMIC_BOXSIZE` should be an integer. [Neil Cook]
- `Apero.core.core.drs_database.py` - make sure checking `last_mod` done
  correctly `(exclude_files` + `last_mod` should be arrays not pandas table
  columns) [Neil Cook]
- Update language database. [Neil Cook]
- Update requirements + apero-pip env. [Neil Cook]
- `Apero.tools.module.setup.drs_reset.py` - deal with not having index/log
  database in reduced/tmp resets. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - replace all non
  alphanumeric characters (except `"_")` with `_` (then remove double `__)`
  [Neil Cook]
- `Apero.base.drs_db.py` - add `tname_in_db` function to check tables in
  database for database.tname. [Neil Cook]
- `Apero.core.core.drs_database.py` - add a `last_modified` check for raw
  files (to update them if they've changed) [Neil Cook]
- Update date/version/changelog/update notes/documentation. [Neil Cook]


0.7.073 (2021-01-29)
--------------------
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - deal with "switch"
  arguments (should be user defined only) [Neil Cook]
- `Apero.core.core.drs_file.py` - deal with not selecting DEBUG-uncorr
  files (assume they don't have runargs) [Neil Cook]
- `Apero.science.preprocessing.detector.py` - finish `correct_cosmics`
  function + add typing. [Neil Cook]
- `Apero.recipes.*.cal_preprocess_*.py` - add changes to add
  `correct_cosmics` functionality. [Neil Cook]
- `Apero.core.math.general.py` - add `xpand_mask` function (for pp cosmic)
  [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add `PP_COSMIC` keywords.
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add `PP_COSMIC`
  constants. [Neil Cook]


0.7.072 (2021-01-27)
--------------------
- `Apero.recipe.spirou.cal_preprocess_spirou.py` - start adding cosmic ray
  reject code. [Neil Cook]
- `Apero.core.core.drs_file.py` - add loading all extensions to
  `drs_file.get_data`. [Neil Cook]
- `Apero.science.calib.localisation.py` + `wave.py` - add `KW_PID` to writing
  functions. [Neil Cook]
- `Apero.core.instruments.default.default_constants.py` - add
  `PLOT_TELLUP_CLEAN_OH` to `__all__` [Neil Cook]
- Update language database. [Neil Cook]


0.7.071 (2021-01-26)
--------------------
- `Apero.science.telluric.gen_tellu.py` - add EA's changes to sky model.
  [Neil Cook]
- `Apero.science.calib.wave.py` - add `KW_PID` to wave writing functions.
  [Neil Cook]
- `Apero.plotting.plot_functions.py` - add `plot_tellup_clean_oh` function.
  [Neil Cook]
- Apero.data.spirou.telluric - update `sky_PCs.fits`. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  `TELLUP_CLEAN_OH` to plots. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `TELLUP_OHLINE_NBRIGHT`. [Neil Cook]


0.7.070 (2021-01-22)
--------------------
- Documentation - todo.rst - add to known issues. [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - fix hasattr. [Neil
  Cook]
- Update setup/envs/apero-pip. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - deal with Etienne using 0 as
  flag - bad bad bad. [Neil Cook]
- `Apero.core.core.drs_file.py` - do not check metric for `DARK_DARK` and
  `HC_HC`. [Neil Cook]


0.7.069 (2021-01-20)
--------------------
- Update language database. [Neil Cook]
- `Apero.core.core.drs_file.py` - need to deal with metric removing all
  files. [Neil Cook]
- Update typo in documentation `WAVE_{FIBER}` --> `LEAKM_{FIBER}` [Neil
  Cook]
- README.md - update typo - `WAVE_{FIBER}` --> `LEAKM_{FIBER}` [Neil Cook]
- `Apero.core.core.drs_file.py` - must update kind when `forced_dir`. [Neil
  Cook]
- `Apero.core.core.drs_database.py` - must update kind when `forced_dir`.
  [Neil Cook]
- `Apero.core.core.drs_argument.py` - must update kind when `forced_dir`.
  [Neil Cook]


0.7.068 (2021-01-19)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - need to make sure
  directory is set to None if not the master recipe. [Neil Cook]
- Update TODO. [Neil Cook]
- `Apero.recipes.spirou.*` - make sure recipes with two levels end log1 as
  well as log2. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - edit how we `write_logfile` when set
  present (only log set) else log self. [Neil Cook]
- `Apero.recipes.spirou.cal_thermal_spirou.py` - must update some header
  keys to match `cal_thermal` (not `cal_extract` that was used internally)
  [Neil Cook]
- Update todo. [Neil Cook]
- `Apero.plotting.core.py` - matplotlib.use does not have warn argument in
  3.3.3. [Neil Cook]


0.7.067 (2021-01-15)
--------------------
- `Apero.core.instruemnts.spirou.file_definitions.py` - add
  `remove_drs_hkeys` and `remove_std_hkeys`. [Neil Cook]
- `Apero.recipes.*.out_postprocess_{instrument}.py` - add processing
  header updates. [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - add
  `NON_CHECK_DUPLICATE_KEYS`, `FORBIDDEN_OUT_KEYS` methods. [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add `post_exclude`
  argument where required. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `POST_HDREXT_COMMENT_KEY`. [Neil Cook]
- `Apero.core.core.drs_file.py` - add header modifications to DrsOutFile
  (and DrsOutFileExtension) [Neil Cook]
- `Apero.core.constants.constant_functions.py` - add `post_exclude` to
  Keyword class. [Neil Cook]


0.7.066 (2021-01-14)
--------------------
- `Apero.core.instruemtns.spirou.file_definitions.py` - add TODOs re:
  meeting with Chris. [Neil Cook]
- Update documentation. [Neil Cook]
- `Apero.tools.recipe.dve.apero_constants.py` - add way to generate
  glossary from constants/keywords. [Neil Cook]
- `Apero.base.base.py` - add bool to the STRTYPES. [Neil Cook]
- `Apero.instruments.default.default_keywords.py` - add descriptions for
  Keywords. [Neil Cook]
- Update todo/update notes. [Neil Cook]
- `Apero.tools.recipes.dev.apero_constants.py` - add check that dev wants
  to clean constants (and return success/fail) [Neil Cook]
- Update descriptions of Const. [Neil Cook]
- `Apero.tools.module.utils.constants_tools.py` - simplify description
  tool - manually edit after. [Neil Cook]


0.7.065 (2021-01-13)
--------------------
- `Apero.tools.module.utils.constants_tools.py` - add todo to change
  adding descriptions to constants. [Neil Cook]
- Update todo and update notes. [Neil Cook]
- `Apero.tools.recipes.dev.apero_constants.py` - add a tool for dealing
  with constants. [Neil Cook]
- `Apero.tools.module.testing.drs_dev.py` - fix mod from ImportModule.
  [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - add settings for
  `apero_constants.py`. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - fix mod from dev recipes. [Neil
  Cook]
- Correct typos in `default_consts`. [Neil Cook]
- `Apero.core.core.drs_file.py` - remove dprtype filter on combine metric
  1 (accept all files) [Neil Cook]


0.7.064 (2021-01-11)
--------------------
- Update TODO list. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.core.drs_file.py` - metric 1 only valid for specific types -
  deal with this. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `COMBINE_METRIC_THRESHOLD1` and `COMBINE_METRIC1_TYPES`. [Neil Cook]
- `Apero.core.core.drs_file.py` - add metric for rejecting combine files.
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add `COMBINE_THRESHOLD`.
  [Neil Cook]


0.7.063 (2021-01-08)
--------------------
- Update language database. [Neil Cook]
- Update `update_notes` + readme + todo.rst. [Neil Cook]
- `Apero.recipes.nirps_ha.out_postprocess_nirps_ha.py` - copy over work
  from SPIRou to NIRPS (placeholder until we have a post process file
  for NIRPS) [Neil Cook]
- `Apero.core.instruments.*` - update `recipe_definitions.py` and
  `file_definitions.py` (and copy to NIRPS) [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add
  `add_non_file_args` function (to deal with setting --night,
  --wnightlist, --bnightlist from processing) [Neil Cook]
- `Apero.recipe.*.out_{instrument}` -->
  `apero.recipe.*.out_postprocess_{instrument}` [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - make all out file
  types not required. [Neil Cook]
- Update run.ini files with `out_postprocess`. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add `POST_CLEAR_REDUCED`
  and `POST_OVERWRITE` to constants. [Neil Cook]
- `Apero.core.core.drs_file.py` - update `process_links` and return
  success/failure. [Neil Cook]


0.7.062 (2021-01-07)
--------------------
- `Apero.recipes.spirou.out_spirou.py` - continue work on `out_spirou.py`.
  [Neil Cook]
- `Apero.core.instruments.spirou.output_filenames.py` - continue work on
  `post_file` (outfunc) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - update out files
  (continued work) [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - reformat `index_keys`. [Neil
  Cook]
- `Apero.core.core.drs_file.py` - move `output_dictionary` to DrsInputFile,
  and continue work on DrsOutFile. [Neil Cook]
- `Core.core.drs_database.py` - fix hkeys loop in
  `IndexDatabase.get_entries()` and add `_hkey_condition`. [Neil Cook]
- `Tools.recipe.bin.apero_listing.py` + `apero.core.core.drs_database.py` -
  update `apero_listing.py` to handle wrong number of columns. [Neil Cook]


0.7.061 (2021-01-06)
--------------------
- `Apero.recipes.out_spirou.py` - continue adding code to process
  `post_process` files. [Neil Cook]
- `Apero.core.instruments.spirou.*` - add `post_file` options. [Neil Cook]
- `Apero.core.instruments.*.default_config.py` - add `DRS_DATA_OUT`
  directory (for post processed files) [Neil Cook]
- `Setup.install.py` + `apero.tools.module.setup.drs_installation.py` - add
  database options from command line. [Neil Cook]


0.7.060 (2021-01-05)
--------------------
- Update language database and todo list. [Neil Cook]
- `Tools.module.database.database_gui.py` - fix saving of database (table
  should be database.tname not self.kind) [Neil Cook]
- `Apero.*` - add first work for post processing `(out_{instrument}.py)`
  [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add `KW_IDENTIFIER`.
  [Neil Cook]
- `Core.core.drs_file.py` - add DrsOutFileExtension and DrsOutFile for
  post processing of files. [Neil Cook]
- Update `default_constants.py` `default_keywords.py` `pseudo_const.py`. [Neil
  Cook]
- Update language database + update notes. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - get template from user
  definition (if present) [Neil Cook]
- Documentation - add `cal_shape_spirou_schematic`. [Neil Cook]
- Update documentation. [Neil Cook]
- Update `file_definitions.py` and `recipe_definitions.py`. [Neil Cook]
- `Apero.core.core.drs_file.py` - make checksum upper case. [Neil Cook]


0.7.059 (2020-12-24)
--------------------
- Update object database. [Neil Cook]
- `Apero.tools.module.database.manage_databases.py` - update
  `make_object_reset` (OBJNAME-->OBJECT) [Neil Cook]
- Update notes and todo. [Neil Cook]
- `Apero.tools.module.setup.drs_reset.py` - for reseting tmp/red dirs also
  reset databases. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add shortname to
  processing for all recipes. [Neil Cook]
- `Apero.science.calib.wave.py` - add wave coeffs table. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - add sname (shortname) and rtype
  (raw/tmp/red) [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add rtype tp recipe log
  (raw/tmp/red) [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - add short name. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - change columns. [Neil
  Cook]
- `Apero.core.core.drs_file.py` - checksum for filename (untested) [Neil
  Cook]
- `Apero.core.core.drs_database.py` - add delete row functions (for reset)
  [Neil Cook]
- `Core.core.drs_argument.py` - add special shortname argument (to carry
  short name forward to recipe) [Neil Cook]


0.7.058 (2020-12-22)
--------------------
- Update todo + `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - deal with being offline
  (warning + skip step) [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - deal with multiple `__` in a
  row (replace with `_)` [Neil Cook]
- `Tools.recipes.spirou.cal_drift_spirou.py` - added support for `OBJ_FP`
  and `DARK_FP` for `cal_drift`. [Neil Cook]
- `Apero.science.calib.shape.py` - `max_dxmap_info` must have three terms.
  [Neil Cook]


0.7.057 (2020-12-22)
--------------------
- Update todo (more tasks) [Neil Cook]
- `Apero.tools.module.database.manage_databases.py` - add the new
  `astro_obj.update_objects`. [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - add an update target method to
  `astro_obj`. [Neil Cook]
- Update todo. [Neil Cook]
- `Apero.science.calib.shape.py` - pep8 too long line. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - set `log_file` and `plot_dir` to "Not Set"
  [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add back log file and correct typo
  kwargs --> skwargs. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - correct
  `PP_BAD_EXPTIME_FRACTION`. [Neil Cook]
- `Apero.science.calib.localisation.py` - fix qc logic for `MAX_RMPTS_POS`
  and `MAX_RMPTS_WID`. [Neil Cook]
- `Apero.tools.recipe.spirou.cal_expmeter_spirou.py` - add --fibers input
  to choose fibers to add to mask. [Neil Cook]
- `Apero.core.core.drs_misc.py` - try to fix integer scalar bug. [Neil
  Cook]


0.7.056 (2020-12-20)
--------------------
- Re-save shape master schematic. [Neil Cook]
- Add shape master schematic + add tools pages (empty for now) [Neil
  Cook]
- Add to localisation documentation. [Neil Cook]
- Add update object database to `apero_processing.py`. [Neil Cook]


0.7.055 (2020-12-17)
--------------------
- Add 10% exptime limit in preprocessing. [Neil Cook]
- Update documentation. [Neil Cook]


0.7.054 (2020-12-16)
--------------------
- Update todo/update notes and documentation. [Neil Cook]
- Update todo list. [Neil Cook]
- Update todo list. [Neil Cook]
- Add `apero_database.py` - to import csv file to database and export
  database to csv file. [Neil Cook]
- Update language database. [Neil Cook]
- Update documentation. [Neil Cook]
- `Apero.base.drs_base` + `apero.lang.core.drs_lang.py` - `drs_base.BETEXT`
  from langdb.csv and language proxy from same function. [Neil Cook]
- Update version/date/changelog/documentation. [Neil Cook]


0.7.053 (2020-12-15)
--------------------
- `Apero-drs.setup.install.py` - update requirements path and weird import
  modules (not equal to module name) [Neil Cook]
- Correct requirements. [Neil Cook]
- Update todo list. [Neil Cook]
- `Apero.tools.recipe.bin.apero_reset.py` - must work out files to exclude
  before warn statement. [Neil Cook]
- `Apero.tools.module.setup.drs_instllation.py` - add database
  installation steps. [Neil Cook]
- `Apero.lang.core.drs_lang.py` - need to check whether language database
  has a table yet (and don't try getting it if it doesn't exist yet)
  [Neil Cook]
- `Apero.base.base.py` - try getting all parameters from allparams (if we
  are updating an installation these all will be filled, if installing
  for first time some will be filled) [Neil Cook]


0.7.052 (2020-12-14)
--------------------
- Update documentation. [Neil Cook]
- Only resolve objects for `OBJ_FP` and `OBJ_DARK` + do not add multiple
  rows for `KW_OBJNAME`. [Neil Cook]


0.7.051 (2020-12-12)
--------------------
- Continue updating documentation. [Neil Cook]
- `Core.instrument.spirou.default_constants.py` - change central column to
  2044 (was 2500 - why?) [Neil Cook]
- Update documentation. [Neil Cook]


0.7.050 (2020-12-10)
--------------------
- Update todo list. [Neil Cook]
- `Apero_reset.py` + `apero_processing.py` - do not warn if reset log file
  is present (and skip it) [Neil Cook]
- Update language database. [Neil Cook]
- Apero.documentation.working.user.general.todo.rst - update todo list.
  [Neil Cook]
- `Apero.plotting.core.py` - deal with plt = None. [Neil Cook]
- `Apero.tools.moduile.processing.drs_processing.py` - deal with no plt
  import. [Neil Cook]


0.7.048 (2020-12-10)
--------------------
- `Apero.core.instruments.default.grouping.py` +
  `apero.tools.module.processing.drs_processing.py` - add master value to
  set directory name. [Neil Cook]
- Apero.lang - force the encoding (remove bad characters) [Neil Cook]
- Apero.lang - update reset files. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - revert to Process
  (Pool is not working) [Neil Cook]
- `Apero.lang.core.drs_lang.py` - make sure reset csv files are utf-8
  encoded. [Neil Cook]


0.7.047 (2020-12-07)
--------------------
- `Apero-drs.apero.base.drs_db.py` - user and host must come from
  arguments. [Neil Cook]
- `Apero-drs.apero.base.drs_db.py` - must reset path after call to super.
  [Neil Cook]
- `Apero-drs.apero.base.drs_db.py` - path must be set before we check
  mysql. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - try fixing freezing
  Pool. [Neil Cook]


0.7.046 (2020-12-04)
--------------------
- `Apero.data.nirps_ha.calibdb.MASTER_WAVE_NIRPS_HA.fits` - update default
  wave solution. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - import matplotlib to
  close plots. [Neil Cook]
- `Apero.plotting.core.py` - move import for matplotlib to separate
  function `(import_matplotlib)` [Neil Cook]
- `Apero.data.nirps_ha.reset.calibdb` - Add Etiennes new `MASTER_WAVE` file
  for NIRPS. [Neil Cook]
- `Apero.io.drs_fits.py` - deal with HIERARCH keys and keys longer than 8
  characters better. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - deal with not using
  recipe. [Neil Cook]


0.7.045 (2020-12-02)
--------------------
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - move `class_name` outside `__init__`
  [Neil Cook]
- `Apero.core.instruments.default_keywords.py` - add `combine_method` for
  keywords that require it. [Neil Cook]
- `Apero.core.instrument.*.pseudo_const.py` - add `class_name`. [Neil Cook]
- `Apero.core.core.drs_file.py` - update combine to include updating the
  headers. [Neil Cook]
- `Apero.core.core.drs_base_classes.py` - move `class_names` outside
  `__init__` [Neil Cook]
- `Apero.core.constants.constant_functions.py` - add `combine_method` to
  Keyword Class. [Neil Cook]
- Update todo list. [Neil Cook]
- `Apero.core.instruments.default.grouping.py` - continue work on
  grouping. [Neil Cook]
- For key, item in `self.__dict__` --> for key, item in
  `self.__dict__.items()` [Neil Cook]


0.7.044 (2020-12-01)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - for skip add
  nightname to whitelist. [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - typo `get_key` --> `get_hkey`.
  [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - add a `group_func` storage in recipe
  instance. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add group funcs
  for all functions to be used in `apero_processing`. [Neil Cook]
- `Apero.tools.module.processing.drs_grouping_functions.py` +
  `apero.core.instruments.default.grouping.py` - add grouping functions -
  so `apero_processing` can use custom functions to group files/args for
  processing. [Neil Cook]


0.7.043 (2020-11-30)
--------------------
- Update todo/update/docs. [Neil Cook]
- Apero.science.telluric - add berv coverage to template construction.
  [Neil Cook]
- Add `plot_mktemp_berv_cov` to `plot_functions.py`. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` `default_keywords.py` -
  add berv correction keywords/constants. [Neil Cook]


0.7.042 (2020-11-27)
--------------------
- `Apero.base.drs_db.py` - correct typo values--> values=values. [Neil
  Cook]
- `Core.instruments.*.pseudo_const.py` - add `FIBER_LOC`. [Neil Cook]
- `Apero.science.calib.localisation.py` - update cent/wid coefficient
  tables. [Neil Cook]
- `Apero.base.drs_db.py` - force table to be set. [Neil Cook]


0.7.041 (2020-11-26)
--------------------
- `Apero.base.drs_base.py` - do not call exception - raise exception.
  [Neil Cook]
- `Apero.base.drs_db.py` - correct self.database.get to include table.
  [Neil Cook]
- Update todo list + documentation. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.tools.module.database.manage_database.py` - must do a super call
  in Database Exception + set self.tname after super (MySqlDatabasE)
  [Neil Cook]
- `Apero.base.drs_db.py` - remove reference to 'MAIN' (replace with
  database.tname) - so mysql can write to different tables - make sql
  tname be `{kind}_{profile}` from database.yaml. [Neil Cook]
- `Apero.apero.instruments.spirou.recipe_defintions.py` - add masknormmode
  option. [Neil Cook]
- `Apero.science.velocity.general.py` - add in ccf mask norm options.
  [Neil Cook]
- Update documentation. [Neil Cook]
- Update update notes + todo. [Neil Cook]
- `Apero.core.core.drs_database.py` - if all rows have rawfix=1 don't do
  loop. [Neil Cook]
- `Apero.core.core.drs_database.py` - do not fix header if rawfix == 1.
  [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add some print
  statements about progress + update language database. [Neil Cook]
- `Apero.tools.recipes.dev.apero_langdb.py` - add reload option (to reload
  the database from reset files but not regenerate reset files) [Neil
  Cook]
- Update language database. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - format global
  condition better. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - only show
  overwriting value if original value was not null (None) + move all
  conditional filters that are not recipe specific outside the recipe
  loop. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - filter objects in `SCIENCE_TARGETS` and
  `TELLURIC_TARGETS` by tstars+ostars (i.e. all on disk) [Neil Cook]


0.7.040 (2020-11-25)
--------------------
- Update documentation. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - correct typo value --> objname. [Neil
  Cook]
- Merge remote-tracking branch 'origin/v0.7.000-pre' into v0.7.000-pre.
  [Neil Cook]
- `Apero.tools.processing.drs_processing.py` - correct SQL logic for
  conditions. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` +
  `tools.module.processing.drs_processing.py` - add template stars to
  `process_adds/add_extra/update_args`. [Neil Cook]
- `Apero.base.drs_db.py` - correct arg for error (DatabaseError) [Neil
  Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  `teplate_required` to `tellu_seq` and `science_seq`. [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - have to search colnames of
  table. [Neil Cook]
- `Apero.tools.module.processing.py` - deal with `RECAL_TEMPLATE` = False
  and rejecting objnames with templates. [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - add `list_current_templates`
  function. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - add `template_required` flag (to be
  added in sequences) [Neil Cook]
- `Apero.core.instruments.spirou.py` - add `template_required` to MKTELLU3,4
  FTELLU2,3. [Neil Cook]
- `Apero.data.*.reset.runs` - correct typo: `RECAL_TEMPALTES` -->
  `RECAL_TEMPLATES`. [Neil Cook]


0.7.039 (2020-11-24)
--------------------
- Update language database. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add code to set
  `science_targets` and `telluric_targets` from command line args + add
  rejecting via odometer codes. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add
  `ODOCODE_REJECT_GSHEET_ID` and `ODOCODE_REJECT_GSHEET_NUM` to constants.
  [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - add getting the rejection list
  from googlesheet. [Neil Cook]
- `Apero.data.*.reset.runs.*run.ini` - add `USE_ODO_REJECTLIST` and
  `RECAL_TEMPLATES` to run.ini files. [Neil Cook]
- `Apero.core.instruments.default.recipe_definitions.py` - add
  `--science_targets` and `--telluric_targest` to argumnets of
  `apero_processing`. [Neil Cook]
- `Apero.core.core.drs_text.py` - add `cull_leading_trailing` function.
  [Neil Cook]


0.7.038 (2020-11-23)
--------------------
- `Apero.recipes.spirou.obj_mk_template_spirou.py` +
  `science.telluric.tempalte_tellu.py` - deal with copying hdict/header
  better. [Neil Cook]
- `Apero.core.core.drs_file.py` - try to populate `output_dict` (for index
  database) differently. [Neil Cook]
- Apero - telluric - add TEMPLATE TIME to `mk_tellu` / `fit_tellu` products.
  [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - add a
  `generate_template_hash` function. [Neil Cook]
- `Apero.*` - telluric - add number of files and template hash for better
  id of template. [Neil Cook]
- `Apero.recipes.spirou.cal_preprocess_spirou.py` - add object database
  outside for loop. [Neil Cook]
- Add first test of a setup.py. [Neil Cook]
- Update requirements/environments. [Neil Cook]
- Update environments to use mostly pip - astropy 4.1. [Neil Cook]
- `Apero.science.calib.localisation.py` - add coefficients as tables in
  the fits files. [Neil Cook]


0.7.037 (2020-11-20)
--------------------
- `Apero.lang.core.drs_lang.py` - only report when tkey is not tvalue
  (otherwise we get duplication) [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add python modules being used to
  log. [Neil Cook]
- `Apero.base.base.py` - add `RECOMM_USER` and `RECOMM_DEV`. [Neil Cook]
- Update `requirements_developer.txt` and rint must be a single number
  (not array) [Neil Cook]


0.7.036 (2020-11-18)
--------------------
- Update installation. [Neil Cook]
- Update installation. [Neil Cook]
- Update installation. [Neil Cook]
- Update installation. [Neil Cook]
- Update installation. [Neil Cook]
- `Apero.lang.core.drs_lang.py` - deal with no language database and
  return proxy to language database. [Neil Cook]
- `Apero.base.drs_db.py` - add a proxy language database (for when we
  don't have access to the database) [Neil Cook]
- Update changelog/version/date/documentation/language database. [Neil
  Cook]


0.7.035 (2020-11-18)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - do not worry about
  nulls - all raw filters should be present in index database. [Neil
  Cook]
- `Apero.core.utils.drs_recipe.py` - remove files from `add_filters` (should
  only be raw filters because we use raw files) [Neil Cook]
- `Apero.core.core.drs_file.py` - if column is masked don't filter by it.
  [Neil Cook]


0.7.034 (2020-11-17)
--------------------
- `Apero.*` - correct problems with textentry. [Neil Cook]
- `Apero.base.*` `apero.core.core.*` - add/update import rules. [Neil Cook]
- `Apero.base.*` - move none base modules to core.core. [Neil Cook]
- `Apero.base.drs_exceptions.py` - reorganise exceptions. [Neil Cook]
- `Apero.*` - replace TextEntry with textentry. [Neil Cook]


0.7.033 (2020-11-14)
--------------------
- Update language database. [Neil Cook]
- `Apero.base.drs_base.py` `drs_db.py` `drs_text.py` + `lang.core.drs_lang.py` -
  use BETEXT `base_error` and `base_printer`. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - move `LANG_DB_COLUMNS`
  to `base.py` (same with INSTRUMENTS definition) [Neil Cook]
- `Apero.tools.recipe.dev.apero_langdb.py` - update for new language
  database. [Neil Cook]
- `Apero.tools.module.database.manaage_database.py` - deal with change to
  language db functionality. [Neil Cook]
- Update language database files. [Neil Cook]
- `Apero.core.core.drs_database.py` - move language database stuff to
  `drs_db.py`. [Neil Cook]
- `Apero.base.*` - start moving around base functionality (for base
  lang/print/error integration) [UNFINISHED] [Neil Cook]
- `Apero.base.drs_base.py` - add place to add base base functions. [Neil
  Cook]
- `Apero.base.drs_db.py` - add BaseDatabaseManager and LanguageDatabase
  classes. [Neil Cook]
- `Apero.base.base.py` - add language variables to base and re-organise
  order of base constants. [Neil Cook]


0.7.032 (2020-11-12)
--------------------
- `Apero.core.core.drs_argument.py` - change sql column names to not be
  reserved names and change X==Y -> X=Y. [Neil Cook]
- `Apero.base.drs_db.py` - pandas functions have to be abstracted. [Neil
  Cook]
- `Apero.recipes.*.cal_wave_*` + `apero.science.calib.wave.py` - add calls
  to database and missing database keys. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - allow log database from parent. [Neil
  Cook]
- `Apero.base.drs_db.py` - add doc strings to new functions. [Neil Cook]
- `Apero.base.drs_db.py` + `apero.core.core.drs_database.py` +
  `apero.tools.module.database.database_gui.py` + `manage_databases.py` -
  modify MySQL feature (after testing) [Neil Cook]


0.7.031 (2020-11-10)
--------------------
- `Apero.science.preprocessing.gen_pp.py` - do not hard code googlesheet
  columns - now defined at top and separate from database col names.
  [Neil Cook]
- `Apero.tools.module.database.database_gui.py` + `manage_databases.py` -
  add path back to `database_wrapper`. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - deal with reloading filemod and
  recipemod when instrument changes. [Neil Cook]
- `Apero.core.core.drs_database.py` - deal with sqlite3 vs mysql (with
  paths) [Neil Cook]
- `Apero.base.drs_db.py` - make sure all table names end with `_TABLE` (to
  avoid SQL commands) [Neil Cook]


0.7.030 (2020-11-09)
--------------------
- `Apero.tools.module.database.manage_database.py`  - replace calls to
  `drs_db.Database` with `drs_db.database_wrapper` and calls to 'MAIN' table
  with self.kind. [Neil Cook]
- `Apero.tools.module.database.database_gui.py`  - replace calls to
  `drs_db.Database` with `drs_db.database_wrapper` and calls to 'MAIN' table
  with self.kind. [Neil Cook]
- `Apero.science.preprocessing.gen_pp.py` - replace calls to
  `drs_db.Database` with `drs_db.database_wrapper` and calls to 'MAIN' table
  with self.kind. [Neil Cook]
- `Apero.core.core.drs_database.py` - replace calls to `drs_db.Database`
  with `drs_db.database_wrapper` and calls to 'MAIN' table with self.kind.
  [Neil Cook]
- `Apero.base.drs_db.py` - start implementing MySQL as an alternative to
  sqlite [UNFINISHED/UNTESTED] [Neil Cook]
- `Apero.tools.recipes.bin.apero_log_stats.py` - update to use from
  database. [Neil Cook]


0.7.029 (2020-11-04)
--------------------
- `Apero.tools.resources.images.spirou_logo.png` - tmp icon for apero
  explorer app. [Neil Cook]
- `Apero.tooks.recipe.bin.*` - remove instrument from arguments (now from
  `DRS_UCONFIG` install yaml) [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - deal with reset and
  validate codes no longer needing instrument. [Neil Cook]
- `Apero.tools.module.database.database_gui.py` - add `is_openable` and
  `load_file` functions to database handler + add option if file is open
  to open it (in right click popup menu) [Neil Cook]
- `Apero.core.utils.drs_startup.py` - check that instrument is None or
  matches install.yaml (in `DRS_UCONFIG)` [Neil Cook]
- `Apero.core.instruments.default.recipe_definitions.py` - remove all
  instrument arguments (now get from `DRS_UCONFIG` install yaml) [Neil
  Cook]
- `Apero.base.drs_db.py` - fix backup replace path. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - remove
  `RESET_LOGFITS`. [Neil Cook]
- `Apero.data.*.reset.runs.*` - remove references to `reset_logfits` - now a
  database. [Neil Cook]
- `Apero.science.calib.wave.py` - wavefile must have params. [Neil Cook]
- `Apero.science.extract.berv.py` - correct typo DPRTPYE-->DPRTYPE. [Neil
  Cook]


0.7.028 (2020-10-30)
--------------------
- Recipes - update `get_berv` parameters. [Neil Cook]
- `Apero.science.extract.berv*` - finish update to berv code (using. [Neil
  Cook]
- `Apero.recipes.*cal_extract_*` - update args for `get_berv`. [Neil Cook]
- `Apero.io.drs_fits.py` - make sure get function pushes NaN back to
  np.nan. [Neil Cook]


0.7.027 (2020-10-29)
--------------------
- Update update notes + add update header file. [Neil Cook]
- `Apero.science.prepreocessing.py` - make AstroObject pickeable. [Neil
  Cook]
- `Apero.sciience.extract.berv2.py` - redo berv code now object resolving
  done in preprocessing [UNFINISHED] [Neil Cook]
- `Apero.recipes.spirou.cal_preprocess_spirou.py` - add the `resolve_target`
  function to update header. [Neil Cook]
- `Apero.io.drs_fits.py` - add a `set_key` function (for using a
  keywordstore) [Neil Cook]
- Apero.data.database.reset.object.csv - update colnames. [Neil Cook]
- `Apero.core.instruments.*.deafult_keywords.py` - add `DRS_{RESOLVE}`
  keywords. [Neil Cook]
- `Apero-drs.apero.core.core.drs_database.py` - cahnge "GAIAID" -->
  `GAIA_COL_NAME`. [Neil Cook]


0.7.026 (2020-10-28)
--------------------
- Apero.data.spirou.database.reset.object.csv - update object reset file
  (with new values) [Neil Cook]
- `Apero.tools.module.database.manage_database.py` - must load objdbm.
  [Neil Cook]
- `Apero.tools.moduile.database.manage_database.py` - update object
  database and add new way to reset object csv file. [Neil Cook]
- `Apero.science.preprocessing.py` - move `general.py` --> `gen_pp.py`. [Neil
  Cook]
- `Apero.recipes.spirou.cal_preprocess` - todo - resolve target. [Neil
  Cook]
- `Apero.core.instruments.spirou.default_keywords.py` - update
  objra/objdec to `ra_deg` and `dec_deg`. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - update columns for
  object database (sources) [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - update `OBJ_LIST`
  constants. [Neil Cook]
- `Apero.core.core.drs_database.py` - make sure obj database adds sources
  + use set (update row) when gaia id exists (do not add a new row)
  [Neil Cook]


0.7.025 (2020-10-26)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - `run_process` function
  - `generate_run_table` requires module not recipe (should be the recipe
  to run not the recipe it is called from) [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - update `get_non_tellu_objs` for
  use with index database. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_db_spirou.py` +
  `obj_mk_tellu_db_spirou.py` + `obj_spec_spirou.py` - updaet with database
  interface. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - make sure filters are stripped of
  leading/trailing white spaces. [Neil Cook]


0.7.024 (2020-10-23)
--------------------
- `Apero.tools.module.processing.drs_processing.py` - modify `run_process`
  to work with index database. [Neil Cook]
- `Apero.recipes.spirou.obj_mk_tellu_db_spirou.py` - start work to fix
  this [UNFINISHED] [Neil Cook]
- `Apero.core.utils.drs_utils.py` - allow `update_index_db` to take in a
  database (so we don't read many times), modify `find_files` to accept
  lists of filters. [Neil Cook]
- `Apero.core.core.drs_database.py` - add a `get_entries` method to
  LogDatabase (for skip table) [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - add aliases column
  from object database. [Neil Cook]
- `Apero.core.core.drs_database.py` - add to object database functions.
  [Neil Cook]


0.7.023 (2020-10-21)
--------------------
- `Apero.tools.module.database.manage_databases.py` - log database should
  use `LOG_DB_COLUMNS` from pconst. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - load database on creation. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - change `drs_log.RecipeLog` to
  `drs_utils.RecipeLog`. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - group is sql keyword
  - use groupname. [Neil Cook]
- `Apero.tools.module.database.database_gui.py` - `list_database` now
  returns classes - fix return and get paths. [Neil Cook]
- `Apero.core.core.drs_file.py` - `remove_insuffix` in args should be None
  not False (leave to default value unless set) [Neil Cook]


0.7.022 (2020-10-20)
--------------------
- `Apero.core.core.drs_file.py` - catch bad files in `last_modified`. [Neil
  Cook]
- `Apero.base.drs_db.py` - exectue --> execute. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - remove
  `obj_mk_tellu_db` and `obj_fit_tellu_db` from `limited_seq`. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_db_spirou.py` - remove
  `apero.io.drs_text` `(apero.base.drs_text)` [Neil Cook]
- `Apero.core.core.drs_file.py` - only add `last_modified` time if file
  exists - and set used = 0 if file doesn't exist (for some reason)
  [Neil Cook]
- `Apero-base.drs_db.py` - in colnames use `self._execute` (to catch the
  database lock) [Neil Cook]


0.7.021 (2020-10-15)
--------------------
- `Apero.core.core.drs_database.py` - `add_entries` func add doc string.
  [Neil Cook]
- `Apero.base.drs_db.py` - try to deal with sqlite database is locked
  error (try again up to a max wait time) [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - preclean filepath should be from
  telluric database directory (Issue #651) [Neil Cook]
- `Apero.science.polar.general.py` - update polar recipe with bug from
  Issue #648. [Neil Cook]


0.6.132 (2020-10-15)
--------------------
- `Apero.science.telluric.gen_tellu.py` - preclean filepath should be from
  telluric database directory (Issue #651) [Neil Cook]
- Apero.data.spirou.reset.runs - reformat run.ini files (more logical
  order) [Neil Cook]
- Update polar code - Issue #648. [Neil Cook]
- Update language database. [Neil Cook]
- Add .run to .gitignore. [Neil Cook]
- `Apero_processing.py` - add ptime. [Neil Cook]
- `Apero.core.math.general.py` - correct math for `iuv_spline` nanmask -->
  ~nanmask. [Neil Cook]
- `Apero.core.math.general.py` - deal with too many NaNs in spline -
  correct eargs. [Neil Cook]
- `Apero.core.math.general.py` - deal with too many NaNs in spline. [Neil
  Cook]
- `Apero.science.telluric.gen_tellu.py` - correct what goes into the
  headers for TQCCL and TQCCP (was `qc_values` --> `qc_logic,qc_pass)` [Neil
  Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - EXTOBJ -->
  EXTTELL. [Neil Cook]
- Merge branch 'developer' into working. [Neil Cook]
- Merge branch 'master' into developer. [Neil Cook]
- Merge branch 'master' into working. [Neil Cook]
- Update README.md. [Neil Cook]

  update processing tables in README.md
- Update README.md. [Neil Cook]

  update readme.md `pp_seq_opt`
- Update processing tables in README.md. [Neil Cook]
- Merge remote-tracking branch 'origin/developer' into developer. [Neil
  Cook]
- Update `drs_database.py`. [Neil Cook]

  removed chmod to 644
- `Apero.tools.module.processing.drs_processing.py` - `send_email` should be
  False not 'False' [Neil Cook]


0.7.020 (2020-10-14)
--------------------
- Apero - continue adding log features. [Neil Cook]
- Apero.core.utils - start adding log database. [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - fix `create_symlinks`.
  [Neil Cook]
- `Apero-drs.setup.install.py` - os.environ[CARD] requires a str not a
  Path. [Neil Cook]
- `Apero-drs.setup.install.py` - must activate `DRS_UCONFIG` in environ.
  [Neil Cook]
- `Apero.base.base.py` - need to reload iparams and dparams after creating
  yaml files. [Neil Cook]
- `Apero.base.base.py` - for installation we cannot have DPARAMS and
  IPARAMS. [Neil Cook]
- `Setup.install.py` - have `__file__` path absolute. [Neil Cook]
- `Setup.install.py` - add print statement (For test) [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - `DRS_DATA_RECUC`:
  'red'-->'reduced' [Neil Cook]
- Udpate language database. [Neil Cook]


0.7.019 (2020-10-14)
--------------------
- `Apero.tools.module.setup.*` - create yamls and update database
  creation. [Neil Cook]
- Apero-drs/config - remove redundant ini files. [Neil Cook]
- `Apero.tools.module.gui.general.py` - get `DRS_UCONFIG` from base. [Neil
  Cook]
- Apero.tools.module.database - update paths to use database yaml file.
  [Neil Cook]
- `Apero.io.drs_lock.py` - need max wait time (used to be database
  setting) [Neil Cook]
- `Apero.core.instruments.*.default_config.py` - remove database settings
  (now in yaml) [Neil Cook]
- `Apero.core.core.drs_database.py` - change how set path works. [Neil
  Cook]
- `Apero.core.constants.param_functions.py` - only cache when `from_file` is
  True (otherwise don't ever read files) [Neil Cook]
- `Apero.base.py` - add yaml reading functions here. [Neil Cook]
- `Apero-drs/*` - work on yaml inputs for install + database. [Neil Cook]
- `Apero.science.extract.other.py` - deal with exceptions/errors from
  extrecipe better. [Neil Cook]
- `Apero.recipes.spirou.cal_dark_master_spirou.py` - set nightname to
  'other' [Neil Cook]
- `Apero.core.utils.drs_startup.py` - test is mod is None (as well as mod
  instance None) [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - typo intputtype -->
  inputtype. [Neil Cook]
- `Apero.core.core.drs_file.py` - typo `DRS_CALIB_DB` --> `DRS_DATA_ASSETS`.
  [Neil Cook]
- `Apero.core.core.drs_argument.py` - deal with directory better. [Neil
  Cook]
- `Apero.data.spirou.reset.runs.*.ini` - reorganise run.ini files. [Neil
  Cook]


0.7.018 (2020-10-11)
--------------------
- `Apero-drs.apero.science.calib.badpix.py` - chaange recipe.outputdir to
  recipe.outputtype. [Neil Cook]
- Sort out disambiguity between inputdir outputdir inputtype outputtype
  (former should be None or Path, later should be 'raw', 'red', 'tmp',
  'calib', 'asset' etc) [Neil Cook]


0.7.017 (2020-10-10)
--------------------
- `Apero.core.utils.drs_startup.py` - parg --> pargs[parg] for settings
  params. [Neil Cook]
- `Apero.core.core.drs_file.py` - outfile must update params. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - need to update input files with
  params (after we have added to them) [Neil Cook]
- `Apero.core.core.drs_database.py` - need to not check dirname if
  check=False (in `DatabaseManager.set_path)` [Neil Cook]
- `Apero.core.core.drs_argument.py` - need to deal with empty types in
  `_check_file_logic`. [Neil Cook]


0.7.016 (2020-10-10)
--------------------
- Add default calibdb/objectdb csv files for NIRPS. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - `find_files` correct typing pd.dataframe
  --> pd.DataFrame. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - do not check path of index database
  here - sometimes we may not have it (only on reset?) [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - frecipe must get params (it changed
  previously) [Neil Cook]
- `Apero.core.instruments.nirps_ha.deafult_config.py` - update some
  settings for database (c.f. spirou) [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - correct columns for
  `index_database` columns. [Neil Cook]
- `Apero.core.core.drs_file.py` - correct `remove_insuffix` default value
  should be None. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - write a new `find_files` function that
  uses the index database. [Neil Cook]
- Move `find_files` to `drs_utils.py`. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - change location of `get_output_dir` and
  `get_input_dir`. [Neil Cook]
- `Apero.core.core.drs_file.py` - move `get_dir` `get_input_dir` and
  `get_output_dir` here. [Neil Cook]
- `Apero.core.core.drs_database.py` - add `_update_params` so we only update
  database when new request comes in (unless forced) [Neil Cook]
- `Core.core.drs_argument.py` - update check directory and check file to
  use indexdb instead of opening headers. [Neil Cook]
- `Apero.base.drs_db.py` - count should return an int. [Neil Cook]


0.7.015 (2020-10-08)
--------------------
- `Apero.tools.recipe.bin.apero_listing.py` - update listing to update
  index database. [Neil Cook]
- 'reduced' --> 'red', from apero.core.core import `drs_database`. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Apero.io.*` - sort out imports. [Neil Cook]
- `Apero.core.util.drs_utils.py` - sort out imports. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - get IndexDatabase (for `recipe_setup)`
  [Neil Cook]
- `Apero.core.instruments.*.recipe_definitions.py` - change 'reduced' to
  'red' [Neil Cook]
- `Apero.core.core.drs_log.py` - move `setup_inputs` to `drs_recipe.py`. [Neil
  Cook]
- `Apero.core.core.drs_file.py` - update write functions (add runstring
  and kind for index database) [Neil Cook]
- `Apero.core.core.drs_database.py` - deal with no instrument + move
  `drs_database.py` from `core.utils.drs_database.py`. [Neil Cook]
- `Apero.core.core.drs_argument.py` - add IndexDatabase to Argument Checks
  (unfinished) [Neil Cook]
- `Core.constants.param_functions.py` - deal with no value in listp and
  dictp. [Neil Cook]
- `Apero.base.drs_db.py` - typo :param columns: --> :param column: [Neil
  Cook]


0.7.014 (2020-10-07)
--------------------
- Update language database. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - continue integrating
  index database. [Neil Cook]
- `Apero.core.utils.drs_database.py` - continue work integrating index
  database. [Neil Cook]
- `Apero.core.instruemnts.*.default_constants.py` - change REPROCESS
  columns (for index database) [Neil Cook]
- `Apero.core.core.drs_file.py` - change kwargs for hkeys in NpyFile.
  [Neil Cook]
- `Apero.tools.recipe.bin.apero_processing.py` - continue work integrating
  index database. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` +
  `apero.tools.module.processing.drs_processing.py` - move
  processing/reprocessing functionality to `drs_processing`. [Neil Cook]
- `Apero.core.utils.drs_database.py` - continue work on index database.
  [Neil Cook]
- `Apero.base.drs_db.py` - add count and unique functions. [Neil Cook]


0.7.013 (2020-10-07)
--------------------
- `Apero.tools.module.processing.drs_processing.py` +
  `apero.recipes.bin.apero_processing.py` - start update with
  IndexDatabase (unfinished) [Neil Cook]
- `Apero.science.polar.general.py` - change `KW_ACQTIME` to `KW_MJDEND`. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_utils.py` - modify `update_index_db`. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - deal with filemod better. [Neil Cook]
- `Apero.core.utils.drs_database.py` - continue working on
  IndexDatabaseManager. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - update `drs_finput`
  with hkeys (still need to do this for nirps) [Neil Cook]
- `Apero.core.instruments.deafult_keywords.py` - `KW_ACQTIME` --> MJDEND.
  [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - adjust pseudo const for
  index files. [Neil Cook]
- `Apero.core.core.drs_file.py` - change kwargs to hkeys. [Neil Cook]
- `Apero.base.drs_db.py` - add command to database error (on execute)
  [Neil Cook]
- `Apero.core.math.general.py` - add nan spline to account for `iuv_spline`
  going wrong (with NaNs len < k + 1) [Neil Cook]


0.7.012 (2020-10-05)
--------------------
- `Apero.tools.recipes.bin.apero_processing.py` - start adding
  IndexDatabase functionality. [Neil Cook]
- `Apero.tools.module.setup.drs_reset.py` - change
  `create_databases-->manage_database`. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - start adding
  IndexDatabase functionality. [Neil Cook]
- `Apero.tools.module.database.manage_database.py` - renamed from
  `create_databases.py`. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.io.drs_path.py` - allow copytree to log. [Neil Cook]
- `Apero.core.utils.py` - add utils module for functions that must import
  from all other utils. [Neil Cook]
- `Core.utils.drs_database.py` - add features to IndexDatabaseManager.
  [Neil Cook]
- `Apero.core.instruments.*.pseudo_const.py` - add `INDEX_HEADER_KEYS` and
  modify `INDEX_DB_COLUMNS`. [Neil Cook]
- `Core.core.drs_file.py` - tag some functions to be changed to database
  functions. [Neil Cook]
- `Apero.base.drs_misc.py` - allow `get_uncommon_paths` to accept Path as
  well as string. [Neil Cook]
- `Apero.base.drs_db.py` - add column names to set function. [Neil Cook]
- Change `drs_database2.py` --> `drs_database.py`. [Neil Cook]


0.7.011 (2020-10-02)
--------------------
- `Apero.tools.module.setup.drs_reset.py` - create databases after
  reseting files (otherwise databases are removed) [Neil Cook]
- `Apero.io.drs_image.py` - `unix_char_code` moved from `drs_startup` to
  `drs_misc`. [Neil Cook]
- `Apero.science.calib.dark.py` - add `out_fmt` for `get_mid_obs_time`. [Neil
  Cook]
- `Apero.science.calib.shape.py` - add `out_fmt` for `get_mid_obs_time`. [Neil
  Cook]


0.7.010 (2020-10-01)
--------------------
- `Apero.science.telluric.gen_tellu.py` -  `get_non_tellu_objs` add doc
  string. [Neil Cook]
- `Apero.recipes.spirou.obj_mk_template_spirou.py` - key is just filetype
  now (fiber separate) `filetype_fiber` --> filetype. [Neil Cook]
- `Apero.core.utils.drs_database2.py` - allow `iarmass/tau_Water/tau_others`
  to be string (to handle 'None') [Neil Cook]
- `Apero.science.telluric.fit_tellu.py` - number of trans files should be
  one less than length (but mask <= instaed of <) [Neil Cook]
- `Apero.science.wave.py` - fix file for `out_wave_fp/out_wave_hc`. [Neil
  Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` +
  `obj_mk_template_spirou.py` - add database=telludbm for tellu database
  functions. [Neil Cook]
- `Apero.recipe.spirou.cal_dark_master_spirou.py` - `drs_fits` --> `drs_file`
  import. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - EXTOBJ -->
  EXTTELL + continue update to new database system for tellurics. [Neil
  Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - EXTOBJ -->
  EXTTELL. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - `TELLU_CONV` should
  be of `wavem_fp` or `wavem_hc` drs file type. [Neil Cook]
- `Apero.core.core.drs_file.py` - add filename as arg to
  `construct_filename` (used for certain outfuncs) [Neil Cook]
- `Apero.base.drs_db.py` - only open cursor when require and close it
  after to avoid locking. [Neil Cook]


0.7.009 (2020-09-30)
--------------------
- `Apero.science.telluric.gen_tellu.py` - move database interface over
  from old text database to new sql database. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - add database inpout to
  `telluric.tellu_preclean`. [Neil Cook]
- `Apero.io.drs_fits.py`, `io.drs_image.py`, `io.drs_lock.py`, `io.drs_path.py`,
  `io.drs_table.py` - add import rules (to avoid circular imports) [Neil
  Cook]
- `Apero.core.utils.drs_database2.py` - update telluric database manager.
  [Neil Cook]
- `Apero.core.utils.drs_data.py` - add npy file type. [Neil Cook]
- `Apero.core.core.drs_file.py` - reformat `get_hkey`. [Neil Cook]
- `Apero.base.drs_db.py` - add colnames function and `_decode_value`
  function. [Neil Cook]
- Move DrsFits functions from `apero.io.drs_fits` to
  `apero.core.core.drs_file` (they should be with the class not IO
  functions) - functions moved: `get_index_files`, `find_files`,
  `find_raw_files`, combine, `fix_header`, `id_drs_file`, `get_mid_obs_time`,
  `_get_files`, `_get_path_and_check`, [Neil Cook]
- Update processing tables in README.md. [Neil Cook]
- Update `UPDATE_NOTES.txt` (probably prematurely) [Neil Cook]
- Update requirements (split into conda/pip for those installating using
  these lists) [Neil Cook]
- Move apero-drs/misc to apero-utils repo. [Neil Cook]


0.7.008 (2020-09-29)
--------------------
- `Apero.io.drs_fits.py` - need to deal with key == '' [Neil Cook]
- `Apero-drs.misc.tools.profiler.apero_profiler.py` - add recipe profiler.
  [Neil Cook]


0.7.007 (2020-09-25)
--------------------
- `Apero.io.drs_table.py` - pickling/python typing/docstrings. [Neil Cook]
- `Apero.io.drs_path.py` - continue pickling/python typing/docstrings.
  [Neil Cook]
- `Apero.base.drs_text.py` - move `test_format` here from `drs_table.py`.
  [Neil Cook]


0.7.006 (2020-09-24)
--------------------
- `Apero.io.drs_lock.py` - make sure classes are pickle-able, add python
  typing and docstrings. [Neil Cook]
- `Apero.io.drs_image.py` `drs_lock.py` - continue
  pickling/typing/docstring. [Neil Cook]
- Apero.core.instruments - fix pep8. [Neil Cook]


0.7.005 (2020-09-22)
--------------------
- `Drs_fits.find_files` -- add filters arg (dict) [Neil Cook]
- `Apero.io.drs_fits.py` - continue pickling/typing/docstring adding.
  [Neil Cook]
- `Apero.io.drs_fits.py` - start pickling/python typing/doc string. [Neil
  Cook]
- `Misc.tools.copy_master_db.py` - code to only copy master database.
  [Neil Cook]


0.7.004 (2020-09-19)
--------------------
- `Setup.install.py` - correct typo barycorrp=y --> barycorrpy. [Neil
  Cook]
- Build documentation. [Neil Cook]
- `Apero.tools.module.documentation.drs_changelog.py` - change how we
  produce changelog.rst. [Neil Cook]
- `Apero.science.extract.berv.py` - remove func as input parameter. [Neil
  Cook]
- `Apeor.core.utils.drs_startup.py` - instrument = 'None' not just None.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - copy `output_dict` + datatype + dtype from
  instance2. [Neil Cook]
- Build documentation. [Neil Cook]
- Build documentation. [Neil Cook]
- Build documentation. [Neil Cook]
- Add empty recipe documentation. [Neil Cook]
- `Apero.io.drs_fits.py` - close the hdu and for now keep the image in
  primary hdu (remove later) [Neil Cook]
- `Apero.core.utils.drs_database.py` - remove chmod 644 for copying to
  databases. [Neil Cook]
- `Apero.core.core.drs_file.py` - deep copy header/hdict when copying
  file. [Neil Cook]


0.7.003 (2020-09-16)
--------------------
- Add .run to .gitignore. [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - add TODO to see if
  we can see whats wrong (later) [Neil Cook]
- `Apero.science.*` - fix after debug run. [Neil Cook]
- `Apero.plotting.core.py` - deal with no pdfpath set (skip commit) [Neil
  Cook]
- `Apero.core.recipes.*.*` - update after debug run. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.io.drs_fits.py` - fix after debug run. [Neil Cook]
- `Apero.core.math.fast.py` - remove `display_func` from jit function. [Neil
  Cook]
- `Apero.core.instruments.*.file_definitions.oy` - update
  `out_orderp_straight`. [Neil Cook]
- `Apero.core.core.*.py` - fix issues after debug run. [Neil Cook]
- `Apero.core.constants.param_funtions.py` - chagne
  ConfigError-->DrsCodedException. [Neil Cook]


0.7.002 (2020-09-15)
--------------------
- `Apero.core.utils.drs_recipe.py` - correction for typing/structural
  changes. [Neil Cook]
- `Apero.io.drs_fits.py` - `drs_file` must have params. [Neil Cook]
- `Apero.io.drs_path.py` - update `get_uncommon_path`. [Neil Cook]
- Apero - `apero.core.drs_log` --> `apero.core.core.drs_log` + instrument =
  None --> instrument = 'None' [Neil Cook]
- `Apero.core.instruments.*.output_filenames.py` - generalize inputs.
  [Neil Cook]
- `Apero.core.core.drs_file.py` - make changes to
  `DrsInputFile.check_params`. [Neil Cook]
- `Apero.core.core.drs_argument.py` - change `recipe.drs_params` -->
  recipe.params. [Neil Cook]
- `Apero.core.constants.param_functions.py` - instrument variable should
  be tested for null test None and 'None' [Neil Cook]
- `Apero.base.drs_misc.py` - fix `drs_misc.get_uncommon_path` (first path
  should be the longest) [Neil Cook]
- `Apero.base.drs_exceptions.py` - Exit has not `__init__` [Neil Cook]
- `Apero.core.utils.drs_startup.py` - add doc strings/python typing. [Neil
  Cook]


0.7.001 (2020-09-14)
--------------------
- `Apero.core.utils.drs_recipe.py` - continue typing/pickling/docstrings.
  [Neil Cook]
- `Apero.tools.module.processing.drs_processing.py` - `send_email` should be
  False not 'False' [Neil Cook]


0.7.000 (2020-09-10)
--------------------
- `Apero-drs.misc.tools.create_science_targets.py` - add telluric targets
  (may want to upload these too) [Neil Cook]
- Merge branch 'master' into v0.7.000-pre. [Neil Cook]

  # Conflicts:
  #    `UPDATE_NOTES.txt`
  #    `apero/core/instruments/default/default_config.py`
  #    `apero/core/utils/drs_startup.py`
  #    `apero/io/drs_fits.py`
  #    `apero/recipes/spirou/pol_spirou.py`
  #    `apero/science/telluric/gen_tellu.py`
  #    `apero/tools/module/processing/drs_processing.py`
- Merge pull request #645 from njcuk9999/developer. [Neil Cook]

  Developer --> master v0.6.131
- Update date/version/changelog/docs/update notes/read me. [Neil Cook]
- `Apero.recipes.spirou.pol_spirou.py` - hack from Issue #639 re: linear
  algebra error. [Neil Cook]
- Identical? [Neil Cook]
- `Apero.core.core.drs_startup.py` - format of splash update. [Neil Cook]
- Update date/version/docs/changelog. [Neil Cook]
- Update object query list. [Neil Cook]
- Issue #644 - deal with table = None in `generate_run_list` + add
  --test=True to codes which use processing `(obj_mk_tellu_db` an
  `dobj_fit_tellu_db)` [Neil Cook]
- `Apero.tools.module.setup.drs_processing.py` - deal with table being
  None (just to test if things work with this option) [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_db_spirou.py` - add break point and
  `TEST_RUN` = True for test. [Neil Cook]
- `Apero.io.drs_fits.py` - remove breakpoint. [Neil Cook]
- `Apero.io.drs_fits.py` - try to fix copying comments. [Neil Cook]
- `Apero.recipes.nirps_ha.cal_pp_master_nirps_ha.py` - move break point to
  test error. [Neil Cook]
- `Apero.io.drs_fits.py` - deal with header key not being str. [Neil Cook]
- `Apero.io.drs_fits.py` - deal with header key not being str. [Neil Cook]
- `Apero.recipes.nirps_ha.cal_wave_master_nirps_ha.py` -- move breakpoint.
  [Neil Cook]
- `Apeor.data.nirps_ha.calib` - add `catalogue_UNe.csv` file. [Neil Cook]
- `Apero.science.extract.general.py` - remove breakpoint
  `apero.core.instruments.default.default_constants.py` - make
  `LEAKM_WSMOOTH` an int. [Neil Cook]
- `Apero.science.extract.general.py` - move breakpoint. [Neil Cook]
- `Apero.io.drs_image.py` - deal with only one image in `large_image_median`
  (return image without medianing) [Neil Cook]
- `Apero.recipes.nirps_ha.cal_shape_nirps_ha.py` -- move break point.
  [Neil Cook]
- `Apero.recipes.nirps_ha.cal_shape_nirps_ha.py` -- move break point.
  [Neil Cook]
- `Apero.recipes.nirps_ha.cal_shape_nirps_ha.py` -- add break point. [Neil
  Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` +
  `science/telluric/fit_tellu.py` + `gen_tellu.py` + `mk_tellu.py` - fix
  problem with qc for tellu pre clean. [njcuk9999]
- Update `requirements_current.txt`. [Neil Cook]

  security dependency requires update
- Merge pull request #642 from njcuk9999/developer. [Neil Cook]

  Developer - Master
- Apero - moved `drs_file` from apero.core.utils --> apero.core.core (used
  in `drs_argument.py)` - continue pickling/docstring/python-typing of
  `apero.core.utils.drs_recipe`. [Neil Cook]
- Apero - start changes to DrsRecipe (linearizing, pickling, doc
  strings, python typing) [Neil Cook]
- Apero - fix usage of Dict[value-type] --> Dict[key-type, value-type]
  [Neil Cook]
- Apero - change `get_key` & `read_header_key-->get_hkey`,
  `read_header_key_2d_list-->get_hkey_2d`,
  `read_header_key_1d_list-->get_hkey_1d`. [Neil Cook]
- `Apero.core.utils.drs_file.py` - finish upgrade of `drs_file`
  (pickling/docstrings/python typing) [Neil Cook]
- Apero - manage getting data and header via `DrsFitsFile.get_data()` and
  `DrsFitsFile.get_header()` -- used to be .data and .header. [Neil Cook]
- `Apero-drs.misc.problems.visu_calibs.py` - add plotting option. [Neil
  Cook]
- `Apero-drs.misc.problems.visu_calibs.py` - visualizer for which
  calibration was chosen for which star. [Neil Cook]
- Issue #644 - deal with table = None in `generate_run_list` + add
  --test=True to codes which use processing `(obj_mk_tellu_db` an
  `dobj_fit_tellu_db)` [Neil Cook]
- `Apero.core.utils.drs_file.py` - continue work on docstring/python
  typing/pickling. [Neil Cook]
- `Apero.core.utils.drs_file.py` - continue work on docstring/python
  typing/pickling. [Neil Cook]
- Apero.core.utils - continue with doc string / python typing /
  pickling. [Neil Cook]
- `Apero.io.drs_fits.py` - try to fix copying comments. [Neil Cook]
- `Apero.io.drs_fits.py` - deal with header key not being str. [Neil Cook]
- `Apero.core.constants.param_functions.py` - pep8 cleanup. [Neil Cook]
- `Apero.io.drs_image.py` - continued correction to `large_median_image`
  (for when there is 1 file) [Neil Cook]
- `Apeor.data.nirps_ha.calib` - add `catalogue_UNe.csv` file. [Neil Cook]
- `Apero.core.instruments.default.default_constants.py` - make
  `LEAKM_WSMOOTH` an int. [Neil Cook]
- `Apero.io.drs_image.py` - deal with only one image in `large_image_median`
  (return image without medianing) [Neil Cook]
- `Apero.utils.drs_data.py` - continue adding doc strings. [Neil Cook]
- Apero.core.math - update pickling/docstrings/python typing + move
  DrsMathException to `drs_exceptions.py`. [Neil Cook]
- `Apero.io.drs_fits.py` - change call to `pconst.HEADER_FIXES`. [Neil Cook]
- `Apero.core.utils.drs_startup.py` - chagne wlog to logger in RecipeLog
  construction. [Neil Cook]
- `Apero.core.instruments.default.pseudo_const.py` - change typing of
  `REPORT_KEYS()` [Neil Cook]
- `Core.core.drs_log.py` - finish pickling/typing/docstrings. [Neil Cook]
- `Apero.core.constants.param_functions.py` - move base classes out of
  here and move `capitalise_keys` to `drs_text.py` + pep8 changes. [Neil
  Cook]
- `Apero.core.constants.param_functions.py` - move base classes out of
  here and move `capitalise_keys` to `drs_text.py`. [Neil Cook]
- `Apero.core.constants.constant_functions.py` - move CKCaseINSDict here
  (requires Const and Keyword classes) [Neil Cook]
- Apero.core.instruments - update docstrings/typing/pickling. [Neil
  Cook]
- `Apero.base.drs_text.py` - move `capitalise_key` to here (from
  `param_functions.py)` [Neil Cook]
- `Apero.base.drs_base_classes.py` - add base classes here. [Neil Cook]
- Apero - remove usage of apero.core in favour of
  `apero.core.core.drs_log` and `apero.core.utils.drs_startup`. [Neil Cook]
- Apero - move `pcheck/find_params` to `param_functions` and make class (to
  add WLOG) - change all calls to `pcheck/find_params`. [Neil Cook]
- `Apero.core.core.drs_log.py` - add typing/pickling/docstrings
  [UNFINISHED] [Neil Cook]
- `Apero.core.param_functions.py` - correct pep8. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` +
  `science/telluric/fit_tellu.py` + `gen_tellu.py` + `mk_tellu.py` - fix
  problem with qc for tellu pre clean. [Neil Cook]
- `Misc.tool.screate_science_targets.py` - update arg list. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - keywordargument kind = 'kwarg' not
  'kwargs' [Neil Cook]
- `Apero.core.core.instruments.*.recipe_definitions.py` - remove all
  references to nargs (not used- set by dtype) [Neil Cook]
- `Apero.core.core.drs_argument.py` - must define kind otherwise crash in
  self.exception. [Neil Cook]
- `Core.core.constants.param_functions.py` - CKKCaseINSDict should not
  force to lists (copy/paste error) [Neil Cook]
- `Apero.core.utils.drs_recipe.py` - update `set_arg` and `set_kwarg` remove
  `**kwargs` and explicitly type arguments. [Neil Cook]
- `Apero.core.instruments.*.recipe_definitons.py` - change path= -->
  parent= [Neil Cook]
- `Apero.core.core.drs_argument.py` - pos can be int str or None. [Neil
  Cook]
- `Misc.tools.create_science_targets.py` - update target list. [Neil Cook]
- `Apero.base.drs_misc.py` - move `get_uncommon_path` to `drs_misc.py`. [Neil
  Cook]
- `Core.core.drs_argument.py` - add pickling and python type checking to
  all classes and functions. [Neil Cook]
- Merge branch 'developer' into v0.7.000-pre. [Neil Cook]

  # Conflicts:
  #    README.md
  #    `apero/core/instruments/default/default_config.py`
- `Apero.core.utils.drs_recipe.py` + `drs_startup.py` +
  `tools.module.processing.drs_processing.py` +
  `tools.module.testing.drs_dev.py` - change call to
  constants.getmodnames: path --> `return_paths`. [Neil Cook]
- `Apero.core.core.drs_argument.py` + `drs_log.py` - move textwrap to
  `apero.base.drs_text.py`. [Neil Cook]
- `Apero.base.*` + `apero.core.constants.*` - add python type checking,
  pickle-able classes and doc strings. [Neil Cook]
- `Apero.base.*` - make all classes pickle-able. [Neil Cook]
- `Apero.core.core.drs_log.py` + `apero.core.utils.drs_startup.py` - change
  how Colors class works. [Neil Cook]
- `Apero.base.*` - update pep8 and python type checking for base module.
  [Neil Cook]
- `Apero.science.calib.general.py` + `localisation.py` + `shape.py` - make
  sure calib file return is string. [Neil Cook]
- `Apero.io.drs_fits.py` - import pathlib. [Neil Cook]
- `Apero.science.calib.wave.py` - remove break ppoint. [Neil Cook]
- `Apero.io.drs_fits.py` - add some python type checking. [Neil Cook]
- `Apero.core.utils.drs_database2.py` - add some python type checking.
  [Neil Cook]
- Apero.data.spirou.database.reset.calib.csv - update default keys
  `WAVE_D` --> `WAVEM_D`. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.*` - move fiber in `get_dbkey()` to argument in `load_calib_file`.
  [Neil Cook]
- `Apero.recipes.*.*` - remove params from `add_calib_file` and
  `add_tellu_file`. [Neil Cook]
- `Apero.*` - continue adding `drs_database2` functionality. [Neil Cook]
- `Core.utils.drs_database2.py` - `add_calib_file` + `add_tellu_file` add a
  `copy_files` option. [Neil Cook]
- Save language.xls. [Neil Cook]
- `Apero-drs.misc.tools.create_science_targets.py` - update target list.
  [Neil Cook]
- `Apero.io.drs_path.py` - move `drs_break`. [Neil Cook]
- `Apero.core.utils.drs_database*` - continue work on database update.
  [Neil Cook]
- `Apero.core.utils.drs_recipe.py` + `drs_startup.py` - move calls to
  `drs_break`. [Neil Cook]
- Apero.lang.core - move calls to `drs_break`. [Neil Cook]
- Apero.recipes + apero.science + apero.tools - move around calib db
  stuff. [Neil Cook]
- `Apero.core.instruments.*.*` - add/modify calib db constants. [Neil
  Cook]
- `Apero.core.core.drs_log.py` - move `dispaly_func` call. [Neil Cook]
- `Apero.core.constants.param_functions.py` - move `break_point` +
  `display_func` + `get_relative_folder` + `_copy_pdb_rc` + `_remove_pdb_rc` +
  `_get_prev_count`. [Neil Cook]
- `Apero.base.drs_misc.py` - move `display_func` here and `_get_prev_count`.
  [Neil Cook]
- `Apero.base.drs_exceptions.py` - add `base_printer`. [Neil Cook]
- `Apero.base.drs_break.py` - move break function here. [Neil Cook]
- `Apero.base.base.py` - add `PDB_RC_FILENAME`. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.7.000-pre' into v0.7.000-pre.
  [Neil Cook]
- Update README.md. [Neil Cook]

  update `pp_seq_opt`
- Move base functionality to apero.base and update all codes with
  changes - correct bugs. [Neil Cook]
- Move base functionality to apero.base and update all codes with
  changes. [Neil Cook]
- `Apero.tool.smodule.database.database_gui.py` - fix crash in pandastable
  + add way to save/update sql database. [Neil Cook]
- `Apero.data.spirou.reset.runs.calib_run.ini` - add `calib_run.ini`
  example. [Neil Cook]
- `Apero.core.core.drs_database2.py` - add typing and doc strings to
  database function. [Neil Cook]
- `Apero.core.math.fast.py` + `general.py` - add typing to most functions.
  [Neil Cook]
- Merge branch 'v0.6.130-pre' into v0.7.000-pre. [Neil Cook]

  # Conflicts:
  #    `UPDATE_NOTES.txt`
- `Core.instruments.*.pseudo_const.py` - make all obj names upper. [Neil
  Cook]
- `Core.core.drs_database2.py` - add empty database for when we don't have
  a dataframe. [Neil Cook]
- Merge branch 'v0.6.130-pre' into v0.7.000-pre. [Neil Cook]
- `Apero.science.telluric.fit_tellu.py` - must mask `expo_water/expo_others`
  for trans files. [Neil Cook]
- Merge branch 'v0.6.130-pre' into v0.7.000-pre. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - nanmin --> nanmax. [Neil Cook]
- `Apero.recipes.spirou.obj_mk_tellu_spirou.py` - pep8 white space before
  operator. [Neil Cook]
- `Core.core.drs_database2.py` + `tools.module.database.*` - continue to add
  and test database functionality. [Neil Cook]
- `Core.core.drs_database2.py` + `tools.module.database.*` - continue to add
  and test database functionality. [Neil Cook]
- `Core.core.drs_database2.py` + `tools.module.database.*` - continue to add
  and test database functionality. [Neil Cook]
- Merge branch 'v0.6.130-pre' into v0.7.000-pre. [Neil Cook]
- `Apero.core.instruments.*.default_config.py` - add database filenames.
  [Neil Cook]
- `Apero.core.drs_database2.py` - first commit - start work on buliding
  database class. [Neil Cook]
- Merge branch 'v0.6.130-pre' into v0.7.000-pre. [Neil Cook]

  # Conflicts:
  #    `apero/data/spirou/telluric/tapas_all_sp.fits.gz`
  #    `apero/tools/module/processing/__init__.py`
  #    `apero/tools/recipes/bin/apero_database.py`
- `Apero.tools.module.gui.database_gui.py` +
  `apero.tools.recipes.bin.apero_database.py` - add first commit of
  database gui. [Neil Cook]
- Move `drs_processing.py` and `drs_trigger.py` to processing
  tools.module.processing (from setup) [Neil Cook]
- Move `drs_processing.py` and `drs_trigger.py` to processing
  tools.module.processing (from setup) [Neil Cook]
- `Apero.science.calib.wave.py` - `add_hkey` values-->value. [Neil Cook]
- `Apero.science.calib.wave.py` - correct TREGIONS. [Neil Cook]
- `Apero.io.drs_data.py` - fix `fit_1m` `fit_ll` filename input to
  `load_text_file`. [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Apero.io.drs_path.py` - pep8 changes. [Neil Cook]
- `Apero.tools.reicpes.*.cal_pphotpix_spirou.py` - `DRS_DATA_ASSET` -->
  `DRS_DATA_ASSETS`. [Neil Cook]
- `Apero.tools.module.setup.drs_reset.py` - copy tree when reseting +
  construct path for assets path. [Neil Cook]
- `Apero.tools.module.setup.drs_processing.poy` - deal with no skip table.
  [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - `DRS_DATA_ASSET` -->
  `DRS_DATA_ASSETS` + change output to `get_whitelist/get_blacklist`. [Neil
  Cook]
- `Science.calib.wave.py` - `DRS_DATA_ASSET` --> `DRS_DATA_ASSETS`. [Neil
  Cook]
- `Apero.recipes.spirou.obj_*_tellu_*` - change return to
  `get_blacklist/get_whitelist`. [Neil Cook]
- `Apero.io.drs_data.py` - `DRS_DATA_ASSET` ---> `DRS_DATA_ASSETS`. [Neil
  Cook]
- `Apero-drs.setup.install.py` - add --assetdir definition. [Neil Cook]
- `Apero.tools.reicipes.bin.apero_reset.py` - add a reset for assets
  directory. [Neil Cook]
- `Apero.tools.recipes.bin.apero_mkdb.py` - make calib + telluric database
  from assets dir. [Neil Cook]
- `Apero.tools.module.setup.drs_reset.py` - deal with reseting assets dir
  + relative dirs from there. [Neil Cook]
- `Apero.tools.module.setup.drs_installation.py` - add assets dir to
  installed directory list. [Neil Cook]
- `Apero.tools.recipes.*.cal_pphotpix_*.py` - make hotpix file + debug
  file spawn from assets dir. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - make
  `get_whiltelist/get_blacklist` files spawn from assets dir. [Neil Cook]
- `Apero.science.calib.wave.py` - make `update_smart_fp_mask` file spawn
  from assets dir. [Neil Cook]
- `Apero.io.drs_data.py` - make all relfolders relative to assets
  directory. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - make ./data paths
  relative to assets dir. [Neil Cook]
- Apero.data - move around assets (eventually move out and online) [Neil
  Cook]
- `Apero.core.instruments.*.default_config.py` - update paths to assets.
  [Neil Cook]
- `Apero.core.constants.constant_functions.py` - force dtype in
  `Constant.__init__` to Union[None, str, type] [Neil Cook]
- Move old INTROOT code to apero-utils. [Neil Cook]
- `Apero-drs.misc.database_test` - update test database files. [Neil Cook]
- `Apero-drs.misc.tools.create_science_targets.py` - update target lists
  and version. [Neil Cook]


0.6.131 (2020-08-27)
--------------------
- Update version in readme for master/developer/working. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.6.130 (2020-08-21)
--------------------
- Update README.md. [Neil Cook]

  update `pp_seq_opt`
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- `Core.instruments.*.pseudo_const.py` - make all obj names upper. [Neil
  Cook]
- `Apero.science.telluric.fit_tellu.py` - must mask `expo_water/expo_others`
  for trans files. [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - set
  `FTELLU_NUM_TRANS` to 20. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tell_spirou.py` - add tpreprops to inputs
  of `gen_abso_pca_calc`. [Neil Cook]
- `Science.telluric.fit_tellu.py` - add a trans file mask based on
  `expo_h2o` and `expo_others` (and use closest N trans files to science
  object) [Neil Cook]
- `Apero.core.instruments.*.file_definitions.py` + `recipe_definitions.py` -
  add `ABSO1_NPY` (for trans `expo_h2o+exp_others` vector) [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` + `default_keywords.py` -
  add `KW_FTELLU_NTRANS` and `FTELLU_NUM_TRANS`. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - nanmin --> nanmax. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - when saving pre-clean only mask
  to exp(-2) not exp(-1) [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - make sure we don't spline
  outside magic grid. [Neil Cook]
- Update `UPDATE_NOTES.txt`. [Neil Cook]
- Merge remote-tracking branch 'origin/v0.6.130-pre' into v0.6.130-pre.
  [Neil Cook]
- Update wave.py. [Neil Cook]

  `apero.science.calib.wave.py` - `add_hkey` values-->value
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - add break point for EA.
  [Neil Cook]
- Apero-drs.misc.INTROOT - move old INTROOT code to apero-utils. [Neil
  Cook]
- `Apero.science.calib.wave.py` - correct TREGIONS. [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - make sure q2dsff
  file links to correct file. [Neil Cook]
- Update language database. [Neil Cook]
- `Apero.science.extract.general.py` - add `write_extraction_files_ql`
  function (to write quick look files) [Neil Cook]
- `Apero.recipes.spirou.cal_extract_spirou.py` - add quick look switches.
  [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add Q2DS and
  Q2DSFF files for quicklook. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - add quick look
  e2ds/e2dsff files. [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add `EXT_QUICK_LOOK`
  constant value. [Neil Cook]
- `Apero.tools.recipes.spirou.cal_drift_spirou.py` - clean up. [Neil Cook]
- `Apero.core.core.drs_startup.py` - remove type function (doesn't work as
  :type:) [Neil Cook]
- Update the update notes (work in progress) [Neil Cook]
- `Apero.tools.recipe.spirou.cal_drift_spirou.py` - add first version of
  `cal_drift_spirou`. [Neil Cook]
- `Apero.recipes.*.cal_shape_master_*.py` - correct `ALLOWED_FP_TYPES`
  (didn't break but would on change of input) [Neil Cook]
- Merge remote-tracking branch 'origin/developer' into v0.6.130-pre.
  [Neil Cook]

  # Conflicts:
  #    `UPDATE_NOTES.txt`
- Merge remote-tracking branch 'origin/developer' into developer.
  [njcuk9999]
- `Apero.science.calib.shape.py` - filenames must be filtered as well
  (append to `valid_files)` [njcuk9999]
- `Apero.science.extract.general.py` - correct typo from release.
  [njcuk9999]
- Update object query list. [njcuk9999]
- Update mtl sync codes. [njcuk9999]
- `Apero.tools.recipes.spirou.cal_drift_spirou.py` - first commit plan for
  `cal_drift_spirou.py`. [Neil Cook]
- `Apero-drs.apero.science.calib.wave.py` - add header keys NBO/NREGIONS
  and update gaussian params with names in hdr. [Neil Cook]
- `Apero-drs.tools.recipes.*.*` - update instrumental tool recipe names to
  follow conventions. [Neil Cook]
- `Apero.science.telluric.template_tellu.py` - copy data and delete infile
  when done (hopefully stops having so many fits file open at once)
  [Neil Cook]
- `Apero.io.drs_fits.py` - readfits - add options to copy data implicity
  (slower) [Neil Cook]
- `Apero.core.core.drs_file.py` - `read_file/read_data/read_header` - add
  option to copy data implicitly. [Neil Cook]
- `Apero-drs.update_notes.txt` - update update notes. [njcuk9999]
- `Apero.data.spirou.reset.runs.*` - update runs and add complete + other
  run.ini. [njcuk9999]
- Apero-drs.README.md - update read me with latest version. [njcuk9999]
- `Apero.core.instruments.*.recipe_definitions.py` - update args for
  thermal. [njcuk9999]
- `Apero.data.spirou.reset.runs.*run.ini` - update THIM and THTM --> `THI_M`
  and `THT_M`. [njcuk9999]
- Update changelog/date/version/update notes/documentation. [njcuk9999]


0.6.129 (2020-07-29)
--------------------
- `Apero.science.calib.general.py` - add `check_fp` and `check_fp_files`
  functionality. [njcuk9999]
- `Apero.recipes.spirou.cal_shape_master_spirou.py` + `cal_shape_spirou.py`
  + `cal_wave_master_spirou.py` + `cal_wave_night_spirou.py` - check 2d fp
  files are good to use before using them! [njcuk9999]
- `Apero.io.drs_image.py` - correct typo in comment. [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - add in check fp
  constants. [njcuk9999]
- `Apero.core.instruments.*.file_definitions.py` - add `LFC_FP` to file
  types (Issue #641) [njcuk9999]
- `Apero.plotting.plot_functions.py` + `apero.science.extract.general.py` -
  remove reference to wave (change to wavemap) [njcuk9999]
- `Apero.plotting.plot_functions.py` - remove reference to wave (change to
  wavemap) [njcuk9999]
- `Apero.science.calib.flat_blaze.py` - try `curve_fitting` two ways (when
  first method fails) [njcuk9999]
- `Misc.problems.spikes.*` - add test codes for EA. [njcuk9999]


0.6.128 (2020-07-28)
--------------------
- `Apero.science.extract.general.py` - address spikes in s1d data (EA
  changes) [njcuk9999]
- `Apero.io.drs_fits.py` + `apero.lang.core.drs_exceptions.py` - get the
  filename from abspath and don't print in DrsHeaderError. [njcuk9999]
- `Apero.core.core.drs_file.py` + `apero.core.instruments.*.pseudo_const.py`
  + `apero.io.drs_fits.py` + `apero.lang.core.drs_exceptions.py` - add
  checks for header key and deal with exception of not finding them
  properly + update language database. [njcuk9999]
- `Apero.core.core.drs_file.py` - rvalue and value do not exist.
  [njcuk9999]
- `Apero.core.core.drs_file.py` - add breakpoint to test error.
  [njcuk9999]
- `Apero.core.core.drs_file.py` - must check that id header keys exist and
  report error it not + update language db. [njcuk9999]
- Update version/date/changelog/documentation/update notes. [njcuk9999]


0.6.127 (2020-07-24)
--------------------
- `Apero.tools.modeul.setup.drs_processing.py` - filter objects by dprtype
  and obstype. [njcuk9999]
- `Apero.core.core.drs_recipe.py` - have to make sure string is not in
  null text before making a string list. [njcuk9999]
- `Apero.core.core.drs_recipe.py` - add break point to test `mk_template`
  with All. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - only keep log entries
  that finished (we will only skip finished recipes) [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - remove breakpoint + only
  keep unique entries in `skip_storage`. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - need to remove all
  arguments until we find one to keep (as --args might have spaces after
  them) [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - change skip runstring
  comparison from adding all arguments to just keeping required
  arguments. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add --master to skip
  remove args (added after this step) [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move breakpoint.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move breakpoint.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - update breakpoint to test
  thermal/wave/extract. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add `add_set_kwargs` to add
  optional args to runstring (for skip check comparison) [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move break point.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move break point.
  [njcuk9999]
- `Apero.lang.core.drs_execptions.py` + `core.core.drs_log.py` - remove
  @profile. [njcuk9999]
- `Apero.lang.core.drs_execptions.py` - add @profile. [njcuk9999]
- `Apero.core.core.drs_log.py` - add more @profile. [njcuk9999]
- `Apero.core.core.drs_log.py` - add @profile to test speed. [njcuk9999]


0.6.126 (2020-07-23)
--------------------
- `Apero.tools.module.setup.drs_processing.py` - add break point and test
  timings. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add break point and test
  timings. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - only strip recipe.name
  not column. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - strip `.py` from name.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add break point to test
  skipping. [njcuk9999]
- `Apero.io.drs_fits.py` - make sure wnightnames and bnightnames are
  defined. [njcuk9999]
- `Apero.io.drs_fits.py` - deal with filtering files by
  whitelist/blacklist nightnames (accept 'All') [njcuk9999]
- `Apero.core.core.drs_log.py` - correct missing `lang.drs_text`.
  [njcuk9999]
- `Apero.tools.modules.setup.drs_processing.py` + `apero_processing.py` -
  re-work skipping file feature and change
  `SCIENCE_TARGETS/TELLUIRC_TARGETS` to "All" [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.io.drs_text.py` - add `null_text` and `true_text` functions for
  determining with text is unset/true. [njcuk9999]
- `Apero.data.*.reset.runs.*` - update all ini files. [njcuk9999]
- `Core.core.drs_recipe.py` - when `SCIENCE_TARGETS` is None use "other
  stars" list (non-tellurics) + allow `TELLUIC_TARGETS` and
  `SCIENCE_TARGETS` = ALL or None. [njcuk9999]
- Change from apero.lange import `drs_text` --> from apero import lang.
  [njcuk9999]


0.6.125 (2020-07-22)
--------------------
- `Apero.science.telluric.gen_tellu.py` - some pep8 correction.
  [njcuk9999]
- `Apero.science.telluric.gen_tellu.py` - correct argument of
  40-019-00043. [njcuk9999]
- `Apero.core.core.drs_log.py` - `add_level` does not have WLOG -->
  self.wlog. [njcuk9999]
- `Apero.core.core.drs_log.py` + `drs_startup.py` - RecipeLog cannot use
  WLOG (get it from construction) [njcuk9999]
- Update README.md. [njcuk9999]
- Merge branch 'neil' into working. [njcuk9999]
- Merge branch `'neil_tellu`' into neil. [njcuk9999]

  # Conflicts:
  #    `apero/recipes/spirou/obj_fit_tellu_spirou.py`
  #    `apero/recipes/spirou/obj_mk_tellu_spirou.py`
- Update language database. [njcuk9999]
- Move text to language database. [njcuk9999]
- Update language database. [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]
- Merge branch 'neil' of https://github.com/njcuk9999/apero-drs into
  neil. [njcuk9999]
- Os.walk should alwawys follow symbolic links. [njcuk9999]
- Update object database (now 65 entries) [njcuk9999]
- Update the windows setup files (to include forcing utf8) - Issue #640.
  [njcuk9999]
- Merge pull request #632 from njcuk9999/neil. [Neil Cook]

  Neil --> Working (based on mini run test error)
- Merge pull request #631 from njcuk9999/neil. [Neil Cook]

  Neil --> Working (for mini data test)


0.6.124 (2020-07-21)
--------------------
- Update language database. [njcuk9999]
- Apero.science.telluric - remove language database todos. [njcuk9999]
- `Apero.telluric.fit_tellu.py` - undo import removal. [njcuk9999]
- `Apero.telluric.fit_tellu.py` - `fit_tellu_write_corrected` must have
  nprops as input. [njcuk9999]
- `Apero.telluric.fit_tellu.py` - correct blaze correction. [njcuk9999]
- `Apero.recipe.spirou.obj_fit_tellu_spirou.py` +
  `apero.science.telluric.fit_tellu.py` - do not normalize by the blaze,
  just apply the recon. [njcuk9999]
- `Apero.recipe.spirou.obj_fit_tellu_spirou.py` +
  `apero.science.telluric.fit_tellu.py` - must get blaze/wave inside
  function and normalize inside. [njcuk9999]
- `Apero.recipe.spirou.obj_fit_tellu_spirou.py` +
  `apero.science.telluric.fit_tellu.py` - fix arguments for
  `correct_other_science`. [njcuk9999]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - try out the correction
  of A and B files + add break point to test. [njcuk9999]
- `Apero.data.core.pdbrc_full` - rename .pdbrc. [njcuk9999]
- `Apero.core.instruments.*.output_filenames.py` - remove calibration date
  prefix. [njcuk9999]
- `Core.constants.param_functions.py` - change name of default .pdbrc file
  (to avoid deletion if in that directory) [njcuk9999]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` +
  `science.telluric.fit_tellu.py` - the spectrum must be divided by the
  `recon_abso_res` not the `recon_abso`. [njcuk9999]
- `Apero.science.telluric.fit_tellu.py` - recon is flatten so `abso_e2ds`
  needs to be too (49,4088)-->200312. [njcuk9999]
- `Apero.science.telluric.gen_tellu.py` - need at least k+1 points to
  spline. [njcuk9999]


0.6.123 (2020-07-18)
--------------------
- `Apero.core.instruments.*.default_keywords.py` - add parents for
  `KW_MKTELL_THRES_TFIT` and `KW_MKTELL_TRANS_FIT_UPPER_BAD`. [Neil Cook]
- `Apero.science.telluric.fit_tellu.py` - add back in `KW_MKTELL_THRES_TFIT`
  and `KW_MKTELL_TRANS_FIT_UPPER_BAD`. [Neil Cook]
- `Apero.core.*.default_constants.py` + `default_keywords.py` - add back in
  `MKTELLU_THRES_TRANSFIT` and `MKTELLU_TRANS_FIT_UPPER_BAD`. [Neil Cook]
- `Aper.science.telluric.gen_tellu.py` - put back in break points. [Neil
  Cook]
- `Apero.science.telluric.mk_tellu.py` - remove tau from plot. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - add tpclfile to index file.
  [Neil Cook]
- `Apero.recipe.spirou.obj_*_tellu_spirou.py` -  end logging properly when
  file skipped. [Neil Cook]
- `Apero.recipe.spirou.obj_*_tellu_spirou.py` - add printout validating
  files. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - add that we read pclean from
  file. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - correct typo. [Neil Cook]
- `Core.instruments.*.default_keywords.py` - move CCF water/others to
  header (from images) [Neil Cook]
- `Apero.io.drs_fits.py` - `_read_fitsmulti` - add log option. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - compare file basenamse for
  tpclfile. [Neil Cook]
- `Apero.recipe.spirou.obj_mk_tellu_spirou.py` - add break point to see
  loading of preclean file. [Neil Cook]
- `Apero.science.telluric.mk_tellu.py` - mixed up `recov_airmass` and
  `recov_water` (blame EA) [Neil Cook]
- `Apero.science.telluric.*` - remove `FINER_CWIDTH` and
  `KW_MKTELL_FIN_CONV_WID`. [Neil Cook]
- `Apero.science.telluric.*` - remove `FINER_CWIDTH` and
  `KW_MKTELL_FIN_CONV_WID`. [Neil Cook]
- `Apero.science.telluric.__init__.py` - remove unused alias. [Neil Cook]
- `Apero.science.telluric.mk_tellu.py` - remove lowpassfilter (to math
  module) + sort out unused header keys/unused constants. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - remove `load_tapas_convolved`
  function + edit iteration msg. [Neil Cook]
- `Aper.recipes.spirou.obj_mk_tellu_spirou.py` - remove tapas conv not
  needed in `mk_tellu` any more (done in tellu pre-clean) + rename
  `calculate_telluric_absorption` to `calculate_tellu_res_absorption`. [Neil
  Cook]
- `Recipes.spirou.obj_fit_tellu_spirou.py` - `fit_tellu` must
  `load_conv_tapas` for first time (not done in `mk_tellu` any more) [Neil
  Cook]
- `Core.math.genearl.py` - add lowpassfilter function from EA. [Neil Cook]
- `Core.instruments.*.default_keywords.py` - remove unused keywords. [Neil
  Cook]
- `Core.instruments.*.default_constants.py` - remove unused constants.
  [Neil Cook]
- `Apero.science.telluric.mk_tellu.py` - update lowpassfilter. [Neil Cook]
- `Apero.core.instruments.spirou.default_constants.py` - change conv width
  and orders. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - `trans_mask` must be floats when
  saved to fits. [Neil Cook]
- `Apero.core.core.drs_file.py` - correct typo mapf slist-->list. [Neil
  Cook]
- `Apero.science.telluric.gen_tellu.py` - corrections with EA. [Neil Cook]
- `Apero.plotting.plot_functions.py` - correct `set_title`. [Neil Cook]
- `Apero.plotting.plot_functions.py` - add plot definitions + correct
  gauss function guess/return. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - add print outs and edit mas
  files (no title) [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - make sure we can deal with
  `conv_paths` unset (none found) [Neil Cook]
- `Aper.core.instruments.*.file_definitions.py` - add dbname/dbkey for
  `TELLU_TAPAS`. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - update ohline filename + ravel
  ohpcshift + add warning to `sky_model` < 0. [Neil Cook]
- `Apero.core.instruments.*.file_definitons.py` - fix `out_tellu_spl_npy`.
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - correct typo
  `TELLUP_ABSO_EXP_KEXP` --> `TELLUP_ABSO_EXPO_KEXP`. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - deal with no pclean files found.
  [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - do not require clean files (may
  not exist) [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - add
  `out_tellu_pclean` to file sets `out_file` and `tellu_file`. [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` `mk_tellu.py` - fix imports. [Neil
  Cook]
- `Apero.recipes.spirou.obj_*_tellu_spirou.py` - add break points to test
  EA changes. [Neil Cook]


0.6.122 (2020-07-17)
--------------------
- `Apero.science.telluric.template_tellu.py` - add possible todo later.
  [Neil Cook]
- `Misc.hybrid_tellu.hybrid_tellu.py` - add EA changes after questions.
  [Neil Cook]
- `Apero.recipes.spirou.*tellu*.py` + `science.telluric.*.py` - continue to
  add EA pre-cleaning changes. [Neil Cook]
- `Apero.plotting.plot_functions.py` - add `plot_tellup_wave_trans` and
  `plot_tellup_abso_spec` functions for tellu pre-cleaning. [Neil Cook]
- `Apero.core.instruments.*.recipe_definition.py` - add plots and outputs
  to `obj_mk_tellu` and `obj_fit_tellu` recipe definitions. [Neil Cook]
- `Apero.core.instruments.spirou.file_definitions.py` - add
  `out_tellu_pclean` file. [Neil Cook]
- `Apero.core.instruments.*.default_keywords.py` - add `KW_TELLUP` keywords.
  [Neil Cook]
- `Apero.core.instruments.*.default_constants.py` - add TELLUP constants +
  PLOT constants. [Neil Cook]
- `Core.core.drs_file.py` - add listtype argument and deal with booleans
  and list dtype better + add mapf to `add_hkey` method to add string
  lists. [Neil Cook]


0.6.121 (2020-07-16)
--------------------
- `Misc.hybrid_tellu.hybrid_tellu.py` - add questions for EA about code.
  [Neil Cook]
- `Apero.science.telluric.gen_tellu.py` - add EA telluric pre-cleaning.
  [Neil Cook]
- `Apero.science.telluric.*` - `general.py` --> `gen_tellu.py` in imports.
  [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - temp add params here
  (for constants file) [Neil Cook]
- `Aper.core.math.gauss.py` - add `gauss_function_nodc`. [Neil Cook]
- `Apero.core.instruemnts.spirou.file_definitions.py` - add
  `out_tellu_abso_npy`. [Neil Cook]
- `Apero-drs.misc.hybrid_tellu.*` - add temp space for EA pre-cleaning
  code. [Neil Cook]
- `Obj_fit_tellu_spirou.py` - prep for EA precleaning changes. [Neil Cook]
- `Apero.science.telluric.*` - rearrange telluric functions. [Neil Cook]
- `Data.spirou.telluric.*` - add telluric pre-cleaning data. [Neil Cook]
- `Apero.plotting.plot_functions.py` - add label change to cron plot.
  [Neil Cook]
- `Core.core.drs_database.py` - do not load image/header if not required.
  [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - add break point for EA
  changes. [Neil Cook]
- `Apero.science.telluric.general.py` -  correct typo. [Neil Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` +
  `science.telluric.general.py` - add adjustments to test fit tellu. [Neil
  Cook]


0.6.120 (2020-07-14)
--------------------
- `Apero.*` - remove break points. [Neil Cook]
- `Apero.tools.module.setup.drs_processing.py` - remove break point. [Neil
  Cook]
- `Apero.recipes.spirou.obj_fit_tellu_spirou.py` - add
  `correct_other_science` to correct fibers A and B for tellurics. [Neil
  Cook]
- `Apero.science.velocity.general.py` - add todo about filename. [Neil
  Cook]
- `Core.core.drs_log.py` - deal with directory (nightname) not defined -
  go into "other" directory. [Neil Cook]
- Apero.science.telluric - change where Templates/BigCubes are saved to
  (no info about nightname) - fix. [Neil Cook]
- Apero.science.telluric - change where Templates/BigCubes are saved to
  (no info about nightname) [Neil Cook]
- Apero.science.telluric - change where Templates/BigCubes are saved to
  (no info about nightname) [Neil Cook]
- `Apero.science.telluric.general.py` - continue etiennes changes. [Neil
  Cook]


0.6.119 (2020-07-13)
--------------------
- `Apero.science.telluric.general.py` - must set key for header (remove
  later) [Neil Cook]
- `Apero.recipes.spirou.obj_mk_tellu_spirou.py` +
  `science.telluric.general.py` - start adding changes for EA telluric
  cleaning. [Neil Cook]
- Update README.md. [Neil Cook]
- `Misc.tools.apero_diff.py` - update paths. [Neil Cook]
- `Apero.recipe.spirou.poly_spirou_new.py` - continue updating polar code.
  [Neil Cook]
- `Apero.recipes.spirou.cal_extract_spirou.py` - undo commentation. [Neil
  Cook]
- `Apero.io.drs_data.py` - update colnames from `load_sp_mask_lsd`. [Neil
  Cook]
- Apero.data.spirou.lsd - add masks. [Neil Cook]
- Remove `apero.data.core.runs.*` [Neil Cook]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  `obj_fit_tellu` to `full_seq`. [Neil Cook]
- `Apero.core.instruments.*.recipe_defintiions.py` - make `obj_mk_tellu_db`
  and `obj_fit_tellu_db` non master recipes (do not require master night
  to run these) [Neil Cook]
- README.md - remove some formatting. [Neil Cook]


0.6.118 (2020-07-09)
--------------------
- `Apero.science.extract.crossmatch.py` + `science.extract.crossmatch.py` -
  move breakpoint. [njcuk9999]
- `Apero.science.extract.crossmatch.py` - add break point to investigate
  obj table. [njcuk9999]
- `Apero.core.constants.param_functions.py` - add normpath (see Issue
  #635) [njcuk9999]
- `Apero.recipes.spirou.pol_spirou.py` - add back in constants removed for
  upgrade (Issue #639) [njcuk9999]
- `Apero.science.velocity.general.py` - replace hard coded C with reffiber
  form pseudo constants `(FIBER_KINDS)` [njcuk9999]


0.6.117 (2020-07-07)
--------------------
- `Misc.tools.create_science_targets.py` - add all priority targets to
  string. [njcuk9999]
- `Apero.io.drs_fits.py` - deal with INFs and -INFs in floats (for
  headers) --> pipe to string INF/-INF. [njcuk9999]
- `Aper.core.math.general.py` - create a better exception when len(x) <
  k+1 in `iuv_spline`. [njcuk9999]
- `Apero.core.core.drs_log.py` - divide up errors better. [njcuk9999]
- `Apero.science.telluric.general.py` - if column is filename make it
  absolute paths. [njcuk9999]


0.6.116 (2020-07-06)
--------------------
- Update the readme (working version update) [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.115 (2020-07-04)
--------------------
- Update language database. [njcuk9999]
- `Apero.io.drs_fits.py` - move printouts to language database.
  [njcuk9999]
- `Apero.io.drs_fits.py` - only print out whitelisted/blacklisted if night
  dir not seen before. [njcuk9999]
- `Apero.io.drs_fits.py` - modify blacklist/whitelist logic. [njcuk9999]
- `Apero.io.drs_fits.py` - do not scan all directories when
  whitelist/blacklist used. [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add `PI_NAMES` filter.
  [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - add
  `REPROCESS_PINAMECOL` constant. [njcuk9999]
- `Apero.data.spirou.reset.runs.*run.ini` - add `PI_NAME` variable.
  [njcuk9999]
- `Apero.core.core.drs_recipe.py` - must check filter values for
  None/'None' and '' and skip filter for values that are unset.
  [njcuk9999]


0.6.114 (2020-07-04)
--------------------
- `Apero.core.coire.drs_file.py` +
  `apero.tools.module.setup.drs_processing.py` - deal with None/'None',''
  values in filedict (assume true as not set by file) [njcuk9999]
- `Apero.core.core.drs_recipe.py` - move `break_point`. [njcuk9999]
- `Apero.core.core.drs_recipe.py` - correct typo with filters from
  `file_filters`. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - modify break point.
  [njcuk9999]
- `Apero.core.core.drs_recipe.py` - deal with multiple file filters.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add break point to test
  filters. [njcuk9999]
- `Drs_file.py` - change debug output in `check_table_keys` and update
  language database. [njcuk9999]
- `Apero.core.core.drs_startup.py` + `apero.core.core.drs_startup.py` - add
  state string return and fix test run returns. [njcuk9999]
- `Aper.tools.recipe.bin.apero_processing.py` +
  `apero.core.core.drs_startup.py` - add keys parameter to allow custom
  copying of variables from `__main__` namespace. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - pass pid, success, passed
  properly back to processing from each job. [njcuk9999]
- `Apero.io.drs_fits.py` + `apero.recipes.*.*.py` - combine need recipe (for
  indexing) [njcuk9999]
- `Apero.core.core.drs_log.py` - make sure `set_plot_dir` has correct
  arguments. [njcuk9999]
- `Apero.core.core.drs_log.py` - `set_plot_dir` update children (and write
  to file) [njcuk9999]
- `Apero.plotting.core.py` - `recipe.log.set_plot_dir` takes params.
  [njcuk9999]
- `Apero.*` - replace `RAW_OUTPUT_KEYS`, `REDUC_OUTPUT_KEYS` and
  `RAW_OUTPUT_KEYS` with `OUTPUT_FILE_HEADER_KEYS`. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add pid to returns from
  linear process (for pickup by trigger) [njcuk9999]
- `Apero.plotting.html.py` - html figure should be just the basename (not
  the absolute path) [njcuk9999]
- `Apero.plotting.core.py` - update plot location in log when updated in
  plot. [njcuk9999]
- `Apero.core.instruments.default.pseudo_const.py` - add pid and fiber to
  reduced dir index.fits. [njcuk9999]
- `Core.core.drs_startup.py` - add nightname to index.fits and sort by lat
  modified. [njcuk9999]
- `Core.core.drs_log.py` - add `set_plot_dir` and `plot_dir` attribute to add
  plot directory to log.fits. [njcuk9999]


0.6.113 (2020-07-02)
--------------------
- Update language database. [njcuk9999]
- `Apero.science.telluric.general.py` - add print out for number of
  files/tpyestr for `get_tellu_objs`. [njcuk9999]
- `Apero.science.telluric.general.py` - add function `get_tellu_objs` to get
  telluric objects from telluric database. [njcuk9999]
- `Apero.recipes.spirou.obj_mk_tempalte_spirou.py` - distinguish between
  getting files from disk or telluric database (telluric database files
  are cleaned for QC) [njcuk9999]
- `Misc.tools.apero_diff.py` - fix bug. [njcuk9999]
- `Apero.science.telluric.general.py` - `load_tellu_file` func add
  `return_entires` and allow user to set mode + `fit_tellu_quality_control`
  - use snr qc for ftellu only. [njcuk9999]
- `Core.instruments.*.default_constants.py` + `default_keywords.py` - add
  back in some missing FTELLU constants + modify QC keywords.
  [njcuk9999]
- `Core.core.drs_database.py` - add a mode="ALL" to `get_key_from_db`.
  [njcuk9999]
- `Apero.core.core.drs_recipe.py` - inherit filters from given files (only
  if not already in filter list) [njcuk9999]
- `Apero.core.instruments.spirou.file_definitions.py` - add outfunc to
  `raw_lfc_lfc`. [njcuk9999]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add to
  engineering sequences. [njcuk9999]


0.6.112 (2020-06-29)
--------------------
- `Apero.core.core.drs_recipe.py` - only do `pconst.DRS_OBJ_NAME` if value
  is a string. [njcuk9999]
- `Apero.io.drs_fits.py` - must sort the kwargs by the sortmask for files.
  [njcuk9999]
- `Apero.data.spirou.reset.runs/science_run.ini` - correct typo.
  [njcuk9999]
- `Apero.core.instruments.spirou.recipe_defintions.py` - make sure
  `tellu_seq` and `science_seq` only extraction `OBJ_FP` and `OBJ_DARK` files.
  [njcuk9999]
- Update language database. [njcuk9999]
- `Tools.recipes.spirou.update_berv.py` - add prefix removal. [njcuk9999]


0.6.111 (2020-06-27)
--------------------
- `Tools.recipes.spirou.update_berv.py` - update berv code to account for
  more extracted files and fibers. [njcuk9999]
- `Apero.core.core.drs_file.py` - output dict needs to look in (1) hdixt
  (1) header. [njcuk9999]
- `Apero.science.extract.general.py` - add break point to explore problem
  with indexing. [njcuk9999]
- Make sure os.walk returns sorted files. [njcuk9999]
- Make sure all glob.glob and os.listdir and Path.glob are sorted
  alphabetically. [njcuk9999]
- `Apero.science.extract.berv.py` + `apero.science.extract.crossmatch.py` -
  add hdr objname for objects without valid simbad object name.
  [njcuk9999]
- `Apero.science.extract.crossmatch.py` - correct typo intable --> table.
  [njcuk9999]
- `Apero.science.extract.berv.py` - add debug print out of final input
  berv parameters. [njcuk9999]
- `Apero.science.extract.crossmatch.py` - carefully force data type for
  columns in object look up table (inlookuptable function) [njcuk9999]
- `Apero.science.extract.berv.py` - refractor some variables names (to
  distinguish from other variables) [njcuk9999]
- `Apero.io.drs_table.py` - add `force_dtype_col` function to deal with
  making sure columns are required data types. [njcuk9999]
- `Apero.core.core.drs_log.py` - deep copy anything in pcheck (should not
  be a shallow copy) [njcuk9999]
- `Apero.recipes.spirou.cal_extract_spirou.py` - add breakpoint.
  [njcuk9999]


0.6.110 (2020-06-25)
--------------------
- `Apero.tools.module.setup.drs_processing.py` - remove break point (error
  fixed) [njcuk9999]
- `Apero.science.calib.general.py` - make sure `objname_inputs` is upper
  case (for comparison with file case) [njcuk9999]
- `Recipes.*.cal_extract_*.py` - log1.writelog --> `log1.write_logfile`.
  [njcuk9999]
- `Misc.tools.create_science_targets.py` - add additional files to
  archive. [njcuk9999]
- `Apero.core.core.drs_recipe.py` - find `science_targets` and clean them
  (as well as telluric targets) - to match drs preprocessing objnames.
  [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add breakpoints to see
  crash. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move science target
  definitions. [njcuk9999]
- Changelog.md - update some old syntax. [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - move where
  `science_targets` is updated. [njcuk9999]
- Update `science_targets` (after clean up) [njcuk9999]
- `Apero.tools.module.setup.drs_processing.py` - add break point to test
  problem. [njcuk9999]
- `Misc.tools.create_science_targets.py` - add a list of science targets
  to the tar.gz file list. [njcuk9999]


0.6.109 (2020-06-24)
--------------------
- `Apero.plotting.plot_functions.py` - catch NaNs and deal with them in
  the plot. [njcuk9999]
- `Apero.science.velocity.general.py` - wsum2 cannot be negative (attempt
  2) [njcuk9999]
- `Apero.science.velocity.general.py` - wsum2 cannot be negative either.
  [njcuk9999]
- `Misc.tools.update_header_keys.py` - deal with missing headers better +
  add subdir / no subdir options. [njcuk9999]
- Update language database. [njcuk9999]
- `Science.velocity.general.py` - wsum cannot be less than zero otherwise
  wnoise is complex - set wnoise to inf if wsum is zero (we divide by
  wnoise later --> set ccf noise and ccf snr to NaN) [njcuk9999]
- Find all places where OBJNAME is used (not from the header) and pass
  value through pp header fix code for objname (in a consistent way)
  [njcuk9999]


0.6.108 (2020-06-22)
--------------------
- `Apero.science.velocity.general.py` - change
  `spline_weight(omask_centers)to` sweights. [njcuk9999]
- `Apero.science.velocity.general.py` - add a weight to ignore bad (not
  mask=good) sections of ccf. [njcuk9999]
- `Apero.science.velocity.general.py` - add break point to investigate
  crash. [njcuk9999]
- `Apero.misc.tools.update_header_keys.py` - make parallel. [njcuk9999]
- `Apero.io.drs_text.py` - remove debug print outs and deal with empty
  string (set to None) [njcuk9999]


0.6.107 (2020-06-20)
--------------------
- `Apero.science.extract.other.py` - get nightname from filename dir and
  dirname from the dir of the night name - file can change this.
  [njcuk9999]
- `Apero.core.core.drs_startup.py` - add debug printouts. [njcuk9999]
- `Apero.core.core.drs_startup.py` + `drs_recipe.py` - need to make
  `force_dirs` from recipe. [njcuk9999]
- `Apero.core.core.drs_startup.py` - need to deal with indir/outdir being
  none before checking abspath. [njcuk9999]
- `Apero.core.core.drs_startup.py` - need to check if force input/output
  dir argument has been used - if it has need to update recipe.inputdir
  and/or recipe.outputdir and update INPATH, OUTPATH. [njcuk9999]
- `Apero.core.core.drs_recipe.py` - add option if force is true to read
  input/output dir from recipe definition (now updated if force is on
  from raw/tmp/reduced to abspath) [njcuk9999]
- `Apero.science.extract.other.py` - force indir for extraction (combined
  files are stored in the reduced dir) [njcuk9999]
- `Core.core.drs_startup.py` - add getting of `forec_indir/outdir` and push
  into `get_input/output_dir` functions (overwrites default
  raw/tmp/reduced etc dirs) [njcuk9999]
- `Core.core.drs_recipe.py` - modify `get_input_dir` and `get_output_dir` and
  make force input/outdur special arguments. [njcuk9999]
- `Core.core.drs_argument.py` - add force input and output dirs.
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.106 (2020-06-18)
--------------------
- `Apero.core.core.drs_file.py` - add `is_combined` and combined list to
  keys, in combine function change the basename (i.e. 123, 124, 125 -->
  12F3T5) and save combined to reduced. [njcuk9999]
- `Apero.core.core.drs_startup.py` - make sure inpath, nightname and
  output are strings. [njcuk9999]
- `Apero.io.drs_fits.py` - write combined file to the reduced folder (with
  the new file name) [njcuk9999]
- `Apero.io.drs_text.py` - add `common_text` and `combine_uncommon_text`
  functions to handle list of files --> single filename. [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.science.calib.badpix.py` - change writing badpix file to use flat
  file (only important for processing with output names) [njcuk9999]
- `Core.instruments.spirou.recipe_defintions.py` - change order of
  arguments `(cal_shape_master)` - just important for processing with
  output names. [njcuk9999]
- `Core.instruemnts.spirou.file_definitions.py` - change badpix out files
  to use `flat_flat`. [njcuk9999]
- `Core.instruments.*.file_definitions.py` - change badpix `dark_dark` -->
  `flat_flat`. [njcuk9999]


0.6.105 (2020-06-17)
--------------------
- `Misc.tools.valid_raw_directories.py` - add a WORKSPACE for rawsym as
  well as raw. [njcuk9999]
- `Misc.tools.apero_diff.py` - only work out the fraction of finite
  pixels. [njcuk9999]
- `Misc.ea_alder32_code.py` - possible solution to file naming issue.
  [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - correct `_create_link`
  (Issue #630) [njcuk9999]
- `Science.calib.general.py` - remove breakpoint. [njcuk9999]
- `Apero.science.calib.background.py` - add break point in `cal_loc`.
  [njcuk9999]
- `Apero.science.calib.background.py` - add break point in `cal_loc`.
  [njcuk9999]


0.6.104 (2020-06-16)
--------------------
- `Misc.database_test.database.*` - first test and commit of database
  overhaul. [njcuk9999]
- `Apero.science.preprocessing.detector.py` - correct return to
  `nirps_correction`. [njcuk9999]
- `Apero.science.preprocessing.detector.py` - make sure we read the mask
  in get pp master and record to header `(nirps_ha)` [njcuk9999]
- `Apero.data.nirps_ha.engineering.hotpix_pp.csv` - add file to default
  files. [njcuk9999]
- `Apero.core.instruments.nrips_ha.recipe_definitons.py` +
  `data.nrips_ha.reset.runs` - update run.inis and sequences for nirps.
  [njcuk9999]


0.6.103 (2020-06-15)
--------------------
- `Apero.core.instruments.nirps_ha` - update nirps recipes after spirou
  changes. [njcuk9999]
- `Apero.recipes.nirps_ha` - update nirps recipes after spirou changes.
  [njcuk9999]
- `Misc.tools.update_header_keys.py` - add hack tool to update certain
  header keys on mass (no warning - careful of use!) [njcuk9999]
- Apero.data.spirou.reset.calibdb - update master wave solution +
  `master_calib_SPIROU.txt` (use more recent wave solutions + different
  for each fiber) [njcuk9999]
- `Apero.science.velocity.general.py` - add additional check for no valid
  pixels after blaze cut (keep) --> should avoid NaNs when no lines in
  order (Issue #622) [njcuk9999]
- Update the language database. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- `Apero.science.velocity.general.py` - add break point to investigate
  Issue #622. [njcuk9999]


0.6.102 (2020-06-12)
--------------------
- Merge pull request #629 from njcuk9999/working. [Neil Cook]

  Working --> Developer (tested with mini-run successfully)
- Update README.md. [Neil Cook]
- Merge pull request #627 from njcuk9999/neil. [Neil Cook]

  Neil --> working
- `Apero.core.instruments.spirou.recipe_defintions.py` - allow --plot to
  go to -1 (dev mode plot NOTHING) - not recommended for general use.
  [njcuk9999]
- `Misc.tools.valid_raw_directories.py` - add code to test the validity of
  an APERO raw directory. [njcuk9999]
- `Misc.tools.apero_mtl_sync_master.py` - update version and local path.
  [njcuk9999]
- Merge pull request #626 from njcuk9999/working. [Neil Cook]

  Working
- Merge pull request #625 from njcuk9999/neil. [Neil Cook]

  Neil
- Update `install.py` and `requirements_current.txt`. [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]
- `Apero.science.telluric.general.py` - remove break point. [njcuk9999]
- `Apero.core.instruments.*.file_defintiions.py` +
  `apero.core.instruments.default.output_filenames.py` - use basename
  instead of filename (avoids confusion in file defintions with
  `set_file)` [njcuk9999]
- `Apero.core.instruments.default.output_filenames.py` - be more careful
  with filename when setting a file (should not be a path) [njcuk9999]
- `Apero.science.telluric.general.py` - add break point to test tellu bug.
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]
- `Misc.tools.apero_diff.py` - add time/version/id key to file - and order
  columns better for output. [njcuk9999]
- `Apero.core.core.drs_database.py` - need to lock db files while they are
  being read (to avoid two or more cores opening at once) [njcuk9999]
- `Apero-drs.misc.tools.apero_diff.py` - add code to compare two DRS
  reductions. [njcuk9999]
- `Apero.core.core.drs_file.py` - correct typo - os.abspath -->
  os.path.abspath. [njcuk9999]
- Update date/version/changelog. [njcuk9999]
- Merge pull request #621 from njcuk9999/working. [Neil Cook]

  Working --> Developer
- Merge pull request #620 from njcuk9999/neil. [Neil Cook]

  `tools.module.setup.drs_installation.py` - `Path(in_tool_path)` --> str(i…
- Merge pull request #619 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #618 from njcuk9999/neil. [Neil Cook]

  Neil --> working


0.6.101 (2020-06-09)
--------------------
- `Apero.science.velocity.general.py` - remove breakpoint (problem solved)
  - Issue #623. [njcuk9999]
- `Apero.core.core.drs_file.py` - make filename absolute path in all cases
  (Issue #623) [njcuk9999]
- Add break point to test Issue 623. [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - value.exists() --> not
  value.exits() (Issue #624) [njcuk9999]


0.6.100 (2020-06-08)
--------------------
- `Misc/tools/apero_diff.py` - code to find differences between two
  reductions. [njcuk9999]
- `Apero.science.calib.dark.py` - add back in the dark removal of the low
  frequency dark. [njcuk9999]
- `Apero.recipe.spirou.cal_extract_spirou.py` - remove breakpoints.
  [njcuk9999]
- `Apero.core.instruments.spirou.default_constants.py` - add HCONE and
  HCTWO to `THERMAL_CORRECTION_TYPE2`. [njcuk9999]
- Move the break point. [njcuk9999]
- Move the break point. [njcuk9999]
- `Apero.science.velocity.general.py` - move breakpoint. [njcuk9999]
- `Apero.science.velocity.general.py` - add break point fto `fit_fp_peaks`.
  [njcuk9999]
- Update the `apero_mtl_sync` codes. [njcuk9999]
- `Requirements_current.txt` - add pyyaml requirement. [njcuk9999]
- Update env with yaml/pyyaml. [njcuk9999]
- `Tools.module.setup.drs_installation.py` - `Path(in_tool_path)` -->
  `str(in_tool_path)` [njcuk9999]
- `Apero-drs.setup.install.py` - correct typo `Path(drs_path)` -->
  `str(drs_path)` [njcuk9999]
- Update date/version/changelog/update notes/documentation. [njcuk9999]


0.6.099 (2020-06-04)
--------------------
- `Misc.tools.ccf_drift_plot.py` - add another ccf header key plot.
  [njcuk9999]
- Update update-notes for version 0.6.098. [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - correct typo join( -->
  joinpath( [njcuk9999]
- Apero-drs.setup.envs.README.md - add a read me to detail how to
  use/mask conda env files. [njcuk9999]
- Setup.env.apero-env-2020-06-03.txt - add env pip install copy.
  [njcuk9999]
- Setup.env.apero-env-2020-06-03.txt - add yml conda env copy.
  [njcuk9999]
- Setup.env.apero-env-2020-06-03.txt - add explicit environment copy.
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.098 (2020-06-01)
--------------------
- `Apero.plotting.plot_functions.py` - adjust ccf plot. [njcuk9999]
- `Apero.plotting.plot_functions.py` - update scale and add legend to
  `plot_ccf_photon_uncert`. [njcuk9999]
- `Apero.science.velocity.general.py` - correct `rv_noise` for
  `compute_ccf_fp`. [njcuk9999]
- `Apero.science.velocity.general.py` - correct `rv_noise`. [njcuk9999]
- `Apero.science.velocity.general.py` - add breakpoint to test bug.
  [njcuk9999]
- `Apero.science.velocity.general.py` - add EA calculation of DVRMS CC
  (from CCF) [njcuk9999]
- `Apero.science.velocity.general.py` - remove redundant 1/1/x --> x.
  [njcuk9999]
- `Apero.plotting.plot_functions.py` - Update `plot_ccf_photon_uncert` for
  ccf + sp noise. [njcuk9999]
- `Core.instruments.*.default_keywords.py` - remove `KW_CCF_MEAN_RV_NOISE`
  (now use `KW_CCF_DVRMS_SP` and `KW_CCF_DVRMS_CC)` [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - add str. [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - add int/float/bool.
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.097 (2020-05-30)
--------------------
- `Setup.install.py` and `setup.newprofile.py` - change os.path to
  pathlib.Path. [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` - replace os.path with
  pathlib.Path. [njcuk9999]
- `Apero.io.drs_path.py` - change copy tree to use pathlib.Path.
  [njcuk9999]
- `Apero.core.constants.param_functions.py` - allow `get_relative_folder` to
  accept pathlib.Path. [njcuk9999]
- `Apero.core.instruments.*.default_keywords.py` - add `KW_CCF_DVRMS_SP` and
  `KW_CCF_DVRMS_CC` keyword arguments. [njcuk9999]
- `Apero.science.velocity.general.py` - add a photon noise per order
  calculation and save to ccf table/header. [njcuk9999]
- Documnetation.working.user.general.todo.rst - update todo list.
  [njcuk9999]
- `Apero.recipes.spirou.pol_spirou_new.py` and
  `science.polar.general_new.py` - continue work on new polar code from
  @eder. [njcuk9999]
- `Apero.data.spirou.reset.runs.mini_run.ini` - add extra science targets
  (rv standards) [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - remove polar consts
  (for now) [njcuk9999]


0.6.096 (2020-05-27)
--------------------
- `Setup.newprofile.py` - add TODO as setup file is at the wrong path and
  needs fixing. [njcuk9999]
- `Apero.core.math.general.py` - add back in continuum function for now
  (until new polar code ready) [njcuk9999]
- `Td_data/apero-drs/setup/newprofile.py` - add debug and clean options.
  [njcuk9999]
- `Misc.tools.ccf_plot.py` - separate out science and reference fiber
  results into frames for plot. [njcuk9999]
- `Apero.recipes.spirou.pol_spirou_new.py` and
  `science.polar.general_new.py` - continue polar update from @eder.
  [njcuk9999]


0.6.095 (2020-05-25)
--------------------
- Test for git version adding for EA. [njcuk9999]
- `Apero.science.calib.dark.py` - make `large_image_median` -->
  `large_image_combine` and specify the median math mode (same as before
  but changed input) [njcuk9999]
- `Apero.recipes.spirou.cal_shape_master_spirou.py` +
  `apero.science.calib.shape.py` + `apero.io.drsimage.py` - make
  `large_image_median` --> `large_image_combine` and use a mean to combine
  fpcube and return fpmaster instead. [njcuk9999]
- `Apero.science.calib.shape.py` - add back break point to investiage
  fpdata shape error. [njcuk9999]


0.6.094 (2020-05-24)
--------------------
- `Apero.science.calib.shape.py` - need to increase row every iteration
  row+=1. [njcuk9999]
- `Apero.io.drs_image.py` + `apero.science.calib.shape.py` - move break
  point. [njcuk9999]
- `Apero.io.drs_image.py` - add breakpoint to figure out problem.
  [njcuk9999]
- `Apero.io.drs_image.py` - correct typo `b_it` --> `f_it`. [njcuk9999]
- `Apero.io.drs_image.py` - add more printouts. [njcuk9999]
- `Apero.io.drs_image.py` - make sure bins are scaled by number of pixels
  in image0. [njcuk9999]
- `Apero.io.drs_image.py` - make sure npy files have leading zeros.
  [njcuk9999]
- `Apero.io.drs_image.py` - remove dirs until filepath does not exist.
  [njcuk9999]
- `Apero.io.drs_image.py` + `science.calib.dark.py` and
  `science.calib.shape.py` - allow reading of fits and npy files in
  `large_image_median`. [njcuk9999]
- `Apero.io.drs_image.py` - fix npyfilelist. [njcuk9999]
- `Apero.io.drs_image.py` - clean up and fix typo. [njcuk9999]
- `Apero.io.drs_image.py` - correct typo wargs -> `*wargs`. [njcuk9999]
- `Apero.science.calib.dark.py` - correct outdir (no directory defined)
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` and
  `apero.science.calib.wave.py` - add rv difference bettwen fibers QC.
  [njcuk9999]
- `Apero.core.instruments.*.default_connstants.py` - add
  `WAVE_CCF_RV_THRES_QC`. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` +
  `cal_wave_master_spirou.py` + `apero.science.calib.wave.py` - remove break
  points and printouts --> fixed? [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` +
  `cal_wave_master_spirou.py` + `apero.science.calib.wave.py` - remove break
  points and test fix. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` +
  `cal_wave_master_spirou.py` + `apero.science.calib.wave.py` - add
  printouts to test differences (with breakpoints) [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` +
  `apero.science.calib.wave.py` - add more breakpoints. [njcuk9999]
- Updaet date/version/changelog/documentation. [njcuk9999]


0.6.093 (2020-05-22)
--------------------
- `Apero.science.calib.wave.py` - add force fiber to get wavesolution - do
  not use wprops in `night_wavesolution` (use only wavemap and wavefile)
  [njcuk9999]
- `Apero.recipes.*.cal_wave_night_*.py` - `night_wavesolution` now does not
  take wprops as input - only take wavemap and wavefile, and force fiber
  to be fiber=fiber (not use fiber) [njcuk9999]
- `Apero.science.calib.wave.py` - force two iterations of each wave
  solution, first time with AB, second time with own solution.
  [njcuk9999]
- `Apero.science.calib.wave.py` - force two iterations of each wave
  solution, first time with AB, second time with own solution.
  [njcuk9999]
- `Apero.recipe.spirou.cal_wave_master_spirou.py` - correct rkeys/wkeys.
  [njcuk9999]
- `Apero.science.calib.wave.py` - create `process_fibers` function - loop
  around fibers and run `night_wavesolution` (update dcavity and
  hclines/fplines when master is run) [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` - change way we
  calculate A, B and C (after AB, both AB, A, B and C are calculated in
  same way as night solution) [njcuk9999]
- `Apero.recipe.spirou.cal_wave_night_spirou.py` - change fpfiles -->
  rawfplines. [njcuk9999]
- `Apero.science.calib.wave.py` - add waveinit and nbpix to nprops.
  [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` and
  `cal_wave_night_spirou.py` - add `WFP_FILE`. [njcuk9999]
- `Apeor.core.constants.param_functions.py` - make sure source is not
  None. [njcuk9999]
- `Apeor.core.constants.param_functions.py` - correct typo np.ndarr -->
  np.ndarray. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` and
  `cal_wave_night_spirou.py` - move the break point. [njcuk9999]
- `Apero.recipes.spirou.cal_ccf_spirou.py` - add other key sources.
  [njcuk9999]
- `Core.lang.core.drs_lang_db.py` - add new terms. [njcuk9999]
- `Core.constants.param_functions.py` - add typing to param dict.
  [njcuk9999]
- `Apero.core.core.drs_file.py` - add nameattr `(get_instanceof` is now more
  generic) [njcuk9999]
- `Core.constants.constant_functions.py` - change `_DisplayText` -->
  DisplayText. [njcuk9999]


0.6.092 (2020-05-20)
--------------------
- `Apero.recipes.spirou.pol_spirou_new.py` +
  `apero.science.polar.general_new.py` - continue adding eders new polar
  recipe. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` - add break point to
  wave night. [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - add back
  `THERMAL_CORRECT` (why did it get removed?) [njcuk9999]


0.6.091 (2020-05-20)
--------------------
- `Apero.science.polar.general_new.py` - add PolarObjOut getting of tellu
  and ccf files. [njcuk9999]
- `Apero.recipes.spirou.pol_spirou_new.py` +
  `apero.science.polar.general_new.py` - continue work on loading polar
  files (finding ccf + tellu files) [njcuk9999]
- `Apero.core.instruments.default.output_filenames.py` - change wlog
  import. [njcuk9999]
- `Apero.core.core.drs_file.py` - add `reconstruct_filename` to get another
  filename close to input one (i.e. change of fiber) [njcuk9999]
- `Misc.tools.wave_drift_comp.py` - remove second plt.close() [njcuk9999]
- `Apero.science.calib.wave.py` - move break point to test rvs.
  [njcuk9999]
- `Apero.science.calib.wave.py` - add print out about saving fp mask.
  [njcuk9999]
- `Misc.tools.ccf_plot.py` - update how we get values. [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.science.calib.wave.py` - change how we construct outfile for
  `update_smart` mask. [njcuk9999]
- `Misc.tools.wave_drift_compy.py` - separate the frames into individual
  figures. [njcuk9999]
- `Apero.science.calib.wave.py` - correct typo in `update_smart_mask` u.nm
  --> uu.nm. [njcuk9999]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add WAVENIGHT
  plots to wave master. [njcuk9999]
- Update flow diagram for `cal_wave_master`. [njcuk9999]
- `Apero.science.calib.wave.py` - remove inverse of `fit_ll_d` polynomial
  (not required any more) [njcuk9999]


0.6.090 (2020-05-15)
--------------------
- `Apero.science.calib.shape.py` - update `construct_master_fp` to use large
  image median (better memory handlings to avoid memory errors)
  [njcuk9999]
- `Apero.science.calib.dark.py` - update `construct_master_dark` to use
  large image median (better memory handlings to avoid memory errors)
  [njcuk9999]
- `Apero.science.calib.wave.py` - add `WFP_FILE` for HC solution (set to
  None) [njcuk9999]
- `Apero.science.calib.wave.py` - correct typo `read_header_keys` -->
  `read_header_key`. [njcuk9999]
- `Apero.science.calib.wave.py` - add `update_smart_fp_mask` function to re-
  generate smart-fp-mask. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` - after wave solution
  calculated add a night wave solution for master fiber + add option to
  update smart FP mask after cavity poly updated. [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - add
  `WAVE_CCF_SMART_MASK` constants (for re-generating smart mask)
  [njcuk9999]
- `Misc.problems.test_crossmatch.py` - add pascals most recent query/gaia
  link. [njcuk9999]


0.6.089 (2020-05-14)
--------------------
- `Misc.tools.wave_drift_comp.py` - update wave drift code plot to add
  diff plot. [njcuk9999]
- `Documentation.working._static.yed` - update `cal_wave_master` flow
  diagrams. [njcuk9999]
- `Apero.science.extract.general.py` - in `write_extraction_files`
  `exclude_groups=loc` for e2dsfile (get them just from loc file later)
  [njcuk9999]
- `Apero.science.calib.wave.py` - read `WFP_FILE` from header, add WAVEINIT
  (WAVE INIT key at this point is same as WAVEFILE) - could differ after
  this, change value of `WFP_FILE` to wprops['WFPFILE'], when writing wave
  solutions update WAVEFILE, WAVETIME, WAVESOURCE and `WFP_FILE` to the
  new file itself, for `copy_original_keys` new to avoid copying wave keys
  from hcfile. [njcuk9999]
- `Cal_wave_night_spirou.py` - get back nprops from night write wavesol -
  pass these to update e2ds HC and FP files, return updated hc and fp
  e2ds files, use these to populate ccf output. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` - move `write_ccf`
  function and use updated e2ds files to populate it. [njcuk9999]


0.6.088 (2020-05-13)
--------------------
- `Apero.tools.recipes.utils.get_grid_models.py` - get the goettingen and
  convert to single table. [njcuk9999]
- `Apero.science.velocity.general.py` - modify `get_ccf_mask` and
  `ccf_calculation` with EA changes. [njcuk9999]
- `Apero.science.calib.dark.py` and `shape.py` - add large image median
  funtionality (as untested + unused versions) [njcuk9999]
- `Apero.io.drs_image.py` - add `npy_filelist`, `npy_fileclean` and
  `large_image_median` (untested) [njcuk9999]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  modifications to `pol_spirou_new`. [njcuk9999]
- `Core.core.drs_startup.py` - add `unix_char_code` function (to spawn from
  PID) [njcuk9999]
- `Misc.updates_to_drs.new_ccf_ea_2020-05-13.py` - another iteration by
  EA. [njcuk9999]
- `Apero.science.polar.general_new.py` - use as staging ground for eders
  changes (compared to 0.6+ version in general.py) [njcuk9999]
- `Apero.science.berv.py` - if infile is not defined should use header
  only to get berv keys. [njcuk9999]
- `Apeor.recipes.spirou.pol_spirou_new.py` - start filling out code
  (compared to Eders version and 0.6+ version and 0.5 version)
  [njcuk9999]
- `Apero.core.instruments.spirou.recipe_definitions.py` - add
  `pol_spirou_new` (for eders updates) [njcuk9999]


0.6.087 (2020-05-12)
--------------------
- `Apero.recipes.nirps_ha.cal_preprocess_nrips_ha.py` - add header as arg
  to `pp.nirps_correction`. [njcuk9999]
- `Apero.core.instruments.*.*` - update `nirps_ha` with changes to spirou.
  [njcuk9999]
- `Misc.updates_to_drs.mf_ccf_mask_may2020.py` - add EA code for injestion
  into the drs. [njcuk9999]
- `Apero.science.calib.wave.py` - do not use `FIBER_WAVE_TYPEs` for non
  master wave solution (i.e. use AB, A, B and C  not just AB, C)
  [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - be more descriptive
  about littrow HC and FP constants. [njcuk9999]
- `Apero.recipe.nirps_ha.py` - update changes in `nirps_ha` recipes (from
  spirou) [njcuk9999]


0.6.086 (2020-05-11)
--------------------
- Update language database. [njcuk9999]
- `Setup.install.py` - allow the user (on crash) to enter a path
  themselves and try again (for Claires issue that I cannot reproduce)
  [njcuk9999]
- `Apero.core.core.drs_recipe.py` - check against `input_dir` (from recipe
  definitions) [njcuk9999]
- `Apero.core.core.drs_argument.py` - remove break point - error fixed.
  [njcuk9999]
- `Apero.core.core.drs_argument.py` - add break point to fix error.
  [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` and
  `cal_wave_night_spirou.py` - add `velocity.write_ccf` to these codes (to
  save CCF for FPs) [njcuk9999]
- `Apero.core.instruments.spirou.recipe_defintions.py` - add `CCF_RV` to
  `cal_wave_master` and `cal_wave_night`. [njcuk9999]
- `Documentation.working._static.yed.*` - update `spirou_map_all`
  graphs/pdfs. [njcuk9999]


0.6.085 (2020-05-09)
--------------------
- `Misc.problems.shell_vs_call.py` - first commit of shell vs call test
  code for Andres/LAM. [njcuk9999]
- `Documentation.working._static.yed.apero_cal_wave_master.*` - update
  `cal_wave_master` flow diagram. [njcuk9999]
- `Documentation.working._static.yed.apero_cal_wave_master.*` - add
  `cal_wave_master` flow diagram. [njcuk9999]
- `Apero_rv` - add code, wrapper and utility functions for new ccf code
  (thanks to EA and his requirements) [njcuk9999]
- `Apero.tools.recipe.spirou.get_ext_fplines.py` - add file/dprtype/object
  printout. [njcuk9999]


0.6.084 (2020-05-06)
--------------------
- `Apero-drs.setup.install.py` - add detailed debug of root/cwd/pythonpath
  and sys.path. [njcuk9999]
- `Apero-drs.setup.install.py` - add another debug printout. [njcuk9999]
- Apero.tools.module.setup and `setup.install.py` - add debug mode.
  [njcuk9999]
- `Apero.tools.module.setup.drs_installation.py` + `setup.install.py` - add
  `--clean_no_warning` for those who like deleting data without prompts
  (Issue #579) [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.083 (2020-05-05)
--------------------
- `Recipes.spirou.cal_extract_spirou.py` +
  `toools.recipes.spirou.get_ext_fplines.py` - change `EXT_FPLIST` -->
  `EXT_FPLINES`. [njcuk9999]
- `Apero.tools.recipes.spirou.get_ext_fplines.py` - have to set plot
  location. [njcuk9999]
- `Science.extract.general.py` - add debug print outputs when fiber and
  dprtype are incorrect. [njcuk9999]
- `Apero.io.drs_fits.py` - `HEADER_FIXES` requireds hdict input and output.
  [njcuk9999]
- `Core.instruments.*.pseudo_const.py` - require hdict to be populated.
  [njcuk9999]
- `Misc.tools.apero_mtl_sync_master.py` - add tmp files to uploads.
  [njcuk9999]
- `Apero.tools.recipes.spirou.get_ext_fplines.py` - first commit of
  extract fplines (separate from extract code) [njcuk9999]
- `Apero.tools.module.testing.drs_dev.py` - add mod to temp
  RecipeDefinition. [njcuk9999]
- `Apero.science.extract.general.py` - add `ref_fplines` function.
  [njcuk9999]
- `Apero.science.calib.wave.py` - add a required condition to
  `get_wavelines`. [njcuk9999]
- `Apero.recipes.spirou.cal_wave_night_spirou.py` - add fiber to
  `get_wavelines`. [njcuk9999]
- `Apero.recipes.*.cal_extract_spirou.py` - add fplines creation.
  [njcuk9999]
- `Core.instruments.*.recipe_defintions.py` - add `EXT_FPLINES`. [njcuk9999]
- `Core.instruments.*.file_definitions.py` - add `ext_fplines`. [njcuk9999]
- `Core.instruments.default_constant.py` - add `WAVE_FP_DPRLIST` to
  constants. [njcuk9999]
- `Core.core.drs_log.py` - add doc string for `find_param`. [njcuk9999]
- `Core.instruments.spirou.default_config.py` - change calibDB mode to
  closest. [njcuk9999]
- Merge branch 'developer' of https://github.com/njcuk9999/apero-drs
  into developer. [njcuk9999]
- Update README.md. [Neil Cook]

  update versions
- Merge pull request #617 from njcuk9999/developer. [Neil Cook]

  Developer
- Merge pull request #608 from njcuk9999/developer. [Neil Cook]

  Developer
- Merge pull request #605 from njcuk9999/developer. [Neil Cook]

  Developer --> master
- Merge pull request #585 from njcuk9999/working. [Neil Cook]

  Working --> Master
- `Setup.install.py` - kill infinite loop to find apero. [njcuk9999]
- Merge pull request #616 from njcuk9999/working. [Neil Cook]

  Working
- Merge pull request #615 from njcuk9999/neil. [Neil Cook]

  update update notes/todo/known issues
- Update update notes/todo/known issues. [njcuk9999]
- Merge pull request #614 from njcuk9999/neil. [Neil Cook]

  neil --> working
- Update date/version/changelog/documentation. [njcuk9999]
- Merge pull request #607 from njcuk9999/working. [Neil Cook]

  Working
- Merge pull request #606 from njcuk9999/neil. [Neil Cook]

  update readme
- Merge pull request #604 from njcuk9999/working. [Neil Cook]

  Working --> Developer
- Merge pull request #603 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #591 from njcuk9999/working. [Neil Cook]

  Working --> Developer
- Merge pull request #590 from njcuk9999/neil. [Neil Cook]

  neil --> working
- Merge pull request #589 from njcuk9999/working. [Neil Cook]

  Working --> Developer
- Merge pull request #587 from njcuk9999/neil. [Neil Cook]

  Neil override: neil --> working
- Merge pull request #582 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #581 from njcuk9999/neil. [Neil Cook]

  Merge allowed


0.6.082 (2020-05-04)
--------------------
- `Apero.tools.resources.setup.apero.*.*` - update the MKL environment
  exports. [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.io.drs_fits.py` - add the getting of a time variable from the
  index files and sort by it before returning - all files should be in
  date order at point of return. [njcuk9999]
- `Apero.tools.recipes.spirou.update_berv.py` - remove from `__future__`
  import. [njcuk9999]
- `Apero.recipe.spirou.cal_shape_master_spirou.py` +
  `apero.science.calib.shape.py` - get dxrms and pass to qc (Issue #602)
  [njcuk9999]
- `Core.instruments.*.default_constants.py` - add `SHAPE_MASTER_DX_RMS_QC`
  value (Issue #602) [njcuk9999]
- `Core.core.drs_database.py` - remove break point. [njcuk9999]
- `Apero..science.calib.shape.py` - get rms value for dx-min(ddx) (Issue
  #602) [njcuk9999]
- `Apero.science.extract.crossmatch.py` - add back warnings for issues
  with crossmatching - were only debug messages (Issue #612) [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - update gaia url for
  tap query (Issue #612) [njcuk9999]
- `Apero.core.core.drs_file.py` - need to return False if `copy_cards` has a
  group argument but header key not found in defined keywords.
  [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.081 (2020-05-01)
--------------------
- `Science.calib.wave.py` - only update `dd_cavity` when indcavity is None
  (not the opposite) [njcuk9999]
- `Apero-drs.requirements_current.txt` - change PIL--> Pillow. [njcuk9999]
- Update the date/version/changelog/documentation. [njcuk9999]
- `Misc.tools.ccf_plot.py` - update plot. [njcuk9999]
- `Aspero.science.calib.wave.py` - remove `break_point`. [njcuk9999]
- `Aspero.science.calib.wave.py` - do not update the `d_cavity` when a input
  dcavity (indcavity) is provided. [njcuk9999]
- `Apero.plotting.plot_functions.py` - add a ylabel for wave night hist
  graph. [njcuk9999]


0.6.080 (2020-04-30)
--------------------
- `Apero.core.core.drs_file.py` - correct header card copy bug (Issue
  #611) [njcuk9999]
- `Apero.core.instruemnts.*.default_keywords.py` - correct `KW_INFILE2` and
  `KW_INFILE3`. [njcuk9999]
- `Apero.plotting.plot_functions.py` - remove frame 3. [njcuk9999]
- `Plotting.plot_functions.py` and `science.calib.shape.py` - remove frame
  3, function `get_offset_sp` and xpeak2 etc. [njcuk9999]
- `Plotting.plot_functions.py` and `science.calib.shape.py` - remove frame
  3, function `get_offset_sp` and xpeak2 etc. [njcuk9999]
- `Apero.science.calib.general.py` - deal with `n_entries` == 1 for filename
  not equal to None. [njcuk9999]
- `Apero.science.calib.general.py` - `n_entries` must = 1 (only need one
  fpmaster) [njcuk9999]
- `Apero.science.calib.general.py` - fix value if it is a
  filename/DrsFitsFile instance. [njcuk9999]
- `Cal_shape_master_spirou.py` - params['INPUTS']['FPMASTER'][0][0]
  [njcuk9999]
- `Cal_shape_master_spirou.py` - filename for FPMASTER should be [0]
  [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.science.calib.shape.py` - typo arg --> args. [njcuk9999]
- `Apero.science.calib.shape.py` - if we have no HC lines do not try to
  find Nth line fppeak using HC (assume that it is correct from fp)
  [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.science.calib.shape.py` - add `break_point` to test error.
  [njcuk9999]
- `Apero.core.instruments.spirou.default_constants.py` - go back to new
  line list. [njcuk9999]
- `Misc.tools.mk_master_hc_cat.py` - change path of `wave_hclines`.
  [njcuk9999]
- Update wave calib files. [njcuk9999]
- `Apero.core.instruments.spirou.default_constants.py` - change wave
  catalogue back to original. [njcuk9999]
- `Apero.science.calib.wave.py` - remove sigclip mask. [njcuk9999]
- `Apero.science.calib.shape.py` - pep8 update. [njcuk9999]
- `Apero.science.calib.wave.py` - add break point from EA. [njcuk9999]
- `Apero.core.instruments.default.default_constants.py` -
  `WAVE_LINELIST_START` should be an integer. [njcuk9999]
- `Apero.io.drs_data.py` - correct typo `data_start` --> datastart.
  [njcuk9999]
- `Apero.core.instruments.spirou.default_constants.py` - change linelist
  start to line 1. [njcuk9999]
- `Apero.core.core.drs_file.py` and `science.extract.general.py` - add
  `copy_header` function (in addition to `copy_hdict)` and for s1d files
  copy the header from the e2ds file not the hdict (which only has new
  keys in) - Issue #610) [njcuk9999]
- `Apero.science.extract.general.py` - add break point to investigate no
  header in s1d. [njcuk9999]
- Update date/version/changelog/documentation. [njcuk9999]


0.6.079 (2020-04-28)
--------------------
- Update language database. [njcuk9999]
- `Misc/tools/mk_master_hc_cat.py` + `data.spirou.calib.catalogue_UNe.csv` -
  code to update the hc linelist. [njcuk9999]
- `Apero.core.instruemnts.spirou.defalut_constants.py` - update catalogue
  file and fmt. [njcuk9999]
- `Apero.core.instruments.spirou.default_constants.py` - pep8 adjustment.
  [njcuk9999]
- `Apero.plotting.plot_functions.py` - add summary descriptions for two
  wave night summary plots. [njcuk9999]
- `Apero.science.calib.wave.py` - add `wave_expected` (after) plot for hc
  and fp. [njcuk9999]
- `Apero.scioence.calib.wave.py` - and catch warning statement around
  madmask. [njcuk9999]
- Update language database. [njcuk9999]
- `Science.calib.wave.py` - remove breakpoint + and range for second
  iteration. [njcuk9999]
- `Apero.plotting.plot_functions.py` - correct wave night figures.
  [njcuk9999]
- `Apero.science.calib.wave.py` - add break point to test EA new code.
  [njcuk9999]
- `Plotting.plot_functions.py` - correct typo kwargs['waveref'] -->
  kwargs['waverefs'] [njcuk9999]
- `Core.instruments.*.default_keywords.py` - correct typo groupu-->group.
  [njcuk9999]
- `Apero.core.instruments.default.default_constants.py` - remove
  `PLOT_WAVENIGHT_DIFFPLOT` from `__ALL__` [njcuk9999]
- `Apero.science.calib.wave.py` - add EA updates to `night_wavesolution`.
  [njcuk9999]
- `Recipes.spirou.cal_wave_night_spirou.py` - add fiber to inputs of
  `night_wavesolution` (for plot saving) [njcuk9999]
- `Plotting.plot_functions.py` - modify wave night plotting
  `(wavenight_iterplot` + `wavenight_histplot)` and remove
  `wavenight_diffplot` after ea changes. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - modify debug/summary
  plots after EA changes. [njcuk9999]
- Update language database. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - remove
  `WAVENIGHT_DIFFPLOT` from debug plot list. [njcuk9999]
- `Core.instruments.default_constants.py` and `default_keywords.py` -
  add/remove/modify wave night constants/keywords with new update from
  EA. [njcuk9999]
- `Misc.tools.ccf_plot.py` - update graph. [Neil Cook]


0.6.078 (2020-04-27)
--------------------
- `Recipes.nirps_ha.cal_preprocessing_niprs_ha.py` - update pp for nirps
  (from spirou updates) [njcuk9999]
- `Recipes.spirou.cal_preprocessing_spirou.py` and
  `science.preprocessing.general.py` - fix qc to print only when log=True
  + redo QC after iteration loop. [njcuk9999]
- `Misc.tools.wave_drift_comp.py` - test drift in fibers. [njcuk9999]
- `Apero.recipe.spirou.cal_preprocess_spirou.py` - deal with a QC after a
  shift in pixels. [njcuk9999]
- Update date, version, changelog, documentation. [njcuk9999]


0.6.077 (2020-04-24)
--------------------
- /locale/ --> /lang/ [njcuk9999]
- Apero.locale --> apero.lang. [njcuk9999]
- `Io.drs_fits.py` + `science.preprocessing.identification.py` - fix for
  preprocessing to use input file (was changed due to copyother change)
  [njcuk9999]
- `Apero.science.preprocessing.detector.py` - add a border mask to remove
  hotpix that lie near the edge (we need to scan around them so these
  are not useful) [njcuk9999]
- `Apero.io.drs_data.py` + `apero.science.preprocessing.detector.py` -
  format hotpix table correctly. [njcuk9999]
- `Apero.core.instruments.*.default_constants.py` - add back in
  `PP_CORRUPT_MED_SIZE`. [njcuk9999]
- `Apero.science.calib.wave.py` - add rhcl and rfpl to output (for saving
  to file) [njcuk9999]
- `Core.instruments.spirou.file_definitions.py` + `recipe_definitions.py` -
  add `WAVE_HCLIST` and `WAVE_FPLIST`. [njcuk9999]
- `Recipes.spirou.cal_wave_master_spirou.py` + science.velocity.general.py
  - remove the wave test code. [njcuk9999]
- `Recipe.spirou.cal_wave_master_spirou.py` + science.velocity.general.py
  - push correct e2ds fiber into ccf code. [njcuk9999]
- `Science.calib.wave.py` - data `llprops['LL_FINAL']` --> wprops['WAVEMAP']
  [njcuk9999]
- `Recipes.spirou.cal_wave_master_spirou.py` + science.velocity.general.py
  - add wavetest to test wavemap values. [njcuk9999]
- `Science.calib.wave.py` - add master wave sol to solutions (after
  plotting) [njcuk9999]
- `Recipes.spirou.cal_wave_master_spirou.py` science.calib.wave.py
  `science.velocity.general.py` - move break points. [njcuk9999]


0.6.076 (2020-04-22)
--------------------
- `Apero.science.calib.wave.py` - correct wave fp header keys. [njcuk9999]
- `Apero.core.instruemnts.spirou.default_constants.py` - add smart FP mask
  as default from EA. [njcuk9999]
- Add updated cavit length equation files. [njcuk9999]
- Add EA smark fp mask from cavity file. [njcuk9999]
- `Science.velocity.general.py` - deal with bounds and change remove wide
  peaks criteria. [njcuk9999]
- `Science.velocity.general.py` - deal with bounds and change remove wide
  peaks criteria. [njcuk9999]
- `Science.velocity.general.py` - remove exception breakpoints.
  [njcuk9999]
- `Science.velocity.general.py` - adjust dc and shape p0 values.
  [njcuk9999]
- `Apero.science.velocity.general.py` - add breakpoints to fit fp
  exceptions (For test) [njcuk9999]
- `Science.velocity.general.py` - deal with bounds being out-of-bounds.
  [njcuk9999]
- `Apero.science.velocity.general.py` - add back in pcov. [njcuk9999]
- `Apero.science.velocity.general.py` - correct bounds. [njcuk9999]
- `Apero.science.velocity.general.py` - add bounds to fp fit. [njcuk9999]
- `Science.velocity.general.py` - add break point to test. [njcuk9999]
- `Apero.science.velocity.general.py` - set `peak_spacing` = 5 (old drs
  value) [njcuk9999]
- `Apero.science.calib.wave.py` and `apero.science.velocity.general.py` -
  remove params from `fit_fp_peaks`. [njcuk9999]


0.6.075 (2020-04-21)
--------------------
- `Apero.science.velocity.general.py` - reduce the peak criteria to half
  the order peak size. [njcuk9999]
- `Apero.science.velocity.general.py` - change outputs for `fit_fp_peaks`.
  [njcuk9999]
- `Apero.science.velocity.general.py` - dcpenormpercentak --> dcpeak.
  [njcuk9999]
- `Apero.science.velocity.general.py` - fix typo normpercentile -->
  normpercent. [njcuk9999]
- `Science.calib.wave.py` - move print outs to language database.
  [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.science.velocity.general.py` - deal with `curve_fit` warnings.
  [njcuk9999]
- `Apero.science.calib.wave.py` - add warnings back to code. [njcuk9999]
- Update language database. [njcuk9999]
- `Apero.core.instruments.default_keywords.py` - add `KW_WFP_WIDUSED` for
  storing width per order. [njcuk9999]
- `Apero.science.calib.wave.py` - move constants to wave file and update
  header. [njcuk9999]
- `Apero.science.velocity.general.py` - move constants to constants files.
  [njcuk9999]
- `Core.instruments.*.default_constants.py` + `default_keywords.py` - adjust
  wave fp constants after fp finding update. [njcuk9999]
- `Science.calib.wave.py` - need new cond2 for FP. [njcuk9999]
- `Science.calib.wave.py` - add breakpoint to test `get_master_lines`.
  [njcuk9999]
- `Science.velocity.general.py` - change limit 0.3 --> 0.1. [njcuk9999]
- `Science.calib.wave.py` - remove breakpoint. [njcuk9999]
- `Science.calib.wave.py` - update output from line fit. [njcuk9999]
- `Core.instruments.*.default_contants.py` - update cavity file.
  [njcuk9999]
- `Science.velocity.general.py` - change EWPEAK to PEAK2PEAK and modify
  `remove_wide_peaks` (width is peak to peak not normalized width)
  [njcuk9999]
- `Core.instruemnts.spirou.default_constants.py` - change
  `WAVE_FP_NORM_WIDTH_CUT` from 0.25 to 15. [njcuk9999]
- `Science.velocity.general.py` - add `fit_fp_peaks` function. [njcuk9999]
- `Science.calib.wave.py` - FP should use `ea_airy` function. [njcuk9999]
- `Science.velocity.general.py` - determine fp peak size from the data
  (median of all peak widths) [njcuk9999]
- `Science.velocity.general.py` - modify the FP peak finding (now use the
  `ea_airy` function) [njcuk9999]
- `Core.math.general.py` - add `ea_airy_function` (for FP peak finding)
  [njcuk9999]
- `Core.insturments.spirou.default_constants.py` - change the border and
  box size for FP peak finding (now using `ea_airy)` [njcuk9999]
- `Science.velocity.general.py` - add breakpoint to test gaussian.
  [njcuk9999]


0.6.074 (2020-04-20)
--------------------
- `Apero.core.math.__init__.py` - add `gauss_beta_function`. [njcuk9999]
- `Misc.problems.new_ccf_code.py` - add EA changes to give option to play
  with convolution kernel. [njcuk9999]
- `Misc.nirps_tools.correct_sims.py` - write code to correct the headres
  of simulations. [njcuk9999]
- `Apero.science.velocity.general.py` - swap gaussian fit fot
  `gaussian_beta` fit in `function=measure_fp_peaks`. [njcuk9999]
- `Apero.science.calib.wave.py` - change inverse coefficient fit for
  updating `pixel_ref` (rpixels --> rwaveref) [njcuk9999]
- `Apero.core.math.gauss.py` - add `gauss_beta_function` for
  ((x-x0)/sigma)^beta. [njcuk9999]


0.6.073 (2020-04-18)
--------------------
- `Apero.science.calib.wave.py` - add iteration for WAVEREF plot.
  [njcuk9999]
- `Apero.plotting.plot_functions.py` - update the title depending on where
  used. [njcuk9999]
- `Documentation.working.user.general.known_issues.rst` - update known
  issues. [njcuk9999]
- `Science.calib.wave.py` - update plot (give before and after)
  [UNFINISHED] [njcuk9999]


0.6.072 (2020-04-17)
--------------------
- `Apero.plotting.plot_functions.py` and `science.velocity.general.py` -
  update wave fiber plot size + add fiber name to ccf fp plot.
  [njcuk9999]
- `Apero.plotting.plot_functions.py` - make markers smaller. [njcuk9999]
- Wave codes - pep8 corrections. [njcuk9999]
- `Science.calib.wave.py` - correct typo `WAVE_OTHERFIBER` -->
  `WAVE_FIBER_COMPARISON`. [njcuk9999]
- Update todo list. [njcuk9999]
- `Science.velocity.general.py` - do not limit fp ccf to fiber c (AB,A,B
  valid too) [njcuk9999]
- `Apero.recipes.spirou.cal_wave_master_spirou.py` - only do main code for
  `master_fiber` and then add functionality to process other fibers (fit
  from FPLINES) + CCF and write loops. [njcuk9999]
- `Apero.plotting.plot_functions.py` - add `plot_wave_fiber_comparison`.
  [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - add `wave_fiber_comp`
  plots. [njcuk9999]
- Update language database. [njcuk9999]
- `Core.instruments.default.default_constants.py` - add wave fiber
  constants. [njcuk9999]
- `Documentation.working.user.general.known_issues.rst` - update known
  issues. [njcuk9999]
- `Misc.problems.new_ccf_code.py` - update `CCF_RV_NULL` and add `IN_RV` (copy
  from apero-utils) [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - add `EXTRACT_S1D_WEIGHT`
  to debug plots. [njcuk9999]
- `Core.core.drs_log.py` - change typo fmt-->format. [njcuk9999]
- `Science.calib.wave.py` - add wave time to hc and fp solutions.
  [njcuk9999]
- `Science.velocity.general.py` - make `null_targetrv`. [njcuk9999]
- `Core.instrument.*.default_constant.py` - NULLVAL for RV is now a abs
  limit. [njcuk9999]


0.6.071 (2020-04-16)
--------------------
- `Apero.recipes.nirps_ha.cal_preprocess_nirps_ha.py` - change instrument
  SPIROU --> `NIRPS_HA`. [njcuk9999]
- `Apero.io.drs_data.py` - `load_hotpix` fmt is 'csv' not 'None' [njcuk9999]
- `Apero.io.drs_data.py` - `read_table` default table is fits. [njcuk9999]
- `Core.core.drs_log.py` - Table.read log --> fmt='fits' [njcuk9999]
- `Tools.recipe.bin.apero_processing.py` - remove old break point.
  [njcuk9999]
- `Tools.module.setup.drs_processing.py` - if we have to find the recipe
  set the file mod after finding it. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - replace `_run` with `_seq`
  and add engineering sequence `(hc1_hc1` extract, `fp_fp` extract, `dark_fp`
  extract) [njcuk9999]
- `Data.spirou.reset.runs.*` - update sequences `_run` --> `_seq`. [njcuk9999]
- `Recipes.spirou.cal_wave_night_spirou.py` - remove one of the
  breakpoints. [njcuk9999]
- `Core.instruments.spirou.file_definitions.py` - add back in thermal e2ds
  with correct `kw_output`. [njcuk9999]
- `Recipes.spirou.cal_wave_night_spirou.py` - add breakpoint for testing.
  [njcuk9999]


0.6.070 (2020-04-15)
--------------------
- `Core.instruments.spirou.recipe_defintions.py` - add `EXTRACT_S1D_WEIGHT`.
  [njcuk9999]
- README.md - update raw file table. [njcuk9999]
- `Apero.tools.recipes.bin.apero_mkdb.py` - skip master files. [njcuk9999]
- Update language database. [njcuk9999]
- `Tools.recipes.bin.apero_mkdb.py` - skip master default files.
  [njcuk9999]
- `Core.core.drs_file.py` + `io.drs_fits.py` - do not report error from read
  header in id. [njcuk9999]
- `Core.instruments.spirou.file_definitions.py` - `out_wave_night` - `WAVE_FP`
  --> `WAVE_NIGHT`. [njcuk9999]
- `Science.extract.other.py` - correct `KW_OUTPUT` for thermal files.
  [njcuk9999]
- `Core.core.drs_file.py` + `io.drs_fits.py` - deal with copyother and
  trying to open files with wrong extensions. [njcuk9999]
- `Data.spirou.reset.runs.mini_run.ini` - set `reset_run` to False by
  default. [njcuk9999]
- `Core.core.drs_file.py`  in `check_read` get `load_data` option from call
  args. [njcuk9999]
- `Core.core.drs_file.py`  in `check_read` get `load_data` option from call
  args. [njcuk9999]
- `Tools.recipes.bin.apero_mkdb.py` - do not get data when identifying
  file. [njcuk9999]
- `Core.core.drs_file.py` - read file after copying parameters (so
  datatype is correct) [njcuk9999]
- `Core.core.drs_file.py` - do not copy over drsfile.datatype from infile
  (in copyother) [njcuk9999]
- `Instruments.spirou.file_definitions.py` - update `KW_OUTPUT` (should be
  WAVEM) [njcuk9999]
- `Core.core.drs_database.py` - fix error in writing to database.
  [njcuk9999]
- `Science.calib.wave.py` - add WAVETIME to nprops (for header)
  [njcuk9999]
- `Recipe.spirou.cal_wave_night_spirou.py` + `science.calib.wave.py` - add
  input dcavity for fibers A,B,C (use cavity width from AB) [njcuk9999]
- `Core.instrument.*.default_keywords.py` - add dcavity source.
  [njcuk9999]


0.6.069 (2020-04-09)
--------------------
- `Recipe.spirou.cal_ccf_spirou.py` - correct typo `rv_props1` --> `rv_props2`
  for WAVESOURCE. [njcuk9999]
- `Core.instruments.spirou.recipe_defintions.py` - add tmp (commented)
  polar recipe. [njcuk9999]
- `New_ccf_code.py` - add help. [njcuk9999]
- `Core.core.drs_log.py` and `io.drs_lock.py` - correct write statement
  (log--> mode=a) [njcuk9999]


0.6.068 (2020-04-08)
--------------------
- `Science.velocity.general.py` - add rv wave source to ccf header.
  [njcuk9999]
- Misc.old - move `cal_wave_spirou.py` [old code] to misc. [njcuk9999]
- `Science.calib.wave.py` - add wave time to wprops + add it to header
  when present (i.e. in `add_wave_keys)` [njcuk9999]
- `Recipes.spirou.cal_ccf_spirou.py` - add wave source for rv fiber to
  header. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - remove old `cal_wave`.
  [njcuk9999]
- `Cpre.instruments.*.default_keywords.py` - modify ccf rv wave keys.
  [njcuk9999]
- `Cal_ccf_spirou.py` - save rv wavefile, rv wave time and rv time diff
  (file->wave) to header. [njcuk9999]
- `Core.instruments.*.defaults_keywords.py` - add `KW_CCF_RV_WAVEFILE`,
  `KW_CCF_RV_WAVETIME` and `KW_CCF_RV_TIMEDIFF` (for ccf) [njcuk9999]
- `Misc.problems.new_ccf_code.py` - update code, make it completely
  independent of the drs + add writing file + add switch for OBJ and FP
  + add plots (and plot switch) [njcuk9999]


0.6.067 (2020-04-07)
--------------------
- Split `create_pp_hotpix.py` into two bits - one for each instrument +
  update for drs integration (via `drs_dev` tmp functions) [njcuk9999]
- `Science.preprocessing.detector.py` - update get hot pixel function to
  load ypix and xpix from file. [njcuk9999]
- `Apero.io.drs_data.py` - change `load_full_flat_pp` to `load_hotpix`.
  [njcuk9999]
- `Data.spiroiu.engineering.hotpix_pp.csv` - update hotpix file for
  spirou. [njcuk9999]
- `Core.instruments.*.default_constants.py` - modify pp constants for new
  hotpix function/file. [njcuk9999]


0.6.066 (2020-04-07)
--------------------
- Add a hotpix mask for spirou. [njcuk9999]
- Tools.recipes.utils.README.md - add a directory for utilities.
  [njcuk9999]
- `Tools.recipe.utils.create_pp_hotpix.py` - add EA hotpix generator.
  [njcuk9999]
- `Tools.recipes.spirou.update_berv.py` - rename from `cal_update_berv.py`.
  [njcuk9999]
- `Core.math.general.py` - add in the `normal_fraction` math function.
  [njcuk9999]


0.6.065 (2020-04-03)
--------------------
- Replace open+read/write+close --> with open+read/write. [njcuk9999]
- `Tools.recipes.spirou.expmeter_spirou.py` - change `copy_hdict` -->
  `copy_original_keys`. [Neil Cook]
- `Tools.recipes.spirou.expmeter_spirou.py` - corerct code after testing.
  [Neil Cook]
- `Core.core.drs_file.py` - make `add_hkey` accept list or tuple for
  keywordstore. [Neil Cook]
- `Tools.recipes.spirou.expmeter_spirou` - add saving to file (using
  `drs_dev` FileDefinitions and Tmp files) [Neil Cook]
- `Tools.module.testing.drs_dev.py` - add TmpInputFile,  TmpFitsFile and
  TmpNpyFile and FileDefinition to allow external file defintions (for
  tools and testing) [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- `Tools.recipes.spirou.expmeter_spirou.py` - move exposuremeter constants
  to constants file (use params) [njcuk9999]
- `Core.instruments.*.default_constants.py` - add exposure meter
  constants. [njcuk9999]
- `Misc/tools/apero_mtl_sync_master.py` - add master sync code. [Neil
  Cook]


0.6.064 (2020-04-02)
--------------------
- Update language database. [njcuk9999]
- `Io.drs_lock.py` - deal with locking and removing files bug (Impossible
  error should now be impossible) [njcuk9999]
- `Core.core.drs_database.py` - check calibration is copied after copying
  (so we don't update database if there was an uncaught error)
  [njcuk9999]
- Documentation.working.user.general.todo.rst - update todo list.
  [njcuk9999]
- `Tools.recipes.spirou.expmeter_spirou.py` - continue work on
  functionality. [njcuk9999]
- `Io.drs_fits.py` - add function `add_header_key` (for when we don't have a
  drs fits file) [njcuk9999]
- `Core.math.general.py` - add inverse functionality to rot8. [njcuk9999]
- Update readme. [njcuk9999]
- Update date/version/changelog/update notes. [njcuk9999]


0.6.063 (2020-04-01)
--------------------
- `Apero.data.spirou.reset.runs.mini_run.ini` - turn off MKTELLDB and
  FTELLDB runs (use individuals) [njcuk9999]
- `Apero.recipes.spirou.cal_leak_spirou.py` - qcparams is a dict --> user
  ref fiber. [njcuk9999]
- `Apero.recipes.spirou.cal_leak_spirou.py` - add qc to log.fits.
  [njcuk9999]
- `Core.instruments.default.recipe_definitions.py` - master is reserved
  keyword --master --> --mlog. [njcuk9999]
- `Recipe.spirou.expmeter_spirou.py` - continue work on exposuremeter.
  [Neil Cook]
- `Science.telluric.general.py` - fix `core.get_file_definition`. [Neil
  Cook]
- `Tools.recipe.spirou.expmeter_spirou.py` - add params to arguments of
  `simage_to_drs`. [Neil Cook]
- `Tools.module.utils.inverse.py` - add required keys. [Neil Cook]
- `Science.telluric.general.py` - provide fiber fot `TELLU_CONV`. [Neil
  Cook]
- `Tools.recipes.spirou.expmeter_spirou.py` - add telluric map (from mask
  making) - UNFINISHED. [Neil Cook]
- `Tools.module.utils.inverse.py` - move imports to top. [Neil Cook]
- `Science.telluric.general.py` - add second way to get `TELLU_CONV` if not
  defined in outputs. [Neil Cook]
- `Io.drs_fits.py` - add two conditions to find files with fibers `_fiber_`
  or `_fiber`. [Neil Cook]
- `Tools.recipes.spirou.expmeter_spirou.py` - add changes to use
  `inverse.py` code. [njcuk9999]
- `Tools.module.utils.inverse.py` - add `drs_image_shape` function and
  reference full image size from params and make
  `calc_central_localisation` take filename or header. [njcuk9999]
- `Core.instruments.*.default_constants.py` - add in `IMAGE_X_FULL` and
  `IMAGE_Y_FULL` (for reference) [njcuk9999]
- `Core.instruments.default.pseudo_const.py` - add `INDIVIDUAL_FIBERS`
  function. [njcuk9999]
- `Tools.module.utils.inverse.py` - add changes with order profile. [Neil
  Cook]
- Update version/date/documentation/changelog. [Neil Cook]


0.6.062 (2020-03-31)
--------------------
- `Tools.module.utils.inverse.py` - test out making straight image and
  shifting by x and y. [Neil Cook]
- `Core.core.drs_log.py` - correct typo `('DRS_RECIPE_KIND`' is not None)
  --> `(params['DRS_RECIPE_KIND']` is not None) [Neil Cook]
- `Core.core.drs_log.py` - deal with `DRS_DATA_MSG_FULL` set to None. [Neil
  Cook]
- `Core.isntruments.default.default_config.py` - add to `__ALL__` [Neil
  Cook]
- `Core.isntruments.default.default_config.py` - add some constant that
  are set in `drs_setup` (for when we are not using setup) [Neil Cook]
- `Science.calib.general.py` - check that inputs is in params (may not be)
  [Neil Cook]
- `Core.core.drs_recipe.py` - add a quick way to make a recipe (using
  params) [Neil Cook]
- `Tools.recipes.spirou.exposuremeter_spirou.py` and
  `module.utils.inverse.py` - start work on inversing drs (exspoure meter
  etc) [njcuk9999]
- `Core.core.drs_recipe.py` - directory must be an absolute path (if we
  are in the reduced folder it wont be without these changes --> causes
  an error later) [njcuk9999]
- `Core.core.drs_argument.py` - paths for commonpath must be absolute -->
  enforce this explicitly. [njcuk9999]
- `Core.core.drs_argument.py` - add breakpoint to test error. [njcuk9999]
- `Core.core.drs_recipe.py` - `break_point` to test error. [njcuk9999]
- `Core.core.drs_recipe.py` - deal with sys.argv having a full path as
  first argument (don't know why this is happening) [njcuk9999]
- `Core.core.drs_recipe.py` - remove path from recipe name (for argparse)
  [njcuk9999]
- `Science.velocity.general.py` - add EA changes from `new_ccf_code` test.
  [njcuk9999]
- `Misc.problems.new_ccf_code.py` - add EA fixes. [njcuk9999]


0.6.061 (2020-03-29)
--------------------
- `Science.telluric.general.py` - correc typo `KW_FTELLU_TEMP` -->
  `KW_FTELLU_TEMPLATE`. [Neil Cook]


0.6.060 (2020-03-28)
--------------------
- `Misc.problems.new_ccf_code.py` - add comments. [Neil Cook]
- `Misc.problems.new_ccf_code.py` - add better plot for EA. [Neil Cook]
- `Misc/problems/new_ccf_code.py` - correction to stand alone ccf code.
  [njcuk9999]
- `Misc/problems/new_ccf_code.py` - stand alone test of ccf code.
  [njcuk9999]
- `Science.velocity.general.py` - add in the condition that targetrv is
  equal to the null value (-9999.99 for spirou) [njcuk9999]
- Update language database. [njcuk9999]
- `Core.instruments.*.default_constants.py` - add `CCF_OBJRV_NULL_VAL`.
  [njcuk9999]
- `Core.instruments.spirou.default_keywords.py` - correct typo
  `KW_FTELLU_TEMPLATEKW_FTELLU_TEMPLATE` --> `KW_FTELLU_TEMPLATE`.
  [njcuk9999]
- `Recipes.spirou.obj_fit_tellu_spirou.py` and science.telluric.general.py
  - add a keyword for which template was used (or if not set to None)
  [njcuk9999]
- `Core.instruments.*.default_keywords.py` - add `KW_FTELLU_TEMPLATE`.
  [njcuk9999]
- `Core.core.drs_file.py` - change `drs_path()` --> `drs_path.numpy_load()`
  [njcuk9999]
- `Core.core.drs_database.py` + `drs_file.py` `io.drs_path.py`
  `science.telluric.general.py` - replace np.load with `drs_path` function
  (mitigate certain errors?) [njcuk9999]


0.6.059 (2020-03-26)
--------------------
- Update date/version/changelog/documentation. [njcuk9999]
- `Core.core.drs_database.py` - fix typo master in entries --> master in
  entries.colnames. [Neil Cook]
- `Core.core.drs_database.py` - add break point to test database error.
  [njcuk9999]
- `Science.extract.general.py` - correct leakage correction (extimage -->
  `extimage[order_num])` [njcuk9999]
- `Science.velocity.general.py` - add breakpoint to test error.
  [njcuk9999]
- `Science.velocity.general.py` - null value of targetrv is not NaN - if
  so deal with it. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - change `default_ref` of
  ccf to `CCF_NO_RV_VAL`. [njcuk9999]
- `Core.instruments.default.default_constants.py` - add `CCF_NO_RV_VAL` (set
  to np.nan) [njcuk9999]
- Update language database. [njcuk9999]
- `Io.drs_lock.py` - add exceptions and warnings for os.remove and
  os.removedirs (should not crash in lock) [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - change ccf --rv
  default from None to 'None' [njcuk9999]
- `Core.instruments.*.default_config.py` - add `TELLU_DB_MATCH` and
  `DB_MATCH`. [njcuk9999]
- `Core.core.drs_file.py` `locale.core.drs_text.py` and
  `science.telluric.general.py` - allow np.load to have `allow_pickle`.
  [njcuk9999]
- `Core.core.drs_database.py` - add a different db match for telluric and
  calibration database. [njcuk9999]


0.6.058 (2020-03-24)
--------------------
- `Tools.module.setup.drs_processing.py` - correct test for `TEST_RUN`.
  [njcuk9999]
- `Tools.recipes.bin.apero_processing.py` - add breakpoint. [njcuk9999]
- `Tools.recipes.bin.apero_processing.py` - remove breakpoint. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - update leak files in
  sequences (should be e2dsff fiber AB) [njcuk9999]
- `Tools.module.setup.drs_processing.py` - change message when just a
  test. [njcuk9999]
- `Recipes.bin.apero_processing.py` - add breakpoint to test leakage
  error. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - change `cal_leak`
  inputtype e2ds --> reduced. [njcuk9999]
- `Core.core.drs_database.py` - 'master' should only be used for databases
  with 'master' column. [njcuk9999]
- Data.spirou.reset.runs - update run.ini files. [njcuk9999]
- `Tools.module.setup.drs_processing.py` - do not check for master if
  recipe is None. [njcuk9999]
- `Science.velocity.general.py` - add warning to suppress warning about
  NaNs in greater than mask. [njcuk9999]
- `Science.velocity.general.py` - add threshold for the blaze. [Neil Cook]
- Update language database. [njcuk9999]
- `Science.velocity.general.py` - mask `mask_centers` and `mask_weights` to
  just fall in the order in question. [njcuk9999]
- `Core.instruments.*.default_keywords.py` - change WNTDWAVEB -->
  WNTDWAVB. [njcuk9999]
- `Cal_wave_night_spirou.py` - add breakpoint to investigate bug.
  [njcuk9999]
- `Core.instruemnts.spirou.recipe_defintions.py` - `cal_leak` should not be
  a master recipe. [njcuk9999]


0.6.057 (2020-03-24)
--------------------
- Apero.tools.module.setup and `setup/*.py` - add newprofile script to add
  a new profile quickly (copy of currently in use) [njcuk9999]
- `Science.velocity.general.py` - need to set ccf to NaN if mask has no
  values for this order. [njcuk9999]
- Update language database. [njcuk9999]
- `Science.velocity.general.py` - add breakpoint to test error.
  [njcuk9999]
- `Science.velocity.general.py` - add a nansum to `ccf_ord`. [njcuk9999]
- `Science.velocity.general.py` - add a nansum to `ccf_ord`. [njcuk9999]
- `Science.velocity.general.py` - add break point. [njcuk9999]
- `Recipes.spirou.cal_badpix_spirou.py` - remove breakpoint in `cal_badpix`.
  [njcuk9999]
- `Tools.module.setup.drs_processing.py` - correct --master   ==True -->
  True. [njcuk9999]
- `Tools.module.setup.drs_processing.py` - add --master=True. [njcuk9999]
- `Core.core.drs_argument.py` -  --master now has to be True or False.
  [njcuk9999]
- `Core.core.drs_argument.py` - correct wlog type (should be debug)
  [njcuk9999]
- Update language database. [njcuk9999]
- `Core.core.drs_argument.py` - update `_IsMaster` function (no arguments)
  [njcuk9999]
- `Tools.module.setup.drs_processing.py` - change master arg to have no
  arguments. [njcuk9999]
- `Tools.module.setup.drs_processing.py` - add push to add --master arg
  for master recipes. [njcuk9999]
- `Recipes.spirou.cal_badpix_spirou.py` - add break point (to test)
  [njcuk9999]
- Update language database. [njcuk9999]
- `Core.core.drs_startup.py` - add comment for `debug_key`. [njcuk9999]
- `Core.core.drs_recipe.py` - get master from `input_parameters` and update
  `'IS_MASTER`' if True. [njcuk9999]
- `Core.core.drs_database.py` - remove `is_master` from database `get_entry`,
  now modify mask2 (always keep master calibrations) [njcuk9999]
- `Core.core.drs_argument.py` - add `is_master` argument (make any recipe a
  master) [njcuk9999]
- Update language database. [njcuk9999]
- `Data.*.reset.calibdb.master_calib_*.txt` - add master column to default
  master db files. [njcuk9999]
- `Core.instruments.*.default_config.py` - add column to `calib_db_cols`
  (master) [njcuk9999]
- `Core.core.drs_database.py` - add column to calibration database
  (master) and if recipe is master except from "older" [njcuk9999]


0.6.056 (2020-03-22)
--------------------
- `Core.instruments.spirou.file_defintions.py` - save badpix from dark not
  flat. [njcuk9999]
- Update language database. [njcuk9999]
- `Core.core.drs_database.py` - correct error message 00-002-00006.
  [njcuk9999]
- `Core.instruments.*.pseudo_const.py` - add `MASTER_DB_KEYS` function.
  [njcuk9999]
- `Core.drs_database.py` - get master keys from pseudo consts. [njcuk9999]
- `Core.core.drs_startup.py` - add a `IS_MASTER` key to params (True when
  recipe is a master recipe) [njcuk9999]
- `Core.core.drs_database.py` - if database case = 'older' and we have a
  master but no older use closest. [njcuk9999]


0.6.055 (2020-03-22)
--------------------
- `Io.drs_fits.py` - pep8 change. [njcuk9999]
- `Core.instruemnts.*.pseduo_const.py` - BERV outputs should use BERV key
  (make it clear) [njcuk9999]
- `Core.instruments.*.default_keywords.py` - update `KW_MID_OBSTIME_METHOD`
  (more consistent) [njcuk9999]
- `Core.core.drs_recipe.py` - only check required for dtype = file/files.
  [njcuk9999]
- `Core.core.drs_argument.py` - DrsArgument required is True by default
  for args and False by default for kwargs. [njcuk9999]
- `Core.instruments.*.pseudo_const.py` - correct typo need first element
  in list (not the list itself) [njcuk9999]
- `Core.instruments.*.pseudo_const.py` - correct typo `KW_OBNAME` ->
  `KW_OBJNAME`. [njcuk9999]
- .gitignore - ignore all python files in tools. [njcuk9999]
- `Tools.module.setup.drs_processing.py` - fix nightname needed for non-
  trigger run. [njcuk9999]
- Data.spirou.rset.runs - update run.ini files with leakage codes.
  [njcuk9999]
- `Core.instruments.spirou.recipe_defintions.py` - update the sequences
  with leakage codes. [njcuk9999]
- `Data.spirou.reset.calibdb.master_calib_SPIROU.txt` - add default leak
  master files to calibDB (only to use when we don't have any files)
  [njcuk9999]
- Data.spirou.ccf - add new masks from Andres. [njcuk9999]
- Data.reset.calibdb - add `MASTER_LEAK` files. [njcuk9999]
- `Science.velocity.general.py` - deal with unset targetrv (input target
  rv for ccf) - if unset try to get key from header - else set it to
  zero. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - change the default
  value of --rv (for ccf) to None (i.e. unset) [njcuk9999]
- `Core.instruments.spirou.default_constants.py` - change default mask to
  `masque_sept18_andres_trans50.mas`. [njcuk9999]
- `Core.instruments.*.default_config.py` - change `CALIB_DB_MATCH` to
  'older' - no matter where on a night we are it should always use
  calibrations before. [njcuk9999]
- `Core.instruments.*.pseduo_const.py` - add fix for object name having
  spaces (#Issue 598) -- now have key DRSOBJN. [njcuk9999]
- `Core.instruments.*.default_keywords.py` - add OBJECTNAME and change
  OBJNAME to DRSOBJN (new keyword just for drs) [njcuk9999]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.054 (2020-03-10)
--------------------
- `Sciecne.extract.general.py` - continue adding leak functionality. [Neil
  Cook]
- `Apero.science.calib.flat_blaze.py` - allow flat to be loaded quietly.
  [Neil Cook]
- `Recipes.spirou.cal_leak_spirou.py` - continue work on EA implementation
  - add `save_uncorrected_ext_fp` and `write_leak` functions. [Neil Cook]
- `Recipes.spirou.cal_leak_master_spirou.py` - add cprops (for header
  keys) and pipe to `write_leak_master`. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_strings.py` - add module for generic string manipulation [TODO:
  find other generic functions and move here] [Neil Cook]
- `Io.drs_path.py` - add copyfile function (with logging) [Neil Cook]
- `Core.instruments.*.default_keywords.py` - add LEAK header keywords.
  [Neil Cook]
- `Core.instruments.*.file_definitions.py` - add `out_leak_master` to
  `out_file` set and `calib_file` set. [Neil Cook]
- `Core.instruments.*.defalut_constants.py` - add LEAK and `EXT_S1D`
  parameters. [Neil Cook]
- `Core.core.drs_file.py` - add an include/exclude part to wild cards so
  we can search header for specific header keys + add `get_qckeys` method.
  [Neil Cook]


0.6.053 (2020-03-09)
--------------------
- `Recipes.spirou.cal_leak_spirou.py` and `science.extract.general.py` - add
  function `dark_fp_regen_s1d` [Neil Cook]
- `Recipes.*.cal_extract_*.py` - get s1d infile from params
  `(EXT_S1D_INTYPE)` formally hardcoded to E2DSFF. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add `EXT_S1D_INTYPE` to
  constants. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add `EXT_S1D_INTYPE` to
  constants. [Neil Cook]
- `Recipe.spirou.cal_leak_spirou.py` and `science.extract.general.py` - add
  outputs to `extgen.correct_dark_fp` function and make changes to
  function return. [Neil Cook]
- `Documentation.working._static.yed.spirou_all.graphml` - save flow
  diagram for spirou. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - fix call to `_linear_process`
  group should be a keyword argument (Issue #599) [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - update rv keyword OBSRV
  --> OBJRV. [Neil Cook]


0.6.052 (2020-03-05)
--------------------
- `Cal_leak_master_spirou.py` - deal `num_files` = 0. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add `blaze_norm_percentile`
  `(CCF_BLAZE_NORM_PERCENTILE)` [Neil Cook]
- `Science.velocity.general.py` - EA corrections to RV CCF (normalisation)
  [Neil Cook]


0.6.051 (2020-03-04)
--------------------
- `Science.extract.general.py` - add leak functions. [Neil Cook]
- `Apero.recipes.spirou.cal_leak_spirou.py` - continue with EA adaptation.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Core.isntruments.spirou.recipe_definitons.py` - update `cal_leak`. [Neil
  Cook]
- `Core.instruments.spirou.default_constants.py` - comment these out for
  now. [Neil Cook]
- `Core.instruments.nirps_ha.default_keywords.py` [APERO] - add
  `KW_LEAK_CORR`. [Neil Cook]
- `Core.instruments.default.default_keywords.py` - add `KW_LEAK_CORR`
  keyword. [Neil Cook]


0.6.050 (2020-03-03)
--------------------
- `Science.extract.general.py` [APERO] - add `correct_master_dark_fp`
  `correct_dark_fp` `master_dark_fp_cube` `get_extraction_files` functions
  [UNFINISHED] [Neil Cook]
- `Documentation.working._static.yed.spirou_map.graphml` [APERO] - add
  leak to spirou flow diagram. [Neil Cook]
- `Recipe.spirou.obj_mk_tellu_spirou.py` [SPIROU] - correct typo. [Neil
  Cook]
- `Recipes.spirou.cal_leak_spirou.py` - first commit add start of `cal_leak`
  code (from EA code) [Neil Cook]
- `Recipes.spirou.cal_leak_master_spirou.py` - continue work on
  implementing EA's code. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` [APERO] - deal with not having nightname column for
  tmp/reduced index files. [Neil Cook]
- `Core.instruments.*.recipe_definitions.py` - update `cal_leak_master` and
  add `cal_leak`. [Neil Cook]
- `Core.instruments.*.file_definitions.py` [APERO] - set intype for
  `out_leak_master`. [Neil Cook]
- `Core.instruments.*.pseudo_const.py` - add `FIBER_KINDS` (science and
  reference) [Neil Cook]
- `Core.instruments.*.default_constants.py` [APERO] - add LEAKM and LEAK
  constants. [Neil Cook]
- `Core.core.drs_file.py` [APERO] - `read_header_key_1d_list` - update input
  and param dict. [Neil Cook]


0.6.049 (2020-03-02)
--------------------
- `Tools.module.setup.drs_processing.py` [APERO] - move `find_raw_files`,
  `_get_path_and_check`, `_get_files` to `io.drs_fits`. [Neil Cook]
- `Recipes.spirou.cal_leak_master_spirou.py` [APERO] - first commit
  [UNFINISHED] of the master leakage creation recipe. [Neil Cook]
- `Nrips_ha.cal_pp_master_nirps_ha.py` [NIRPS] - add nirps master pp code
  to get `flat_flat` mask. [Neil Cook]
- `Recipes.*` and `tools.*` - correct call to `drs_fits.find_files` (now
  requires recipe for raw finding) [Neil Cook]
- `Io.drs_fits.py` [APERO] - update `find_files` to correctly find raw
  files, add `find_raw_files` function, move `fix_header` to here. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Core.instruments.nirps_ha.file_definitions.py` [NIRPS] - replace fiber
  AB,A,B,C with A,B. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` [SPIROU] - add
  `out_leak_master`. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - add
  `ALLOWED_LEAKM_TYPES`. [Neil Cook]
- `Core.instruments.*.recipe_definitions.py` [APERO] - move DrsRecipe
  construction closer to each recipe + add to recipe list + add
  `cal_leak_master` + add `cal_pp_master`. [Neil Cook]
- `Core.instruments.*.pseudo_const.py` [APERO] - add `VALID_RAW_FILES` to
  instruments seperately. [Neil Cook]
- `Core.instruments.nirps_ha.file_definitions.py` [NIRPS] - add
  `out_pp_master` file for the mask master flat pp file + add
  `out_leak_master` for `leak_master` code + remove polar file definitions.
  [Neil Cook]
- `Core.instruments.nirps_ha.default_keywords.py` - add a `PPMSTR_NSIG`
  keyword to keep track when it is used. [Neil Cook]
- `Core.instruments.nirps_ha.default_constants.py` - add `ALLOWED_PPM_TYPES`
  `PPM_MASK_NSIG` `PP_MEDAMP_BINSIZE` and `ALLOWED_LEAKM_TYPES`. [Neil Cook]
- `Default.default_keywords.py` [NIRPS] - add `PPMSTR_NSIG` constants (for
  nirps pp correction) [Neil Cook]
- `Core.instruments.default.default_constants.py` - add PPM and LEAKM
  keywords. [Neil Cook]
- `Core.core.drs_startup.py` - deal with case in `find_files` where we do
  not have full params set up yet (i.e. WLOG will crash) --> raise
  ConfigError. [Neil Cook]
- `Core.core.drs_recipe.py` - when we have a master recipe set directory
  from `params['MASTER_NIGHT']` [Neil Cook]
- Update changelog/date/version/documentation. [Neil Cook]
- Update changelog/date/version/documentation. [Neil Cook]


0.6.048 (2020-02-28)
--------------------
- Documentation.working.user.general.todo.rst - update todo list. [Neil
  Cook]
- `Tools.recipes.spirou.exposuremeter_spirou.py` - first commit of
  exposure meter code [UNFINISHED] [Neil Cook]
- Tools.recipes.spirou - move `cal_update_berv.py` to tools. [Neil Cook]
- `Io.drs_fits.py` - add "night" to `find_files` (to filter just one night)
  [Neil Cook]
- Update language database. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - correct `NIGHT_NAME` -->
  NIGHTNAME and cause exception when TRIGGER=True and NIGHTNAME unset.
  [Neil Cook]
- Update run.ini files `(NIGHT_NAME` --> NIGHTNAME) [Neil Cook]
- `Tools.module.setup.drs_processing.py` - update how filters are obtained
  and add error when incorrect. [Neil Cook]
- Update language database. [Neil Cook]
- `Data.spirou.reset.runs.trigger_night_calbi_run.ini` - correct run and
  skip pp parameters. [Neil Cook]
- Readme.md - update sequences. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `pp_run_opt`
  (preprocessing with options -- must turn all off to only select one)
  [Neil Cook]
- `Data.spirou.reset.runs.trigger*.ini` - add pp seqeunce elements. [Neil
  Cook]
- `Tools.module.setup.drs_processing.py` - add trigger from file. [Neil
  Cook]
- `Core.instruments.spirou.recipe_defintions.py` - add `pp_run_sci` sequence
  (preprocess `OBJ_DARK`, `OBJ_FP` only) [Neil Cook]
- Update run.ini files. [Neil Cook]
- `Core.core.drs_recipe.py` - deal with having no files in a recipe that
  requires files. [Neil Cook]
- Update language database. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add section to stop processing
  recipes when we are in trigger mode. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - `update_run_table` needs to take
  value from rlist if already populated. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - deal with trigger run when
  removing engineering nights (i.e. deal with when we have no objects in
  a directory) [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.default.recipe_defintions.py` - update dtype for
  --trigger argument. [Neil Cook]
- Update language database. [Neil Cook]
- Documentation.working.user.general.todo.rst - update todo list. [Neil
  Cook]
- `Core.instruments.default.recipe_defintions.py` - add --trigger option
  to `apero_processing.py`. [Neil Cook]
- `Drs_installation.py` -- check "clean" argument for update. [Neil Cook]
- `Setup.install.py` - pass args to update. [Neil Cook]
- `Setup.install.py` - print that we are locating install path. [Neil
  Cook]
- `Tools.module.setup.drs_reset.py` -- do not remove head when removing
  paths in clean install. [Neil Cook]
- `Io.drs_lock.py` - add checks in `__remove_empty__` for symbolic links.
  [Neil Cook]
- `Core.constants.param_functions.py` - add check for stty for posix os.
  [Neil Cook]
- Update requirements (in .txt and install.py) [Neil Cook]
- Update version/date/changelog/documentation. [Neil Cook]


0.6.047 (2020-02-27)
--------------------
- `Documentation.working.dev.developer_guide.rst` [APERO] - add another
  section todo. [Neil Cook]
- `Science.extract.general.py` [APERO] - pep8 change. [Neil Cook]
- Documentation.working.user.genearl.todo.rst - update todo list. [Neil
  Cook]
- `Tools.recipe.bin.apero_go.py` [APERO] - a program to aid finding where
  data directories are (try cd <quote>python `apero_go.py` INSTRUMENT
  --data<quote> to change to data dir. [Neil Cook]
- `Recipes.spirou.cal_wave_*` - change how we update hc and fp files once
  wave solution is updated (correct e2ds/e2dsff/e2dsll and remake
  s1dw/s1dv) [Neil Cook]
- `Io.drs_lock.py` - make all lock normal print outs debug print outs
  (hide unless in debug mode) [Neil Cook]
- `Data.spirou.reset.runs.hc_run.ini` - update run/skip section. [Neil
  Cook]
- `Data.spirou.reset.runs.*.ini` - update `RUN_INI_FILES` (more appropriate
  names + updated values) [Neil Cook]
- `Core.instruments.*.recipe_defintions.py` - add wave plot `(extract_s1d)`
  [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` [APERO] - add
  `apero_go.py` tools recipe. [Neil Cook]
- README.md - add short name to sequence description. [Neil Cook]


0.6.046 (2020-02-27)
--------------------
- `Tools.recipe.bin.apero_processing.py` - add a save stats call to save
  to stats file. [Neil Cook]
- `Tools.module.setup.drs_processing.py` [APERO] - save a stats fits and
  stats txt to run folder (under stats) [Neil Cook]
- `Tools.module.setup.drs_installation.py` - fix force resets without
  warning. [Neil Cook]
- Update language database. [Neil Cook]


0.6.045 (2020-02-26)
--------------------
- `Tools.module.setup.drs_installation.py` - deal with tool sub-dirs not
  existing (first time install) [Neil Cook]
- `../setup/install.py` - search up levels for apero. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - correct `in_tool_path` (how we
  add bin sub-dir) [Neil Cook]
- `Tools.module.setup.drs_installation.py` - correct `valid_path` for
  validation recipe. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - make tool links generic
  (based on sub-dirs) + make paths os independent. [Neil Cook]
- `Apero.tools.resources.setup.*` - update paths to add multiple sub-
  paths. [Neil Cook]
- Apero.tools.recipes - move general --> bin and add instrument tool
  directories. [Neil Cook]


0.6.044 (2020-02-24)
--------------------
- `Science.preprocessing.detector.py` [NIRPS] - add nirps preprocessing
  functions from EA [UNFINISHED + QUESTIONS] [Neil Cook]
- `Misc.nrips_tools.nirps_pp.py` - copy over EA preprocessing code. [Neil
  Cook]
- `Recipes.nirps_ha.cal_preprocess_nirps_ha.py` [NIRPS] - copy over SPIROU
  code and implement EA changes [UNFINISHED] [Neil Cook]
- `Core.math.general.py` [APERO] - add medbin function. [Neil Cook]
- `Core.core.drs_startup.py` - allow llmain to be dict or None (via Union)
  [Neil Cook]


0.6.043 (2020-02-22)
--------------------
- Update documentation. [Neil Cook]
- Working.user.genearl.todo.rst - update todo list. [Neil Cook]
- `Misc.tools.apero_mtl_sync.py` - finish off code (formally `mtl_sync.py)`
  [Neil Cook]


0.6.042 (2020-02-20)
--------------------
- Working.user.general.todo.rst [APERO] - update todo list. [Neil Cook]
- `Core.math.general.py` [APERO] - pep8 change to robust nan std function.
  [Neil Cook]
- `Data.nirps_ha.reset.calibdb.MASTER_WAVE_NIRPS_HA.fits` - add a first
  attempt at wave solution for `NIRPS_HA` from optical model. [Neil Cook]
- `Science.extract.general.py` [NIRPS] - NIRPS does not have thermal make
  these keys added to header conditional on presence in eprops. [Neil
  Cook]
- `Science.calib.flat_blaze.py` [NIRPS/SPIROU] - change keep, rms and nan
  some outliers in flat. [Neil Cook]
- `Recipes.nirps_ha.cal_shape_nirps_ha.py` [NIRPS] - convert `cal_shape`
  from spirou code. [Neil Cook]
- `Recipes.nirps_ha.cal_shape_master_nirps_ha.py` [NIRPS] - remove hc and
  dxmap stuff from spirou code. [Neil Cook]
- `Recipes.nirps_ha.cal_flat_nirps.py` [NIRPS] - add flat/blaze code
  (converted from spirou) [Neil Cook]
- `Recipes.nirps_ha.cal_extract_nirps_ha.py` [NIRPS] - add extraction code
  (converted from spirou) [Neil Cook]
- Update database. [Neil Cook]
- `Core.math.general.py` - add `robust_nanstd` function. [Neil Cook]
- `Core.instruments.spirou.recipe_defintions.py` - update shape master
  help example. [Neil Cook]
- `Core.instruments.nirps_ha.recipe_defintions.py` - remove hc
  inputs/outputs from shape master. [Neil Cook]
- `Core.instruments.nirps_ha.pseudo_const.py` [NIRPS] - update
  `FIBER_LOC_COEFF_EXT`. [Neil Cook]
- `Core.instruments.nirps_ha.default_constants.py` [NIRPS] - change
  `SHAPE_UNIQUE_FIBERS`, `QC_FF_MAX_RMS`, `EXT_RANGE1`, `EXT_RANGE2`,
  `EXT_S1D_WAVEEND`, `EXTRACT_S1D_PLOT_ZOOM1`, `EXTRACT_S1D_PLOT_ZOOM2`. [Neil
  Cook]
- `Misc.tools.mtl_sync.py` - remove requirement of using apero. [Neil
  Cook]


0.6.041 (2020-02-20)
--------------------
- `Misc.tools.mtl_sync.py` - first commit (code for users to get data from
  montreal) [Neil Cook]
- Remove unused doc files. [Neil Cook]
- Update documentation. [Neil Cook]
- `Tools.module.documentation.drs_documentation.py` - replace `copy_tree`
  --> copytree (from `drs_path)` [Neil Cook]
- `Io.drs_path.py` [APERO] - add copytree function (copies all files from
  src to dst) [Neil Cook]
- `Apero.science.calib.shape.py` - remove private functions in shape.
  [Neil Cook]
- `Recipes.nirps_ha.cal_shape_master_nirps_ha.py` - copy over code from
  spirou. [Neil Cook]
- `Plotting.plot_functions.py` [APERO] - update loc plot and shape plot.
  [Neil Cook]
- `Data.*.reset` [APERO] - update master wave solutions (distinguish
  spirou and `nirps_ha)` [Neil Cook]
- `Core.instruments.*.file_defintions.py` [APERO] - correct `out_dark` files
  (suffix needs underscore) [Neil Cook]
- `Core.instruments.*.default_constants.py` [NIRPS] - update loc constants
  + update comment for `LOC_COLUMN_SEP_FITTING`. [Neil Cook]


0.6.040 (2020-02-18)
--------------------
- `Apero.science.calib.badpix.py` and `localisation.py` [APERO] -
  `RAW_TO_PP_ROTATION` and pep8 changes. [Neil Cook]
- `Recipes.spirou.cal_preprocess_spirou.py` [SPIROU] - update header key
  `KW_BERV_OBSTIME_METHOD` --> `KW_MID_OBSTIME_METHOD`. [Neil Cook]
- `Recipes.nirps_ha.*.py` [NIRPS] - add `cal_badpix`, `cal_dark_master`,
  `cal_loc` for `nirps_ha`. [Neil Cook]
- `Io.drs_image.py` [APERO] - link `rotate_image` function to
  math.genearl.rot8. [Neil Cook]
- `Io.drs_data.py` [APERO] - fix arguments to error 00-012-00001. [Neil
  Cook]
- Update documentation. [Neil Cook]
- Update documentation. [Neil Cook]
- `Data.nirps_ha` [NIRPS] - rename data folder from nirps --> `nirps_ha`.
  [Neil Cook]
- `Apero.core.math.general.py` [APERO] - add rot8 function to deal with
  rotation modes of images. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - add `RAW_TO_PP_ROTATION`
  value. [Neil Cook]
- `Core.instruments.nirps_ha.default_constants.py` - tweak NIRPS values
  from SPIROU values. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` [APERO] - get
  instruments from Constants. [Neil Cook]
- `Core.instruments.default.default_constants.py` [APERO] - add
  `RAW_TO_PP_ROTATION` constant. [Neil Cook]


0.6.039 (2020-02-17)
--------------------
- `Documentaqtion/working/dev/developer_guide.rst` [APERO] - add github
  interface as section. [Neil Cook]
- `Core.instruments.nirps_ha.recipe_definitions.py` - change spirou
  references to `nirps_ha`. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` [SPIROU] - rename
  internal instance names `obj_pol_spirou` and `obj_spec_spirou` --> `obj_pol`
  and `obj_spec`. [Neil Cook]
- `Documentation.working._static.yed.spirou_map_2020-01-22_all.graph`
  [SPIROU] - update yed graph. [Neil Cook]
- `Recipes.nirps_ha.cal_dark_nirps_ha.py` - copy over spirou recipe. [Neil
  Cook]
- Update the language database [APERO] add nirps files as duplicates of
  spirou for start. [Neil Cook]
- `Core.instruments.nirps_ha.pseudo_const.py` [NIRPS] - update splash from
  spirou --> nirps. [Neil Cook]
- `Core.instruments.deafult.default_config.py` [NIRPS] - add `NIRPS_HA` to
  list of instruments. [Neil Cook]
- `Tools.module.setup.drs_installation.py` [APERO] - force userconfig to
  have a os.sep as last character. [Neil Cook]
- NIRPS: start config file copy. [Neil Cook]


0.6.038 (2020-02-10)
--------------------
- `Tools.recipes.general.apero_log_stats.py` - remove hard coded path.
  [Neil Cook]
- Printout of the `limited_run.ini` on `mini_data` for `apero_processing.py`
  2020-02-10 13:56:00. [Neil Cook]
- Update yed graphs. [Neil Cook]
- Update yed graphs. [Neil Cook]
- Update changelog. [Neil Cook]
- Update python versions, yed graphs and update notes. [Neil Cook]
- Update `readme/known_issues/todo`. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.037 (2020-02-07)
--------------------
- `Core.core.drs_recipe.py` - add a pre-filter of table (so we are not
  scanning all files every time) [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - filelogic must be
  exclusive for `mk_tellu`, `fit_tellu` and `pol_spirou` + update sequences
  (only e2dsff not e2ds) [Neil Cook]
- Documentation - add yed graphs. [Neil Cook]
- Documentation.working - update python installation, code links. [Neil
  Cook]
- Documentation.output - update docs. [Neil Cook]
- `Tools.module.drs_documentation.py` - update ssh host. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.036 (2020-02-05)
--------------------
- `Plotting.latex.py` - must clean characters [ and ] - leads to error in
  pdflatex. [Neil Cook]
- `Science.calib.wave.py` + `science.calib.wave1.py` - update master wave to
  look for all master wave types and generate new error if none found.
  [Neil Cook]
- `Recipe.spirou.obj_mk_tellu_spirou.py` + `obj_fit_tellu_spirou.py` -
  update headers to use correct wave solutions for outputs. [Neil Cook]
- `Plotting.core.py` - add numpy import. [Neil Cook]
- Update language database. [Neil Cook]
- `Recipe.spirou.obj_mk_template_spirou.py` and
  `science.telluric.general.py` - update wave solution of template. [Neil
  Cook]
- `Recipes.test.demo_spirou.py` - add param dict section. [Neil Cook]
- `Spirou.recipe_definitions.py` - add `old_run` (with no master/night wave)
  [Neil Cook]


0.6.035 (2020-02-04)
--------------------
- Update the language database. [Neil Cook]
- `Tools.module.testing.drs_dev.py` - add a demo class to store demo
  functions (keep out of demo as they would just confuse the point)
  [Neil Cook]
- `Recipes.test.demo_spirou.py` - add a recipe that demonstrates the
  different features of APERO. [Neil Cook]
- `Locale.core.drs_text.py` - add a language level in cache data so we are
  name.instrument.language cache. [Neil Cook]
- `Locale.core.drs_lang_db.py` - move dictionary to static call (once per
  import) -- loads quicker. [Neil Cook]
- Data.spirou.demo - add demo data. [Neil Cook]
- `Core.core.drs_log.py` - correct the language must be a string not a
  list. [Neil Cook]
- `Testing.drs_dev.py` - add module to allow recipe definition to come
  from recipe (used to add rmod to core.setup) [Neil Cook]
- `Science.extract.berv.py` - `use_pyasl` in quiet mode in barycorrpy (just
  for calculating bervmax) [Neil Cook]
- `Science.extract.berv.py` - allow berv to be calculated quietly. [Neil
  Cook]
- `Core.core.drs_startup.py` - allow recipe definition to come from input
  (i.e. define in recipe - for initial testing) [Neil Cook]
- Add new blank codes with recipe definition inline. [Neil Cook]
- Remove from `__future__` import division imports (no longer supporting
  python 2) [Neil Cook]
- `Misc.tools.cal_update_berv.py` - add switch for skipping. [Neil Cook]
- `Apero.science.extract.berv.py` - use pyasl to measure berv maximum.
  [Neil Cook]
- `Misc.tools.cal_update_berv.py` - update `.write-->.write_file`. [Neil
  Cook]
- `Recipes.spirou.cal_wave_master_spirou` + `cal_wave_night_spirou` - add
  TODOs to update s1d files AFTER new wave solution generated. [Neil
  Cook]
- `Apero.plotting.plot_functions.py` - deal with all NaNs in flux[mask] -
  only set ylim if values are finite. [Neil Cook]
- `Apero.plotting.core.py` - add a `set_interactive` method to try to change
  backend. [Neil Cook]


0.6.034 (2020-02-03)
--------------------
- `Documentation.working.dev.developer_guide.rst` - add more sections to
  dev section [UNFILLED] [Neil Cook]
- Update language databases. [Neil Cook]
- `Core.core.drs_file.py` - change `get_keyword_instance` --> `get_instanceof`
  (more generic) [Neil Cook]
- `Core.constants.param_functions.py` - write all doc strings [UNFINISHED]
  up to end of ParamDict. [Neil Cook]
- `Core.constants.constant_functions.py` - fill out all doc-strings. [Neil
  Cook]
- `Core.cosntants.__init__.py` - add comment to `catch_sigint`. [Neil Cook]
- README.md - add changes to sequences (now doing `cal_wave_master)` [Neil
  Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.033 (2020-01-31)
--------------------
- Add flow diagram for locking wait times. [Neil Cook]
- `Plotting.latex.py` - add switch to turn on/off latex pdf making + add
  fix to latex command to make it non-interactive (Issue #586) [Neil
  Cook]
- `Plotting.latex.py` - add -interaction=nonstopmode to not allow latex
  to pause running on error. [Neil Cook]
- `Core.core.drs_recipe.py` - remove breakpoint. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - deal with unset event (non-
  parallel process) [Neil Cook]
- `Core.core.drs_argument.py` - make sure reicpe is updated before we run
  `display_func`. [Neil Cook]
- `Core.instruments.default.default_config.py` - update the value of debug
  mode (only print at debug>=10) [Neil Cook]
- `Core.constants.constants_functions.py` - update types in doc string.
  [Neil Cook]
- `Core.core.drs_recipe.py` - move `break_point` to exception. [Neil Cook]
- `Core.core.drs_recipe.py` - add breakpoint to address error. [Neil Cook]
- `Core.core.drs_recipe.py` - add breakpoint to address error. [Neil Cook]
- `Constants.constant_functions.py` - add doc strings. [Neil Cook]
- `Core.core.drs_file.py` - add `display_funcs` and pep8 changes. [Neil
  Cook]


0.6.032 (2020-01-30)
--------------------
- `Dark_fp_run.ini` - add dark fp run script. [Neil Cook]
- `Core.instruments.spirou.recipe_defintions.py` - add `pp_run` and
  `dark_fp_run` sequences. [Neil Cook]
- `Io.drs_lock.py` - make sure we do not remove lock path
  `(drs_msg_path/lock/)` [Neil Cook]


0.6.031 (2020-01-29)
--------------------
- `Core.core.drs_file.py` - update `display_func` for `hkeys_exist`. [Neil
  Cook]
- `Core.core.drs_argument.py` - add comments to special arg make functions
  + display func to DrsArgument. [Neil Cook]
- `Core.core.drs_argument.py` - add display func + pep8 corrections. [Neil
  Cook]
- `Core.core.drs_recipe.py` - change DRSArgumentParser -->
  DrsArgumentParser. [Neil Cook]
- `Core.core.drs_argument.py` - add `display_funcs` and comments for Parser
  functions. [Neil Cook]
- `Misc.updates_to_drs.mk_night_wave.py` - add dymanic paths to EA code.
  [Neil Cook]
- `Science.extract.telluric.general.py` - change read --> readfits. [Neil
  Cook]
- `Science.extract.general.py` - change read --> `read_file`. [Neil Cook]
- `Science.calib.background.py` + `badpix.py` + `dark.py` - change read -->
  readfits. [Neil Cook]
- `Recipe.spirou.cal_wave_night_spirou.py` - pep8 changes. [Neil Cook]
- `Locale.core.drs_exceptions.py` - add `__main__` section. [Neil Cook]
- `Io.drs_fits.py` - change read --> readfits. [Neil Cook]
- `Drs_data.py` - change read --> readfits. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add force extract
  options. [Neil Cook]
- `Locale.core.drs_lang_db.py` - move constant/params text to dict (linked
  to language database) [Neil Cook]
- `Core.core.drs_file.py` - change read --> read file. [Neil Cook]
- `Core.core.drs_database.py` - change read to readfits (and
  `read_database)` [Neil Cook]
- `Core.constant.param_functions.py` - add `display_func` and comments.
  [Neil Cook]
- `Core.constants.constant_function.py` - add comments and display func.
  [Neil Cook]
- Update language database. [Neil Cook]


0.6.030 (2020-01-28)
--------------------
- `Plotting.plot_functions.py` - pep8 clean up. [Neil Cook]
- `Science.calib.wave1.py` - add hclines and fplines arguments to
  `get_master_lines` (to get lists from file) and for reference file use
  these arguments to start with the master. [Neil Cook]
- `Plotting.plot_functions.py` - copy x and y in wave night plot function
  and catch nan in greater than less than with the "with warnings"
  command. [Neil Cook]
- Add `display_func`. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.029 (2020-01-27)
--------------------
- `Data.spirou.reset.runs.limited_run.ini` - update default
  `limited_run.ini`. [Neil Cook]
- Update spirou flow map. [Neil Cook]
- `Recipes.spirou.cal_wave_night_spirou.py` - remove breakpoint. [Neil
  Cook]
- `Locale.core.drs_exception.py` - add wlogbasic (basicalogger wrapper
  with same args as WLOG) [Neil Cook]
- DrsFitsFile.read --> `read_file`. [Neil Cook]
- `Core.core.drs_log.py` - move `display_func` main to `param_functions` -
  keep here the use of wlog and textentry (too low in `param_functions)`
  [Neil Cook]
- `Core.core.drs_file.py` - add `display_funcs` and change `read-->read_file`.
  [Neil Cook]
- `Core.core.drs_database.py` - add display funcs. [Neil Cook]
- `Core.core.drs_argument.py` - update `func_name` comments - no access to
  inputs cannot breakfunc here. [Neil Cook]
- `Core.constants.constant_functions.py` - add messages to show `func_name`
  breakfunc can't work here (too low) [Neil Cook]
- `Recipes.spirou.cal_wave_night_spirou.py` - correct typo set -->
  `set_sources`. [Neil Cook]
- `Recipes.spirou.cal_wave_night_spirou.py` - add rv properties to nprops.
  [Neil Cook]
- `Science.calib.wave1.py` - add wavefile, wavesource, nbo, deg to nprops.
  [Neil Cook]
- `Core.core.drs_startup.py` - breakpoint --> `break_point`. [Neil Cook]
- `Core.constants.__init__.py` - breakpoint --> `break_point`. [Neil Cook]
- `Core.constants.param_functions.py` - rename breakpoint --> `break_point`.
  [Neil Cook]
- `Recipes.spirou.cal_wave_night_spirou.py` - add breakpoint to check
  errors. [Neil Cook]
- `Recipes.spirou.cal_wave_night_spirou.py` - replace hcfile and fpfile
  for `hc_e2ds_file` and `fp_e2ds_file`. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - key `WAVE_NIGHT_WAVE`
  --> `WAVEMAP_NIGHT`. [Neil Cook]
- `Spirou_map` -- update flow chart. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add shape to master
  sequence. [Neil Cook]
- `Spirou_map` -- update flow chart. [Neil Cook]
- `Recipe.spirou.cal_shape_master_spirou.py` - add way to load fpmaster
  from file/calibDB -- FOR DEBUG ONLY. [Neil Cook]


0.6.028 (2020-01-24)
--------------------
- `Science.calib.shape.py` - EA changes to shape (remove `corr_dx_from_fp)`
  [Neil Cook]
- Add new spirou flow maps. [Neil Cook]
- `Recipe.spirou.cal_shape_master_spirou.py` - add breakpoint for
  debugging. [Neil Cook]
- `Plotting.plot_functions.py` - change `corr_dx_from_fp_arr` to shifts.
  [Neil Cook]
- Language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add changes for wave
  master/night. [Neil Cook]
- `Misc.tools.compare_e2ds.py` - add code to compare used calibrations
  between two e2ds files. [Neil Cook]
- Update spirou flow graph maps. [Neil Cook]


0.6.027 (2020-01-23)
--------------------
- `Science.calib.wave1.py` - corrections after EA changes. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add rv plots to
  `cal_Wave_night` definition. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - adjust `WAVE_LITTROW_QC`
  values. [Neil Cook]


0.6.026 (2020-01-22)
--------------------
- `Science.calib.wave1.py` - disable the littrow QC (still breaking) [Neil
  Cook]
- `Recipe.spirou.cal_wave_master_spirou.py` + `science.calib.wave1.py` -
  continue work on EA fixes. [Neil Cook]
- `Plotting.plot_functions.py` - remove line and add markers to wave night
  plot. [Neil Cook]
- `Core.math.general.py` - deal with median = 0 (over half the points are
  zero) [Neil Cook]
- `Core.instruments.*.default_constants.py` +
  `core.instruments.spirou.recipe_defintions.py` - add
  `PLOT_WAVENIGHT_HISTPLOT`. [Neil Cook]
- `Documentation.working._static.yed` - add yed diagrams. [Neil Cook]


0.6.025 (2020-01-21)
--------------------
- `Misc.tools.nirps_lsf.py` - EA tool to get the line spread function for
  NIRPS. [Neil Cook]
- `Recipes.spirou.cal_wave_master_spirou.py`, `cal_wave_night_spirou.py` and
  `science.calib.wave1.py` - continue work on EA changes to wave solution
  master/night combo. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - correct `cal_wave_night`
  outputs and plots. [Neil Cook]
- `Core.instruments.spirou.file_defintions.py` - correct typo in
  `out_wavem_fp` `WAVE_FP` --> `WAVEM_FP`. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - update
  `WAVE_HC_TFIT_ORDER_FIT_CONT`. [Neil Cook]
- `Core.core.drs_file.py` - added exclude groups to `copy_original_keys`.
  [Neil Cook]


0.6.024 (2020-01-20)
--------------------
- `Recipes/spirou.cal_wave_*.py` + `science.calib.wave*.py` - continue work
  on implementing EA changes. [Neil Cook]
- `Science.telluric.general.py` - remove breakpoint. [Neil Cook]
- `Science.extract.general.py` - correct `add_wave_keys`. [Neil Cook]
- `Plotting.plot_functions.py` - correct where we get nbo + add title.
  [Neil Cook]
- Update language database. [Neil Cook]
- Data.core..pdbrc - add alias commands to pdbrc for ease of use. [Neil
  Cook]
- `Core.instruments.spirou.default_constants.py` - change wave fit degree
  from 4 --> 5 (EA: 4th order does not catch structure) [Neil Cook]
- `Core.core.drs_startup.py` - add DebugExit class to catch pdb/ipdb
  exits. [Neil Cook]
- `Core.core.drs_recipe.py` - add `make_breakfunc` (special argument) [Neil
  Cook]
- `Core.core.drs_log.py` - allow `display_func` to have break at function
  name (if --breakfunc used) [Neil Cook]
- `Core.core.drs_database.py` - fix display func. [Neil Cook]
- `Core.constants.param_functions.py` - fix breakpoint to have levels (set
  by .pdbrc) [Neil Cook]
- `Core.core.drs_argument.py` - add break function special argument. [Neil
  Cook]


0.6.023 (2020-01-17)
--------------------
- `Io.drs_lock.py` - add some randomisation to the 240 reset. [Neil Cook]
- `Io.drs_lock.py` - reset the lock file after 240 seconds (can help with
  stuck lock files) [Neil Cook]
- `Science.extract.berv.py` - must define iteration for using
  `use_barycorrpy` (due to locking -- both iterations will use same lock
  files) [Neil Cook]
- `Recipes/spirou.cal_wave_master_spirou.py` + `science.calib.wave1.py` -
  make changes for `cal_wave_master` (UNFINISHED) [Neil Cook]
- `Science.calib.shape.py` - fix `poly_cavity` (should be un-inverted) [Neil
  Cook]
- `Io.drs_lock.py` - need to re-check that path exists when creating lock
  file. [Neil Cook]
- Misc nirps directory. [Neil Cook]


0.6.022 (2020-01-16)
--------------------
- `Setup.install.py` and pythoninstallion.rst - update recommended way to
  install python and modules. [Neil Cook]
- `Setup/install.py` - add comments on how installed (after installing
  conda) [Neil Cook]
- `Reipces.spirou.cal_wave_master_spirou.py` - add `cavity_poly` for FP
  master lines (always use the most up-to-date version) [Neil Cook]
- `Science.calib.wave.py` - move master line const to const file, move
  location of cavity file, add valid line print out to `get_master_lines`,
  add `fp_fit` paramets to llprops. [Neil Cook]
- `Science.calib.shape.py` - replace getting cavity file from old to new
  location (made in wave solution) [Neil Cook]
- `Recipe.spirou.cal_wave_master_spirou.py` - make note that we need to
  decide when/how to update cavity file. [Neil Cook]
- `Io.drs_data.py` - remove cavity file loading. [Neil Cook]
- Data.spirou.calib - update cavity files. [Neil Cook]
- `Core.instruments.*.deafult_constants.py` - remove cavity length
  constants. [Neil Cook]
- `Cal_wave_master_spirou.py` - fix inputs to `get_master_lines`. [Neil
  Cook]
- `Plotting.plot_functions.py` - fix waveref plot (for `get_master_lines)`
  [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - fix pep8 + change
  `hclist_master` nad `fplist_master` to `drs_finput`. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add WAVEREF constants. [Neil
  Cook]


0.6.021 (2020-01-15)
--------------------
- `Science.calib.wave.py` - correct typos. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - change `WAVEM_HCLL` -->
  `WAVE_HCLL`. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - remove WAVEHCLL master
  (redundant) [Neil Cook]
- `Scuebce.telluric.general.py` - add lower and upper bounds for hband
  coming from constants. [Neil Cook]
- `Plotting.plot_functions.py` - add better comments and fix pep8. [Neil
  Cook]
- `Core.instruments.*.default_constants.py` - add `MKTELLU_HBAND_LOWER` and
  `MKTELLU_HBAND_UPPER` and change `MKTELLU_QC_AIRMASS_DIFF` from 0.1 -->
  0.3. [Neil Cook]
- `Plotting.plot_functions.py` - change style on plot point. [Neil Cook]
- `Science.telluric.general.py` - only use `good_domain` for the absorption
  fit. [Neil Cook]
- `Science.telluric.general.py` - test of `good_domain` (1500 to 1750 nm)
  [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` +
  `science.telluric.general.py` - add `--use_template`. [Neil Cook]
- `Plotting.plot_functions.py` - normalise for plotting. [Neil Cook]
- `Plotting.plot_functions.py` - correct measured transmission for
  plotting. [Neil Cook]
- `Plotting.plot_function.py` + `science.telluric.general.py` - correct
  plotting when having a template. [Neil Cook]
- `Science.telluric.general.py` - add breakpoint. [Neil Cook]
- `Core.core.drs_log.py` - fix typo lists should be appended for qc values
  + add master log analysier (add to `apero_log_stats` later?) [Neil Cook]
- `Recipes.spirou.obj_mk_template_spirou.py` - fix qc params when skipping
  object (must be lists) [Neil Cook]


0.6.020 (2020-01-14)
--------------------
- `Core.core.drs_log.py` - make log more readable + add qc  columns. [Neil
  Cook]


0.6.019 (2020-01-13)
--------------------
- Update `master_tellu_SPIROU.txt`. [Neil Cook]
- Update documentation. [Neil Cook]
- Update version/date/changelog/documentation. [Neil Cook]


0.6.018 (2020-01-10)
--------------------
- `Recipes.spirou.obj_mk_template_spirou.py` - add logging for when file
  is skipped (and qc passes) [Neil Cook]
- `Recipe.dev.apero_changelog.py` and
  `module.documentation.drs_changelog.py` - need to format changelog so it
  works as .rst file (for documentation) [Neil Cook]
- Update documentation. [Neil Cook]
- `Tools.module.documentation.drs_documentation.py` - make sure we copy
  the contents of output folder not the folder itself. [Neil Cook]
- `Tools.recipes.dev.apero_documentation.py` - add update option to making
  documentation (for updating doc website) [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - make sure path is in nights
  list + sort by htime. [Neil Cook]
- `Tools.resources.setup.apero.bash.setup*` - correct typo -- missing
  speech mark. [Neil Cook]
- `Science.calib.wave.py` - seperate master and old wave writing functions
  + add in night qc and write functions. [Neil Cook]
- `Cal_wave_night_spirou.py` - add in ccf computation. [Neil Cook]
- `Cal_wave_master_spirou.py` - change writing functions to master
  functions (to separate from `cal_wave` -- old) - master now writes to
  key WAVEM. [Neil Cook]
- Update the `master_*_SPIROU.txt` files - default master files now
  `WAVEM_D_{fiber}` [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - need a set of files
  for master (can remove non-master if we go with master/night recipes)
  [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - need a set of files for
  master (can remove non-master if we go with master/night recipes)
  [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - group all wave header
  keys. [Neil Cook]
- `Core.core.drs_startup.py` - add argument 'required' to
  `get_file_definition` to allow not finding a key and return None if this
  is the case. [Neil Cook]
- `Core.core.drs_log.py` - add pipes to the end of each qc to ease
  splitting in log analysis. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.calib.wave.py` - move logs to language database. [Neil Cook]
- `Setup.install.py` - remove blank spaces. [Neil Cook]
- Update date/version/changelog/documentation. [Neil Cook]


0.6.017 (2020-01-08)
--------------------
- `Setup.install.py` - add dev section to modules (sphinx, ipdb,
  gitchangelog) [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - change dtype to
  'bool' [Neil Cook]
- `Tools.recipe.general.apero_log_stats.py` - allow saving of all the log
  files to one file. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - update recipe print outs.
  [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - correct error/warn sample.
  [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - correct typo. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - keep all error/warning
  messages and use error/warn samples to keep just one for each code.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Tools.module.testing.drs_log.stats.py` - add separations between
  warnings/errors. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - add print out of unique
  errors/warnings. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - change eval --> int. [Neil
  Cook]
- `Drs_startup.py` log file should use group (only used to save where log
  files are correctly) [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - try to locate log file if not
  found immediately. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - add check if log file exists.
  [Neil Cook]
- `Plotting.core.py` - try fix to plt.show, plt.close. [Neil Cook]
- `Core.constants.constant_functions.py` - add parent/author to set
  method. [Neil Cook]
- Correct README.md. [Neil Cook]
- `Sciecne.calib.wave.py` - correct typo `IC_LITTROW` --> `WAVE_LITTROW`, move
  wave night params to config. [Neil Cook]
- Constants - start adding parents to keywords and add `wave_night`
  constants. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` - change where we get the log
  fits file from. [Neil Cook]
- `Data/spirou/reset/runs/batch_run.ini` - correct batch run as example of
  EA `mini_data`. [Neil Cook]
- `Tools/resource/setup/*` - update all environmental variables. [Neil
  Cook]
- `Misc.tools.ccf_plot.py` - basic plot to plot all ccfs for a given
  object (minus the mean) [Neil Cook]
- `Setup.install.py` - astropy must be v3.2 or greater. [Neil Cook]
- `Tools.recipes.dev.apero_changelog.py` - update locations of docs. [Neil
  Cook]
- `Tools.recipes.dev.apero_documentation` - add codes to build
  documentation [unfinished] [Neil Cook]
- Re-build documentation. [Neil Cook]
- Update documentation (add fontawesome icons) [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add `remake_doc`
  `(apero_documentation)` to recipe definitions. [Neil Cook]
- Reorganise documentation - move build into working dir and have an
  output dir. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- Update docs - `known_issues` and todo. [Neil Cook]
- `Tools.module.documentation.drs_changelog.py` - add function to update a
  file based on a prefix and add in a suffix. [Neil Cook]
- `Tools.recipes.dev.apero_changelog.py` - add doc changes to changelog
  (including copying changelog) [Neil Cook]


0.6.016 (2020-01-06)
--------------------
- `Misc.updates_to_drs.mk_night_wave.py` - question for EA. [Neil Cook]
- `Science.calib.wave.py` - continue work adding wave night functions.
  [Neil Cook]
- `Recipe.spirou.cal_wave_night_spirou.py` - continue work on EA code.
  [Neil Cook]
- `Plotting.plot_functions.py` - add wave night plots. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add debug plots to
  wave night recipe def. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add wave night plots to
  constants. [Neil Cook]
- `Science.velocity.general.py` - add ccf per order normalisation to table
  2 of ccf output. [Neil Cook]
- Continue work adding `cal_wave_night` functionality. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `cal_wave_night`
  recipe. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - correct typo in raw file
  definition. [Neil Cook]
- `Io.drs_lock.py` - mkdir can be accessed by two parallel processes at
  the same time - try 10 times with a sleep timer to allow one to
  complete and other to pass on before raising an error (due to e.g. bad
  file path) [Neil Cook]
- `Tools.module.setup.drs_processingl.py` - if we have a master item do
  not skip if file is missing (cause error) [Neil Cook]
- `Tools.resources.setup.*` - add alias to installation dir. [Neil Cook]
- `Setup/inall.py` - add --name to `install.py` to allow different profiles
  to be set up on the same system. [Neil Cook]
- Update changelog/version/date. [Neil Cook]
- Add apero-data and gitignore contents. [Neil Cook]
- `Core.instruments.default.deafult_config.py` - change default locations
  to a relative location. [Neil Cook]
- `Core.core.drs_startup.py` - do not index if there are no outputs
  (including lock) [Neil Cook]
- `Tools.recipe.general.apero_validate.py` - remove recipe log from non-
  instrument recipe. [Neil Cook]


0.6.015 (2020-01-04)
--------------------
- `Io.drs_lock.py` - remove unused imports. [Neil Cook]
- `Io.drs_fits.py` - all writing to file must be locked (for
  parellisation) based on filename. [Neil Cook]
- `Science.telluric.general.py` - change write --> `write_file`. [Neil Cook]
- `Science.polar.general.py` - change write --> `write_file`. [Neil Cook]
- `Science.extract.general.py` - change write --> `write_file`. [Neil Cook]
- `Science.calib.wave.py` - change write --> `write_file`. [Neil Cook]
- `Science.calib.shape.py` - change write --> `write_file`. [Neil Cook]
- `Science.calib.localisation.py` - change write --> `write_file`. [Neil
  Cook]
- `Science.calib.flat_blaze.py` - change write --> `write_file`. [Neil Cook]
- `Science.calib.dark.py` - change write --> `write_file`. [Neil Cook]
- `Science.calib.badpix.py` - change write --> `write_file`. [Neil Cook]
- `Recipe.spirou.cal_wave_spirou.py` - change write --> `write_file`. [Neil
  Cook]
- `Recipe.spirou.cal_Wave_master_spirou.py` - change write --> `write_file`.
  [Neil Cook]
- `Recipe.spirou.cal_thermal_spirou.py` - change write --> `write_file`.
  [Neil Cook]
- `Recipes.spirou.cal_preprocess_spirou.py` - change write --> `write_file`.
  [Neil Cook]
- `Recipes.spirou.cal_extract_spirou.py` - change write --> writelog.
  [Neil Cook]
- `Core.core.drs_file.py` - change write --> `write_file` (more unique)
  [Neil Cook]


0.6.014 (2020-01-03)
--------------------
- `Io.drs_lock.py` - make all lock files under the `DRS_DATA_MSG` path (not
  the group modified path) [Neil Cook]
- `Io.drs_lock.py` - add absolute path to the files. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- `Core.core.drs_log.py` - if `use_group=False` need to reset `drs_data_msg`
  (otherwise it will already have group name in even if group=None)
  [Neil Cook]
- `Tools.module.setup.drs_reset.py` - remove breakpoint. [Neil Cook]


0.6.013 (2020-01-02)
--------------------
- Continue work on sphinx documentation (html and linux) [njcuk9999]
- `Recipes.spirou.cal_extract_spirou.py` - remove breakpoint. [Neil Cook]
- `Core.core.drs_startup.py` - make sure log file does not use group
  (different groups may need to lock same file) [Neil Cook]
- `Core.core.drs_log.py` - give an option to turn off using group. [Neil
  Cook]
- `Recipes.spirou.cal_extract_spirou.py` - force breakpoint. [Neil Cook]
- `Recipes.spirou.cal_extract_spirou.py` - add breakpoint to help find
  problem. [Neil Cook]
- `Core.core.drs_log.py` - pep8 correction. [Neil Cook]


0.6.012 (2019-12-31)
--------------------
- Start of documentation with Sphinx. [njcuk9999]


0.6.011 (2019-12-23)
--------------------
- `Core.core.drs_log.py` - try to catch log problems. [Neil Cook]
- Update date/version/changelog/readme. [Neil Cook]


0.6.010 (2019-12-19)
--------------------
- `Science.calib.wave.py` + `recipes.spirou.cal_wave_master_spirou.py` - add
  hc/fp line creation from EA. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add `PLOT_WAVEREF_EXPECTED`.
  [Neil Cook]
- `Plotting.plot_functions.py` - add `plot_waveref_expected`. [Neil Cook]
- `Io.drs_data.py` - add a raw mode for getting the cavity file. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.py` - add plot `WAVEREF_EXPECTED` for hc/fp
  lines. [Neil Cook]
- `Core.instrumnets.*.pseudo_const.py` - add `FIBER_DPR_POS` (correct dpr
  type for fiber) [Neil Cook]
- `Core.instruments.spirou.file_defintions.py` - add dbname,key and
  datatype for hc and fp master line files. [Neil Cook]
- Re-make directories (if they don't exist) [Neil Cook]
- `Io.drs_lock.py` - replace `__remove__empty__` function. [Neil Cook]
- `Core.core.drs_log.py` - only continue with `DRS_DATA_MSG_FULL` if it
  exists. [Neil Cook]
- `Core.core.drs_startup.py` - fix location of where we define
  `drs_data_msg_full` the first time. [Neil Cook]
- `Core.core.drs_startup.py` - must pass group to log dir. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - deal with KeyboardInterrupt.
  [Neil Cook]
- `Drs_log.py` - sort out log structure. [Neil Cook]
- `Drs_reset.py` - should not remove read of path. [Neil Cook]
- Update the reset codes to reset log.fits files. [Neil Cook]
- `Core.core.drs_startup.py` - only use recipe.log if `recipe_kind` =
  'recipe' [Neil Cook]
- `Core.core.drs_log.py` - set logfitsfiles name from constants. [Neil
  Cook]
- `Core.instruments.default.default_config.py` - add `DRS_LOG_FITS_NAME`.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_lock.py` - replace print statements for WLOG. [Neil Cook]
- Add reset options to run files. [Neil Cook]
- Remove recipe.log from non-recipe scripts (i.e. tools) [Neil Cook]
- `Core.core.drs_startup.py` - address not initially having instrument for
  `DRS_RECIPE_KIND`. [Neil Cook]
- `Core.core.drs_startup.py` - correctly manage KeyboardInterrupts. [Neil
  Cook]
- Correctly manage KeyboardInterrupts. [Neil Cook]
- `Core.core.drs_log.py` - add way to add an error (if found at the right
  time) [Neil Cook]
- `Core.instruments.default.pseudo_const.py` and `io.drs_lock.py` - update
  `drs_data_msg` path (to full path) [Neil Cook]
- `Core.core.drs_startup.py` - get recipe kind and add to params and
  figure out how to log to files only once we have correct information.
  [Neil Cook]
- `Core.core.drs_log.py` - add `recipe_kind` to `recipe_log`. [Neil Cook]
- `Core.instruments.*.recipe_definitions.py` - add a kind to every recipes
  ("test","recipe","tool","processing") for logging. [Neil Cook]
- `Core.core.drs_recipe.py` - add a recipe kind (for logging) [Neil Cook]
- `Core.core.drs_log.py` - sort logs into night names and by `recipe_kind`.
  [Neil Cook]
- `Core.core.drs_log.py` - add group and runstring to recipe log fits
  file. [Neil Cook]
- Update date/version/changelog/readme. [Neil Cook]
- Update doc string. [Neil Cook]


0.6.009 (2019-12-18)
--------------------
- `Core.core.drs_log.py` + `drs_log_stats.py` - add option to save time of
  file and then do log analysis on --since --before log files only.
  [Neil Cook]
- `Recipes/test/blank_spirou.py` - blank recipe. [Neil Cook]
- Update doc strings for recipes. [Neil Cook]
- `Misc/updates_to_drs/mk_night_wave.py` - EA code to do nightly
  wavelength solution. [Neil Cook]
- `Plotting.plot_functions.py` - log scale on some wave plots. [Neil Cook]
- `Science.calib.wave.py` - update wave triplet fit by EA. [Neil Cook]
- `Science.calib.wave.py` - add breakpoint to look at wave res map
  problem. [Neil Cook]
- `Science.calib.wave.py` - EA changes to triplets fit. [Neil Cook]
- `Recipe/spirou/cal_wave_spirou.py` - force initial wavelength solution
  as the master. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - change the number of
  triplet iterations to 1. [Neil Cook]
- `Science.calib.wave.py` - EA modifications to triplet fitting. [Neil
  Cook]
- Update changelog.md to include `core.core.drs_recipe` fixes. [Neil Cook]
- `Core.core.drs_recipe.py` - add other list arguments -- attempt to
  correct bug. [Neil Cook]
- `Core.core.drs_recipe.py` - add other list arguments (i.e. --fpfiles=X Y
  Z) as separate elements of `str_arg_list`. [Neil Cook]
- `Core.core.drs_recipe.py` - add other list arguments (i.e. --fpfiles=X Y
  Z) as separate elements of `str_arg_list`. [Neil Cook]
- Update date/version/changelog/readme. [Neil Cook]


0.6.008 (2019-12-17)
--------------------
- README.md - correct typo "processing" --> `"apero_processing`" [Neil
  Cook]
- `Setup/install.py` - install.update does not require "args" as input.
  [Neil Cook]
- `Drs_log_stat` - reset the code to remove xytext change (doesn't work
  currently) [Neil Cook]
- `Science.calib.wave.py` - add EA changes (no `linear_minimisation` now use
  `wave_lmfit)` [Neil Cook]
- Update language database. [Neil Cook]
- `Core.core.drs_startup.py` - only start in quiet mod if fkwargs['quiet']
  is True. [Neil Cook]
- `Core.core.drs_recipe.py` - fix bug introduced by having --arguments
  only (need to append all list items to string for `self.str_arg_list`.
  [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - tweak hc tfit order fit
  continuum parameters (EA) [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - change hc tfit order
  fit continuum constants (EA) [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - lower the values of the
  wave hc tfit order fit continnum (EA) [Neil Cook]
- `Science.calib.wave.py` - add breakpoint to test problem. [Neil Cook]
- `Science.calib.wave.py` - attempt fix of wave solution triplets rms
  diverging. [Neil Cook]
- `Science.calib.wave.py` - add breakpoint. [Neil Cook]
- `Science.calib.flat_blaze.py` - EA played with bounds. [Neil Cook]
- `Tools.recipes.general.apero_log_stats.py` - tweak plot. [Neil Cook]
- `Tools.recipes.general.apero_log_stats.py` - tweak plot. [Neil Cook]
- `Tools.recipes.general.apero_log_stats.py` - add recipe mode - correct
  bug. [Neil Cook]
- `Tools.recipes.general.apero_log_stats.py` - add recipe mode. [Neil
  Cook]
- `Plotting.plot_functions.py` - correct pep8. [Neil Cook]
- `Science.calib.wave.py` - remove break points. [Neil Cook]
- `Science.calib.flat_blaze.py` - add comments to EA new additions. [Neil
  Cook]
- `Science.calib.dark.py` - correct bug `dark_time` must be an array. [Neil
  Cook]
- Changelog/readme/date/version. [Neil Cook]


0.6.007 (2019-12-16)
--------------------
- `Tools/bin/apero_log_stats.py` - start adding options for stats on
  specific recipes. [Neil Cook]
- `Science/extract/other.py` - add extra printout to show files were
  extracted and loaded from extraction (before silent in log) [Neil
  Cook]
- `Science/extract/extraction.py` - add extra arguments for
  `calculate_blaze_flat_sinc`. [Neil Cook]
- `Science.calib.flat_blaze.py` - fix issue with fitting blaze function
  (and given better error if `curve_fit` fails) [Neil Cook]
- `Science.calib.dark.py` and `science.calib.shape.py` - make sure files for
  cubes are deep copied (try to prevent memory issues) [Neil Cook]
- `Cal_wave_spirou.py` - update convergence test on hc solution (EA bug
  fix) [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add recipe argument
  to log stats. [Neil Cook]
- Data.core.runs - `limited_run.ini` - update the default limited run.
  [Neil Cook]
- `Install.py` / `drs_installation.py` - Allow user to define all userinputs
  from the command line (Issue #579) [Neil Cook]
- `Drs_startup.py` - need to re-set the instrument when found in params.
  [Neil Cook]
- Update changelog/data/version/readme. [Neil Cook]


0.6.006 (2019-12-13)
--------------------
- Update non-instrument specified recipes (and make sure
  `apero_processing` can be run correctly from main call. [Neil Cook]
- `Drs_startup.py` - need to be careful when we don't have an instrument
  set. [Neil Cook]
- `Setup.install.py` - correct help string. [Neil Cook]
- `Tools.module.testing.drs_log_stats.py` + `tools.recipes.general.py` - add
  log stat code to `apero_log_stats.py`. [Neil Cook]
- `Plotting.plot_functions.py` - add `plot_logstats_bar` plot. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add logstats recipe.
  [Neil Cook]
- Update language database and add recipe to `apero_tools`. [Neil Cook]
- `Tools.module.documentation.drs_changelog.py` - update
  VERSIONSTR/DATESTR with changes to const files. [Neil Cook]
- Update `default_config/default_constants` with groups and some
  descriptions. [Neil Cook]
- `Core.core.drs_startup.py` - allow quiet to be passed from fkwargs.
  [Neil Cook]
- `Core.core.drs_log.py` - move textwrap to constants. [Neil Cook]
- `Core.constants.param_functions.py` - add `"from_file`" and "cache"
  optiosn to `load_config` (for installation purposes) [Neil Cook]
- `Core.constants.constant_functions.py` - move textwrapper here, add
  description to constants, add `write_line` method for writing user
  configs + add '=' to end of update string to make constants unique.
  [Neil Cook]
- `Setup.install.py` + `drs_installation.py` - add an update mode to the
  `install.py` (and fix reset bug) [Neil Cook]


0.6.005 (2019-12-12)
--------------------
- Updates to installation script (UNFINISHED) [Neil Cook]
- `Io.drs_lock.py` - change warning message (name.lock) [Neil Cook]
- `Cal_preprocessing_spirou.py` - typo fix qc inputs. [Neil Cook]
- `Core.core.drs_recipe.py` - change "-" to "--" [Neil Cook]
- Update tools with recipe log. [Neil Cook]
- `Science.telluric.genearl.py` - return `qc_params` and passed in qc
  functions. [Neil Cook]
- `Core.core.drs_log.py` - add `no_qc` and RECIPE to log file and only write
  newlog on `add_level`. [Neil Cook]
- `Cal_thermal_spirou.py` - add `no_qc`. [Neil Cook]
- `Science.preprocessing.general.py` - add quality control to function.
  [Neil Cook]
- `Science.calib.badpix.py` - remove redundant code. [Neil Cook]
- Modify recipes and add recipe logging. [Neil Cook]


0.6.004 (2019-12-12)
--------------------
- `Recipe.spirou.*` - test locking [not working yet] [Neil Cook]
- `Io.drs_lock.py` - provide function to lock function. [Neil Cook]
- `Core.ocre.drs_startup.py` - setup the recipe log. [Neil Cook]
- `Core.core.drs_recipe.py` - add a self.log to store to RecipeLog. [Neil
  Cook]
- `Core.core.drs_log.py` - add RecipeLog. [Neil Cook]
- Make sure all arguments that are words start with -- [Neil Cook]
- Update date/changelog/version. [Neil Cook]


0.6.003 (2019-12-10)
--------------------
- Update README.md. [Neil Cook]
- `Tools.module.listing.file_explorer.py` - deal with no ds9 path set
  (Issue #576) [Neil Cook]
- Fix typos for `apero_validate` and `apero_reset` (Issue #577) [Neil Cook]
- `Core.instruments.default.pseudo_const.py` - modify logfile to have .log
  and latex to replace .log (make unique) [Neil Cook]
- `Core.instruments.default.default_config.py` - `DRS_DS0_PATH` and
  `DRS_PDFLATEX_PATH` should be str not 'path' (Issue #576) [Neil Cook]
- Localisation - remove breakpoints. [Neil Cook]
- Update readme `(cal_preprocessing` --> `cal_preprocess)` [Neil Cook]
- `Localisation.py` - fix bug with loc order 0. [Neil Cook]
- `Science.calib.localisation.py` - move break point. [Neil Cook]
- `Science.calib.localisation.py` - changes to fix loc. [Neil Cook]
- `Cal_loc_spirou.py` - move break point. [Neil Cook]
- `Cal_loc_spirou.py` - add breakpoint to test qc failure. [Neil Cook]
- `Tools.module.setup.py` - `drs_installation.py` - add to clean install
  message. [Neil Cook]
- README.md - update read me with extra comments. [Neil Cook]
- Prepare `cal_wave_master_spirou.py`. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - update 'apero-validate.py'
  --> `'apero_validate.py`' [Neil Cook]
- `Recipes.spirou.cal_wave_spirou.py` - correct typo in comment. [Neil
  Cook]
- `Science.calib.wave.py` - add a TODO. [Neil Cook]
- `Tools.modules.setup.drs_processing.py` - correct returns for
  `prerun_test()` [Neil Cook]
- Change the `file_explorer` name. [Neil Cook]
- `Core.core.drs_recipe.py` - fix telluric test. [Neil Cook]
- Update config/changelog/readme/version. [Neil Cook]


0.6.002 (2019-12-09)
--------------------
- `Core.core.drs_recipe.py` - change souce of tellurics (shouldn't be
  here) [Neil Cook]
- Get whitelist for tellurics in `drs_processing.py`. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add a pre-run test to test if
  files exist before running. [Neil Cook]
- `Tools.module.listing.file_explorer.py` - update plotting function and
  check before loading ds9. [Neil Cook]
- `Science.velocity.general.py` - remove old function `(create_drift_file)`
  [Neil Cook]
- `Science.extract.crossmatch.py` - add simbad query (when we have no ra
  and dec and only have object name) [Neil Cook]
- `Science.calib.wave.py` - remove todo. [Neil Cook]
- `Science.calib.localisation.py` - add rorder to params (for plotting)
  [Neil Cook]
- `Science.calib.flat_blaze.py` - make it clear `calculate_blaze_flat`
  should not be used. [Neil Cook]
- `Recipes.spirou.cal_shape_master_spirou.py` - remove master cube npy
  debug. [Neil Cook]
- Plotting - add general use image/plot functions + add cursor + add
  main() and allow use without recipe defined + add new graph type
  "show" [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_table.py` - remove redundant lock checks (new system works
  better) [Neil Cook]
- `Io.drs_lock.py` - push messages into language database. [Neil Cook]
- `Io.drs_data.py` - remove todo. [Neil Cook]
- `Core.math.gauss.py` - remove todo here. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add plots that were
  missing. [Neil Cook]
- `Core.instruments.default.file_defintions.py` - remove unused file
  objects. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add Help strings.
  [Neil Cook]
- `Core.instruments.*.default_*.py` - add config/constants/keyword args.
  [Neil Cook]
- `Core.core.drs_recipe.py` - deal with `TELLURIC_TARGETS` being set to None
  (get all) [Neil Cook]
- `Core.core.drs_log.py` - remove old WLOG string warning. [Neil Cook]
- `Core.core.drs_database.py` - set Database constants from constants
  files. [Neil Cook]
- `Core.core.drs_argument.py` - add help string for `set_quiet`. [Neil Cook]
- Convert readme.md to pdf. [Neil Cook]
- Add subsections to contents in README.md. [Neil Cook]
- Add descriptions for each recipe in the README.md. [Neil Cook]
- Correct typo in readme. [Neil Cook]
- Update changelog/version/date. [Neil Cook]
- Correct typos in `file_definitions`. [Neil Cook]
- Update the read me with recipe + output descriptions. [Neil Cook]


0.6.001 (2019-12-06)
--------------------
- Remove old breakpoints. [Neil Cook]
- `Science.calib.wave.py` - add breakpoint for debugging. [Neil Cook]
- `Flat_blaze.py` - fix bug with sinc fitting (bounds for quad and cube
  parameters to constraining) [Neil Cook]
- Add error dumps directory. [Neil Cook]
- `Io.drs_lock.py` - make all lock files go to the log/lock dir and add a
  way to remove all empty ones of these (after processing is complete)
  using `drs_lock.reset_lock_dir`. [Neil Cook]
- Update the Lock (not longer need lockdir --> will all go to log
  directory (under the a lock dir) [Neil Cook]
- Update README.md. [Neil Cook]
- Update README.md. [Neil Cook]
- `Io.drs_lock.py` - remove the lock directory if directory is empty.
  [Neil Cook]
- `Science.calib.wave.py` - badvalues must be a string list. [Neil Cook]
- `Core.core.drs_startup.py` - random seed needs to be set to randomise
  the cores. [Neil Cook]


0.5.124 (2019-12-05)
--------------------
- `Tools.module.setup.drs_processing.py` - set `multi_process` back to group
  by core (Process) [Neil Cook]
- `Tools.module.setup.drs_processing.py` - correct typo manager.event -->
  manger.Event. [Neil Cook]
- Update language database. [Neil Cook]
- Parallel test2 - test out Pool (from @cusher) [Neil Cook]
- `Tools.modules.setup.drs_processing.py` - test out Pool (from @cusher)
  [Neil Cook]
- Add second parallel check based on @cusher example. [Neil Cook]
- Update log and group names (slightly shorter - no host) [Neil Cook]
- Update `analyse_logs.py`. [Neil Cook]
- `Core.core.drs_startup.py` - add a random set of charaters to the end of
  pid to make unique. [Neil Cook]
- Add contents to main README.md. [Neil Cook]
- Update default run scripts. [Neil Cook]
- `Tools.module.setup.drs_reset.py` - change empty dir param (typo) [Neil
  Cook]
- Update paths given changes to tool name/location. [Neil Cook]
- Update paths given changes to tool name/location. [Neil Cook]
- Remove dashes from program names to allow importing. [Neil Cook]


0.5.123 (2019-12-05)
--------------------
- `Core.drs_startup.py` - make sure pids are really unlikely to be the
  same (add random component) [Neil Cook]
- `Io.drs_lock.py` - deal with folder/queue files disappear during lock
  process. [Neil Cook]
- `Misc/problems/*` - add copy to analyse log files for preprocessing +
  modify the parallel test. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - change grouping --> only number
  of cores files per group (instead of total/cores per group  per
  recipe) [Neil Cook]
- `Recipe/spirou/cal_preprocess_spirou.py` - change error message. [Neil
  Cook]


0.5.122 (2019-12-04)
--------------------
- `Misc.problems.parellel_test_20191203.py` - minimum working version of
  parallisation problem. [Neil Cook]
- `Misc.problems.parellel_test_20191203.py` - minimum working version of
  parallisation problem. [Neil Cook]
- `Core.core.drs_startup.py` - add SystemExit to the possible exceptions
  to catch. [Neil Cook]
- Add an export command to `file_explorer`. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - make optional programs not
  create "None" path. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - fix typo. [Neil Cook]
- `Setup/install.py` - check for python 3. [Neil Cook]
- Add ds9/pdflatex to the codes. [Neil Cook]
- Add `DRS_DS9_PATH` and `DRS_PDFLATEX_PATH` to constants. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - macs still suck. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - macs suck. [Neil Cook]


0.5.121 (2019-12-02)
--------------------
- Add README.md to bin and dev tool folders. [Neil Cook]
- Change `__INSTRUMENT__` = None to `__INSTRUMENT__` = 'None' and move
  tools/bin and tools/dev to the new loc + add chmod + symlinks. [Neil
  Cook]
- - make `file_explorer.py` work again. [Neil Cook]
- Add runs to default user config files. [Neil Cook]
- Add README.md to reset run files. [Neil Cook]
- `Tools.bin.reset.py` + `drs_reset.py` - add run files to reset. [Neil
  Cook]
- `Core.instruments.*.default_config.py` - add `DRS_RESET_RUN_PATH`. [Neil
  Cook]
- Add reset run files. [Neil Cook]
- `Science.preprocessing.identification.py` - fileset must be string to go
  into .join. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - add the `pp_lfc_lfc` to
  `pp_file` set. [Neil Cook]
- `Science.calib.general.py` - catch warnings for unphysical pixel nan
  setting. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.120 (2019-11-29)
--------------------
- Replace old locking mechanism with new one. [Neil Cook]
- `Science.calib.general.py` - fix upper and lower limit after conversion
  to electrons. [Neil Cook]
- `Science.extract.extraction.py` - change breakpoint location. [Neil
  Cook]
- Change breakpoint location. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.calib.flat_blaze.py` - add breakpoint. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - correct install messages.
  [Neil Cook]
- `Apero/tools/module/setup/drs_installation.py` + `setup.install.py` -
  update the installation after Etienne's first attempt. [Neil Cook]
- Update README.md. [Neil Cook]
- Processing add to README.md. [Neil Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Drs_startup` + `drs_lock` - continue to test the locking mechanism. [Neil
  Cook]
- `Core.core.drs_database.py` - correct typo. [Neil Cook]


0.5.119 (2019-11-29)
--------------------
- `Io.drs_lock.py` - change name of function in @sync call. [Neil Cook]
- `Drs_startup` + `drs_lock` - try to improve locking. [Neil Cook]
- `Core.core.drs_startup.py` - correct name of function. [Neil Cook]
- `Io.drs_table.py` - remove use of locking (for debug) [Neil Cook]
- `Io.drs_lock.py` - add a randomisation to the wait time (so multiple
  hits don't start at the same time) [Neil Cook]
- Add to readme. [Neil Cook]
- Test out new lock. [Neil Cook]
- Add more readme.md. [Neil Cook]
- Merge remote-tracking branch 'origin/dev' into dev. [Neil Cook]
- Update README.md. [Neil Cook]
- Update readme.md. [Neil Cook]
- Update readme.md. [Neil Cook]
- `Io.drs_lock.py` - add a printout when file unlocks (debug?) [Neil Cook]
- Update language database. [Neil Cook]
- Update the README.md with new installation instructions. [Neil Cook]
- `Tools.module.setup.drs_installation.py` - add in skipping of reset if
  not `clean_install` (and print that we are doing reset) [Neil Cook]
- Update `data_example`. [Neil Cook]
- `Science.calib.general.py` `shape.py` - fix typo and remove breakpoint.
  [Neil Cook]
- `Scence.calib.general.py` - remove unphysical pixel values (set to NaN)
  [Neil Cook]
- `Io.drs_image.py` - fix for high bad pixels (clean with border) [Neil
  Cook]
- `Core.instruments.*.default_keywords.py` - add frmtime and saturate +
  add comments for input header keys. [Neil Cook]
- `Io.drs_table.py` - change the locking order. [Neil Cook]
- `Science.calib.shape.py` - move breakpoint. [Neil Cook]
- Update debug table. [Neil Cook]
- `Science.calib.shape.py` - remove old breakpoint. [Neil Cook]
- Add breakpoints and saving of fpcube for debug. [Neil Cook]
- `Science.calib.background.py` - correct axis order in `sz_small`. [Neil
  Cook]
- Add `dark_fp_sky` and `lfc_lfc` file types. [Neil Cook]
- `Core.core.drs_startup.py` - fix for quiet always being found (even when
  None) [Neil Cook]
- `Core.instruments.spirou.default_config.py` - remove INTROOT references.
  [Neil Cook]
- `Io.drs_table.py` - try to add more informative error in `write_table`
  (index.fits is not saving every time in parallel) [Neil Cook]


0.5.118 (2019-11-27)
--------------------
- Etiennes speed up codes. [Neil Cook]
- `Tools.module.setup.drs_reset.py` - update `__NAME__` [Neil Cook]
- `Tools.module.setup.drs_installation.py` - add print headers, add
  validation command, add quiet mode to reset, add paths before
  executing os.system commands. [Neil Cook]
- `Tools.dev.requirement_check.py` - add code (from SpirouDRS) to check
  requirements. [Neil Cook]
- `Tools.bin.validate.py` - add code to validate (for now just a splash
  screen) [Neil Cook]
- `Setup.install.py` - add validation check for required/recommended
  modules. [Neil Cook]
- Remove unused imports. [Neil Cook]
- `Misc.fast_convolve_correct_local_background.py` - etiennes correct to
  add (speed up) [Neil Cook]
- Remove unused imports. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add `required_check`
  program (in tools) [Neil Cook]
- Update permissions. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.core.*.py` - add quiet option so setup info/splash is not
  displayed. [Neil Cook]
- `Core.constants.param_functions.py` - add window size function. [Neil
  Cook]
- Tools.resources.setup - rename from terrapipe --> apero. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - fix problem with
  listing.instrument name and add validate placeholder. [Neil Cook]
- Update .gitignore. [Neil Cook]
- Terrapipe --> apero, move INTROOT2 to .., move INTROOT to misc. [Neil
  Cook]
- Terrapipe --> apero, move INTROOT2 to .., move INTROOT to misc. [Neil
  Cook]
- Terrapipe --> apero, move INTROOT2 to .., move INTROOT to misc. [Neil
  Cook]
- `Core.instruments.spirou.file_definitions.py` - correct `out_dark_master`
  (accept `dark_dark_tel` and `dark_dark_int)` [Neil Cook]
- `Setup.install.py` - add a todo (need to make sym links) [Neil Cook]
- `Tools.module.setup.drs_reset.py` - add functionality to skip warning if
  folder is empty (there is no point warning if we have an empty folder)
  [Neil Cook]
- `Tools.module.setup.drs_installation.py` - add functionality to install
  drs. [Neil Cook]
- `Setup/install.py` - fill out the installation code (formally in
  `drs_installation.py)` [Neil Cook]
- `Tools.bin.reset.py` - add directory to `reset_confirmation`. [Neil Cook]
- `Tools.bin.validate.py` - add placeholder (needs filling out) [Neil
  Cook]
- `Tools.resources.setup/*` - add env setup codes. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.117 (2019-11-26)
--------------------
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` + `obj_mk_tellu_db_spirou.py`
  + `obj_spec_spirou.py` - add global output list for displaying errors at
  the end. [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` + `obj_mk_tellu_db_spirou.py`
  + `obj_spec_spirou.py` - add global output list for displaying errors at
  the end. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - `run_process` and
  `combine_outlist`. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add `run_process` function to run
  a recipe. [Neil Cook]
- `Science.extract.other.py` - remove breakpoint. [Neil Cook]
- Recipes.spirou - change `pol_spirou` name + add place holders for
  `obj_spec_spirou` and `obj_pol_spirou`. [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` `obj_mk_tellu_db_spirou.py` -
  add new functions to `run_process`. [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` `obj_mk_tellu_db_spirou.py` -
  add new functions to `run_process`. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `obj_spec_spirou`
  and `obj_pol_spirou`. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add white/black list
  kwarg to processing. [Neil Cook]
- `Core.core.drs_startup.py` - Add a group title to header (if in group)
  [Neil Cook]
- `Core.constants.param_functions.py` - if we have a list then just return
  `(map_listparameter` function) [Neil Cook]
- `Recipes.spirou.cal_thermal_spirou.py` - add log message for writing
  thermal files. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - set
  `thermal_always_extract` to False. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - move `group_name` to `drs_startup`.
  [Neil Cook]
- `Tools.bin.processing.py` - update link to `group_name` (now in
  `drs_startup)` [Neil Cook]
- `Science.extract.other.py` - add breakpoint to test code. [Neil Cook]
- `Recipes.spirou.cal_thermal_spirou.py` - remove breakpoint. [Neil Cook]
- `Core.core.drs_startup.py` - move `group_name` construct from processing
  to `drs_startup`. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - construct group name and pass
  it to recipe via `linear_process`. [Neil Cook]
- `Tools.bin.processing.py` - generate group name. [Neil Cook]
- `Recipes.spirou.cal_thermal_spirou.py` - add breakpoint for debugging.
  [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - change order to reflect
  current and wanted input header keys. [Neil Cook]
- `Core.core.drs_log.py` - add group handling. [Neil Cook]
- `Core.core.drs_startup.py` - add group handling. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - update the dtype
  setting for --cores in processing recipe. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - update the default
  setting for --cores in processing recipe. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add blacklist, whitelist, cores
  and test run arguments from user input. [Neil Cook]
- `Tools.bins.processing.py` - update instrument name. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add arguments to
  processing recipe. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.calib.wave.py` - correct input to `get_input_files`. [Neil Cook]
- `Core.core.drs_database.py` - add in debug function names to find
  problem. [Neil Cook]
- `Science.calib.dark.py` - add dprtype to dprtypes for dark master table.
  [Neil Cook]
- `Recipes.spirou.cal_dark_master_spirou.py` - get allowed types as a
  list. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - add `DARK_DARK_INT` to
  dark master allowed types. [Neil Cook]
- `Science.calib.dark.py` - add dprtype to dark table. [Neil Cook]
- `Recipes.spirou.cal_dark_master_spirou.py` - allow dark master to use
  multiple `dark_dark` types. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - allow `cal_badpix` to
  use `dark_dark_tel` and `dark_dark_int`. [Neil Cook]
- `Io.drs_fits.py` - improve id file error. [Neil Cook]
- Update language database. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.116 (2019-11-15)
--------------------
- `Tools.module.setup.drs_processing.py` - remove breakpoint. [Neil Cook]
- `Science.extract.general.py` - fix input to `get_input_files`. [Neil Cook]
- `Science.extract.berv.py` - remove breakpoint. [Neil Cook]
- `Science.calib.wave.py` - correct pep8. [Neil Cook]
- `Science.calib.general.py` - add darkfile, abdpixfile, backfile from
  kwargs. [Neil Cook]
- `Core.constants.param_functions.py` - disable the Ctrl+C --> breakpoint
  functionality it doesn't work well. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - deal with optional file args
  being requested. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add extra keys to default run
  keys. [Neil Cook]
- `Core.core.drs_startup.py` - set the source when debug mode taken from
  arguments. [Neil Cook]
- `Core.constants.param_functions.py` - add info and history functions to
  ParamDict and cache some settings for immediate use. [Neil Cook]
- `Science.preprocessing.identification.py` - fix return to `fix_header`
  (for case where we have an input infile) [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add defaults after only if not
  found and warn user. [Neil Cook]
- Update language database. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - add default run keys (for when
  values are not in files) [Neil Cook]
- `Science.velocity.general.py` - add ccf mask to suffix of output file.
  [Neil Cook]
- `Science.velocity.general.py` - add ccf mask to suffix of output file.
  [Neil Cook]
- Add masks from Andres. [Neil Cook]
- `Science.prprocessing.identification.py` - `fix_header`: fix return when
  no infile given. [Neil Cook]
- `Tools.module.setup.drs_processing.py` - `fix_header` make sure header
  comes in as keyword argument. [Neil Cook]
- Science.preprocessing - add recipe as arg in `fix_header` (and push to
  `pseudo_const.py)` [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- `Science.velocity.general.py` - make sure users input of ccf step and
  width is good (ccfstep < ccfwidth / 10) [Neil Cook]
- `Core.instruments.default.*.default_constants.py` - add
  `CCF_MAX_CCF_WID_STEP_RATIO`. [Neil Cook]


0.5.115 (2019-11-14)
--------------------
- Update language database. [Neil Cook]
- `Science.velocity.general.py` - add break point to test crash. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Io.drs_lock.py` - add way to get out of lock loop (Ctrl + C) will now
  delete file - elsewise Ctrl + C goes to debugger (and then exits)
  [Neil Cook]
- `Core.core.drs_database.py` - deal with not having a night name. [Neil
  Cook]
- `Core.core.drs_database.py` - make sure all strings are stripped of
  whitespaces (before and after) [Neil Cook]
- Add new ccf mask. [Neil Cook]
- Rename `error.py` --> `language_db.py`. [Neil Cook]
- `Tools.bin.remake_db.py` -fix `db_time`. [Neil Cook]
- `Tools.bin.remake_db.py` - do not open all files at once (save to master
  one by one) [Neil Cook]
- `Tools.modeul.setup.drs_reset.py` - split `reset_dbdir` to allow accessing
  `copy_default_db`. [Neil Cook]
- `Tools.dev.error.py` - add a TODO here. [Neil Cook]
- `Tools.bin.remake_db.py` - add code to remake databases. [Neil Cook]
- `Science.preprocessing.py` - replace `drs_infile_id` with call to
  `fits.drs_fits`. [Neil Cook]
- `Science.extract.general.py` - add fiber. [Neil Cook]
- `Science.calib.flat_blaze.py` + localisation + wave - add fiber to
  outputs. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - add `id_drs_file` to identify any filename in a
  `drs_file_set` (and return its DrsInputFile/DrsFitsFile instance) [Neil
  Cook]
- `Core.instruments.default.recipe_definitions.py` - add `remake_db`
  (generalised `remake_cdb)` [Neil Cook]
- `Core.instruments.default.default_constants.py` -
  `remake_database_default`. [Neil Cook]
- `Core.instruments.spirou.pseudo_const.py` - pep8 clean up. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add `remake_cdb` recipe
  definition. [Neil Cook]
- `Core.instruments.*.file_definitions.py` - add `calib_file` set and clean
  up (pep8 wise) [Neil Cook]
- `Core.core.drs_file.py` - check if drsfile has recipe (and if not set it
  to self.recipe) [Neil Cook]
- `Core.core.drs_database.py` - make `_get_time` more specific to using
  header/hdict. [Neil Cook]
- `Core.instrument.spirou.default_constants.py` - change to gl581. [Neil
  Cook]
- `Science.velocity.general.py` - correct plot keyword `found_rv` --> rv.
  [Neil Cook]


0.5.114 (2019-11-14)
--------------------
- Science.preprocessing.identification - add the `fix_headers` wrapper
  (passes it to instrument pseudo constants) + add a debug in id process
  to show which drs file we are currently looking at. [Neil Cook]
- `Tools.module.setup.drs_processing` - add header keys via `fix_header`
  (non-instrument specific) [Neil Cook]
- `Science.calib.dark.py` - make sure get dark is getting dark master only
  (dark master is `DARK_DARK_TEL` by default) [Neil Cook]
- `Cal_thermal_spirou.py` - deal with different types of darks (OBJ -->
  `dark_tel`, HC,FP--> `dark_int)` + add switch to turn off thermal
  correction. [Neil Cook]
- `Recipe.spirou.cal_loc_spirou.py` - add `center_fits` to qc (diff of order
  cols must be positive) [Neil Cook]
- `Recipe.spirou.cal_preprocessing.py` - add `fix_header` to fix keys before
  `drs_infile_id`. [Neil Cook]
- `Io.drs_fits.py` - change `get_mid_obs_time` assuming it is now always
  present in header. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.file_definitions` + `recipe_definitions` - split
  `dark_dark` in to `dark_dark_int`, `dark_dark_tel`, `dark_dark_sky`. [Neil
  Cook]
- `Core.instruments.*.pseudo_const.py` - add `HEADER_FIXES` (to control
  instrument specific header fixes required) [Neil Cook]
- `Core.instruments.*.default_keywords.py` - add calibwh and `target_type`
  keywords. [Neil Cook]
- `Core.core.drs_file.py` - fix how we check read before copying. [Neil
  Cook]
- `Core.instruments.*.default_constants.py` - remove skydark references
  and update references to `DARK_DARK` --> `DARK_DARK_INT`, `DARK_DARK_TEL`,
  `DARK_DARK_SKY`. [Neil Cook]


0.5.113 (2019-11-12)
--------------------
- `Core.instruments.spirou.recipe_defintions.py` - add blazefile, flatfile
  and thermal file arguments to required recipes. [Neil Cook]
- `Science.calib.flat_blaze.py` - allow user to set flat and blaze file.
  [Neil Cook]
- `Calib.general.py` - allow user defined thermal file to come from
  calibDB. [Neil Cook]
- `Calib.general.py` - allow user defined file to come from calibDB. [Neil
  Cook]
- `Calib.wave.py` - allow user defined file to come from calibDB. [Neil
  Cook]
- `Calib.shape.py` - allow user defined file to come from calibDB. [Neil
  Cook]
- `Calib.localisation.py` - allow user defined file to come from calibDB.
  [Neil Cook]
- `Calib.dark.py` - allow user defined file to come from calibDB. [Neil
  Cook]
- `Calib.badpix.py` - allow user defined file to come from calibDB. [Neil
  Cook]
- `Calib.background.py` - allow user defined file to come from calibDB.
  [Neil Cook]


0.5.112 (2019-11-12)
--------------------
- `Recipes/spirou/obj_pol_spirou.py` and `science/polar/general.py` - add
  polar s1d (calculation, file writing and plotting) [Neil Cook]
- `Core.instruments.spirou.py` - add s1d plotting. [Neil Cook]
- `Plotting.plot_functions.py` - allow s1d plot to not have fiber
  argument. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` `recipe_definitions.py` -
  add polar s1d outputs. [Neil Cook]
- `Core.instruments.default.default_config.py` - update author list. [Neil
  Cook]
- `Misc/dispatch_object.py` - add argparse arguments. [Neil Cook]


0.5.111 (2019-11-09)
--------------------
- `Tools.module.setup.drs_installation.py` - add `user_interface`,
  `copy_configs` and `update_configs`. [njcuk9999]
- `Core.constants.constant_functions.py` - add `get_constants_from_file` and
  `update_file` functions. [njcuk9999]
- `Core.instruments.default.pseudo_const.py` - add print function to Color
  class (to print in colour) [njcuk9999]
- `Tools.module.setup.drs_installation.py` - first commit of the
  installation script. [njcuk9999]


0.5.110 (2019-11-09)
--------------------
- `Obj_pol_spirou.py` - add generate stats + plotting + writing of files.
  [Neil Cook]
- `Science.calib.dark.py` - add text entry for error 40-011-00006. [Neil
  Cook]
- `Recipe.spirou.cal_shape_spirou.py` - add recipe to args + add new debug
  plot. [Neil Cook]
- `Plotting.plot_functions.py` - add polar plots. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_text.py` - add text entry for error 00-008-00020. [Neil Cook]
- `Io.drs_fits.py` - add text entry for error 00-008-00019. [Neil Cook]
- `Io.drs_data.py` - add text entry for error 09-021-00009. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` + `file_definitions.py` -
  add plot and file definitions for polar + extra debug plot for
  `shape/shape_master`. [Neil Cook]
- `Core.instruments.spirou.py` - add `file_definitions` for polar outputs.
  [Neil Cook]
- `Core.core.drs_startup.py` - remove input params from
  `plotter.close_plots`. [Neil Cook]
- `Core.core.drs_file.py` - make sure all filenames in `add_hkey_1d` and 2d
  are basenames only. [Neil Cook]
- `Instruments.*.default_constants.py` and `default_keywords.py` - add polar
  keywords/constants/plot constants. [Neil Cook]
- `Core.constants.param_functions.py` - ParamDict.copy - add doc string
  (with return type) [Neil Cook]
- `Misc.dispatch_object.py` - code to process tar of objects. [Neil Cook]
- `Misc.dispatch_object.py` - code to process tar of objects. [Neil Cook]
- `Recipes/spirou/cal_ccf_spirou.py` - fix that we need to check whether
  `wprops['WFP_DRIFT']` is None. [Neil Cook]
- `Science.velocity.general.py` - fix bug in plotting. [Neil Cook]
- `Recipes/spirou/cal_ccf_spirou.py` - fix bug with `compute_ccf_fp`. [Neil
  Cook]
- `Recipes/spirou/cal_ccf_spirou.py` - fix bug with `compute_ccf_fp`. [Neil
  Cook]
- `Science.polar.general.py` - update polar class. [Neil Cook]


0.5.109 (2019-11-07)
--------------------
- Update `construct_filename` --> `construct_path`. [Neil Cook]
- `Tools.module.setup.drs_reset.py` - change call to `construct_filename`
  --> `construct_path`. [Neil Cook]
- `Science.polar.*` - add whole lsd module. [Neil Cook]
- `Recipes/spirou/obj_pol_spirou.py` - add call to lsd analysis wrapper.
  [Neil Cook]
- `Io.drs_data.py` - add lsd mask getting. [Neil Cook]
- `Data/spirou/lsd/lsd_order_mask.dat` - add order wavelength file for
  lsd. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add polar lsd constants.
  [Neil Cook]
- Data/spirou/lsd - add lsd masks and meta data. [Neil Cook]


0.5.108 (2019-11-07)
--------------------
- `Science.telluric.general.py` - curve fit forces floats - cast kp as
  bool after it was forced to floats. [Neil Cook]
- `Science.telluric.general.py` - add breakpoint to investigate bug. [Neil
  Cook]
- `Tools.dev.cal_update_berv.py` - re-fix erv measurement - group all
  files by odometer code. [Neil Cook]
- `Tools.dev.cal_update_berv.py` - need to group files to make this
  quicker + skip those that use barycorrpy already. [Neil Cook]


0.5.107 (2019-11-06)
--------------------
- `Recipe/spirou/obj_pol_spirou.py` - continue adding to polar recipe.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Core.maths.*.py` - add continuum calculation function. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add polar constants. [Neil
  Cook]


0.5.106 (2019-11-05)
--------------------
- `Berv.py` - set `leap_update` to False, add file update to
  `cal_update_berv.py`. [njcuk9999]
- Update `object_query_list`. [njcuk9999]
- `Cal_update_berv.py` - print filename processing. [njcuk9999]
- `Science.extract.berv.py` - catch iers warning and display. [njcuk9999]
- `Science.extract.berv.py` - split exception in barycorrpy and iers.
  [njcuk9999]
- `Science.extract.berv.py` - add force=False (force recalculation of
  berv) [njcuk9999]
- `Science.extract.berv.py` - add warn=False (when True prints exception
  when barycorrpy fails) [njcuk9999]
- Merge remote-tracking branch 'origin/dev' into dev. [njcuk9999]

  `pirou_py3` into dev

  # Please enter a commit message to explain why this merge is necessary,
  # especially if it merges an updated upstream into a topic branch.
  #
  # Lines starting with '#' will be ignored, and an empty message aborts
  # the commit.
- Add `cal_update_berv.py` - to update bervs. [njcuk9999]
- Add gui stuff. [njcuk9999]


0.5.105 (2019-11-03)
--------------------
- First commit of a gui module. [njcuk9999]
- Add trigger place-holders. [njcuk9999]
- Rename `drs_reprocess` --> `drs_processing`. [njcuk9999]
- Rename `drs_reprocess` --> `drs_processing`. [njcuk9999]
- `Plotting.core.py` - fix `__NAME__` [njcuk9999]
- `Core.instruments.default.recipe_definitions.py` - rename reprocess.py
  to processing.py. [njcuk9999]


0.5.104 (2019-11-01)
--------------------
- `Science.calib.dark.py` - rearrange steps. [njcuk9999]
- `Science.calib.dark.py` - clean out data. [njcuk9999]
- `Science.calib.dark.py` - replace median with a smart median (smaller)
  [njcuk9999]


0.5.103 (2019-11-01)
--------------------
- `Io.drs_table.py` - fix problem with hdu lists. [njcuk9999]
- `Tools.modules.setup.drs_reprocess.py` - fix bug in keepmask for
  engineering files. [njcuk9999]
- `Drs_reprocess.py` - fix error in remove engineering (fdata-->ftable)
  [Neil Cook]
- Add option to listing code to regenerate rawindex.fits (for all raw
  files) [Neil Cook]
- Add `PI_NAME` to raw columns in index files. [Neil Cook]


0.5.102 (2019-10-30)
--------------------
- Merge remote-tracking branch 'origin/dev' into dev. [njcuk9999]
- `Module.setup.drs_reprocess.py` - add `_remove_engineering` option.
  [njcuk9999]
- `Core.core.drs_recipe.py` - change break for continue if
  DrsRecipeException. [njcuk9999]


0.5.101 (2019-10-29)
--------------------
- `Science.calib.localisation.py` - remove break point. [Neil Cook]
- `Science.calib.localisation.py` - pep8 add second blank line. [Neil
  Cook]
- Test changes to localisation. [njcuk9999]
- Update date/version/changelog. [Neil Cook]


0.5.100 (2019-10-28)
--------------------
- `Science.telluric.general.py` - catch all berv = nan (not allowed) [Neil
  Cook]
- `Science.telluric.general.py` - should be using `USE_BERV` not BERV. [Neil
  Cook]
- Berv update - add in additional barycorrpy parameters. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.telluric.general.py` - catch bad berv value. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.extract.berv.py` - correct setting `use_berv` from estimate.
  [Neil Cook]
- `Science.telluric.general.py` - add break point to identify bug in
  `_wave_to_wave`. [Neil Cook]
- `Science.calib.wave.py` - hc only solution has no CCF --> set CCF used
  keys to None. [Neil Cook]
- `Science.calib.wave.py` - deal with header not having fiber kwarg (is a
  pp file header) [Neil Cook]
- `Science.calib.wave.py` - need to add more empty constants for hc only
  wave sol. [Neil Cook]
- `Obj_pol_spirou.py` - start filling out polarisation code (from SPIRou
  DRS) [Neil Cook]
- Update language database. [Neil Cook]
- `Science.calib.wave.py` - fix differing fiber values from header vs
  usefiber. [Neil Cook]
- `Plot_functions.py` - only add suffix if kind is not None. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.099 (2019-10-25)
--------------------
- `Science.polar.general.py` - add PolarObj class and `validate_polar_files`
  + `valid_polar_file` functions. [Neil Cook]
- `Recipes.spirou.obj_pol_spirou.py` - first commit - start filling out
  polar recipe. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `obj_pol_spirou`.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add polar constants. [Neil
  Cook]
- Plotting - fix `loop_allowed` switch. [Neil Cook]
- `Plotting.*` - fix summary plots using plotloop. [Neil Cook]
- `Plotting.plot_functions.py` - make sure all plots in loops update the
  filename. [Neil Cook]
- `Plotting.plot_functions.py` - fix generators in
  `plot_shape_angle_offset`. [Neil Cook]
- `Flat_blaze` - fix problem with `SHAPE_ANGLE_OFFSET_ALL` arguments. [Neil
  Cook]
- `Flat_blaze` - make threshold for scut = 0.1 + add a cubic term to sinc
  function + adjust the flat/blaze rms calculation. [Neil Cook]
- `Science.calib.shape.py` - try to fix bug with `corr_dx_from_fp`. [Neil
  Cook]
- `Science.calib.shape.py` - remove breakpoint for `lin_mini`. [Neil Cook]
- `Cal_shape_master_spirou.py` - add in breakpoint to address bug. [Neil
  Cook]
- `Core.math.general.py` - fix `linear_minimization` (need to re-calculate
  shapes after masking) [Neil Cook]
- `Recipe.spirou.cal_shape_master_spirou.py` + `science.calib.shape.py` -
  add breakpoint to identify crash. [Neil Cook]
- `Plotting.core.py` - do not clean html warning messages and add text in
  one paragraph. [Neil Cook]
- `Science.calib.wave.py` and `plotting.plot_functions.py` - add fiber to
  `WAVE_FP_IPT_CWD_LLHC` and `SUM_WAVE_FP_IPT_CWID_LLHC` plots. [Neil Cook]
- `Science.calib.wave.py` and `plotting.plot_functions.py` - add fiber to
  `WAVE_FP_IPT_CWD_LLHC` and `SUM_WAVE_FP_IPT_CWID_LLHC` plots. [Neil Cook]
- `Cal_wave_spirou.py` - fix hcprops not having fpprops values (for
  summary) + don't base summary plot on pass/fail just `fp_e2ds_file`
  being set. [Neil Cook]
- `Core.math.fast.py` - fix and catch jit (numba) [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.098 (2019-10-24)
--------------------
- `Recipe.spirou.cal_wave_spirou.py` + `sciecne.calib.wave.py` - add summary
  plot functionality. [Neil Cook]
- `Plotting.*` - add summary plots. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add wave solution
  summary plots. [Neil Cook]
- `Flat_blaze.py` and `extraction.py` - add sloping sinc fit for blaze and
  move summary/qc to modules. [Neil Cook]
- `Obj_fit_tellu_spirou`, `obj_mk_tellu_spirou` and `obj_mk_template_spirou` -
  add telluric plotting. [Neil Cook]
- Move summary + qc + writing to modules (not in main recipes) [Neil
  Cook]
- `Plotting.*` - add telluric plots. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.math.general.py` - add sloped sinc function. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `fit_tellu` plots
  and `mk_template` plots. [Neil Cook]
- `Core.instruments.*.default_*.py` - add blaze sinc constants + plotting
  constants for `fit_tellu`. [Neil Cook]
- Misc - copy of Etiennes sinc function for blaze correction. [Neil
  Cook]
- Update date/version/changelog. [Neil Cook]


0.5.097 (2019-10-23)
--------------------
- `Science.velocity.general.py` - change arguments `(found_rv` --> rv) [Neil
  Cook]
- `Science.telluric.general.py` - add recipe to inputs (for plotting)
  [Neil Cook]
- `Science.calib.wave.py` - fix plots + force wave modes to ints (were
  strings) [Neil Cook]
- `Recipe.obj_mk_tellu_spirou.py` - add debug and summary plots. [Neil
  Cook]
- `Recipe.spirou.cal_loc_spirou.py` - fix check coeffs (Etiennes fix)
  [Neil Cook]
- `Plotting.*.py` - add mktellu plots, fix ioff in pdb, fix mask order in
  html, add warnings to summary document. [Neil Cook]
- `Plotting.*.py` - add mktellu plots, fix ioff in pdb, fix mask order in
  html, add warnings to summary document. [Neil Cook]
- Update the language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add mktellu plot
  outputs. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add wave and mktellu plot
  constants. [Neil Cook]
- `Drs_log.py` - allow use of `output_param_dict` without updating parameter
  dictionary. [Neil Cook]


0.5.096 (2019-10-17)
--------------------
- Update language database. [Neil Cook]
- `Science.velocity.general.py` - add `rv_fit` plot. [Neil Cook]
- `Science.calib.wave.py` - add plotting. [Neil Cook]
- `Plotting.plot_functions.py` - add wave plotting functions. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add wave plots (and a
  ccf plot) [Neil Cook]
- `Core.instruments.*.default_constants.py` - add WAVE plot constants.
  [Neil Cook]
- `SpirouWAVE2.py` - remove todo statement. [Neil Cook]


0.5.095 (2019-10-16)
--------------------
- `Math.fast.py` - rearrange imports. [Neil Cook]
- `Recipes/spirou/cal_loc_spirou.py` - fix problems with clean loc coeffs.
  [Neil Cook]
- `Lin_mini_upgrade.py` - raw source code from Etienne. [Neil Cook]
- `Plotting.plot_functions.py` - close plots if we have an open (before
  plot loop) + fix loc ceoff plot. [Neil Cook]
- `Plotting.py` - add `self.plots_active` (flag that is true when we have
  plots open in interactive mode) [Neil Cook]
- `Core.math.fast.py` + `general.py` - add linear minimisation speed up
  using numba (if present on system) [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `master_run`,
  `calib_run` and `science_run` (for trigger?) [Neil Cook]
- `Core.instruments.*.default_constants.py` - add loc plot/clean up coeff
  constants. [Neil Cook]
- `Core.core.drs_recipe.py` - in `add_extras` value can now be objects other
  than string --> re-test instance. [Neil Cook]
- `Core.core.drs_recipe.py` - fix how we identify special list keys
  (arguments that come from params but are lists) [Neil Cook]
- `Core.core.drs_recipe.py` - fix `new_runs` in `_gen_run`. [Neil Cook]
- `Core.core.drs_recipe.py` + `tools.module.setup.drs_reprocess.py` - deal
  with multiple extra arguments better (from sequences) [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - `obj_mk_template` need
  objname arguments. [Neil Cook]


0.5.094 (2019-10-15)
--------------------
- `Core.instruemnts.spirou.recipe_definitions.py` - fix the full run and
  remove science run sequences. [Neil Cook]
- `Core.instruemnts.spirou.recipe_definitions.py` - add back mk and fit
  tellu limited run individual commands (for object specific) [Neil
  Cook]
- `Science.calib.wave.py` - remove interactive plot sections and add
  `WAVE_HC_GUESS` plot. [Neil Cook]
- `Science.calib.shape.py` - deal with `norm_fp` being zero (skip) [Neil
  Cook]
- `Science.calib.localisation.py` - add `check_coeffs` function. [Neil Cook]
- `Recipe.spirou.cal_loc_spirou.py` - check coefficient and sigma clip /
  smooth them between orders. [Neil Cook]
- `Plotting.plot_functions.py` - add `plot_loc_check_coeffs` and
  `plot_wave_hc_guess`. [Neil Cook]
- `Core.math.general.py` - add `robust_polyfit`. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add loc and wave
  plots. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add loc and wave plot
  constants. [Neil Cook]
- Plotting - make sure location is set in all recipes. [Neil Cook]


0.5.093 (2019-10-14)
--------------------
- `Core.instruments.spirou.recipe_definitions.py` +
  `recipes.spirou.obj_fit_tellu_spirou.py` - must add s1d plot args to
  `fit_tellu`. [njcuk9999]


0.5.092 (2019-10-13)
--------------------
- `Plotting.core.py` + `latex.py` - update layout for stat + qc tables + try
  to latex floating orders. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.extract.general.py` - add fiber to `e2ds_to_s1d` inputs (for
  plotting) [Neil Cook]
- `Plotting.*.py` - continue work on plotting. [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - adjust extract s1d zoom
  parameters. [Neil Cook]
- `Recipe.spirou.*.py` - add `recipe.plot.set_location` (need iterator)
  [Neil Cook]
- `Plotting.plot_functions.py` - remove full spectrum plot (too big) [Neil
  Cook]
- `Science.extract.general.py` - move qc and file writing to functions.
  [Neil Cook]
- `Cal_extract_spirou.py` - add plots + summary document. [Neil Cook]
- `Plotting.plot_functions.py` - add extraction plots. [Neil Cook]
- `Plotter.core.py` - update test case. [Neil Cook]
- Update object query list file. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add plot definitions
  to recipe. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add extract plot constants.
  [Neil Cook]
- `Core.core.drs_recipe.py` - correct problem with recipes that have no
  file arguments (were just being skipped) [Neil Cook]
- `Core.core.drs_file.py` - correct a problem with using fibers = [None]
  [Neil Cook]
- `Plotting.core.py` - fix the addition of fibers to `qc_params` and stat
  table. [Neil Cook]


0.5.091 (2019-10-11)
--------------------
- Add a section to how to (to fill in later) [Neil Cook]
- `Science.calib.shape.py` - move qc and file writing to module + todo
  identified problem. [Neil Cook]
- `Science.calib.localisation.py` - move qc and file writing to module.
  [Neil Cook]
- `Science.calib.flat_blaze.py` - move qc and file writing to module.
  [Neil Cook]
- Recipe.spirou. badpix, dark, flat, loc, shape, `shape_master` - add
  plotting. [Neil Cook]
- `Plotting.*.py` - continue adding plotting functionality. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add plots to shape and
  flat recipes. [Neil Cook]
- `Core.math.general.py` - fix sigfig (deal with zero and non-finites)
  [Neil Cook]
- `Core.instruments.*.default_constants.py` - add plotting constants.
  [Neil Cook]


0.5.090 (2019-10-10)
--------------------
- `Recipe.spirou.cal_shape_master_spirou.py` + `science.calib.shape.py` -
  add plots. [Neil Cook]
- `Recipe.spirou.cal_loc_spirou.py` - fix typo in qc. [Neil Cook]
- `Plotting.*.py` - continue work on plotting functionality. [Neil Cook]
- `Core.math.general.py` - add the sigfig function. [Neil Cook]
- Update the language database. [Neil Cook]
- `Core.instruments.spirou.recipe_defintions.py` - add some plots to
  `cal_shape_master`. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add plot constants. [Neil
  Cook]


0.5.089 (2019-10-10)
--------------------
- Continue adding plotting. [Neil Cook]
- Update how to terrapipe guide. [Neil Cook]
- Update language database. [Neil Cook]
- Data.core..pdbrc - need to go up two levels (up via exception) [Neil
  Cook]
- `Core.isntruments.spirou.recipe_definitions.py` - add loc graphs. [Neil
  Cook]
- `Core.instruments.*.default_constants.py` - add plot constants. [Neil
  Cook]
- `Core.core.drs_startup.py` - change plotter --> plot, move end plotting
  to plotter. [Neil Cook]
- `Core.core.drs_recipe.py` - change plotter --> plot. [Neil Cook]
- `Core.constants.param_functions.py` - fix ipdb exception on exit. [Neil
  Cook]


0.5.088 (2019-10-08)
--------------------
- `Tools.module.setup.drs_reprocess.py` - add plot closing and fix bugs
  with `nightname/str_arg_list` and self.recipe.args. [Neil Cook]
- `Reprocess.py` + `telluric_db` recipes - change how `process_run_list` works
  (now needs recipe) [Neil Cook]
- `Recipe.spirou.cal_dark_spirou.py` - add plots. [Neil Cook]
- `Recipe.spirou.cal_badpix_spirou.py` - add plots. [Neil Cook]
- `Plotting.*.py` - add html, fix some latex issues and add dark/badpix
  plot definitions. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add debug/summary plot
  definitions to `cal_dark` and `cal_badpix`. [Neil Cook]
- `Core.instruments.default.pseudo_const.py` - fix night name in
  `index_lock_filename` definition. [Neil Cook]
- `Core.instruments.output_filenames.py` - fix nightname. [Neil Cook]
- `Core.instruments.*.defaul_*` - add plotting constants. [Neil Cook]
- `How_to_terrapipe.md` - add readme file on how to develop using
  terrapipe. [Neil Cook]
- `Core.core.drs_recipe.py` add `set_debug_plots` and `set_summary_plots`.
  [Neil Cook]


0.5.087 (2019-10-07)
--------------------
- `Core.constants.param_functions.py` - if breakpoints does not have
  params force `allow_breakpoints`. [Neil Cook]


0.5.086 (2019-10-06)
--------------------
- `Tools.module.setup.drs_reprocess.py` - deal with input nightname and
  filename. [njcuk9999]
- `Science.calib.wave.py` - change `'night_name`' to nightname. [njcuk9999]
- Update language database. [njcuk9999]
- `Core.core.drs_recipe.py` - remove breakpoint. [njcuk9999]
- `Core.instruments.default.default_config.py` - add `allow_breakpoints`
  constant. [njcuk9999]
- `Core.core.drs_recipe.py` + `drs_startup.py` - add breakpoint special
  argument. [njcuk9999]
- `Core.core.drs_argument.py` - add breakpoint special argument.
  [njcuk9999]
- `Core.constants.constant_functions.py` - add break point to allow
  stopping at certain point in the code easily. [njcuk9999]
- `Core.constants.__init__.py` - add break point to aliases. [njcuk9999]


0.5.085 (2019-10-05)
--------------------
- `Tools.module.setup.drs_reprocess.py` - add filename and nightname from
  inputs. [njcuk9999]
- Replace . imports with terrapipe imports. [njcuk9999]
- `Plotting.core.py` - replace . imports with terrapipe + store debug
  plots. [njcuk9999]
- `Locale.core.*.py` - replace . imports with terrapipe imports.
  [njcuk9999]
- Update language database. [njcuk9999]
- `Io.*.py` - replace . imports with terrapipe imports. [njcuk9999]
- `Core.__init__.py` - replace . imports with terrapipe imports.
  [njcuk9999]
- `Core.math.*` - replace . imports with terrapipe imports. [njcuk9999]
- `Core.instruments.default.file_definitions.py` - remove call to
  `output_filenames`. [njcuk9999]
- `Core.instruments.*.recipe_definitions.py` - remove `drs_interactive` and
  add filename to reprocess definition. [njcuk9999]
- `Core.instruments.*.default_config` - remove `drs_interactive` and add
  `drs_plot_ext` and `drs_summary_ext`. [njcuk9999]
- `Core.core.*` - remove . imports and add plotter to `drs_startup`.
  [njcuk9999]
- `Core.core.__init__.py` - remove imports. [njcuk9999]
- Core.constants - move . imports to terrapipe imports. [njcuk9999]


0.5.084 (2019-10-04)
--------------------
- Update language database. [Neil Cook]
- `Core.core.drs_recipe.py` - record sys.argv to `self.str_arg_list` if not
  from fkwargs. [Neil Cook]
- Plotting - add in latex functions and summary plot. [Neil Cook]


0.5.083 (2019-10-03)
--------------------
- `Tools.modules.setup.drs_reprocess.py` - change closeall (now in
  plotter) [Neil Cook]
- Modify inputs to `core.post_main` (tools) [Neil Cook]
- Modify inputs to `core.post_main` (tools) [Neil Cook]
- Continue work on plotting functions. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_path.py` - add makedirs function. [Neil Cook]
- `Core.core.drs_startup.py` - remove call to plotter module (and get via
  recipe) [Neil Cook]
- Change inputs to `core.post_main()` [Neil Cook]
- Start work on plotting. [Neil Cook]
- Update the language database. [Neil Cook]
- `Core.instruments.spirou.py` - only calculate ccf for science targets.
  [Neil Cook]
- `Core.core.drs_file.py` - fix type keyword in `check_table_filename`
  should be "allowedfibers" not "fiber" [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - change default ccf
  width to 300 km/s. [Neil Cook]
- Update object list. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - add ccf to limited
  run. [Neil Cook]
- `Core.instruments.default.output_filenames.py` - need to re-get insuffix
  in fiber loop. [Neil Cook]
- `Core.core.drs_file.py` - fix adding fiber to historic files. [Neil
  Cook]
- Update changelog/version/date. [Neil Cook]
- Update object list. [njcuk9999]


0.5.082 (2019-10-02)
--------------------
- `Tools.module.setup.drs_reprocess.py` - deal with traceback as a list or
  string. [Neil Cook]
- `Science.telluric.general.py` - fix bug if we have template must divide
  image by it! [Neil Cook]
- `Science.calib.wave.py` - check for empty wfp variables and set to None.
  [Neil Cook]
- `Recipe.spirou.cal_extract_spirou.py` - correct typo in text entry.
  [Neil Cook]
- `Recipe.spirou.cal_ccf_spirou.py` - add saving of files (via `write_ccf)`
  [Neil Cook]
- Update language database. [Neil Cook]
- Update object list. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` + `recipe_defintions.py` -
  add `out_ccf_fits`. [Neil Cook]
- `Core.instruments.*.default_keywords.py` - add CCF keywords. [Neil Cook]
- `Core.constants.param_functions.py` - correct typo in merge function
  "source" --> "sources" [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.081 (2019-10-01)
--------------------
- `Science.velocity.general.py` - add `locate_reference_file` function and
  work on calculating ccf (now combining with nanmean) [Neil Cook]
- `Science.telluric.general.py` - add `make_1d_template_cube` and
  `mk_1d_template_write` functions. [Neil Cook]
- `Science.extract.berv.py` - add option not to log obtaining berv
  (log=True/False) [Neil Cook]
- `Science.calib.wave.py` - get wave time in wprops. [Neil Cook]
- `Recipe.spirou.obj_mk_template_spirou.py` - add s1d template code to
  `mk_template`. [Neil Cook]
- `Recipe.spirou.cal_ccf_spirou.py` - start adding in ccf fp stuff. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - correct typo "fornat" --> "format" [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add s1d files to set
  outputs. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - add the s1d template
  files + s1d lists for e2ds files. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add new `mk_template`
  constants. [Neil Cook]
- `Core.core.drs_file.py` - add s1d property and fix shape for table.
  [Neil Cook]


0.5.080 (2019-09-30)
--------------------
- `Tools.module.setup.drs_reprocess.py` - fix error in printing errors at
  end (and add these errors to the log properly) [Neil Cook]
- `Core.core.drs_log.py` - add wlog.logmessage (to manually add a message
  to the log file) [Neil Cook]
- `Neil_TODO.md` - update list. [Neil Cook]
- `Terrapipe.science.velocity.general.py` - add test plots while ccf is
  not working. [Neil Cook]
- `Terrapipe.recipes.spirou.py` - add `TEST_RUN` to `obj_fit_tellu_db_spirou`
  and `obj_mk_tellu_db_spirou` and uncomment `mk_obj_template`. [Neil Cook]
- Update language database. [Neil Cook]
- `Terrapipe.io.drs_fits.py` - make sure values are striped of whitespaces
  before comparison. [Neil Cook]
- `Core.core.recipe_definition.py` - add `obj_mk_telludb` and
  `obj_fit_telludb` instead of `obj_mk_tellu/obj_fit_tellu` and
  `obj_mk_template`. [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - deal with adding extra arguments
  to reprocessing recipes. [Neil Cook]
- `Science.calib.wave.py` - remove maxcpp references. [Neil Cook]
- `Core.core.drs_recipe.py` - add extras to recipe (to overwrite arguments
  from reprocessing) [Neil Cook]
- `Core.core.drs_log.py` - update debugging in print function mode. [Neil
  Cook]
- `Core.core.drs_file.py` - do not continue if not valid. [Neil Cook]
- Update language database. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.079 (2019-09-26)
--------------------
- `Tools.module.setup.drs_reprocess.py` - take out pushing skip to recipes
  and add in pushing debug to recipes, rename DEBUG --> `TEST_RUN` to do a
  test run. [Neil Cook]
- `Sciecne.velocity.general.py` - new ccf calculation functions + work on
  ccf for science/fp. [Neil Cook]
- `Science.preprocessing.detectory.py` - remove unused functions/imports.
  [Neil Cook]
- `Science.calib.wave.py` - clean up and move ccf stuff to velocity
  module. [Neil Cook]
- `Cal_preprocess_spirou.py` - pep8 empty line clean up. [Neil Cook]
- `Cal_ccf_spirou.py` - remove nan filling and copy image from infile when
  tellurics are not removed. [Neil Cook]
- Update language database. [Neil Cook]
- Add Etiennes ccf mask for Gl699. [Neil Cook]
- Update run files. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add mask file
  definition and add path in --mask kwarg. [Neil Cook]
- `Core.instruments.*.pseudo_const.py` - add `FIBER_CCF` (defines what is a
  science fiber and what is a reference fiber for CCF calculation. [Neil
  Cook]
- `Core.instruments.*.default_constants.py` + `default_keywords.py` -
  fix/modify constants/keywords for wavecff/ccf. [Neil Cook]
- `Core.core.drs_startup.py` - `_get_arg_strval`: deal with DrsInputFile as
  well as DrsFitsFile. [Neil Cook]
- `Core.core.drs_recipe.py` - add `display_func` and deal with no `drs_files`
  added to files when dtype=file/files, add function `_check_arg_path`.
  [Neil Cook]
- `Core.core.drs_log.py` - `find_param`: add required and default inputs
  (and allow them to return without error) [Neil Cook]
- `Core.core.drs_file.py` - add methods `has_correct_extension`,
  `header_keys_exist`, `has_correct_header_keys`, read, write for
  DrsInputFile. [Neil Cook]
- `Core.core.drs_argument.py` - need to deal with drsfiles being a single
  drsfile + add attribute "path" [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - do not force get the
  wave solution from the calibDB (use header) [Neil Cook]
- `Core.instruments.spirou.default_constants.py` - default wave mode now C
  Lovis method. [Neil Cook]
- `Science.telluric.general.py` - for `drs_data.load_text_file` must define
  dtype. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.078 (2019-09-25)
--------------------
- `Misc.mk_template_s1d.py` - etiennes code to be added to `mk_template`.
  [Neil Cook]
- `Recipe_definitions.py` - only process e2dsff files for `obj_mk_tellu` and
  `obj_fit_tellu`. [Neil Cook]
- `Core.drs_file.py` - make sure tested keys have no white spaces at
  start/end and all are upper case (case insensitive) [Neil Cook]
- `Science.velocity.general.py` - coravelation - fix reporting of number
  of lines found. [Neil Cook]
- `Science.calib.wave.py` - change name of `fp_wavelength_sol_new` to
  `add_fpline_calc_cwid`, remove unused outputs of `assign_abs_fp_numbers`,
  make two method consistent with FP equation d = m `*` ll/2, fix
  `no_overlap_match_calc`, and try to fix NaNs in fp e2ds for ccf
  calculation. [Neil Cook]
- Add cavity length ll and m fit files to data. [Neil Cook]
- Update language database. [Neil Cook]
- `Recipes.spirou.cal_wave_spirou.py` - print that we are updating hc/fp
  files with new wave solution. [Neil Cook]
- `Io.drs_data.py` - load text file needs to default to floats in an
  array. [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - correct typos in
  keywords. [Neil Cook]
- `Core.instrument.*.default_constants.py` - `cavity_length_m_fit.dat`.
  [Neil Cook]


0.5.077 (2019-09-24)
--------------------
- `Science.velocity.general.py` - add `compute_ccf_sciecne` and
  `fill_e2ds_nans` functions (continued work on `cal_ccf_spirou)` [Neil
  Cook]
- `Science.calib.wave.py` - add some extra wave keys (from ccf process)
  [Neil Cook]
- `Cal_wave_spirou.py` - add a TODO for `cal_wave_spirou`. [Neil Cook]
- `Recipe.spirou.cal_ccf_spirou.py` - continue to port code from SpirouDRS
  --> terrapipe. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.isntruments.spirou.recipe_definitions.py` - correct typo in
  `cal_wave` -fpmode definitions (found by @melissa-hobson) [Neil Cook]
- `Core.instruments.*.default_constants.py` + `default_keywords.py` - add
  CCF/RV keys. [Neil Cook]
- `Core.core.drs_file.py` - add option in `read_header_key_1d_list` to try
  to guess dim1 (if manually set to None) [Neil Cook]
- `Core.constants.param_functions.py` - add merge function (to merge one
  param dict into another) [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - fix how we set infile.filetype
  (look at output.intype and deal with None/list/str) [Neil Cook]


0.5.076 (2019-09-23)
--------------------
- `Science.telluric.general.py` - re calculate `tapas_water` and `tapas_other`
  after shift. [Neil Cook]
- `Science.extract.general.py` - fix s1d how we interpolate over NaN gaps.
  [Neil Cook]
- `Core.instruments.spirou.file_definitions.py/recipe_definitions.py` -
  fix intypes for file definitions and tellu `default_refs`. [Neil Cook]
- Udpate object list. [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - fix
  `KW_MKTELL_AIRMASS/WATER` values. [Neil Cook]
- `Core.instruments.*.default_constants` - change telluric
  filetype/dprtype/fiber type definitions. [Neil Cook]
- `Core.core.drs_log.py` - always have log file (put it in home directory)
  [Neil Cook]
- Update changelog/date/version. [Neil Cook]


0.5.075 (2019-09-20)
--------------------
- `Tools.module.setup.drs_reprocess.py` - set filemod and recipemod for
  srecipes that do not have them set. [Neil Cook]
- `Science.telluric.general.py` - guess the sed that goes in (not just
  ones) + sigma clip around `fit_dd` + add a bad mask for sp2 (set to NaN)
  [Neil Cook]
- `Drs_recipe.py` - for process adds method (in DrsRunSequence) add
  filemod and recipemod is frecipe does not have them set. [Neil Cook]
- Update `object_query_list`. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.074 (2019-09-19)
--------------------
- `Science.telluric.general.py` - add an upper and lower limit to keep for
  the pca fit. [Neil Cook]
- `Science.extract.general.py` - fix some minor bugs + pep8 correction.
  [Neil Cook]
- Calib.wave.py, velocity module - change module rv--> velocity, add
  `remove_telluric_domain` function. [Neil Cook]
- `Recipe.spirou.cal_extract_spirou.py` - add `KW_EXT_TYPE`. [Neil Cook]
- `Recipe.spirou.cal_ccf_spirou.py` - first commit + testing of inputs.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - change --add2calib to
  --database, add `cal_ccf` definition. [Neil Cook]
- `Core.instruments.*.default_constants.py` + `default_keywords.py` - add
  first CCF constants. [Neil Cook]
- `Core.core.drs_startup` - change p to param. [Neil Cook]
- `Core.core.drs_database.py` - add a check for
  params['INPUTS']['DATABASE'] to check whether we should save to
  database when `add_file` is used. [Neil Cook]
- `Core.constants.param_functions.py` - deal with copying ParamDict inside
  ParamDict. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_lock.py` - add debug printout for locking. [Neil Cook]
- `Core.math.fast.py` - bn.nansum return bool arrays as bools we don't
  want this. [Neil Cook]
- `Core.core.drs_log.py` - only turn off wrapping for debug wlog entries.
  [Neil Cook]
- `Core.core.drs_database.py` - move locking/checking into copy db file
  function. [Neil Cook]
- Update changelog.md. [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - add shortname to Run class,
  check that all recipes in run table are valid, print group name
  (recipe short name) on group print out. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.math.gauss.py` - mp references should be "fast" references within
  math module. [Neil Cook]
- `Core.instruments.spirou.py` - remove unused recipes + give names to
  wavehc and wavefp. [Neil Cook]
- `Core.core.drs_recipe.py` - `process_adds` should look for ['files',
  'file'] in arg dtype. [Neil Cook]
- `Core.core.drs_log.py` - params may be None - deal with this. [Neil
  Cook]
- `Drs_database.py` - lock the input and output files before copying to
  database. [Neil Cook]
- `Recipes.spirou.cal_loc_spirou.py` - need to import math as mp. [Neil
  Cook]
- Update date/version/changelog. [Neil Cook]


0.5.073 (2019-09-18)
--------------------
- Core.math - add a fast `medfilt_1d` function. [Neil Cook]
- `Core.math.fast.py` - first commit numpy nan functions from bottleneck
  if available. [Neil Cook]
- Change nan numpy functions to mp.nan functions (use bottleneck if
  available for speed up) [Neil Cook]
- `Science.calib.shape.py` - test cube as array. [Neil Cook]
- `Science.calib.shape.py` - add length of cube for printout. [Neil Cook]
- `Science.calib.shape.py` - add printouts to check. [Neil Cook]
- `Science.calib.shape.py` - set transforms/xres/yres to zero. [Neil Cook]
- `Science.calib.shape.py` - test the fpmaster loop (without long parts)
  [Neil Cook]
- Update date/changelog/version. [Neil Cook]


0.5.072 (2019-09-17)
--------------------
- `Tools.bin.reset.py` - remove instrument re-definition (now done in
  core.setup) [Neil Cook]
- `Science.telluric.general.py` - change `KW_DPRTYPES` --> `KW_DPRTYPE`. [Neil
  Cook]
- `Science.calib.shape.py` - add filename and basename (just for
  printing/logging) [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` - fix inputs. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - fix kwargs --objname.
  [Neil Cook]
- `Core.core.drs_argument.py` - checks for arg/kwarg/special arg on naming
  - kwarg and special should have '-' positional should not. [Neil Cook]
- `Science.core.shape.py` - correct type `fpfile_it.image` -->
  `fpfile_it.data`. [Neil Cook]
- Correct `vstack_cols` (needs to handle single row as well as astropy
  table) [Neil Cook]
- `Science.telluric.general.py` - change function `get_objects` to
  `get_non_tellu_objs` and generalise. [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_db_spirou.py` - get dprtypes and robjnames
  in main code. [Neil Cook]
- `Science.calib.shape.py` - calibrate after combining group of FPs. [Neil
  Cook]
- `Core.insturments.spirou.recipe_definitions.py` - change default to
  None. [Neil Cook]
- `Science.telluric.general.py` - add function `get_objects` to get non
  telluric objects. [Neil Cook]
- `Recipe.spirou.obj_fit_tellu_db_spirou.py` - first commit (mostly just
  copy of `obj_mk_tellu_db_spirou)` but does `fit_tellu`, `mk_template`,
  `fit_tellu` on all objects except telluric stars) [Neil Cook]
- `Recipe.spirou.obj_mk_template_spirou.py` - add ending script when files
  are skipped. [Neil Cook]
- `Recipes.spirou.obj_mk_tellu_db_spirou.py` - remove todo (dealt with
  internally) [Neil Cook]
- Update the language database. [Neil Cook]
- `Core.io.drs_table.py` - lock the index file when reading (and don't try
  to open when closing) [Neil Cook]
- `Io.drs_fits.py` - update `find_files` to allow returning of a astropy
  table for all files found (a stack of the valid entries in the index
  files) [Neil Cook]
- `Core.instruments.spirou.recipe_deinfitoins.py` - fix help files + add
  `obj_fit_tellu_db` + add options to feiltypes and fiber arguments. [Neil
  Cook]
- `Cpre.instruments.default.pseudo_const.py` - remove `EXT_TYPE` (and add
  DPRTYPE) to list of indexing columns. [Neil Cook]
- `Core.instruments.*.default_*` - add telluric db keys. [Neil Cook]
- `Core.core.drs_recipe.py` - make vstack a public function and change how
  coluns are added (via list comprehension) [Neil Cook]


0.5.071 (2019-09-16)
--------------------
- `Tools.module.setup.drs_reprocess.py` - add `generate_run_table` to
  generate `run_table` from a set of args/kwargs. [Neil Cook]
- `Tools.module.listing.general.py` - functions for listing.py. [Neil
  Cook]
- `Tools.bin.listing.py` - first commit - code to re-index directories.
  [Neil Cook]
- `Recipes.spirou.obj_mk_template_spirou.py` - correct typo (get filetype
  and fiber from inputs) [Neil Cook]
- `Recipe.spirou.obj_mk_tellu_db_spirou.py` - first commit. [Neil Cook]
- `Io.drs_fits.py` - correct typo and add required switch to
  `get_index_files`. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.recipe_defintions.py` - add `mk_tellu_db` and
  `obj_fit_tellu_db`. [Neil Cook]
- `Core.instruments.default.recipe_definitions.py` - add listing recipe.
  [Neil Cook]
- `Core.core.drs_startup.py` - make indexing and `save_index_file` non
  private functions. [Neil Cook]
- `Core.core.drs_recipe.py` - test log message in `group_run_files` + remove
  old olg test message. [Neil Cook]
- `Core.core.drs_recipe.py` - change how we stack tablelist. [Neil Cook]
- `Core.core.drs_recipe.py` - test wlog statements. [Neil Cook]
- `Core.core.drs_recipe.py` - test wlog statements. [Neil Cook]
- `Core.core.drs_recipe.py` - add print statements. [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - add nightname for all (for when
  ftable is empty) [Neil Cook]
- `Tools.module.listing.file_explorer.py` - change where params comes
  from. [Neil Cook]
- `Io.drs_table.py` - try to fix index file error. [Neil Cook]
- `Core.core.drs_startup.py` - remove unused import. [Neil Cook]
- `Core.core.drs_recipe.py` - clear printer after printing filenames.
  [Neil Cook]
- `Science.preprocessing.identification.py` - need kind to be set (even if
  file not found) for error message. [Neil Cook]
- `Science.calib.shape.py` - need to only copy extract parameters for
  those that are not skiped. [Neil Cook]
- `Io.drs_table.py` - remove table before writing it (to try to get rid of
  "file exists" error) [Neil Cook]
- Add "runs" folder to data. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- `Science.extract.berv.py` - fix bug that berv will be set to NaN if
  coming from header (need to check both key and output[0] for kwargs)
  [Neil Cook]
- `Core.instruments.default.pseudo_const.py` - fix bug that p is locked
  (so set manually) [Neil Cook]
- `Drs_changelog.py` - fix bug in updating version/date. [Neil Cook]


0.5.070 (2019-09-13)
--------------------
- `Tools.bin.reprocess.py` - change how master table is defined (keys
  `'KW_MID_OBS_TIME`' and `'KW_DPRTYPE`' need values creating as not in raw
  file headers), filters need to check for lists. [Neil Cook]
- `Science.telluric.general.py` - add some new logging. [Neil Cook]
- `Sciecne.calib.dark.py` - add some new logging for dark master creation.
  [Neil Cook]
- `Recipes.spirou.obj_fit_tellu_spirou.py` - change how image2 is
  normalised by blaze (not the same as `mk_tellu)` [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - add `get_dprtype`. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - move filemod to pseudo
  consts + add `KW_DPRTYPE` to limited run for `fit_tellu/mk_tellu`. [Neil
  Cook]
- `Core.instruments.spirou.py` - add some new intypes. [Neil Cook]
- `Core.instruments.*.pseudo_const.py` - add FILEMOD and RECIPEMOD
  definitions. [Neil Cook]
- `Core.instruments.*.default*` - add end of file and debug constants.
  [Neil Cook]
- `Core.core.drs_startup.py` - get filemod and recipemod from pseudo
  constants (and re-get them if we change instrument) [Neil Cook]
- `Core.core.drs_recipe.py` - add some `display_func`, and debug logging +
  add params to `check_table_keys`. [Neil Cook]
- `Core.core.drs_log.py` - add `display_func` and put debug numbers into
  params (not hard coded) [Neil Cook]
- `Core.core.drs_file.py` - add `generate_reqfiles` (for checking infile
  name in `construct_filename)` [Neil Cook]
- `Science.calib.dark.py` - add some extra print outs. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - fix bad shape intypes
  (some should be `hc1_hc1` not `fp_fp)` [Neil Cook]
- `Core.core.drs_recipe.py` - when running a master recipe only do one run
  (multiple are not needed) [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - add changes to `generate_runs` and
  add allowed fibers getting. [Neil Cook]
- `Sciecne.telluric.general.py` - change message in recon s1d writing.
  [Neil Cook]
- `Sciecne.extract.berv.py` - fix berv - properties weren't copying. [Neil
  Cook]
- `Sciecne.calib.background.py` - do not check file for debug (could be
  any input file and we don't care here) [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - add changes to `RAW_OUTPUT_KEYS/REDUC_OUTPUT_KEYS`.
  [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - change sequences (must
  start with full preprocess - master dark + master shape wont work
  otherwise) [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - add intypes to all out
  files (for file history lookup) [Neil Cook]
- `Core.instruments.spirou.default_keywords.py` - `KW_OBJNAME` from OBJNAME
  --> OBJECT. [Neil Cook]
- `Core.instruments.default.pseudo_const.py` - re-work output columns (now
  only `output_keys)` [Neil Cook]
- `Core.instruments.default.py` - add additional features to general
  output file (infile suffix removal) [Neil Cook]
- `Core.core.drs_startup.py` - change how we index using raw and reduc
  output columns --> keys (allows more flexible changing of header keys
  without rewriting full index) [Neil Cook]
- `Core.core.drs_recipe.py` - fix how we generate file names for runs
  (follow file history) [Neil Cook]
- `Core.core.drs_file.py` - add remove insuffix, control better construct
  filename. [Neil Cook]
- `Recipes.spirou.cal_extract_spirou.py` + `cal_flat_spirou.py` - transform
  localisation coefficients to master grid. [Neil Cook]
- `Science.calib.shape.py` - add `ea_transform_coeff` function to transform
  per night localisation coefficients to master grid. [Neil Cook]
- `Science.extract.berv.py` - fix problem when we don't have BERV
  variables (set header keys to None) [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - update shortname of
  `fit_tellu`. [Neil Cook]
- Update language database. [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - deal with fact RunSequence
  recipes are lost after generation (run must take inrecipe when recipe
  is given) [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - deal with fact RunSequence
  recipes are lost after generation (run must take inrecipe when recipe
  is given) [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - take out stop just use
  `event.is_set`. [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - deal with recipe finishing (but
  not successfully) [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - extra stopping criteria added.
  [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - extra stopping criteria added.
  [Neil Cook]
- `Toolts.module.setup.drs_reprocess.py` - make master stop at exception
  always. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.069 (2019-09-11)
--------------------
- `Science.extract.general.py` - fix loading of tapas (in thermal
  correction 1) [Neil Cook]
- `Science.extract.berv.py` - fix how berv is obtained from header. [Neil
  Cook]
- `Science.calib.wave.py` - add a way to get dimensions from header
  (NAXIS2 and NAXIS1) if image (via infile) is not defined. [Neil Cook]
- `Recipe.spirou.obj_fit_tellu_spirou.py` + `obj_mk_tellu_spirou.py` +
  `obj_mk_template_spirou.py` - continue work on telluric functions
  (SpirouDRS --> terrapipe) [Neil Cook]
- `Recipe.spirou.cal_extract_spirou.py` - add fiber key to header. [Neil
  Cook]
- `Locale.core.drs_text.py` - add way to deal with TextEntry args being a
  int/float/bool (still not a list)--> list. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - fix `find_files` (now deals with having a fiber filter
  as well) [Neil Cook]
- `Io.drs_data.py` - return both table and outfilename in `load_tapas`
  function. [Neil Cook]
- `Data.spirou.reset.telludb.master_tellu_SPIROU.txt` - add objname to
  default telluDB entries. [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add outputs to
  telluric recipes. [Neil Cook]
- `Core.instruments.spirou.pseduo_const.py` - fix typo in bervmaxest key.
  [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - make adjustments to
  telluric files. [Neil Cook]
- `Core.instruments.default.output_filenames.py` - allow suffix to be
  added to `set_file`. [Neil Cook]
- `Core.instruments.*.default_constants/default_keywords` - add missing
  `make_tellu`, `fit_tellu` and `make_template` constants/keywords. [Neil
  Cook]
- `Core.core.drs_file.py` - by default overwrite data if already read in
  DrsFitsFile.read() [Neil Cook]
- `Core.core.drs_database.py` - add objname to telludb column. [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` = add total time calculation.
  [Neil Cook]
- `Science.telluric.general.py` - add `make_template_cubes` placeholder.
  [Neil Cook]
- `Recipe.spirou.obj_mk_template_spirou.py` - first commit - port from
  SpirouDRS. [Neil Cook]
- `Recipe.spirou.cal_dark_master/cal_spirou_master` - update call to
  `find_files`. [Neil Cook]
- Recipe.spirou - add `KW_OUTPUT` (needs to be added everywhere we
  `copy_hdict` to separate different files) [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - remove `find_filetypes` and add (more generic)
  `find_files` function. [Neil Cook]
- `Core.instrumets.spirou.py` - add in `obj_mk_template`. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add in `mk_template`
  constants. [Neil Cook]
- `Core.core.drs_database.py` - add in default mode `(CALIB_DB_MATCH)` [Neil
  Cook]
- `Core.constants.constant_functions.py` - for bool arguments make sure
  they are strings to do .lower and change second if to elif. [Neil
  Cook]
- `Core.core.drs_file.py` - update pep8 remove redundant lines. [Neil
  Cook]
- Update version/date/changelog. [Neil Cook]


0.5.068 (2019-09-10)
--------------------
- `Tools.modlue.setup.drs_reprocess.py` - load "adds" when checking
  sequences (taken out of recipe init) [Neil Cook]
- `Science.extract.berv.py` - do not report estimate used when we are
  meant to be return no berv. [Neil Cook]
- `Science.calib.general.py` + `science.telluric.general.py` - need to
  enumerate around entries. [Neil Cook]
- `Locale.core.drs_text.py` - cache data - do not load a textdict again
  for an instrument (now cached) [Neil Cook]
- `Core.math.gauss.py` - import general (for fwhm) [Neil Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add `obj_mk_temp`. [Neil
  Cook]
- `Drs_recipe.py` - remove second deep copy (now copied internally to
  constants.load) [Neil Cook]
- `Core.core.drs_file.py` - replace `KW_DRS_QC` with `params['KW_DRS_QC'][0]`
  [Neil Cook]
- `Core.core.drs_argument.py` - move textdict loading to error handling
  (only needed here) [Neil Cook]
- `Core.constants.param_functions.py` - add caches to speed up loading.
  [Neil Cook]
- Update language database. [Neil Cook]
- Rename `obj_mk_tellu` and `obj_fit_tellu` (add `_spirou` suffix) [Neil Cook]
- Make recipes executable. [Neil Cook]
- Update language database. [Neil Cook]
- `Obj_fit_tellu.py` + `obj_mk_tellu.py` - keep porting telluric code from
  SpirouDRS. [Neil Cook]
- Recipe.spirou - pep8 changes. [Neil Cook]
- `Core.math.__init__.py` - add fwhm alias. [Neil Cook]
- Core.instruments - add telluric constants/keywords/definitions. [Neil
  Cook]


0.5.067 (2019-09-06)
--------------------
- `Science.extract.berv.py` - add additional flag for when estiamte is
  used/not used. [njcuk9999]
- `Extract.berv.py` - add `USE_BERV`, `USE_BJD` and `USE_BERV_MAX` to berv props
  (these are the ones that should be used and will be either estimate or
  barycorrpy values. [njcuk9999]
- `Science.telluric.general.py` - add `gen_abso_pca_calc`,
  `shift_all_to_frame` and `calc_recon_and_correct` functions. [njcuk9999]
- `Obj_fit_tellu.py` - continue porting content from SpirouDRS to
  terrapipe. [njcuk9999]
- Update language database. [njcuk9999]
- `Core.core.drs_database.py` - add default parameters to `get_db_file`.
  [njcuk9999]


0.5.066 (2019-09-05)
--------------------
- `Obj_fit_tellu.py` - update how far we have got. [njcuk9999]
- Update language database. [njcuk9999]
- Science.calib and science.extract - fix calls to `load_calib_file`.
  [njcuk9999]
- `Obj_fit_tellu.py/obj_mk_tellu.py` - continue to port from SpirouDRS to
  terrapipe. [njcuk9999]
- `Core.io.drs_path.py` - add `'get_most_recent`' function. [njcuk9999]
- Core.instruments - add `mk_tellu` constants/keywords. [njcuk9999]
- `Core.core.drs_database.py` - change how loading works (rearrange
  functionality) [njcuk9999]
- `Obj_fit_tellu.py` - start to copy over code from SpirouDRS to
  terrapipe. [njcuk9999]


0.5.065 (2019-09-04)
--------------------
- Update language database. [njcuk9999]
- `Core.core.drs_file.py` - add overall pass/fail QC key. [njcuk9999]
- `Obj_mk_tellu.py` - continue work on adding SpirouDRS code to terrapipe.
  [njcuk9999]
- `Cal_loc_spirou.py` - remove blank space. [njcuk9999]
- Core.instruments - add `mk_tellu` constants. [njcuk9999]
- Update language database. [njcuk9999]
- `Science.rv.general.py` - remove empty lines. [njcuk9999]
- `Recipe.spirou.obj_mk_tellu.py` - continue copying over SpirouDRS code
  `(obj_mk_tellu)` [njcuk9999]
- Core.maths - split out some functions into own scripts (separate from
  general.py) [njcuk9999]
- `Core.instruments.spirou.py` - add `obj_mk_tellu` an `obj_fit_tellu` as
  DrsRecipes. [njcuk9999]
- `Core.core.drs_database.py` - add option to get header from database
  file. [njcuk9999]


0.5.064 (2019-09-02)
--------------------
- `Science.calib.wave.py` - add NBPIX to wprops. [njcuk9999]
- `Core.core.drs_startup.py` - add success and passed to outdict.
  [njcuk9999]
- Fix `end_main` calls. [njcuk9999]
- Tools.module.setup - fix some small bugs. [njcuk9999]
- `Obj_mk_tellu.py` - first commit and functions ported from SpirouDrs.
  [njcuk9999]
- Science.extract - add fiber key and fix orderp logging in npy
  read/write functions. [njcuk9999]
- `Science.calib.wave.py` - allow `get_wavelength` solution to force to
  master. [njcuk9999]
- `Science.calib.general.py` - move `load_calib_file` to `drs_database`.
  [njcuk9999]
- Update language database. [njcuk9999]
- Data.core..pdbrc - update pdb rc file (print out) [njcuk9999]
- `Core.core.recipe_definitions.py` - add reprocess=True to `cal_wave` + add
  wave to `limited_run`. [njcuk9999]
- `Core.instruments.*.default_keywords` - add fiber and `KW_MID_OBS_TIME`.
  [njcuk9999]
- `Core.core.drs_startup.py` - fixes to indexing + pdb debug mode and exit
  functionality. [njcuk9999]
- `Core.core.drs_recipe.py` - `add_output_file` method and remove
  params['OUTPUTS'] [njcuk9999]
- `Core.core.drs_file.py` - add `get_fiber` method. [njcuk9999]
- `Core.core.drs_database.py` - `load_db_file` `load_db_file_from_filename`
  functions. [njcuk9999]
- `Core.core.drs_argument.py` - add a reprocess key as well as required
  key. [njcuk9999]
- `Recipes.spirou.*` - `add_output_file` to allow indexing to work.
  [njcuk9999]


0.5.063 (2019-08-31)
--------------------
- Data.core..pdbrc - add pdb/ipdb script to run on execution (after
  copying to working directory) [njcuk9999]
- `Tools.module.error.find_error.py`
  `tools.module.listing.file_explorer.py` - change exit/cleanup function
  calls. [njcuk9999]
- `Tools.dev.changelog.py` - change exit/cleanup function calls.
  [njcuk9999]
- `Science.extract.other.py` - fix problem with thermal (was returning
  e2ds instance not thermal e2ds instance) [njcuk9999]
- Update the exit/clean up function calls in main and `__main__`
  functions. [njcuk9999]
- Update language database. [njcuk9999]
- Update object query list. [njcuk9999]
- `Core.__init__.py` - add aliases to new exit/cleanup functions.
  [njcuk9999]
- `Core.instruments.default.default_config.py` - add idebug constants.
  [njcuk9999]
- `Core.core.drs_startup.py` - change the way ending is cleared up (ipdb +
  ll redo + locals sorting) [njcuk9999]
- `Core.core.drs_recipe.py` - add special `set_ipython_return` (for idebug
  mode) [njcuk9999]
- `Core.core.drs_argument.py` - add SetIpythonReturn class (for idebug
  mode) [njcuk9999]
- `Core.constants.param_functions.py` - add `get_relative_folder` and.
  [njcuk9999]
- `Tools.module.setup.drs_reprocess.py` - change when to lock/unlock
  params + handle deep copying / deletion better. [njcuk9999]
- `Tools.dev.*` - change call to `core.end_main`. [njcuk9999]
- `Tools.bin.*` - change call to `core.end_main`. [njcuk9999]
- `Science.calib.localisation.py` - use fiber params to get some
  parameters. [njcuk9999]
- `Science.calib.dark.py` - change where filetype comes from (not params)
  [njcuk9999]
- `Receipes.spirou.*` - change call to `core.end_main`. [njcuk9999]
- `Core.instruments.*.pseudo_const.py` - fix writing to params (now
  `fiber_params)` [njcuk9999]
- `Drs_startup.py` - get params from llmain. [njcuk9999]
- `Param_functions.py` - add a way to set while being locked (only for use
  when really know what you are doing) [njcuk9999]


0.5.062 (2019-08-30)
--------------------
- `Tools.module.setup.drs_reprocess.py` - fix copying (deep copy)
  [njcuk9999]
- `Tools.dev.changelog.py` - fix `end_main` and `get_locals()` [njcuk9999]
- `Tools.bin.*` - fix main function `(end_main` + `get_locals)` [njcuk9999]
- `Science.extract.other.py` - remove params['QC'] --> passed. [njcuk9999]
- `Science.extract.general.py` - fix `order_profiles` (must be DrsNpyFile)
  [njcuk9999]
- Science.calib.wave,py - continue work to get `cal_wave_spirou.py` to
  work. [njcuk9999]
- `Science.calib.shape.py` - fix spelling in comment. [njcuk9999]
- `Recipe.spirou.*` - remove params['QC'] --> passed, fix `core.end_main`
  params call. [njcuk9999]
- Update the language database. [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - add a hcmode and
  fpmode (for changing the `WAVE_MODE_HC` and `WAVE_MODE_FP)` [njcuk9999]
- `Output_filenames.py` - add output function to `func_name` (for error
  printing - need to locate the problem better) [njcuk9999]
- Core.core.instruments - deal with copying better (deep copies) + check
  used/unused keys. [njcuk9999]
- `Core.core.drs_startup.py` - deal with copying params better + lock
  after copies. [njcuk9999]
- `Core.core.*` - deal with deep copying better. [njcuk9999]
- `Core.constants.param_functions.py` - add locking/unlocking function -
  stop setting keys to params. [njcuk9999]


0.5.061 (2019-08-29)
--------------------
- `Science.rv.general.py` - fix tabbing typo + other fixes (found after
  first run) [njcuk9999]
- `Science.calib.shape.py` - fix error in log args (C  pos 3 --> 4 )
  [njcuk9999]
- `Cal_wave_spirou.py` + `science.calib.wave.py` - continue work on
  converting spiroudrs to terrapipe. [njcuk9999]
- `Recipes.spirou.cal_shape_spirou.py` - add shape keywords. [njcuk9999]
- `Recipes.spirou.cal_extract_spirou.py` - add shape keywords. [njcuk9999]
- Update language database. [njcuk9999]
- `Io.drs_data.py` - add colnames to ccf mask data function. [njcuk9999]
- `Core.__init__.py` - add `fiber_processing_update`. [njcuk9999]
- `Core.math.general.py` - fix nanpolyfit (if kwargs['w'] is None it
  breaks) [njcuk9999]
- `Core.instruments.spirou.recipe_definitions.py` - add new wave fp
  outputs. [njcuk9999]
- `Core.instruments.spirou.file_definitions.py` - add wave definitions and
  make sure name == `KW_OUTPUT`. [njcuk9999]
- Data.spirou.ccf - add CCF masks. [njcuk9999]
- `Core.instruments.*.output_filenames.py` - add `set_file` function.
  [njcuk9999]
- `Core.instruments.*` - add wave constants/keyword args. [njcuk9999]
- `Core.core.drs_startup.py` - `get_file_definition` needs to remove fiber
  if present + add function `'fiber_processing_update`' [njcuk9999]
- `Core.core.drs_file.py` - add group option to `copy_original_keys`
  (including checking `_check_keyworddict)` [njcuk9999]
- `Core.constants.param_functions.py` - add `get_keyword_instances` (for
  obtaining dictionary of header keys linked to params + their
  instances) [njcuk9999]
- `Core.constants.constant_functions.py` - add group. [njcuk9999]
- `Cal_wave_spirou.py` - corrections from Melissa commit + nanpolyfit
  change. [njcuk9999]


0.5.060 (2019-08-28)
--------------------
- `Tools.module.setup.drs_reprocess.py` - fix updating keys in Run
  (runstring/args/kwargs), deal with wrong nightname. [njcuk9999]
- Update language database. [njcuk9999]
- `Io.drs_fits.py` - correct formatting of Time (need to use dtype)
  [njcuk9999]
- `Core.instruments.spirou.default_keywords.py` - correct typo in
  constants. [njcuk9999]


0.5.059 (2019-08-27)
--------------------
- Science.rv.general - add `get_ccf_mask`, coravelation, `delta_v_rms_2d`
  `calculate_ccf` correlbin and `fit_ccf` functions. [njcuk9999]
- `Cal_wave_spirou.py` - continue updating from SpirouDRS --> terrapipe.
  [njcuk9999]
- Update language database. [njcuk9999]
- Update language database. [njcuk9999]
- `Drs_data.py` - add `load_ccf_mask` function. [njcuk9999]
- `Core.math.*` - add fitgauss, `get_dll` and `get_ll` functions. [njcuk9999]
- `Core.instruments.*.py` - continue adding wave constants/keywords.
  [njcuk9999]
- `Drs_reprocess.py` - fix the return to `self.find_recipe`. [njcuk9999]
- `Drs_reprocess.py` - fix the return to `self.find_recipe`. [njcuk9999]


0.5.058 (2019-08-22)
--------------------
- `Neil_TODO.md` - currently needed before release of terrapipe. [Neil
  Cook]
- `Tools.module.setup.drs_reprocess.py` - change SystemExit to LogExit.
  [Neil Cook]
- `Science.calib.wave.py` - continue convert spiroudrs wave fp solution to
  terrapipe. [Neil Cook]
- Update test files with new `__main__` and exception handling (from
  default and spirou) [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_exceptions.py` - add LogExit and Exit classes. [Neil Cook]
- `Io.drs_text.py` - add save text file. [Neil Cook]
- `Terrapipe.io.drs_data.py` - add load + save cavity files. [Neil Cook]
- `Core.instruments.*` - add `WAVE_FP` constants. [Neil Cook]
- `Core.core.drs_startup.py` - change SystemExit catch to LogExit catch.
  [Neil Cook]
- `Core.core.drs_log.py` - change exit system (now via LogExit) [Neil
  Cook]
- `SpirouWAVE2.py` - another question for Melissa. [Neil Cook]


0.5.057 (2019-08-21)
--------------------
- `Science.calib.wave.py` - continue to add wave fp code. [Neil Cook]
- Update language database. [Neil Cook]
- `SpirouWAVE2.py` - add a todo on progress of terrapipe adding. [Neil
  Cook]
- `Cal_wave_spirou.py` - continue adapting SpirouDRS wave codes to
  terrapipe. [Neil Cook]
- `Science.rv.general.py` - add `measure_fp_peaks` `(create_drift_file)` and
  `remove_wide_peaks`. [Neil Cook]
- `Core.math.general.py` - add `gauss_function`. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.*` - continue to add `wave_fp` constants. [Neil Cook]


0.5.056 (2019-08-21)
--------------------
- `Constants_SPIROU_H4RG.py` - add comments for @melissa-hobson to try to
  explain. [Neil Cook]
- `Cal_wave_spirou.py` and `science.calib.wave.py` - continue work on
  converting from SpirouDRS. [Neil Cook]
- `Cal_loc_spirou.py` - fix comment indentation. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - add `out_wave_hc`,
  `out_wave_fp`, `out_wave_hcline`, `out_wave_hcres` and update recipe
  definitions accordingly. [Neil Cook]
- `Core.instruments.*` - continue adding wave constants + keywords. [Neil
  Cook]
- `Core.core.drs_file.py` - fix `add_hkey_1d` function (no longer using
  kwstore in same way) [Neil Cook]


0.5.055 (2019-08-19)
--------------------
- `Science.calib.wave.py` - continued integration of wave from SpirouDRS.
  [Neil Cook]
- `Cal_wave_spirou.py` - update call to `wave.hc_wavesol`. [Neil Cook]
- `Core.math.general.py` - add `fit_gauss_with_slope` function. [Neil Cook]
- Update language database. [Neil Cook]
- Core.instruments - add wave constants. [Neil Cook]
- `Core.constants.param_functions.py` - `_map_listparameter` and
  `_map_dictparameter` - deal with value == '' [Neil Cook]
- `SpirouWAVE2.py` - clean up (for integration into terrapipe) [Neil Cook]


0.5.054 (2019-08-16)
--------------------
- `Tools.module.setup.drs_reprocess.py` - change how `find_recipe` works.
  [Neil Cook]
- `Science.extract.other.py` - add other extraction functions
  (specifically for extracting files in recipes) [Neil Cook]
- `Recipe.spirou.cal_wave_spirou.py` - start conversion of `cal_wave` /
  wave.py. [Neil Cook]
- `Recipes.spirou.*.py` - add `DATA_DICT` and change average/sum to median
  for combining. [Neil Cook]
- Udpate language database. [Neil Cook]
- `Io.drs_image.py` - only check fiber in params['inputs'] if it is in
  inputs. [Neil Cook]
- `Core.instruments.recipe_definitions.py` - add `cal_wave`. [Neil Cook]
- `Core.instruments.file_definitions.py` - add `out_hcline`. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add wave constants. [Neil
  Cook]
- `Core.core.drs_startup.py` - add `DATA_DICT` functionality + recipemod
  saving. [Neil Cook]
- `Core.core.drs_recipe.py` - add unset recipemod to recipe class. [Neil
  Cook]
- `Core.core.drs_file.py` - change combine to include median. [Neil Cook]
- Merge branch 'melissa' into dev. [Neil Cook]

  Conflicts:
      `INTROOT/config/constants_SPIROU_H4RG.py`
      `INTROOT/misc/cal_HC_E2DS_spirou.py`
- `Cal_wave_spirou`: new QC: consecutive pixels along an order must have
  increasing wavelengths. [melissa-hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]

  Conflicts:
      `INTROOT/bin/cal_CCF_E2DS_FP_spirou.py`
      `INTROOT/misc/cal_CCF_wrap_MH.py`
- SpirouWAVE2 - bug fixes. [melissa-hobson]
- `SpirouWAVE2.py` - implementation of `fit_1d_solution` method for
  `wave_new`. [melissa-hobson]
- `SpirouWAVE2.py` - move polynomial fitting to function. [melissa-hobson]
- SpirouWAVE2 - corrections to saves for line list table. [melissa-
  hobson]
- `Cal_wave_spirou`, `spirouWAVE2.py` - fixed line list table for `wave_new`
  method. [melissa-hobson]
- `Cal_wave_spirou`, `spirouWAVE2.py` - fixed results table for `wave_new`
  method. [melissa-hobson]
- SpirouPlot, spirouWAVE2 - plot fixes. [melissa-hobson]
- Merge branch 'melissa' of `https://github.com/njcuk9999/spirou_py3` into
  melissa. [melissa-hobson]
- `Constants_SPIROU_H4RG`: added wave constants spirouPlot.py: added plots
  for `cal_wave_new` `spirouWAVE2.py` - `cal_wave_new` adaptation -
  `update_cavity` switch and proper paths, plots moved to spirouPlot,
  fitting cleaned up. [melissa-hobson]
- `Cal_wave_new_final` save. [melissa-hobson]
- `Cal_HC_E2DS_EA` - corrected QC mistake. [melissa-hobson]
- `Constants_SPIROU_H4RG`: added wave constants spirouPlot.py: added plots
  for `cal_wave_new` `spirouWAVE2.py` - `cal_wave_new` adaptation -
  `update_cavity` switch and proper paths, plots moved to spirouPlot.
  [melissa-hobson]
- `Constants_SPIROU_H4RG`: added wave constants for FP peak ID
  `spirouWAVE2.py` - `cal_wave_new` adaptation - FP peak ID. [melissa-
  hobson]
- `Constants_SPIROU_H4RG`: added wave constants `spirouWAVE2.py` -
  `cal_wave_new` adaptation. [melissa-hobson]
- `SpirouWAVE2.py` - clarification of `all_lines` creation; fix of start and
  end orders for FP method 0; common parts of FP solution (Littrow, CCF)
  moved outside if loop. [melissa-hobson]
- `Cal_wave_spirou.py`, spirouWAVE2 - cleanup. [melissa-hobson]
- `Cal_wave_spirou.py` - bug fixes. [melissa-hobson]
- `Cal_wave_spirou.py`, `spirouWAVE2.py` - C Lovis method incorporation.
  [melissa-hobson]
- `Cal_wave_spirou.py`, `spirouWAVE2.py` - creation of single unified
  wavelength solution codes. [melissa-hobson]
- `Cal_WAVE_NEW_E2DS_spirou_2.py` - fixes to correctly handle NaNs.
  [melissa-hobson]
- `Cal_HC_E2DS_EA`, `cal_WAVE_E2DS_EA`: New QC that verifies that the
  difference in wavelength fits between consecutive orders is positive.
  [melissa-hobson]
- SpirouWAVE.py, `spirouRV.py` - fixes to correctly deal with NaN
  warnings. [melissa-hobson]
- `SpirouWAVE.py` - in `find_hc_gauss_peaks`, segments with fewer not-nan
  values than gaussian parameters + 1 are ignored. [melissa-hobson]
- Merge branch 'master' into melissa. [melissa-hobson]

  # Conflicts:
  #    `INTROOT/bin/cal_CCF_E2DS_FP_MH_spirou.py`
  #    `INTROOT/bin/cal_CCF_E2DS_FP_spirou.py`
  #    `INTROOT/misc/cal_CCF_wrap_MH.py`
  #    `INTROOT/misc/cal_WAVE_NEW_E2DS_spirou_2.py`
- Merge remote-tracking branch 'origin/melissa' into melissa. [melissa-
  hobson]

  # Conflicts:
  #    `INTROOT/bin/cal_CCF_E2DS_FP_spirou.py`
  #    `INTROOT/misc/cal_CCF_wrap_MH.py`
- Cal CCF bla. [melissa-hobson]
- Merge branch 'master' into melissa. [Melissa Hobson]

  Conflicts:
      `INTROOT/bin/cal_CCF_E2DS_FP_MH_spirou.py`
      `INTROOT/bin/cal_CCF_E2DS_FP_spirou.py`
      `INTROOT/misc/cal_CCF_wrap_MH.py`
      `INTROOT/misc/cal_WAVE_NEW_E2DS_spirou_2.py`
- `Cal_HC` function updates `cal_WAVE_NEW` save all input files. [melissa-
  hobson]
- `Cal_CCF_MH`: allows wavesols as arguments `cal_CCF_wrap`: calls all CCFs.
  [melissa-hobson]
- `Cal_WAVE_E2DS_EA`: fix wave file reading. [melissa-hobson]
- `Recipes.spirou.cal_wave_spirou.py` - first commit. [Neil Cook]


0.5.053 (2019-08-15)
--------------------
- `Tools.module.setup.drs_reprocess.py` - correct how we determine whether
  we have errors in odict. [Neil Cook]
- `Core.instruments.spirou.py` - add `hc_run`. [Neil Cook]
- Update object list. [Neil Cook]
- `Tools.module.setup.drs_reprocess.py` - add shortname to processing list
  and skip RUN=False before generation (speed up) [Neil Cook]
- `Science.extract.berv.py` - make columns lower case (to fix table) [Neil
  Cook]
- `Core.core.drs_startup.py` - lock before making directories (for
  parallisation) [Neil Cook]
- Update language database. [Neil Cook]
- `Science.preprocessing.identification.py` - fix problem shallow copying
  fileset instance (use completecopy) [Neil Cook]
- `Science.preprocessing.detector.py` - add dx/dy and suppress warnings
  for nan problems in pp functions. [Neil Cook]
- `Science.calib.*` - change times to `mid_obs_time` + change `debug_back` to
  recipe.outputs definition. [Neil Cook]
- Berv - shift around berv code + make time used come from `mid_obs_time`.
  [Neil Cook]
- `Cal_preprocess_spirou.py` - add in fix for 1 pixel shift + add in
  calculation of mid observation time. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - add `header_end_time` and `get_mid_obs_time` functions.
  [Neil Cook]
- `Core.instrument.spirou.recipe_definitions.py` - add `debug_back` to
  outputs. [Neil Cook]
- `Core.instruments.*.file_defintions.py` - move `debug_back` to instrument
  setup. [Neil Cook]
- `Drs_database.py` - correct typo need to return t for `get_mid_obs_time`
  call. [Neil Cook]
- `Core.instruments.*.py` - add new time constants. [Neil Cook]
- `Drs_database.py` - go from `start_time` --> `mid_obs_time`. [Neil Cook]


0.5.052 (2019-08-14)
--------------------
- Update object query list. [Neil Cook]
- Update language database. [Neil Cook]
- Reprocessing fix - continue work. [Neil Cook]


0.5.051 (2019-08-13)
--------------------
- Reprocessing - continue work on reprocessing. [Neil Cook]
- Reprocessing - continue work on reprocessing. [Neil Cook]
- `Recipe.spirou.cal_thermal_spirou.py` - fix bug with `THERMAL_E2DS_FILE`
  --> `recipe.outputs['THERMAL_E2DS_FILE']` [Neil Cook]
- `Data.core.object_query_list.fits` - update query list. [Neil Cook]
- `Core.instruemnts.spirou.recipe_definitions.py` - update shortnames +
  add science run. [Neil Cook]
- `Core.core.drs_recipe.py` - copy arguments/files properly (avoid shallow
  copying) [Neil Cook]
- `Core.core.drs_log.py` - add printmessage to WLOG. [Neil Cook]
- `Core.core.drs_file.py` - allow copying of drsfiles (required to allow
  recipe copying) [Neil Cook]
- `Core.core.drs_argument.py` - add changes to allow copying of arguments
  (needed for new recipe copies) [Neil Cook]
- `Drs_reprocess.py` - fix problems with modulemain. [Neil Cook]
- `Recipes.spirou.cal_extract_spirou` - remove unused imports. [Neil Cook]
- `Core.instrument.*` - add reprocessing constants. [Neil Cook]
- `Drs_startup.py` - every call to `import_module` should call `func_name` (so
  we know where they come from) [Neil Cook]
- `Drs_recipe.py` - remove `_import_module` without path. [Neil Cook]
- `Core.constants.param_functions.py` - every call to `import_module` should
  have `func_name` as argument (so we know where it came from) [Neil Cook]
- `Core.constants.constant_functions.py` - every use of `import_module`
  should have `'func_name`' as argument (so we know where it came from)
  [Neil Cook]
- `Recipes.spirou.cal_badpix_spirou.py` - fix bug BACKMAP -->
  recipe.outputs['BACKMAP'] [Neil Cook]
- Update old version file. [Neil Cook]
- Update changelog/version/date. [Neil Cook]


0.5.050 (2019-08-12)
--------------------
- Tools.reprocess - add processing (linear/parallel) functionality.
  [Neil Cook]
- `Science.telluric.general.py` - first commit - add `get_whitelist` and
  `get_blacklist` functions. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_text.py` - first commit - add text reading functionality. [Neil
  Cook]
- `Io.drs_data.py` - add `load_text_file` functionality. [Neil Cook]
- `Data.spirou.tellu_*list.txt` - add telluric black/white list. [Neil
  Cook]
- Core.instruments - add white/black list for tellurics (needed for
  reprocessing) [Neil Cook]
- `Core.core.drs_startup.py` - get recipe definitions module from call.
  [Neil Cook]
- `Drs_recipe.py` - changes to `generate_runs`. [Neil Cook]
- `Core.core.drs_file.py` - outfile should just be the basename. [Neil
  Cook]


0.5.049 (2019-08-10)
--------------------
- `Drs_reprocess.py` - address new bugs. [Neil Cook]
- `Drs_reprocess.py` - address new bugs. [Neil Cook]
- Core.instruments - add outfunc=out.blank (and blank description) [Neil
  Cook]
- `Drs_recipe.py` - add return of runs. [Neil Cook]
- `Drs_reprocessing.py` - update for continued work on reprocessing. [Neil
  Cook]
- Update language database. [Neil Cook]
- Core.instruments - add repreocessing constants. [Neil Cook]
- `Drs_file.py` - add functionality for reprocessing. [Neil Cook]


0.5.048 (2019-08-08)
--------------------
- `Tools.reset.py` - remove `update_params` and set `__INSTRUMENT__` from
  recipe update. [Neil Cook]
- `Reprocess.py/drs_reprocess.py` - continue work on reprocessing
  (unfinished) [Neil Cook]
- `Cal_preprocess_spirou.py` - allow skipping of files if done and
  --skip=True. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.__init__.py` - remove `update_params` (now done in setup) [Neil
  Cook]
- `Core.instruments.spirou.recipe_definitions.py` - add file module to
  DrsRecipe calls, add shortname and master to master recipes, add
  section defining run sequences (run order + filters) [Neil Cook]
- `Core.instruments.spirou.py` - add outfunc for `pp_file`. [Neil Cook]
- `Core.instruments.*.output_filenames.py` - fix how `_calibration_prefix`
  works and add an error if "outpath" is None. [Neil Cook]
- `Core.instruments.*.default_constants.py` - add and update constants.
  [Neil Cook]
- `Drs_startup.py` - update parameters if instrument is in inputs (go from
  no instrument to using an instrument) [Neil Cook]
- `Drs_recipe.py` - add copy function to DrsRecipe add DrsRunSequence
  class. [Neil Cook]
- `Drs_argument.py` - remove debug print statement. [Neil Cook]


0.5.047 (2019-08-07)
--------------------
- `Drs_reprocess.py` - add RUN and SKIP names (unfinished) [Neil Cook]
- Add outfiles from recipe.outputs. [Neil Cook]
- `Recipe_definitions.py` - add `set_outputs` and outputs to all recipes.
  [Neil Cook]
- `Drs_recipe.py` - add `set_outputs` method and outputs attribute (for
  adding output file definitions to files) [Neil Cook]


0.5.046 (2019-08-06)
--------------------
- Tools.bin - first commit of reprocessing (not finished) [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_table.py` - fix problem with no `data_start` keyword in fmt='fits'
  [Neil Cook]
- Core.instruments - add in reprocessing constants. [Neil Cook]
- `Core.core.drs_startup.py` - allow `find_recipe` not be non-private. [Neil
  Cook]
- `Core.core.drs_recipe.py` - add a way to skip checks (for getting arg
  list from runlist) [Neil Cook]
- `Core.core.drs_argument.py` - add a way to skip checks (for getting arg
  list from runlist) [Neil Cook]
- `Core.constants.constant_functions.py` - modify `import_module` to have
  quiet mode. [Neil Cook]
- Update todo statements (more specific) [Neil Cook]


0.5.045 (2019-07-27)
--------------------
- `Sciecne.extract.extraction.py` - remove use of params['FIBER'] [Neil
  Cook]
- `Sciecne.extract.berv.py` - fix `assign_properties`. [Neil Cook]
- `Science.calib.*` - add in the option to get filename from call and from
  params['INPUTS'] [Neil Cook]
- `Cal_thermal_spirou.py` - check if `cal_extract` (for the `DARK_DARK)`
  failed before continuing. [Neil Cook]
- `Cal_shape_master_spirou.py` - remove use of params['FIBER'] [Neil Cook]
- `Cal_loc_spirou.py` - remove use of params['FIBER'] [Neil Cook]
- `Cal_flat_spirou.py` - remove use of params['FIBER'] [Neil Cook]
- `Cal_extract_spirou.py` - add options to skip on DPRTYPE and OBJNAME.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_image.py` - remove use of params['FIBER'] [Neil Cook]
- `Recipe_definitions.py` - add more options (calibration files) [Neil
  Cook]
- `Pseduo_const.py` - remove use of params['FIBER'] [Neil Cook]
- `File_definitions.py` - add `KW_OBSTYPE` to raw files. [Neil Cook]
- `Pseudo_const.py` - remove use of params['FIBER'] [Neil Cook]
- `Recipe_definition` - replace kwarg --> `set_kwarg` and arg --> `set_arg`.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Berv.py` - add things left to do. [Neil Cook]
- Update `example_run_list.txt`. [Neil Cook]
- Update `example_run_list.txt`. [Neil Cook]
- `Core.instruments.spirou.file_defintions.py` - correct suffix for
  `out_shape_debug_ihc`. [Neil Cook]
- `Cal_flat_spirou.py` - correct order call. [Neil Cook]
- `Misc.update_wave_header.py` - script to update `master_wave` header with
  new keys. [Neil Cook]
- `Misc.example_run_list.txt` - list of test codes to run (while
  reprocessing script is being built) [Neil Cook]
- Tools.bin - add reset code (formally `cal_reset.py)` [Neil Cook]
- `Identification.py` - fix `drs_outfile_id` to find files with a different
  prefix. [Neil Cook]
- Science.calib - `get_file_definition` must specify kind (raw/tmp/red)
  [Neil Cook]
- `Cal_preprocess_spirou.py` - correct problems with `drs_outfile_id`. [Neil
  Cook]
- `Cal_dark_master_spirou.py` - deal with no dark files being found. [Neil
  Cook]
- `Drs_data.py` - `construct_filename` function all filename/directory name
  to be unset. [Neil Cook]
- Data.spirou.reset - update `MASTER_WAVE.fits` (new header keys) [Neil
  Cook]
- `Core.__init__.py` - add some new aliases and rearrange order. [Neil
  Cook]
- Update language database. [Neil Cook]
- Core.instruments - add reset functionality + small fixes to run codes.
  [Neil Cook]
- `Core.core.drs_startup.py` - pipe errors in main end script to WLOG
  (were just raising) + add function `update_params` (to update param with
  instrument params) [Neil Cook]
- `Core.core.drs_recipe.py` - add exceptions for bad sys.argv and
  misbehaving parsing to argparse. [Neil Cook]
- `Core.core.drs_file.py` - fix error message (should be the drs file not
  just the name) [Neil Cook]
- Data.spirou.reset - add reset files for calibdb and telludb. [Neil
  Cook]
- Reorganisation of the tools folder. [Neil Cook]
- Tools - update tools now have bin folder and dev folder (rest are
  modules) [Neil Cook]
- `Science.calib.shape.py` - add log for `ea_transform`. [Neil Cook]
- Update language database. [Neil Cook]
- `Object_query_list.fits` - first commit - the gaia query database (so we
  don't have to query online every time) [Neil Cook]
- `Science.extract.general.py` - fix problems with thermal. [Neil Cook]
- `Science.extract.crossmatch.py` - correction to new berv functionality
  including plx limit and mag limit. [Neil Cook]
- `Science.extract.berv.py` - correction to new berv functionality
  (including dberv and rv when present) [Neil Cook]
- `Cal_loc_spirou.py` - add calibs to header. [Neil Cook]
- `Cal_extract_spirou.py` - add rest of the cdb keywords. [Neil Cook]
- `Drs_data.py` - correct problems with `construct_filename` and add unique
  error message for `obj_list` function. [Neil Cook]
- `Core.math.general.py` - apply fix #567 by @melissa-hobson. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.*` - added calibration and extraction (berv) keyword
  defintions. [Neil Cook]
- `SpirouMath.py` - correct issue #567 (fix by @melissa-hobson) [Neil
  Cook]


0.5.043 (2019-07-25)
--------------------
- `Science.extract.berv.py` - add features to query gaia / lookup table.
  [Neil Cook]
- .gitignore - add .lock to ignore list. [Neil Cook]
- `Science.extract.crossmatch.py` - first commit -- adding to query
  gaia/lookup table. [Neil Cook]
- `Science.extract.extraction.py` - change warning keys 0016 --> 016.
  [Neil Cook]
- `Cal_extract_spirou.py` - fix typo `add_berv_keys` requires params. [Neil
  Cook]
- `Drs_data.py` - add return file option to data functions. [Neil Cook]
- Update language database. [Neil Cook]
- Core.instruments - add `obj_list` constants (for gaia crossmatch) [Neil
  Cook]
- `Param_functions.py` - add `set_instance` and `set_instances`. [Neil Cook]


0.5.042 (2019-07-23)
--------------------
- `Science.extract.berv.py` - continue work on adding berv calculation.
  [Neil Cook]
- `Cal_extract_spirou.py` - add header to `get_berv`. [Neil Cook]
- `Dsr_fits.py` - use param.instances to get fmt and dtype for `KW_ACQTIME`.
  [Neil Cook]
- Core.constants - add instance dictionary (like source dictionary) for
  ParamDict. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.*` - add constants for berv. [Neil Cook]
- Changelog.md: refractor `header_time` --> `header_start_time`. [Neil Cook]
- Science.extract - add berv functionality. [Neil Cook]
- `Science.extract.wave.py` - add function `add_wave_keys`. [Neil Cook]
- Science.calib.dark/shape - refractor `header_time-->header_start_time`.
  [Neil Cook]
- `Cal_extract_spirou.py` - add berv stuff. [Neil Cook]
- Update language database. [Neil Cook]
- `Io.drs_fits.py` - rename `header_time` --> `header_start_time`. [Neil Cook]
- `Drs_database.py` - rename `header_time` --> `header_start_time`. [Neil
  Cook]


0.5.041 (2019-07-19)
--------------------
- `Science.extract.general.py` - correct typo: `red_limt` --> `red_limit`.
  [Neil Cook]
- `Science.extract.general.py` - correct corrtype2 type:
  `THERMAL_CORRETION_TYPE1` --> `THERMAL_CORRETION_TYPE2`. [Neil Cook]
- `Cal_extract_spirou.py` - print process of extraction fiber {0} of [{0}
  {1} {2}] [Neil Cook]
- Update language database. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.040 (2019-07-19)
--------------------
- `Science.extract.general.py` - add s1d funtionality and add log message
  to thermal correction. [Neil Cook]
- `Science.calib.wave.py` - get the wfp keys and store in wprops. [Neil
  Cook]
- `Science.calib.localisation.py` - return locofile instance with
  localisation properties. [Neil Cook]
- `Science.calib.flat_blaze.py` - correct blaze getting function (was set
  to get flat) [Neil Cook]
- `Cal_extract_spirou.py` - add s1d functionality. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - fix problem that table cannot be primary hdu (start from
  ext=1 in these cases) [Neil Cook]
- Core.instruments - add s1d constants. [Neil Cook]
- `Drs_file.py` - fix hdict copying header cards, make sure header keys
  only copy basename for paths, add key formating for 1d and 2d keys.
  [Neil Cook]


0.5.039 (2019-07-18)
--------------------
- `Science.extract.general.py` - fix typo `"red_limt`" --> `"red_limit`" [Neil
  Cook]
- `Wave.py` - make wave master use specific fibers and search for file
  defintion. [Neil Cook]
- `Shape.py` - correct program with shape finding (dymap y0[:, ix] -->
  y0[:, dim2//2]) [Neil Cook]
- `Cal_thermal_spirou.py` - add program name for when `cal_thermal` uses
  `cal_extract` `(thermal_extract)`, make sure header is added to outfile
  before adding to calibDB. [Neil Cook]
- `Cal_flat_spirou.py` - add textentry for qc fail message (missed before)
  [Neil Cook]
- `Cal_extract_spirou.py` - update QC should just check for NaN image.
  [Neil Cook]
- `Drs_table.py` - remove `"data_start`" for fits files (in `read_table)`
  [Neil Cook]
- `File_definitions.py` - add wavem file and correct thermal file (should
  be a `general_file` not a `calib_file)` [Neil Cook]
- `Drs_startup.py` - always plot the header line before file processing
  message. [Neil Cook]
- `Drs_database.py` - update the error when there is not hdict or header
  present (must be one or the other) [Neil Cook]
- `Drs_argument.py` - make debug message a text entry. [Neil Cook]
- Update language database. [Neil Cook]
- `SpirouImage.py` - fix the shape problem with dymap bending (fit y0 for
  center pixel not ix'th pixel) [Neil Cook]
- Data.core - add `tapas_all_sp.fits`. [Neil Cook]
- `Extract.general.py` - continue to port thermal correction code. [Neil
  Cook]
- `Shape.py` - remove test cases for dymap generation (still
  unfixed/unworking) [Neil Cook]
- `General.py` - reorganise `load_calib_file` (no `load_calib_table)` [Neil
  Cook]
- `Drs_image.py` - allow fiber type "ALL" [Neil Cook]
- `Drs_data.py` - add `load_tapas`. [Neil Cook]
- `Core.__init__.py` - `copy_kwargs` alias. [Neil Cook]
- `Cal_extract/cal_thermal` - continue work on porting from spirou drs.
  [Neil Cook]
- Update language database. [Neil Cook]
- Core.instruments - add constanst for extraction (thermal mostly) [Neil
  Cook]
- `Drs_startup.py` - add `copy_kwargs` function. [Neil Cook]
- `Drs_recipe.py` - add `set_program` special argument. [Neil Cook]
- `Drs_log.py` - set default values for params. [Neil Cook]
- `Drs_argument.py` - correct how to handle string instead of list for
  files. [Neil Cook]
- `SpirouImage.py` - remove test cases. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - correct comment. [Neil Cook]


0.5.037 (2019-07-10)
--------------------
- Extraction/flat/blaze - continue work to port changes from spiroudrs.
  [Neil Cook]
- Extraction/flat/blaze - continue work to port changes from spiroudrs.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Recipe_definitions.py` - change --extfiber to --fiber. [Neil Cook]
- `Pseudo_const.py` - update constants (add `FIBER_DATA_TYPE)` [Neil Cook]
- `SpirouMath.py` - pep8 change. [Neil Cook]
- `Cal_shape_master_spirou.py` - fix problem FP file should be FPfiles.
  [Neil Cook]
- `Science.extract.py` - work on completing the extraction functions (for
  `cal_flat)` [Neil Cook]
- `Science.calib.shape.py` - fix getting the calibration files (don't want
  to use `file_definitons` for specific instrument) [Neil Cook]
- `Science.calib.localisation.py` - fix `load_orderp`. [Neil Cook]
- `Science.calib.general.py` - check dtype in `add_calibs_to_header`. [Neil
  Cook]
- `Cal_flat_spirou.py` - continue porting over code from spiroudrs. [Neil
  Cook]
- `Recipes.spirou.py` - add missing keywords to header. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_image.py` - fix `get_fiber_types`. [Neil Cook]
- `Drs_fits.py` - add `check_dtype_for_header` function. [Neil Cook]
- `Recipe_definitions.py` - remove extract method. [Neil Cook]
- `Pseudo_const.py` - add `FIBER_WAVE_TYPES`. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py` - fix types in calls.
  [Neil Cook]
- `Core.instruments..output_filenames.py` - tweak `npy_file`. [Neil Cook]
- `Core.instruments.py` - add `cal_flat` constants/keywords. [Neil Cook]
- `Drs_startup.py` - make sure name == file.name if we aren't returning
  all files. [Neil Cook]
- `Drs_log.py` - add dtype to allow listp/dictp to test/convert elements
  before returning. [Neil Cook]
- `Drs_file.py` - fix NpyFile to overwrite needed functions of InputFile.
  [Neil Cook]
- `Core.constants.param_function.py` - modify params.listp and
  params.dictp to add a dtype for list/dict elements. [Neil Cook]


0.5.035 (2019-07-08)
--------------------
- Update language database. [Neil Cook]
- `Science.extraction.py` - first commit (port from spiroudrs) [Neil Cook]
- `Science.calib.shape.py` - change shape files to load from
  `general.load_calib_file`. [Neil Cook]
- `Science.calib.localisation.py` - add `load_orderp`. [Neil Cook]
- `Science.calib.general.py` - add `load_calib_file` and `load_calib_table`.
  [Neil Cook]
- `Cal_extract_spirou.py/cal_flat_spirou.py` - start porting code. [Neil
  Cook]
- `Drs_image.py` - add function `get_fiber_types`. [Neil Cook]
- `Drs_data.py` - change error code. [Neil Cook]
- `File_definitions.py` - add `drs_ninput` and `out_orderp_straight`. [Neil
  Cook]
- `Output_filenames.py` - add `npy_file`. [Neil Cook]
- `Drs_log.py` - allow `find_param` (pcheck) to get listp or dictp as well
  as constant. [Neil Cook]
- `Drs_file.py` - add DrsNpyFile and move some functionality to
  DrsInputFit. [Neil Cook]
- `Param_functions.py` - add `_map_dictparameter` and redefine
  `_map_listparameter`. [Neil Cook]
- `Science.calib.shape.py` - update how shape files are obtained from
  calibDB (including new function `get_shapelocal)` [Neil Cook]
- `Science.calib.localisation.py` - update how we get loco files from
  calibDB. [Neil Cook]
- `Recipes.spirou.cal_loc_spirou.py` - change outfile definiton (and how
  we identify which fiber file is for) [Neil Cook]
- `Cal_extract/cal_flat` -- continue porting functionality from spiroudrs.
  [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_path.py` - correct `__NAME__` [Neil Cook]
- `Drs_fits.py` - allow read function to take function name as argument +
  correct pep8. [Neil Cook]
- `Drs_data.py` - correct typoe in relfolder and filename for
  `load_full_flat_pp()` [Neil Cook]
- `Recipe_defintions.py` - update filetypes (no need to distiguish fiber
  files) [Neil Cook]
- `File_defintions.py` - update all filedefinitions with prefix, suffix,
  filetype where needed. [Neil Cook]
- `Output_filenames.py` - change how getting filenames work (now uses
  prefix/suffix/filetype and deal with having a fiber defined) [Neil
  Cook]
- `Drs_startup.py` - allow `get_file_definition` to return all files found
  (and name to be a string within drs file instance name) [Neil Cook]
- `Drs_recipe.py` - change variable index --> indextable. [Neil Cook]
- `Drs_file.py` - add suffix, prefix, fiber, fibers and rename ext
  -->filetype, index --> indextable, add method `get_dbkey` (adding use
  for fibers) [Neil Cook]
- `Drs_database.py` - change how dbkey is obtained. [Neil Cook]


0.5.034 (2019-07-05)
--------------------
- README.md - move from recipes to terrapipe.recipes. [Neil Cook]
- README.md - move from recipes to terrapipe.recipes. [Neil Cook]
- `File_definitions.py` - remove `slit_shape`. [Neil Cook]
- Constants - add `FIBER_TYPES`. [Neil Cook]
- `Param_functions.py` - add listp method (to turn a string list into a
  list) [Neil Cook]
- `Cal_thermal_spirou.py` - get the nightname from parameter dict. [Neil
  Cook]
- `Science.calib.shape.py` - test how to deal with out of bounds
  coefficients in dymap [UNFINISHED + NOT WORKING] [Neil Cook]
- `Science.calib.general.py` - get number of files (from DrsFitsFile
  instance) and push this into dark correction (for average) [Neil Cook]
- `Science.calib.dark.py` - DARK key should be DARKM. [Neil Cook]
- `Core.instruments.spirou.pseduo_const.py` = flip A and B coefficients to
  match spiroudrs. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_file.py` - add and set numfiles constant (for use when combining
  files to know how many files were combined) [Neil Cook]
- `Cal_shape_master_spirou.py` [terrapipe] - sum files don't average them,
  do not correct background (to make similar to spiroudrs code) and fix
  typo for dxmap0. [Neil Cook]
- `SpirouStartup.py` - only return unique files when returning multiple
  files. [Neil Cook]
- `SpirouImage.py` - fpdata1 --> masterfp, test how to deal with bounds in
  dymap. [Neil Cook]
- `Cal_shape_master_spirou.py` - change fpfile to fpfiles, set frames to
  use all fp files, make fpdata1 not masterfp. [Neil Cook]
- `Science.calib.shape.py` - add `shape_local` functions. [Neil Cook]
- `Science.calib.localisation.py` - change where we add one to the
  coefficient numbers. [Neil Cook]
- `Science.calib.general.py` - add calibration log message. [Neil Cook]
- Update language database. [Neil Cook]
- `Core.instruments.spirou.file_definitions.py/rcipe_defintions` - add
  shape `outputs/shape_local` recipe definition. [Neil Cook]
- `Cal_shape_spirou.py` - first commit - push over code from spiroudrs.
  [Neil Cook]
- `Cal_shape_master_spirou.py` - fix bugs with saving. [Neil Cook]
- `Cal_loc_spirou.py` - change math from average to sum. [Neil Cook]


0.5.032 (2019-07-03)
--------------------
- `Science.calib.wave.py` - correct bug in loading keys from wave header.
  [Neil Cook]
- `Science.calib.shape.py` - add dymap functionality + correct some dxmap
  bugs. [Neil Cook]
- `Science.calib.localisation.py` - correct `get_coefficients` function.
  [Neil Cook]
- `Science.calib.general.py` - add `add_calibs_to_header` function. [Neil
  Cook]
- Update language database. [Neil Cook]
- Constants - continue adding shape constants + add pseudo constant
  functions. [Neil Cook]
- `Drs_log.py` - `find_param` function: function call takes prescendence
  over params[key] [Neil Cook]
- `Cal_shape_master_spirou.py` - continue work on adding spiroudrs code
  (file saving) [Neil Cook]
- `Cal_loc_spirou.py` - change the way calibration files are added to
  header. [Neil Cook]
- `Cal_dark_master_spirou.py` - fix comment. [Neil Cook]
- `SpirouBERV.py` - replace "t" with "jdutc" so all bjds returned. [Neil
  Cook]
- `Calib.science.preprocessing.detector.py` - move loading of full flat to
  `drs_data.py`. [Neil Cook]
- `Calib.science.shape.py` - continue to add functionality from SpirouDRS.
  [Neil Cook]
- `Calib.science.localisation.py` - fix getting localisation coefficients.
  [Neil Cook]
- `Calib.science.badpix.py` - move loading of full flat to `drs_data.py`.
  [Neil Cook]
- `Core.math.general.py` - fix when there are no NaNs (don't interpolate
  linearly) [Neil Cook]
- `Drs_data.py` - first commit: module to control loading of internal drs
  data. [Neil Cook]
- Update language database. [Neil Cook]
- Add line lists and cavity length file. [Neil Cook]
- Add to config parameters. [Neil Cook]
- `Cal_shape_master_spirou.py` - add dxmap and start dymap conversion.
  [Neil Cook]
- `Calib.science.shape.py` - continue to add functionality from SpirouDRS.
  [Neil Cook]
- `Localisation.py/wave.py` - change output return (props only) [Neil
  Cook]
- `Core.math.py` - add fwhm, `iuv_spline`, `median_filter_ea`,
  `gaussian_function_nn`, `gauss_fit_nn`, `gauss_fit_s`. [Neil Cook]
- `Default_constants.py` - add shape constants. [Neil Cook]
- `Cal_shape_master_spirou.py` - change the `get_coefficients`,
  `get_wavesolution`. [Neil Cook]
- `Science.calib.shape.py` - start adding constants for shape master
  dxmap. [Neil Cook]
- `Default_constants.py` - start adding constants for shape master dxmap.
  [Neil Cook]
- `Cal_shape_master_spirou.py` - placeholder for `calculate_dxmap`. [Neil
  Cook]
- `Reprocess.py` - do not scan tmp and reduced files. [Neil Cook]
- `Reprocess.py` - pep8 - remove extra blank space. [Neil Cook]
- `SpirouBACK.py` - correct typo `th_blue_limit` = `p['THERMAL_RED_LIMIT']`
  --> `th_blue_limit` = `p['THERMAL_BLUE_LIMIT']` [Neil Cook]
- `Constants_SPIROU_H4RG.py` - correct typo `THERMAL_BLUE_LIMIT` = 24580 -->
  `THERMAL_BLUE_LIMIT` = 2450 and add `ALLOWED_TELLURIC_DPRTYPES`. [Neil
  Cook]
- `Obj_fit_tellu.py` `obj_mk_tellu.py` - should only process files if
  DPRTPYE is correct, QC should fail if transmission map is all NaNs.
  [Neil Cook]
- `Cal_extract_RAW_spirou.py` - QC should fail if file is all NaNs. [Neil
  Cook]


0.5.029 (2019-06-27)
--------------------
- Update date/version/changelog. [Neil Cook]
- `Science.calib.shape.py` - fix rows missing from `fp_table`. [Neil Cook]


0.5.028 (2019-06-27)
--------------------
- `Science.calib.shape.py` - fix `construct_master_fp` (add `fp_table`
  results) + place holder for `calculate_dxmap`. [Neil Cook]
- `Science.calib.localisation.py` - add `get_coefficients` function. [Neil
  Cook]
- `Science.calib.general.py` - add logging to various steps of
  `calibrate_ppfile`. [Neil Cook]
- `Science.calib.badpix.py` - fix a comment. [Neil Cook]
- `Science.calib.wave.py` - first commit add `get_masterwave_filename` and
  `get_wavesolution` functions. [Neil Cook]
- Update language database. [Neil Cook]
- `File_definitions.py` - add more files to `out_file` file set. [Neil Cook]
- `Recipe_definitions.py` - remove instances of tilt file. [Neil Cook]
- Add default constants/keywords for `shape_master`. [Neil Cook]
- `Drs_startup.py` - fix error reporting in `get_file_definition` and fix
  `found_file` when file not found. [Neil Cook]
- `Drs_file.py` - fix the way keys are read in read/read1d and read2d
  keys. [Neil Cook]
- `Cal_shape_master_spirou.py` - add plan for rest of code add
  localisation and wave files. [Neil Cook]
- `Science.calib.shape.py` - first commit add `fp_master` functions -
  `construct_fp_table`, `construct_master_fp`, `get_linear_transform_params`,
  `ea_transform`, `_max_neighbour_mask` and `_xy_acc_peak`. [Neil Cook]
- `Science.calib.general.py` - first commit add `calibrate_ppfile` function.
  [Neil Cook]
- Science.calib.background/badpix/dark - change the return of calib
  correction functions - now returns fileused + corrected image. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Drs_image.py` - add `clean_hotpix` function. [Neil Cook]
- `Core.math.py` - add fit2dpoly, `linear_minimization` functions. [Neil
  Cook]
- `Recipe_definitions.py` - add `cal_shape_master` and remove `cal_slit`.
  [Neil Cook]
- `Default_constants.py` - add shape master `(fp_master)` constant
  definitions. [Neil Cook]
- `Cal_shape_master_spirou.py` - add master fp generation (untested) [Neil
  Cook]
- `Cal_loc_spirou.py` - update `cal_loc` with changes to how we calibrate
  ppfiles. [Neil Cook]
- `Cal_shape_master_spirou.py` - first commit (placeholder that needs
  filling) [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.5.027 (2019-06-26)
--------------------
- `Drs_path.py` - make sure `night_name` does not start with a separator in
  `"get_nightname`" function. [Neil Cook]
- `Drs_database.py` - allow the addition of the night name to `"add_file`"
  function. [Neil Cook]
- `Cal_dark_master_spirou.py` - add nightname from reference file. [Neil
  Cook]
- `SpirouStartup.py` - remove unused import. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - integrate `_get_time` functionality into `header_time`.
  [Neil Cook]
- `Pseudo_const.py` - add back nirps logo. [Neil Cook]
- `Drs_database.py` - update `_get_time` to use `drs_fits.header_time`. [Neil
  Cook]
- Reorganize config and constants (now all in core sub-module) - update
  module order. [Neil Cook]
- Reorganize config and constants (now all in core sub-module) [Neil
  Cook]
- Reorganize where default settings are kept (now in
  config.instruments.default) -- modifications to fix bugs. [Neil Cook]
- Reorganize where default settings are kept (now in
  config.instruments.default) -- modifications to fix bugs. [Neil Cook]
- Reorganize where default settings are kept (now in
  config.instruments.default) [Neil Cook]
- `Science.calib.dark.py` - correct `dark_master` functionality including
  setup to infile. [Neil Cook]
- `Background.py` - update how debug file is made (with updates to
  `write_multi)` [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_path.py` - change conditions on finding `time_unit` to be astropy
  unit/quantity. [Neil Cook]
- `Drs_fits.py` - update Header class (from @cusher work) [Neil Cook]
- Constants/keywords - add/update values for `dark_master`. [Neil Cook]
- `Drs_startup.py` - fix `get_drs_params` inputs and make warning that code
  did not complete successfully red. [Neil Cook]
- `Drs_file.py` - make corrections to `write_multi` (including new
  `update_header_with_hdict` function) [Neil Cook]
- `Cal_dark_master_spirou.py` - finish converting `dark_master` to
  terrapipe. [Neil Cook]


0.5.026 (2019-06-25)
--------------------
- `Science.calib.dark.py` - add dark master functionality. [Neil Cook]
- Update language database. [Neil Cook]
- Terrapipe.io - add `find_filetypes`, `get_index_files` and `header_time`
  functions. [Neil Cook]
- Constants - add dark master constant definitions. [Neil Cook]
- `Drs_startup.py` - add function `get_file_definition` and update pid
  getting (to add htime) [Neil Cook]
- `File_definitions` - add `dark_master` file definition. [Neil Cook]
- `Cal_dark_master_spirou.py` - first commit and transfer from SpirouDRS.
  [Neil Cook]
- Remove old drsmodule files. [Neil Cook]
- Update version/changelog and date. [Neil Cook]


0.5.025 (2019-06-24)
--------------------
- `Obj_mk_obj_template.py` + spirouTelluric - move location of GetBERV.
  [njcuk9999]
- `SpirouTable.py` - change order of backup operations (always close lock
  file last) [njcuk9999]
- `SpirouTable.py` - fix problem with closing/replacing index.fits.
  [njcuk9999]


0.5.024 (2019-06-24)
--------------------
- `SpirouTable.py` - remove the index file before writing it. [Neil Cook]
- `SpirouRfiles.py` - if reset is true make user confirm it. [Neil Cook]
- `SpirouRfiles.py` - add a raw index file that should save time opening
  already read headers. [Neil Cook]


0.5.023 (2019-06-23)
--------------------
- `SpirouRgen.py` - fix problem when two independent file types defined
  (i.e. `DARK_FLAT` and `FLAT_DARK)` [Neil Cook]
- `SpirouRgen.py` - check that master night name exists (raise error if it
  doesn't) [Neil Cook]


0.5.022 (2019-06-21)
--------------------
- `SpirouRgen.py` - rename `obj_mk_tellu_new` --> `obj_mk_tellu`. [Neil Cook]
- `SpirouFITS.py` - try to create lock directory. [Neil Cook]
- `SpirouBERV.py` - add keys for processing. [Neil Cook]
- `SpirouDB.py` - try to create lock folder if needed. [Neil Cook]
- `SpirouMath.py` - linear bad pix must have at least two non-NaN pixels.
  [Neil Cook]
- `SpirouBACK.py` - deal with thermal being empty or NaN filled entirely.
  [Neil Cook]
- `Obj_mk_tellu_db.py` - renamed `obj_mk_tellu_new` to `obj_mk_tellu`. [Neil
  Cook]
- `Obj_mk_tellu.py` - renamed from `obj_mk_tellu_new.py`. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add berv dtypes. [Neil Cook]
- `Cal_dark_master_spirou.py` - fix type `dark_cube` --> `dark_cube1`. [Neil
  Cook]


0.5.021 (2019-06-20)
--------------------
- `SpirouBERV.py` - update comments to be more specific about inputs.
  [njcuk9999]
- `SpirouBERV.py` - update berv codes to be more specific about units etc.
  [njcuk9999]
- Update berv tests. [njcuk9999]
- `Constants_SPIROU_H4RG.py` - update observatory location. [njcuk9999]


0.5.020 (2019-06-19)
--------------------
- `SpirouKeywords.py` - add keywords to list. [njcuk9999]
- `Berv_error_test.py` - continue testing of berv. [njcuk9999]
- `Reprocess.py` - add back main function. [njcuk9999]
- `SpirouBERVest.py` - degtorad --> deg2rad. [njcuk9999]
- SpirouBERV - testing berv calculation. [njcuk9999]
- SpirouImage/spirouStartup - make sure files is a list (if string make
  a list) [njcuk9999]
- `SpirouLog.py` - add colour option in wlog.printmessage. [njcuk9999]


0.5.019 (2019-06-18)
--------------------
- `SpirouImage.py` - add warning capture for oweight (divide by NaNs okay)
  [njcuk9999]
- `SpirouRfiles.py` - add run directory from param dict. [njcuk9999]
- `Config.py` - add run directory. [njcuk9999]


0.5.018 (2019-06-17)
--------------------
- `SpirouTelluric.py` - add `tau_h20` and `tau_rest` to code. [Neil Cook]
- `SpirouReprocess.py` - add skipping into code. [Neil Cook]
- `SpirouLog.py` - add method: "print message" [Neil Cook]
- `SpirouKeywords.py` - add `tau_h20` and `tau_rest` header keys. [Neil Cook]
- `SpirouConst.py` - update file name function defintions. [Neil Cook]
- `SpirouBACK.py` - correct typo dim2 --> dim1. [Neil Cook]
- `Obj_fit_tellu.py` - add `tau_h20` and `tau_rest` to header. [Neil Cook]
- `Cal_shape_spirou.py` - change debug file defintions (need filename
  defined) [Neil Cook]
- `Cal_preprocess_spirou.py` - make file name come from definition. [Neil
  Cook]


0.5.017 (2019-06-14)
--------------------
- SpirouReprocess - update the reprocessing codes. [Neil Cook]
- `Recipe_defintions.py` - fix some recipe definitions. [Neil Cook]
- `File_definitions.py` - update file definitions. [Neil Cook]


0.5.016 (2019-06-13)
--------------------
- SpirouReprocessing - continue work. [Neil Cook]
- Correct recipe and file definitions for non-input-redo. [Neil Cook]
- `Obj_fit_tellu_db.py` - correct number of required arguments. [Neil
  Cook]


0.5.015 (2019-06-12)
--------------------
- `SpirouReprocess.py` - continue writing code. [Neil Cook]
- `SpirouBACK.py` - fix a problem with one of the returns in
  `correction_thermal`. [Neil Cook]
- `Multiprocess_test.py` - add an event (to terminate all current and
  future jobs on crash) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - update a comment. [Neil Cook]
- Merge branch `'input_redo`' into dev. [Neil Cook]
- Merge branch 'dev' into `input_redo`. [njcuk9999]
- Merge branch 'dev' into `input_redo`. [njcuk9999]
- Merge branch 'dev' into `input_redo`. [njcuk9999]

  # Conflicts:
  #    `INTROOT2/drsmodule/io/drs_lock.py`
- `Drs_lock.py` - Merged 10b82f1 from @cusher into `input_redo`. [njcuk9999]
- Localisation - update parameters for @melissa-hobson. [njcuk9999]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `Localisation.py` - continue work for `cal_loc`. [Neil Cook]
- `Background.py` - fix backfile. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - fix write function having no dtype. [Neil Cook]
- `Constants.default.default_constants.py` - add `fiber_set_num` key. [Neil
  Cook]
- `Config.instruments.spirou.*.py` - add/correct loc keys. [Neil Cook]
- `Drs_file.py` - correct problems with `add_hkeys_2d`. [Neil Cook]
- `Cal_loc_spirou.py` - continue work on input redo `cal_loc`. [Neil Cook]
- `Background.py` - change key for `add_hkey`. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - fix import of `drs_log`. [Neil Cook]
- `General.py` - fix imports. [Neil Cook]
- `Config.instruments.spirou.*.py` - correct keys and constants. [Neil
  Cook]
- `Drs_log.py` - correct the `find_param` function. [Neil Cook]
- `Drs_file.py` - fix when key = keywordstore. [Neil Cook]
- `Drs_database.py` - correct call to `find_param`. [Neil Cook]
- `File_definitions.py` - correct bad extension. [Neil Cook]
- `Cal_loc_spirou.py` - continue fixes to `input_redo` changes. [Neil Cook]
- Update language database. [Neil Cook]
- `Localisation.py` - add `image_superimp` function. [Neil Cook]
- `Drs_fits.py` - move the resize/flip images add convert functions. [Neil
  Cook]
- `Constants.defaults.*.py` - add constants/headers from localisation.
  [Neil Cook]
- Config.math - add `calculate_polyvals` function. [Neil Cook]
- `Instruments.spirou.*.py` - add constants/keywords for localisation.
  [Neil Cook]
- `Drs_file.py` - add method `'copy_hdict`' [Neil Cook]
- `Cal_loc_spirou.py` - continue work on adapting recipe for terrapipe.
  [Neil Cook]
- `Cal_loc_spirou.py` - continue work on adapting recipe for terrapipe.
  [Neil Cook]
- Recipes.spirou - move flip/resize functions. [Neil Cook]
- Update language database. [Neil Cook]
- `Science.calib.localisation.py` - continue work on localisation
  functions. [Neil Cook]
- `Constants.default.*.py` - add localisation constant defintions. [Neil
  Cook]
- `Config.math.general.py` - add `measure_box_min_max`, nanpolyfit. [Neil
  Cook]
- `Config.instruments.spirou.*.py` - add localisation constants. [Neil
  Cook]
- `Output_filenames.py` - make output file function generic. [Neil Cook]
- `File_definitions.py` - make `debug_back` output generic to debug outputs.
  [Neil Cook]
- `Cal_loc_spirou.py` - continue work on porting over `cal_loc`. [Neil Cook]
- `Cal_dark_spirou.py` - modify how combine works for header input files.
  [Neil Cook]
- `Cal_badpix_spirou.py` - modify how combine works for header input
  files. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `Localisation.py` - continue development from `cal_loc`. [Neil Cook]
- `Dark.py` - continue development from `cal_loc`. [Neil Cook]
- `Badpix.py` - continue development from `cal_loc`. [Neil Cook]
- `Background.py` - continue development from `cal_loc`. [Neil Cook]
- Update the language database. [Neil Cook]
- `Drs_fits.py` - work on read/write single and multi functions (should be
  universal) + use @cusher Header class. [njcuk9999]
- `Constants.defaults.*.py` - add `cal_loc` constants. [Neil Cook]
- `Config.__init__.py` - add `find_param` (aliased to pcheck) to `__init__`
  [Neil Cook]
- Config.math - add a general math functions module (and nanpad/killnan
  functions) [Neil Cook]
- `Config.instruments.spirou.*.py` - add `cal_loc` constants and
  definitions. [Neil Cook]
- `Drs_log.py` - upgrade the `find_param` function to look in kwargs if
  definied. [Neil Cook]
- `Drs_file.py` - move read and write to io module. [Neil Cook]
- `Config.core.default.*.py` - add loc constants and definitions. [Neil
  Cook]
- `Cal_loc_spirou.py` - continuing copying over and converting code. [Neil
  Cook]
- `Cal_badpix_spirou.py` - make sure images are np.array copies. [Neil
  Cook]
- `Science/calib/dark.py` - add dark correction function. [Neil Cook]
- `Drs_table.py` - generalise lock functions. [Neil Cook]
- `Drs_path.py` - pep8 corrections. [Neil Cook]
- `Drs_lock.py` - generalise lock functions. [Neil Cook]
- Constants/default - add initial `cal_loc` constants. [Neil Cook]
- Config/instruments/spirou - add initial `cal_loc` constants. [Neil Cook]
- `Drs_startup.py` - make lock functions more general and only index if
  recipe was successful. [Neil Cook]
- `Drs_database.py` - add first methods for new Database class. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Cal_loc_spirou.py` - first commit [unfinished] [Neil Cook]
- `Badpix.py` - fix bugs with conversion. [Neil Cook]
- Update language database. [Neil Cook]
- `Default_keywords` - add default badpix keyword definitions. [Neil Cook]
- `Default_constant.py` - add input kwargs. [Neil Cook]
- `Recipe_definitions.py` - finalise `cal_badpix` definition. [Neil Cook]
- `Output_filenames.py` - add `badpix_file` and `backmap_file`. [Neil Cook]
- `File_definitions.py` - add `out_badpix` and `out_backmap` output files.
  [Neil Cook]
- `Default_keywords.py` - add badpix header keywords. [Neil Cook]
- `Default_constants.py` - add input kwargs. [Neil Cook]
- `Cal_preprocess_spirou.py` - add dimanme for header of `KW_INFILE1`. [Neil
  Cook]
- `Cal_dark_spirou.py` - change `__NAME__` to all lower case. [Neil Cook]
- `Cal_badpix_spirou.py` - update and finish first test. [Neil Cook]
- `Badpix.py` - first commit - space for bad pixel map functions. [Neil
  Cook]
- `Background.py` - first commit space for background functions. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - add `flip_image` function. [Neil Cook]
- `Default_config.py` - add badpix values. [Neil Cook]
- `Default_config.py` - add badpix values. [Neil Cook]
- `Cal_dark_spirou.py` - change name of parmeter for combining files on
  input. [Neil Cook]
- `Cal_badpix_spirou.py` - first commit [UNFINISHED] [Neil Cook]
- `Default_config.py` - update version. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `Drs_reset.py` - first commit of reset code. [Neil Cook]
- `Drs_changelog.py` - add comments and move text to language database.
  [Neil Cook]
- Update language database. [Neil Cook]
- Update language database. [Neil Cook]
- `Default_config.py` - update version and date. [Neil Cook]
- `Drs_changelog.py` - make sure we define outputs=None for recipe without
  outputs. [Neil Cook]
- `Psuedo_const.py` - deal with `DRS_DATA_MSG` being None. [Neil Cook]
- `Drs_changelog.py` - preview is in params['INPUT'] [Neil Cook]
- `Recipe_definitions.py` - add definition for `drs_changelog`. [Neil Cook]
- `Drs_startup.py` - allow no instrument to search for recipe name. [Neil
  Cook]
- Update language database. [Neil Cook]
- `Param_functions.py` - force printing to string. [Neil Cook]
- `Drs_changelog.py` - update with new locations. [Neil Cook]
- `Default_config.py` - give more space for version. [Neil Cook]
- `Drs_changelog.py` - correct number of arguments for
  `get_relative_folder`. [Neil Cook]
- `Recipe_definitions.py` - add change log definition. [Neil Cook]
- Update database. [Neil Cook]
- `Drs_changelog.py` - first commit of drs changelog for input redo. [Neil
  Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `Drs_startup.py` - end with header. [Neil Cook]
- `Drs_log.py` - tidy up logging messages. [Neil Cook]
- `Drs_log.py` - tidy up logging messages. [Neil Cook]
- `Drs_file.py` - remove references to hdict comments (now in fits.Header)
  [Neil Cook]
- `Drs_argument.py` - do not print info. [Neil Cook]
- Change text message. [Neil Cook]
- Change text message. [Neil Cook]
- `Drs_startup.py` - edit title. [Neil Cook]
- `Dark.py` - remove warning about NaNs. [Neil Cook]
- `Drs_database.py` - change how we access hdict. [Neil Cook]
- `Drs_file.py` - deal with how to access hdict. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_startup.py` - edit logo. [Neil Cook]
- `Drs_file.py` - header is now fits.Header not OrderedDict. [Neil Cook]
- Rename drs to terrapipe. [Neil Cook]
- Rename drs to terrapipe. [Neil Cook]
- Merge branch 'dev2' into `input_redo`. [Neil Cook]
- Merge branch 'dev2' into `input_redo`. [Neil Cook]
- `Recipes.spirou.cal_preprocess_spirou.py` - chmod +x. [njcuk9999]
- `Recipes.spirou.cal_dark_spirou.py` - chmod +x. [njcuk9999]
- `Config.instruments.spirou.default_keywords.py` - correct `KW_EXT_TYPE`
  value (was a typo) [njcuk9999]
- `Drs_startup.py` - don't try to create folders when we don't have
  nightname. [njcuk9999]
- `File_explorer.py` - define a path for ds9 (will need moving to some
  installation specific place) and better deal with index col
  differences in error report. [njcuk9999]
- `Constants.default.pseudo_const.py` - add changes from old code (version
  and pversion in index.fits) [njcuk9999]
- `Config.core.drs_file.py` - fix bug "copy" --> "copyother" [njcuk9999]
- Refactor new --> newcopy   and copy --> copyother. [Neil Cook]
- Update datacutmask. [Neil Cook]
- Update language database. [Neil Cook]
- Update constants/config/keywords. [Neil Cook]
- `Drs_recipe.py` - update functions after run through. [Neil Cook]
- `Drs_file.py` - update functions after run through. [Neil Cook]
- `Drs_database.py` - update functions after run through. [Neil Cook]
- Channge ErrorEntry and ErrorText to TextEntry and TextDict. [Neil
  Cook]
- `Drs_fits.py` - deal with zero and one infiles separately. [Neil Cook]
- Update language database. [Neil Cook]
- Update constants files. [Neil Cook]
- Delete drsmodule.config.database (moved to core in single `.py` file)
  [Neil Cook]
- `Drs_startup.py` - add run function (to keep recipes clean) [Neil Cook]
- `Drs_database.py` - update datebase setting (combine calib and telluric)
  [Neil Cook]
- `Cal_preprocess_spirou.py` - update qc to match `cal_dark`. [Neil Cook]
- `Cal_dark_spirou.py` - flesh out functionality. [Neil Cook]
- `Drsmodule.science.calib.dark.py` - add `measure_dark_badpix` function.
  [Neil Cook]
- Update language database. [Neil Cook]
- Drsmodule.constants.default - add dark keys. [Neil Cook]
- Drsmodule.config.instrument.spirou - add dark keys. [Neil Cook]
- Drsmodule.config.database - first commit of database.py, calibdb.py,
  telludb.py. [Neil Cook]
- `Cal_dark_spirou.py` - fill out more of the sections. [Neil Cook]
- `Dark.py` - first commit add `measure_dark` function. [Neil Cook]
- `Drs_fits.py` - add combine and resize functions. [Neil Cook]
- Update language database. [Neil Cook]
- Add new constants to constants/keyword files. [Neil Cook]
- `Drs_log.py` - add `find_param` logger function. [Neil Cook]
- `Drs_file.py` - add combine and `get_key` functions. [Neil Cook]
- `Blank_spirou.py` - update the blank example script. [Neil Cook]
- `Cal_preprocess_spirou.py` - move file processing to
  `config.file_processing_update`. [Neil Cook]
- `Cal_dark_spirou.py` - start filling out code. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_fits.py` - add skeleton for combine function. [Neil Cook]
- `Drsmodule.constants.default.default_constants.py` - add `COMBINE_IMAGES`
  constant. [Neil Cook]
- `Drsmodule.config.__init__.py` - link to `file_processing_update`. [Neil
  Cook]
- `Instruments.spirou.recipe_definitions.py` - add default value for
  combine option. [Neil Cook]
- `Instruments.spirou.default_constants.py` - add `combine_images` constant.
  [Neil Cook]
- `Drs_startup.py` - add general file processing logger. [Neil Cook]
- `Recipes.spirou.cal_preprocessing_spirou` - continue `input_redo`. [Neil
  Cook]
- Drsmodule.science.preprocessing - continue `input_redo`. [Neil Cook]
- Drsmodule.locale - continue `input_redo`. [Neil Cook]
- Drsmodule.io - continue `input_redo`. [Neil Cook]
- Drsmodule.constants.default - continue `input_redo`. [Neil Cook]
- Drsmodule.config.instruments - continue `input_redo`. [Neil Cook]
- Drsmodule.config.core - continue `input_redo`. [Neil Cook]
- Drsmodule.science.preprocessing - continue `input_redo`. [Neil Cook]
- Drsmodule.locale - continue `input_redo`. [Neil Cook]
- Drsmodule.io - continue `input_redo`. [Neil Cook]
- Drsmodule.data - continue `input_redo`. [Neil Cook]
- Drsmodule.constants.default - continue `input_redo`. [Neil Cook]
- Drsmodule.constants.core - continue `input_redo`. [Neil Cook]
- Drsmodule.config.instruments.spirou - continue `input_redo`. [Neil Cook]
- Drsmodule.config.core - continue `input_redo`. [Neil Cook]
- `SpirouRecipe.py` - continue `input_redo`. [Neil Cook]
- `Test_spirou.py` - remove bad code (test to crash) [Neil Cook]
- `Identification.py` - check file by copying `drs_file` over `given_drs_file`
  and then use `self.check_file()` [Neil Cook]
- `Drs_recipe.py` - move checking functionality to `drs_file`. [Neil Cook]
- `Dsr_file.py` - add copy function to `drs_file`. [Neil Cook]
- Update language file. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `Identification.py` - start writing code to identify drs file. [Neil
  Cook]
- `File_definitions` - change append to addset. [Neil Cook]
- `Drs_file.py` - addset functions and plan new checking functions. [Neil
  Cook]
- Update input redo - work on `cal_preprocess`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Continue working on upgrade. [Neil Cook]
- Continue working on upgrade. [Neil Cook]
- Update language database. [njcuk9999]
- Add placeholders for preprocessing functions. [njcuk9999]
- Add spirou preprocessing recipe. [njcuk9999]
- Update test recipes. [njcuk9999]
- Fix module pathing system. [njcuk9999]
- `Config.__init__.py` - add alias to `get_locals`. [njcuk9999]
- `Recipe_definitions` - update preprocessing defintion. [njcuk9999]
- `Default_config.py` - make plot variables an int. [njcuk9999]
- `Drs_startup.py` - add temp messgae for loading arguments + add a code
  unsuccessful message. [njcuk9999]
- `Drs_recipe.py` - change INPUT --> INTPUTS + make param dict.
  [njcuk9999]
- `Drs_log.py` - sort out `LOGGER_ERROR` etc (now stored per PID + add
  Printer class (TLOG) to print temporary messages which disappear if no
  other text inbetween. [njcuk9999]
- `Drs_argument.py` - add a new line in the debug messages (for Printer to
  be on new line) [njcuk9999]
- Add `__init__.py` files to new folders. [njcuk9999]
- `Port_database.py` - output more log messages. [njcuk9999]
- `Test_spirou.py` - fix function call. [njcuk9999]
- Update language database. [njcuk9999]
- `Constants_functions.py` - fix problem with relative imports.
  [njcuk9999]
- `Recipe_definitions.py` - make plot and integer and only allow values 0,
  1, 2. [njcuk9999]
- `Drs_startup.py` - fix the printing of arg log strings (arguments used)
  [njcuk9999]
- `Drs_recipe.py` - fix missed error (should be from database) [njcuk9999]
- `Drs_arguemnt.py` - allow arguments to specify a min and max value (and
  check for it) [njcuk9999]
- Attempt to remove relative imports. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `File_explorer.py` - move data loading / mask applying to different
  threads. [Neil Cook]
- `*.__init__.py` - fix imports (should be empty) [Neil Cook]
- `Locale.core.__init__.py` - fix imports (should be empty) [Neil Cook]
- `File_explorer.py` - update length and add new instrument box. [Neil
  Cook]
- `File_explorer.py` - update about statement. [Neil Cook]
- `File_explorer.py` - continue upgrade. [Neil Cook]
- `File_explorer.py` - continue upgrade. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- `File_explorer.py` - continue to write code. [Neil Cook]
- `File_explorer.py` - add table. [Neil Cook]
- `Config.__init__.py`: add aliases to `__all__` [Neil Cook]
- Drsmodule.io - need to import `drs_log` separately `(drs_startup` uses
  `drs_table)` [Neil Cook]
- `Find_error` - change comment to better represent section. [Neil Cook]
- `Combine_index_files.py` - pep8 changes. [Neil Cook]
- `File_explorer.py` - app to find drs files. [Neil Cook]
- `Drs_table.py` - update doc strings. [Neil Cook]
- `Drs_table.py` - update doc strings. [Neil Cook]
- `Drs_lock.py` - update doc strings. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Added a misc folder and a first misc script. [Neil Cook]
- `Recipes/test/*` - update paths to `drs_setup` (via config) [Neil Cook]
- `__init__.py` - add a functions section (currently blank) [Neil Cook]
- `Tools.*` - update paths to `drs_setup` (via config) [Neil Cook]
- `Plotting.*` - update paths to `drs_setup` (via config) [Neil Cook]
- `Io.*` - update paths to `drs_setup` (via config) [Neil Cook]
- `Config.__init__.py` - add aliases to functions that will be used lots.
  [Neil Cook]
- `Drs_startup.py` - continue improvements to documentation. [Neil Cook]
- `User_config.ini[NIRPS]` - update `DRS_PLOT` value and comment (now an int
  [0, 1, 2]) [Neil Cook]
- `Drs_text.py` - make `get_relative_folder` a public function. [Neil Cook]
- `Find_error.py` - update doc strings to pep8 standards. [Neil Cook]
- `Find_error.py` - update comments. [Neil Cook]
- `Find_error.py` - add drop down instrument box. [Neil Cook]
- `Find_error.py` - improve gui. [Neil Cook]
- `Drs_setup` - add better doc strings. [Neil Cook]
- `Find_error.py` - continued to work on application. [njcuk9999]
- `Drs_text.py` - got args for language database reads. [njcuk9999]
- `Constant_functions.py` - added the source to dtype errors in config
  files. [njcuk9999]
- `Drs_startup.py` - allowed instrument to be None. [njcuk9999]
- Tool to find error codes in database/code. [njcuk9999]
- Drs general - initialise new sub package folders. [Neil Cook]
- Drs general - initialise new sub package folders. [Neil Cook]
- Merge remote-tracking branch `'origin/input_redo`' into `input_redo`.
  [Neil Cook]

  Conflicts:
      `INTROOT2/drsmodule/config/core/drs_startup.py`
- `Default_config.py` - add `DRS_DATA_PLOT`. [Neil Cook]
- Add `drs_data_plot` to start up parameters. [Neil Cook]
- `Drs_recipe.py` - change plotting mode - only if `drs_plot` is 1 (to
  screen) [Neil Cook]
- `User_config.ini` - add plot modes (instead of bool) [Neil Cook]


0.5.014 (2019-06-11)
--------------------
- `SpirouReprocess.py` - add processing (parallalised) to reprocess. [Neil
  Cook]
- `SpirouImage.py` - fix small bug with position of log message. [Neil
  Cook]
- `Multiprocess_test.py` - test of multiple. [Neil Cook]


0.5.013 (2019-06-10)
--------------------
- `SpirouReprocess.py` - first commit reworking of reprocessing script and
  run files (works for unit test and any/all reprocessing) [Neil Cook]
- Correct names. [Neil Cook]
- Bin folder - add `__args__` and `__required__` [Neil Cook]
- `SpirouImage.py` - add in shape qc. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add in shape qc. [Neil Cook]
- `Cal_shape_master_spirou.py` - add in QC (std of shape map) [Neil Cook]
- `SpirouConst.py` - remove overlap file and add `SLIT_SHAPE_BDXMAP_FILE`
  debug file. [Neil Cook]
- `Cal_shape_spirou.py` - produce debug plots to check transform for the
  input fp file + save master shape (x/y) files to header. [Neil Cook]
- `Cal_shape_master_spirou.py` - straighten the dxmap (using dymap) and
  save the bent dxmap as debug product. [Neil Cook]
- `SpirouBACK.py` - add `correction_thermal2` functionality. [Neil Cook]
- `Recipe_control.txt` - add new name for `cal_shape_master`
  `(cal_shape_master_spirou)` [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add more thermal constants and correct
  thermal correction types to single fiber values. [Neil Cook]
- `Cal_shape_master_spirou.py` - correct both dx and dy maps. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - thermal correction must be based on
  individual fiber type not DPRTYPE. [Neil Cook]


0.5.012 (2019-06-08)
--------------------
- `SpirouUnitRecipes.py` - remove `cal_SHAPE_spirou` and add
  `cal_shape_spirou`. [Neil Cook]
- `SpirouImage.py` - add new loading functions (for new calibDB files)
  [Neil Cook]
- `SpirouPlot.py` - add new `thermal_background_debug_plot` function. [Neil
  Cook]
- `SpirouKeywords.py` - add shape and new cdb keys. [Neil Cook]
- `SpirouConst.py` - add `SLIT_SHAPE_LOCAL_FILE` + fix `slit_SHAPE` functions.
  [Neil Cook]
- `SpirouBACK.py` - add `correction_thermal`, `correction_thermal1` and
  `correction_thermal2`. [Neil Cook]
- `Reset_calibDB` - add `tapas_all_sp.fits.gz` to calibDB. [Neil Cook]
- `Recipe_control.txt` - add `cal_shape_spirou.py`. [Neil Cook]
- `Output_keys.py` - add local shape to tags. [Neil Cook]
- `Cal_SHAPE_spirou.py` - moved from bin folder (now old code) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add thermal constants. [Neil Cook]
- `Cal_shape_spirou.py` - first commit new local shape recipe. [Neil Cook]
- `Cal_shape_master_spirou.py` - put FPMASTER in calibDB. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - add FP master file getting. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add thermal correction (untested) [Neil
  Cook]


0.5.011 (2019-06-07)
--------------------
- `Cal_shape_master.py` - apply dxmap and dymap + remove reference to
  FPFILES (--> FPFILE) [Neil Cook]
- `SpirouLOCOR.py` - add modifications for new shape parameters. [Neil
  Cook]
- `SpirouImage.py` - continue working on new shape functionality. [Neil
  Cook]
- `SpirouEXTOR.__init__.py` - add alias to CleanHotpix. [Neil Cook]
- `SpirouMath.py` - change how IUVSpline deals with NaNs (full set of NaNs
  and group of Nans --> fill with linear interp) [Neil Cook]
- `SpirouKeywords.py` - add backgroun key and new shape header keys. [Neil
  Cook]
- `SpirouBACK.py` - return background filename for adding to header. [Neil
  Cook]
- `Cal_shape_master.py` - correct change to table (needed extra term)
  [Neil Cook]
- `Cal_SHAPE_spirou_old.py` - add changes for background file loading.
  [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add shape master/local qc parameters. [Neil
  Cook]
- `Cal_SLIT_spirou.py` - add changes for background file loading. [Neil
  Cook]
- `Cal_shape_master.py` - add changes from Etiennes redo. [Neil Cook]
- `Cal_loc_RAW_spirou.py` - add changes for background file getting. [Neil
  Cook]
- `Cal_ff_raw_spirou.py` - add changes for new shape files. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add changes for new shape files. [Neil
  Cook]


0.5.010 (2019-06-06)
--------------------
- `SpirouImage.py` - add `get_x_shape_map` and `get_y_shape_map` functions and
  aliases. [Neil Cook]
- `SpirouPlot.py` - add `shape_linear_trans_param_plot` debug plot. [Neil
  Cook]
- `SpirouConst.py` - add dxmap, dymap and fpmaster file defintions. [Neil
  Cook]
- `Output_keys.py` - add dxmap, dymap and fpmaster file tags. [Neil Cook]
- `Register_fp_2.py` - add etiennes additional changes. [Neil Cook]
- `Cal_SHAPE_spirou_old.py` - refractor file name. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add new `shape_master` constants. [Neil Cook]
- `Cal_shape_master.py` - continue adapting `cal_shape_master` to handle
  dxmap and dymap. [Neil Cook]
- `Cal_SHAPE_spirou.py` - refractor filename (now need sape x and shape y)
  [Neil Cook]
- `Cal_shape_master.py` - continue adding etiennes changes. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - write todos. [Neil Cook]


0.5.009 (2019-06-05)
--------------------
- `SpirouImage.py` - start adding etiennes new adaptations to
  `register_fp_2`. [Neil Cook]
- `Register_fp_2.py` - add etiennes new register fp code. [Neil Cook]
- `Calc_berv.py` - add berv source / berv est. [Neil Cook]
- `SpirouTelluric.py` - move `get_berv_value` to spirouImage(spirouBERV)
  [Neil Cook]
- `SpirouBERV.py` - add `get_berv_value` and modify current functions to add
  berv estimate + lock berv while calculating barycorrpy. [Neil Cook]
- `SpirouTDB.py` - correct pep8. [Neil Cook]
- `SpirouKeywords.py` - add berv est and berv source. [Neil Cook]
- `Test_bigcube_berv.py` - add `berv/berv_est` test. [Neil Cook]
- `Obj_mk_tellu_new.py` - change how berv is obtained. [Neil Cook]
- `Obj_fit_tellu.py` - change how berv is obtained. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add berv estimate and berv source. [Neil
  Cook]
- `Cal_CCF_E2DS_spirou.py` - add berv estimate and berv source. [Neil
  Cook]
- `Berv_estimate_comparison.py` - test and compare berv estimate to
  barycorrpy. [Neil Cook]


0.5.008 (2019-06-04)
--------------------
- `SpirouImage.py` - correction to `register_fp`. [Neil Cook]
- `SpirouKeywords.py` - estimated BERV keys added. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - estimated BERV keys added to hdict. [Neil
  Cook]
- `SpirouBERV.py` - add implementation of `BERV_EST` and use lock file to
  only open one BERV instance. [Neil Cook]
- `SpirouEXTOR.py` - add quick mode for `clean_hotpix`. [Neil Cook]
- `Merge_fp_fp.py` - correct typo for print statement. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add a way to turn off certain features that
  slow down the code (not to be used for science data) [Neil Cook]
- `SpirouImage.py` - correct `construct_master_fp`. [njcuk9999]


0.5.007 (2019-06-03)
--------------------
- `Cal_shape_master.py` - continued work integrating fp master function.
  [njcuk9999]
- `SpirouImage.py` - continued work on FP master functions. [njcuk9999]
- `Cal_shape_master.py` - change input to 1 hchc and 1 fpfp. [njcuk9999]
- `SpirouImage.py` - add `construct_master_fp`, `group_files_by_time` and
  `register_fp` functions (for `cal_shape_master` and `cal_dark_master)`
  [njcuk9999]
- `Recipe_control.txt` - add `cal_shape_master.py` to recipe control.
  [njcuk9999]
- `Merge_fp_fp.py` - etiennes merge fp code. [njcuk9999]
- `Constants_SPIROU_H4RG.py` - add the `cal_shape_master` constants.
  [njcuk9999]
- `Cal_shape_master.py` - first commit - copy of `cal_SHAPE_spirou.py` -
  with additions from Etienne for making the fp master file. [njcuk9999]
- `Cal_dark_master_spirou.py` - remove code in common with shape master
  into function. [njcuk9999]
- Merge branch 'neil' into dev. [njcuk9999]
- Merge pull request #566 from njcuk9999/header-copy-exact. [Neil Cook]

  Header Copy Exact -- also implemented into INTROOT2 in `input_redo` branch
- Merge pull request #565 from njcuk9999/db-lock-fix. [Neil Cook]

  DB lock check retry bug - Okay this one I can merge with both INTROOT and INTROOT2!
- Fixed a bug with db locking check. [Chris Usher]


0.5.006 (2019-06-01)
--------------------
- Updated to match changes on dev. [Chris Usher]
- Reworked how fits headers are used. [Chris Usher]
- Update test.run. [Neil Cook]
- `SpirouImage.py` - change dark calibration to `dark_master` calibration,
  make sure `read_raw_data` loading primary data array. [Neil Cook]
- `SpirouFITS.py` - adjust `read_raw_data` to add an imageext (otherwise
  defaults 0) [Neil Cook]
- `Recipe_control.txt` - add `cal_dark_master` and `cal_thermal_spirou`. [Neil
  Cook]
- `Cal_thermal_spirou.py` - renamed from `cal_thermal2_spirou.py`. [Neil
  Cook]


0.5.005 (2019-05-30)
--------------------
- `SpirouBERVest.py` - first commit (test of berv estimate) [Neil Cook]
- `SpirouConst.py` - add filename to `EXTRACT_E2DS_FILE`. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add `always_extract`. [Neil Cook]
- `Cal_thermal_spirou.py` - continue work. [Neil Cook]
- `Cal_thermal2_spirou.py` - extraction of darks (using `cal_extract)` [Neil
  Cook]
- Merge branch 'thermal' into dev. [Neil Cook]
- Merge branch 'master' into thermal. [njcuk9999]
- First commit of thermal recipe for Low pass dark/thermal calibration.
  [njcuk9999]
- Add fiber to header. [Neil Cook]
- Add `"DRS_DATE`" and `"DATE_NOW`" to all recipes. [Neil Cook]
- `Cal_dark_master_spirou.py` - fix bugs in while loop. [Neil Cook]


0.5.004 (2019-05-29)
--------------------
- `SpirouImage.py` - correct `get_files` function. [Neil Cook]
- `SpirouEXTOR.py` - fix comment typos. [Neil Cook]
- `SpirouKeywords.py` - add dark master keys. [Neil Cook]
- `SpirouConst.py` - add `DARK_FILE_MASTER` function. [Neil Cook]
- `Output_keys.py` - add `dark_master_file` tag. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add `cal_dark_master` constants. [Neil Cook]
- `Cal_DARK_spirou.py` - correct typo. [Neil Cook]
- `Cal_dark_master_spirou.py` - continue adapting new recipe. [Neil Cook]


0.5.003 (2019-05-28)
--------------------
- `SpirouImage.py` - add `get_files` function. [njcuk9999]
- `SpirouImage.py` - add `get_files` function. [njcuk9999]
- `Hp_dark.py` - store EA `cal_dark_master` code (raw) [njcuk9999]
- `Constants_SPIROU_H4RG.py` - add `dark_master` constant to constants.
  [njcuk9999]
- `Cal_dark_master_spirou.py` - first commit - first integration of EA
  code. [njcuk9999]
- `SpirouKeywords.py` - INFILE should be INF1, INF2, INF3. [njcuk9999]
- Update date/version/changelog. [njcuk9999]
- `Cal_HC_E2DS_EA_spirou.py` - CDBBAD --> CDBLAZE. [njcuk9999]


0.5.002 (2019-05-27)
--------------------
- `SpirouPlot.py` - add `output_rv` to `ccf_rv_ccf_plot`. [njcuk9999]
- `SpirouKeywords.py` - add new CCF keyword defintions. [njcuk9999]
- `Cal_CCF_E2DS_spirou.py` - renamed from `cal_CCF_E2DS_FP_spirou.py`.
  [njcuk9999]
- Deal with move of `cal_CCF_E2DS_FP_spirou.py`. [njcuk9999]
- Move older CCF recipes to misc folder. [njcuk9999]
- Removed old `cal_CCF_E2DS_spirou.py`. [njcuk9999]
- `Cal_CCF_E2DS_spirou.py` - from `cal_CCF_E2DS_FP.py` + cosmetic changes.
  [njcuk9999]
- `Cal_CCF_E2DS_FP_spirou.py` - add changes to allow science without FP.
  [njcuk9999]
- `Cal_FF_RAW_spirou.py` - `IC_EXTRACT_TYPE` --> `IC_FF_EXTRACT_TYPE` (always
  for `cal_FF)` [njcuk9999]
- `SpirouTelluric.py` - change parameter name `MKTELLU_MED_SAMPLING` -->
  `IMAGE_PIXEL_SIZE`. [njcuk9999]
- `SpirouLOCOR.py` - add curve drop parameter. [njcuk9999]
- `Constants_SPIROU_H4RG.py` - change loc threshold. [njcuk9999]
- `SpirouKeyword.py` - Add key word for CCF (telluric cut) [njcuk9999]
- `Constants_SPIROU_H4RG.py` - add new constants for CCF. [njcuk9999]
- `Cal_loc_RAW_spirou.py` - correct a bug in DEBUG (should be > 0)
  [njcuk9999]
- `Cal_CCF_E2DS_FP_spirou.py` - add changes from @Francois for CCF masked
  by tellurics. [njcuk9999]
- `Cal_CCF_E2DS_FP_spirou_new.py` - modify line endings. [njcuk9999]
- `Cal_CCF_E2DS_FP_spirou_new.py` - francois changes to cal ccf (to be
  integrated into `cal_CCF` actual) [njcuk9999]


0.5.001 (2019-05-27)
--------------------
- Merge branch 'master' into neil. [Neil Cook]
- `SpirouConst.py` - fix s1d names. [Neil Cook]
- `SpirouStartup.py` - fix the windows/unix `night_name` bug. [Neil Cook]
- SpirouFITS.py, `spirouDB.py` - reset. [Neil Cook]
- SpirouFITS.py, `spirouDB.py` - fix problem with windows and lock file
  including paths that do not exist (i.e. when using night names with
  sub-directories) [Neil Cook]
- SpirouFITS.py, `spirouDB.py` - fix problem with windows and lock file
  including paths that do not exist (i.e. when using night names with
  sub-directories) [Neil Cook]
- SpirouFITS.py, `spirouDB.py` - fix problem with windows and lock file
  including paths that do not exist (i.e. when using night names with
  sub-directories) [Neil Cook]
- `Extract_trigger.py` - update run. [Neil Cook]
- `SpirouConst.py` - `_w_` --> `_v_` [Neil Cook]
- Update settings for reprocess extract tellu/obj run for May
  pernight/perrun runs. [Neil Cook]
- Move unused test modules to misc. [Neil Cook]
- `Drs_dependencies.py` - add a debug mode. [Neil Cook]
- `Select_per_tc_per_night_calibs.py` - add Feb and April runs to the per
  run selection. [Neil Cook]
- Update date/version/update notes/changelog. [Neil Cook]


0.5.000 (2019-05-10)
--------------------
- `SpirouDB.py` - add lock file in waiting printout. [Neil Cook]
- `SpirouPlot.py` - attempt to `setup_figure` a second time before crashing.
  [Neil Cook]
- `SpirouPlot.py` - attempt to `setup_figure` a second time before crashing.
  [Neil Cook]
- Update test.run. [Neil Cook]
- `SpirouPlot.py` - fix to plot crash. [Neil Cook]
- Update changelog.md. [Neil Cook]
- `Extract_trigger.py` - modify extract trigger. [Neil Cook]
- `SpirouTDB.py` - add locking of file in `put_file`. [Neil Cook]
- `SpirouCDB.py` - add locking of file in `put_file`. [Neil Cook]
- Update date and changelog. [Neil Cook]
- `SpirouCDB.py` - fix calibDB file copy in parallisation. [Neil Cook]
- `Extract_trigger.py` - note problem with parallisation. [Neil Cook]
- Update changelog.md. [Neil Cook]
- `Extract_trigger.py` - update comments. [Neil Cook]
- Changelog.md - update the change log with new commits. [Neil Cook]
- Update test.run. [Neil Cook]
- `Extract_trigger.py` - add email option (start + end) [Neil Cook]
- `SpirouPlot.py` - add fix for large files saved to disk (should be
  temporary fix) [Neil Cook]
- `SpirouLOG.py` - clear out logs after run. [Neil Cook]
- `SpirouImage.py` - replace `IC_S1D_BLAZE_MIN` with `TELLU_CUT_BLAZE_NORM`.
  [Neil Cook]
- `SpirouConst.py` - update version/changelog/constants file. [Neil Cook]
- `Comp_s1d_to_s2d.py` - add a normalised blaze cut. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - change the blaze min value. [Neil Cook]
- `Comp_s1d_to_s2d.py` - compare the output of s1d to s2d. [Neil Cook]
- Test.run - update text.run. [Neil Cook]
- `Time_log_file.py` - code to measure timing of log printouts. [Neil
  Cook]
- `Constnats_SPIROU_H4RG.py` - update s1d starting wavelength from 980 to
  965. [Neil Cook]
- Changed permissions on new tools in spirouTools. [Neil Cook]
- `SpirouMath.py` - add nanpad and killnan functions. [Neil Cook]
- `SpirouBACK.py` - re-add warning around backmask condition. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - chagne `IC_BKGR_BOXSIZE` from 64 to 128.
  [Neil Cook]
- `Drs_local_background.py` - first commit - code to find amplitude scale
  for local background (using `DARK_FLAT)` [Neil Cook]
- `SpirouPlot.py` - add `local_scattered_light_plot`. [Neil Cook]
- `SpirouBACK.py` - add function `make_local_background_map` and
  `measure_local_background`. [Neil Cook]
- `Recipe_control.txt` - add `drs_local_background` to valid receipes. [Neil
  Cook]
- `Constants_SPIROU_H4RG.py` - add constants for `drs_local_background.py`.
  [Neil Cook]
- `Constants_SPIROU_H4RG.py` - update `ic_bkgr_percent` value. [Neil Cook]
- `SpirouBACK.py` - add adjustments to background correction. [Neil Cook]
- `SpirouBACK.py` - fix some bugs with measure background from map
  function. [Neil Cook]
- Update test.run. [Neil Cook]
- `Cal_BADPIX_spirou.py` - background addition - fix typo in new file
  upload to calibDB. [Neil Cook]
- `SpirouBACK.py` - return background image only. [Neil Cook]
- `Cal_extract,FF,loc,SHAPE,slit` - replace old background measurement
  with new one. [Neil Cook]
- `SpirouBACK.py` - correct bug in new function. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - change background from 5 to 10. [Neil Cook]
- `Cal_BADPIX_spirou.py` - resize flat as well as bad pixel. [Neil Cook]
- `SpirouImage.py` - add function `get_background_map`. [Neil Cook]
- `SpirouConst.py` - add function `BKGD_MAP_FILE`. [Neil Cook]
- `SpirouBACK.py` - add functions: `make_background_map` and
  `measure_background_from_map`. [Neil Cook]
- `Output_keys.py` - add background map tag. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add new background map constants. [Neil
  Cook]
- `Cal_BADPIX_spirou.py` - add the background map making and save to
  calibDB. [Neil Cook]
- Merge branch 'dev2' [Neil Cook]

  Conflicts:
      INTROOT/SpirouDRS/spirouUnitTests/Runs/test.run
- Remove CHANGELOG.md. [Neil Cook]
- Update changelog. [Neil Cook]
- Test.run. [Neil Cook]


0.4.123 (2019-05-03)
--------------------
- `Drs_changelog_2.py` - update comments for new changelogger. [Neil Cook]
- `Extract_trigger.py` - update bugs. [Neil Cook]
- `SpirouUnitRecipes.py` - update for `fit_tellu_db`. [Neil Cook]
- `Extract_trigger.py` - update for `fit_tellu_db`. [Neil Cook]
- `SpirouTelluric.py` - remove the print statement. [Neil Cook]
- `Obj_fit_tellu_db.py` - add in second making of the target template.
  [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- `Drs_changelog_2.py` - add changes to allow preview mode. [Neil Cook]
- `Obj_fit_tellu_db.py` - correct type in wlog message. [Neil Cook]
- `SpirouTelluric.py` - p['OBJECTS'] when None will be a string. [Neil
  Cook]
- `Obj_fit_tellu_db.py` - add full run through 1. `fit_tellu` 2. `mk_template`
  3. `fit_tellu`. [Neil Cook]
- `SpirouTelluric.py` - need to clean out sys.argv before running codes.
  [Neil Cook]
- `SpirouDB.py` - need to make sure folder exists otherwise lock will
  persist. [Neil Cook]
- `Obj_fit_tellu_db.py` - correct bug in writing code. [Neil Cook]
- `SpirouTelluric.py` - add `find_objects` function and alias. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - correction to comments. [Neil Cook]
- `Obj_fit_tellu_db.py` - first commit of fit tellu db redo. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.122 (2019-05-02)
--------------------
- `Drs_changelog_2.py` - add updating of drs files. [Neil Cook]
- `Drs_changelog_2.py` - add updating of drs files. [Neil Cook]
- `Update_fileversion.py` - add extra code to fix the fix. [Neil Cook]
- `Drs_changelog_2.py` - update new change log code. [Neil Cook]
- Add git tools to replace `drs_changelog`. [Neil Cook]
- Add git tools to replace `drs_changelog`. [Neil Cook]
- `Update_fileversion.py` - remove skip file check. [Neil Cook]
- `SpirouConst.py` - add new filenames. [Neil Cook]
- `Output_keys.py` - add tellu s1d keys. [Neil Cook]
- `Update_fileversion.py` - first commit fix code for bad header keys.
  [Neil Cook]
- `Obj_fit_tellu.py` - remove old header keys. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - remove old header keys. [Neil Cook]
- Update version. [Neil Cook]


0.4.121 (2019-04-30)
--------------------
- Update trigger. [Neil Cook]
- `Obj_fit_tellu.py` - fix NBLAZE to BLAZE in uniform velocity s1d. [Neil
  Cook]


0.4.120 (2019-04-29)
--------------------
- `Compare_outputs.py` - change paths. [Neil Cook]


0.4.119 (2019-04-26)
--------------------
- `Extract_trigger.py` - correct mistake with extraction trigger. [Neil
  Cook]
- Update test.run. [Neil Cook]
- `SpirouTable.py` - fix problem with NaNs in header (make string) [Neil
  Cook]
- `SpirouTable.py` - fix problem with NaNs in header (make string) [Neil
  Cook]
- `Extract_trigger.py` - should use `DRS_DATA_RAW` in preprocessing. [Neil
  Cook]
- `Obj_fit_tellu.py` - add s1d telluric corrected files. [Neil Cook]
- `SpirouImage.py` - correct s1d ith telluric NaNs. [Neil Cook]
- `Obj_fit_tellu.py` - change to NBLAZE. [Neil Cook]
- `SpirouImage.py` - new s1d - deal with full order being NaNs (for
  telluric) [Neil Cook]
- `Obj_fit_tellu.py` - save s1d for corrected spectrum. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - increase edge smoothing size. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - increase edge smoothing size. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - increase edge smoothing size. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - s1d fix problems with adding new s1d code.
  [Neil Cook]
- `Cal_extract_RAW_spirou.py` - s1d fix problems with adding new s1d code.
  [Neil Cook]
- `SpirouImage.py` - new s1d - iuv spline wrong. [Neil Cook]
- `SpirouImage.py` - edges was wrong. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - correct s1d (now s1dw and s1dv) [Neil
  Cook]


0.4.118 (2019-04-25)
--------------------
- `SpirouImage.py` - write new s1d function. [Neil Cook]
- `SpirouPlot.py` - add `ext_1d_spectrum_debug_plot` plot for debugging s1d
  plot. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add new s1d constants. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - added new s1d code (not finished) [Neil
  Cook]
- `SpirouRV.py` - update pearson r test for NaNs. [Neil Cook]
- Update test.run. [Neil Cook]
- `SpirouRV.py` - catch NaN warnings that are valid. [Neil Cook]
- `SpirouRV.py` - catch NaN warnings that are valid. [Neil Cook]
- `SpirouRV.py` - catch NaN warnings that are valid. [Neil Cook]
- `SpirouRV.py` - catch NaN warnings that are valid. [Neil Cook]
- `SpirouRV.py` - looking for NaN warnings. [Neil Cook]
- `SpirouRV.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - looking for NaN warnings. [Neil Cook]
- `SpirouTelluric.py` - catch warnings from less than for NaNs. [Neil
  Cook]
- `Compare_outputs.py` - script to difference all outputs in two folders
  with files of the same name (output difference) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - turn off plotting all `fit_tellu` orders.
  [Neil Cook]
- `Obj_mk_tellu_new.py` - add warning around less than (for NaNs) [Neil
  Cook]
- `Obj_fit_tellu.py` - remove a NaN sum. [Neil Cook]
- Test.run - update just `mk_tellu/fit_tellu` to test. [Neil Cook]
- Test.run - update just `fit_tellu` to test. [Neil Cook]
- Change np.sum --> np.nansum, np.mean --> np.nanmean, np.median -->
  np.nanmedian etc. [Neil Cook]


0.4.117 (2019-04-24)
--------------------
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit.
  [Neil Cook]
- Change the way InterpolatedUnivariateSpline works. [Neil Cook]
- Update test.run. [Neil Cook]
- Update test.run. [Neil Cook]


0.4.116 (2019-04-10)
--------------------
- Update test.run. [njcuk9999]
- `SpirouRV.py` - deal with NaNs. [njcuk9999]
- `SpirouLOCOR.py` - deal with NaNs. [njcuk9999]
- `SpirouImage.py` - deal with NaNs. [njcuk9999]
- `SpirouPlot.py` - convert zeros to NaNs. [njcuk9999]
- `See_shift.py` - test for pixel shifting by different amounts.
  [njcuk9999]
- `Cal_WAVE_E2DS_EA_spirou.py` - convert zeros to NaNs. [njcuk9999]
- `Cal_SLIT_spirou.py` - change zeros to NaNs. [njcuk9999]
- `Cal_loc_RAW_spirou.py` - change zeros to NaNs. [njcuk9999]
- `Cal_extract_RAW_spirou.py` - change zeros to NaN. [njcuk9999]


0.4.115 (2019-04-08)
--------------------
- `SpirouEXTOR.py` - add options in extraction method to test different
  weighting systems. [njcuk9999]
- `SpirouImage.py` - replace zeros with NaNs. [njcuk9999]
- `SpirouFLAT.py` - replace zero's with NaNs. [njcuk9999]
- `SpirouEXTOR.py` - replace zeros with NaNs. [njcuk9999]
- `SpirouPlot.py` - replace zeros with NaNs. [njcuk9999]
- `SpirouBACK.py` - replace zeros with NaNs. [njcuk9999]
- `Cal_FF_RAW_spirou.py` - replace zeros with nans. [njcuk9999]
- `SpirouEXTOR.py` - readd `raw_weights`. [njcuk9999]


0.4.114 (2019-04-07)
--------------------
- `Cal_FF_RAW_spirou.py` - re-add in new background subtraction. [Neil
  Cook]
- `SpirouEXTOR.py` - reset `raw_weights`. [Neil Cook]
- `SpirouEXTOR.py` - reset `raw_weights`. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - try to match neil branch. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - try to match master. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - test force extractff type to 3c. [Neil Cook]
- `SpirouBACK.py` - add in old measure background function (as test) [Neil
  Cook]
- `Cal_FF_RAW_spirou.py` - redo debananafication. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - undo debananafication. [Neil Cook]
- Reset `cal_loc` (no background) for test. [Neil Cook]
- Reset `cal_loc` (no background) for test. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - remove background subtraction (for test) [Neil
  Cook]


0.4.113 (2019-04-06)
--------------------
- `Cal_FF_RAW_spirou.py` - remove background subtraction (for test) [Neil
  Cook]
- Test.run - update test.run. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - unfix negative values set to zero. [Neil Cook]


0.4.112 (2019-04-05)
--------------------
- `SpirouEXTOR.py` - remove weighting of raw pixels less than zero to very
  low value. [njcuk9999]
- `SpirouConst.py` - update date and version. [njcuk9999]
- `Cal_SHAPE_spirou_old.py` - edit background correction. [njcuk9999]
- `Cal_SLIT_spirou.py` - do not mask out the zeros. [njcuk9999]
- `Caal_loc_RAW_spirou.py` - do not mask out the zeros. [njcuk9999]
- `Cal_FF_RAW_spirou.py` - do not mask out the zeros. [njcuk9999]
- `Cal_extract_RAW_spirou.py` - do not mask out the zeros. [njcuk9999]
- Merge branch 'neil' into dev. [njcuk9999]
- `SpirouBACK.py` - add background debug plot to background finding
  function. [njcuk9999]
- `Cal_SLIT_spirou.py` - add hdr and cdr to background correction (to save
  debug file) [njcuk9999]
- `Cal_loc_RAW_spirou.py` - add hdr and cdr to background correction (to
  save debug file) [njcuk9999]
- `Cal_extract_RAW_spirou.py` - add hdr and cdr to background correction
  (to save debug file) [njcuk9999]
- `Cal_FF_RAW_spirou.py` - add hdr and cdr to background correction (to
  save debug file) [njcuk9999]
- `Misc/cal_SHAPE_spirou_old.py` - add changes to background subtraction.
  [njcuk9999]
- `Cal_low_RAW_spirou.py` - add changes to background subtraction.
  [njcuk9999]
- `Cal_FF_RAW_spirou.py` - add changes to background subtraction.
  [njcuk9999]
- `SpirouWAVE.py` - add initial keep parameter for line width. [njcuk9999]
- `SpirouBACK.py` - add Etienne's changes into
  `measure_background_flatfield`. [njcuk9999]
- `Cal_WAVE_NEW_E2DS_spirou_2.py` - add fix for updating the HC/Fp header
  for wave solution. [njcuk9999]
- `Constants_SPIROU_H4RG.py` - change background correction constants.
  [njcuk9999]
- `Cal_extract_RAW_spirou.py` - change background correction to Etienne's
  new method! [njcuk9999]


0.4.111 (2019-04-04)
--------------------
- `Cal_SHAPE_spirou.py` - fix typo in output filenames (only affected
  debug outputs) [njcuk9999]
- `Cal_CCF_wrap_MH.py` - fix typo in return table values 'cloc' --> 'loc'
  [njcuk9999]
- `Cal_CCF_wrap_MH.py` - call from command line was missing. [njcuk9999]
- `Cal_CCF_wrapper` changes for Melissa (temporary addition of
  `cal_CCF_E2DS_FP_MH_spirou.py)` [njcuk9999]


0.4.108 (2019-04-03)
--------------------
- `SpirouPlot.py` - allow all orders to be plot in tellu plot. [Neil Cook]


0.4.109 (2019-04-03)
--------------------
- Update test.run. [njcuk9999]
- `SpirouWAVE.py` - comment out non-used line. [njcuk9999]
- SpirouDrs.data - undo changes from Melissa Branch. [njcuk9999]
- `Config.py` - undo changes from Melissa Branch. [njcuk9999]
- `Cal_WAVE_E2DS_EA_spirou.py` - undo changes from Melissa branch.
  [njcuk9999]
- `Cal_extract_RAW_spirou.py` - add WFP keys to cal extract and deal with
  not having values. [njcuk9999]
- Merge branch 'neil' into dev. [njcuk9999]
- `SpirouEXTOR.py` - fix normalisation of spelong (E2DSLL) [njcuk9999]
- `Cal_extract_RAW_spirou.py` - add WFP keys to cal extract. [njcuk9999]
- `Cal_CCF_E2DS_FP_spirou.py` - replace manual call to filename.
  [njcuk9999]


0.4.110 (2019-04-03)
--------------------
- `Cal_WAVE_NEW`: fixes to m(x) residuals plot. [melissa-hobson]
- `Cal_CCF_E2DS_FP`: keeps base name only for WFP file. [melissa-hobson]
- `Cal_WAVE_E2DS_EA`: save wave FP CCF keys. [melissa-hobson]
- `Cal_WAVE_NEW`: save wave FP CCF target RV and width. [melissa-hobson]
- `Cal_CCF_E2DS_FP`: writes WFP keys to CCF headers properly. [melissa-
  hobson]
- `Cal_CCF_E2DS_FP`: read correct keyword for drift. [melissa-hobson]
- `Cal_CCF_E2DS_FP`: reads correct keyword for wave sol drift, writes WFP
  keys to CCF headers spirouKeywords: added unique WFP file source
  keyword. [melissa-hobson]
- SpirouKeywords: add wave FP CCF keys to list. [melissa-hobson]


0.4.107 (2019-04-02)
--------------------
- `Cal_WAVE_NEW`: modified FP CCF keywords spirouKeywords: added unique
  WFP keywords for wave FP CCF keys. [melissa-hobson]
- Merge branch 'melissa' of `https://github.com/njcuk9999/spirou_py3` into
  melissa. [melissa-hobson]
- Merge branch 'master' into melissa. [Melissa Hobson]

  Conflicts:
      INTROOT/SpirouDRS/spirouTHORCA/spirouWAVE.py
      `INTROOT/bin/cal_WAVE_E2DS_EA_spirou.py`
      `INTROOT/misc/cal_HC_E2DS_spirou.py`
      `INTROOT/misc/wave_comp_night.py`
- Merge branch 'melissa' of `https://github.com/njcuk9999/spirou_py3` into
  melissa. [melissa-hobson]
- Config save. [melissa-hobson]


0.4.106 (2019-03-29)
--------------------
- Github backup before merging with master. [melissa-hobson]
- `Cal_WAVE_NEW` improved cross-order matching. [melissa-hobson]


0.4.104 (2019-03-28)
--------------------
- Fix bug in extraction modes for `cal_exposure_meter` and
  `cal_wave_mapper`. [Neil Cook]
- `Cal_FF_RAW_spirou.py` - missed the debananafication. [Neil Cook]
- `Cal_extract/cal_ff` - fix mode `extract_shape/ll`. [Neil Cook]
- `Cal_extract/cal_FF` - fix mode selection. [Neil Cook]
- `SpirouImage.py` - DeBananafication needs ParamDict in function call.
  [Neil Cook]
- `Make_1ds_etienne_new.py` - new s1d code to integrate into the drs.
  [Neil Cook]
- `SpirouImage.py` - fix for use of DeBananafication since change to
  function (for `cal_SHAPE` here) [Neil Cook]
- Update `date/version/changelog/update_notes`. [Neil Cook]


0.4.102 (2019-03-28)
--------------------
- `Cal_extract_RAW_spirou.py` - turn off `ic_extract` debug. [Neil Cook]
- Merge branch `'extract_issue555`' into neil. [Neil Cook]
- `SpirouEXTOR.py` - do not round in dy statement. [Neil Cook]


0.4.105 (2019-03-28)
--------------------
- `Cal_HC_E2DS_EA`: log statistics `cal_WAVE_NEW`: improved cross-order FP
  peak matching, store m(x) fits, remove modulo-1-pixel line center
  errors. [melissa-hobson]


0.4.101 (2019-03-25)
--------------------
- `SpirouPlot.py` - add the debanana plot in. [Neil Cook]
- `Misc/new_plot_test.py` - test of plotting fixes. [Neil Cook]
- `Qc_examples.py` - add code to document qc parameters for each output in
  reduced. [Neil Cook]


0.4.100 (2019-03-22)
--------------------
- `SpirouLOCOR.py` - add `get_fiber_data` function and
  `get_straightened_orderprofile` function. [Neil Cook]
- `SpirouEXTOR.py` - fix bug in modes which don't use `pos_a`. [Neil Cook]
- SpirouImage (spirouFile/spirouFITS/spirouImage) - add changes for new
  extraction mode. [Neil Cook]
- `SpirouEXTOR.py` - add etienne's changes to debananafication. [Neil
  Cook]
- `SpirouPlot.py` - add `ext_debanana_plot` to show straightened image.
  [Neil Cook]
- `SpirouConfig.py` - fix ParamDict copy function. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - change mode to '5b' and '5a' [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add changes to all modes '5a' and '5b' to
  work. [Neil Cook]
- Merge branch 'master' into `extract_issue555`. [Neil Cook]
- `Extract_test_5a_5b.py` - want a and b and c separately. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - fix bug in width getting. [Neil Cook]
- `SpirouLOCOR.py` - add function required to get AB + C fiber
  coefficients when needed. [Neil Cook]
- `SpirouEXTOR.py` - add changes required for extract mode 5a/5b. [Neil
  Cook]
- Test of extract mode 5a/5b. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add code required for mode 5a/5b. [Neil
  Cook]


0.4.099 (2019-03-20)
--------------------
- `Tellu_file_number_test.py` - distinguish between `TELL_OBJ` and `TELL_MAP`
  in counting from telluDB. [Neil Cook]
- Merge pull request #557 from njcuk9999/neil. [Neil Cook]

  Neil --> Master. Confirmed successful unit tests.


0.4.098 (2019-03-19)
--------------------
- `Cal_extract_RAW_spirou.py` - fix problem with width getting for fiber
  A. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.097 (2019-03-19)
--------------------
- `SpirouKeywords.py` - remove the "1" suffix (no longer needed) [Neil
  Cook]
- `SpirouEXTOR.py` - set up two new extract functions to test adding of
  fractional contributions of pixels. [Neil Cook]
- Update test.run. [Neil Cook]
- Update test.run. [Neil Cook]
- `SpirouFITS.py` - fix bug with index lock file (when path does not
  exist) [Neil Cook]
- `SpirouFITS.py` - add lock file descriptions for print message. [Neil
  Cook]
- `SpirouStartup.py` - allow `main_end` script to be used not at the end.
  [Neil Cook]
- `SpirouFITS.py` - modify open/close lock file functions. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - reduced max db wait time to 10 minutes.
  [Neil Cook]
- `Cal_preprocess_spirou.py` - index files separately. [Neil Cook]
- Update `extract_trigger` to be able to extract darks. [Neil Cook]
- Merge branch `'sky_dark_fix`' into neil. [Neil Cook]

  Conflicts:
      INTROOT/SpirouDRS/spirouImage/spirouImage.py
      `UPDATE_NOTES.txt`
- Update notes. [Neil Cook]
- `SpirouImage.py` - re-add skydark in. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add option to switch between SKYDARK only
  and "DARK or SKYDARK" (depending which is closest) [Neil Cook]
- `SpirouImage.py` - correct bug in sky dark. [Neil Cook]
- Update `extract_trigger.py`. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.096 (2019-03-18)
--------------------
- `Tellu_file_number_test.py` - update the paths. [Neil Cook]
- `SpirouConst.py` - fix bug with `INDEX_LOCK_FILENAME` - must not use PID
  (must be unique to night name not individual process otherwise does
  not lock out other pids) [Neil Cook]
- Update `extract_trigger.py`. [Neil Cook]
- `SpirouTelluric.py` - remove `extract_file`. [Neil Cook]


0.4.095 (2019-03-16)
--------------------
- `Obj_mk_obj_template.py` - copy all cdb from other outputs. [Neil Cook]
- `SpirouFITS.py` - separate forbidden keys into absolutely don't copy and
  drs don't copy (that will be copied for updating current files) [Neil
  Cook]
- `SpirouFITS.py` - separate forbidden keys into absolutely don't copy and
  drs don't copy (that will be copied for updating current files) [Neil
  Cook]
- `SpirouFITS.py` - need to copy all keys when updating wave solutions.
  [Neil Cook]
- Fix the references to old values of `fp_rv`. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - plot duplicate plot correctly. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - correct typo in WMREF. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - correct typo in WSOURCE (was WAVESOURCE)
  [Neil Cook]
- `SpirouConst.py` - correct typo. [Neil Cook]


0.4.094 (2019-03-15)
--------------------
- `SpirouConst.py` - remove `DRS_EOUT` from forbidden keys (it should follow
  extracted file) [Neil Cook]
- `Calc_berv.py` - make sure CopyOriginalKeys comes first before other
  calls to hdict. [Neil Cook]
- `SpirouFITS.py` - change `QC_HEADER_KEYS` to `FORBIDDEN_HEADER_PREFIXES`.
  [Neil Cook]
- `SpirouKeywords.py` - change some keyword to make them unique (thus can
  remove them) [Neil Cook]
- `SpirouConst.py` - add more forbidden keys, change `qc_keys` to any prefix
  that shouldn't be copied. [Neil Cook]
- `Obj_fit_tellu.py` - CopyOriginalKeys should be called before other
  hdict commands. [Neil Cook]
- Update unit test scripts. [Neil Cook]
- `SpirouRV.py` - fix problem with getting C file from header. [Neil Cook]
- `SpirouConst.py` - add `CCF_FP_TABLE1` and 2. [Neil Cook]
- `Recipe_control.txt` - do not allow `OBJ_DARK` files - only `OBJ_FP`. [Neil
  Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - add a C table as well as a fits table.
  [Neil Cook]
- `Extract_trigger.py` - update settings. [Neil Cook]
- `SpirouKeywords.py` - remove unused keywords. [Neil Cook]
- `SpirouConst.py` - add AB and C files for `CCF_FP`. [Neil Cook]
- `Tellu_file_number_test.py` - change path (for new test) [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - separate AB and C files for output. [Neil
  Cook]
- `SpirouTelluric.py` - fix list of col names for bigcube (only one bad
  file now) [Neil Cook]
- `Extract_trigger` - update trigger. [Neil Cook]
- `SpirouLOCOR.py` - fix localisation error - should be a median not an
  average (option was there but not used) [Neil Cook]
- `SpirouFITS.py` - remove a HUGE BUG - eval('2018-08-05') --> 2005 (as
  date is interpreted as a subtraction)!!!!! [Neil Cook]
- `Tellu_file_number_test.py` - add raw files and disk vs index.fits.
  [Neil Cook]
- `Log_analyser.py` - code to look for errors in set of log files. [Neil
  Cook]
- `Cal_DRIFT_E2DS_spirou.py` - fix typo in get wave sol return. [Neil
  Cook]
- `Cal_SHAPE_spirou.py` - fix typo in cdbbad value name. [Neil Cook]
- `Cal_SHAPE_spirou.py` - fix typo in cdbbad value name. [Neil Cook]


0.4.093 (2019-03-14)
--------------------
- `Cal_preprocess_spirou.py` - fix filename (should only be filename not
  path) [Neil Cook]
- Update date/version/changelog/notes. [Neil Cook]


0.4.092 (2019-03-14)
--------------------
- Make sure all input files are added to header in form: INF#### where
  the first digit shows the file-set and the other three the position
  i.e. for `recipe.py` `night_name` file1 file2 file3 file4   where inputs
  expected are 1 flat and multiple darks header would add INF1001
  INF2001 INF2002 INF2003. [Neil Cook]
- Add header keys for calibration files used to create outputs (CDBDARK,
  CDBWAVE) etc, also add a source for the wave solution (WAVELOC) [Neil
  Cook]
- `SpirouImage.py` - correct the rms percentile to allow more darks to
  pass the rms test. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.091 (2019-03-13)
--------------------
- `Cal_DARK_spirou.py` and `spirouImage.py` - tweak changes to all SKYDARK
  files to be used. [Neil Cook]
- `Extract_trigger.py` - readd the "skip" criteria. [Neil Cook]
- `Drs_reset.py` - skip the log file for this instance of `drs_reset`
  (otherwise can get stuck) [Neil Cook]
- `Drs_reset.py` - fix removal of files when in dir (if still present)
  [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - correct bad qc parameters. [Neil Cook]
- `Obj_mk_tellu_new.py` - fix typo in qc parameters. [Neil Cook]
- `Obj_mk_tellu_new.py` - fix typo in qc parameters. [Neil Cook]
- `Drs_reset.py` - fix typo in reset1. [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - fix bug with new `qc_pass` criteria. [Neil
  Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - fix bug with new `qc_pass` criteria. [Neil
  Cook]
- `Unit_test.py` - update logging (log all) [Neil Cook]
- `SpirouFITS.py` - add function `"add_qc_keys`" to take the keys and push
  them into hdict correctly. [Neil Cook]
- `SpirouConst.py` - change PPVERSION to VERSION for reduced index.fits.
  [Neil Cook]
- Update QC parameters (to store in order) [Neil Cook]
- Update changelog. [Neil Cook]
- `Drs_reset.py` - set DEBUG = False in reset, add the removal of all sub-
  directories in drs folders. [Neil Cook]
- `SpirouStartup.py` - fix bug that we only need lock file is outputs is
  not None. [Neil Cook]
- Update changelog. [Neil Cook]
- `SpirouConst.py` - add version to the index files. [Neil Cook]
- Update extraction trigger. [Neil Cook]


0.4.090 (2019-03-12)
--------------------
- Update extraction trigger. [Neil Cook]
- `SpirouPOLAR.py` - add `qc_pass`. [Neil Cook]
- `SpirouFITS.py` - add a test for formatting defined in the keyword (for
  1d and 2d lists only) [Neil Cook]
- `SpirouKeywords.py` - add `KW_DRS_QC_PASS` + change position of number in
  QCV, QCN, QCL. [Neil Cook]
- `SpirouConst.py` - change the `qc_keys` to look for. [Neil Cook]
- Add `qc_pass` parameter (flag for each qc parameter) [Neil Cook]


0.4.103 (2019-03-12)
--------------------
- Updates to `cal_WAVE_NEW_2`. [melissa-hobson]
- Updated to `cal_HC`, `cal_WAVE_NEW`. [melissa-hobson]


0.4.089 (2019-03-11)
--------------------
- `Extract_trigger.py` - update the settings ready for re-runs of
  extractions. [Neil Cook]
- `SpirouStartup.py` - fix where we lock the index file. [Neil Cook]
- `SpirouConst.py` - add an `INDEX_LOCK_FILENAME` to lock the indexing in
  parallel processes. [Neil Cook]
- `Tellu_file_number_test.py` - code to test the number of telluric files
  at difference stages of the DRS. [Neil Cook]
- Merge pull request #553 from njcuk9999/dev. [Neil Cook]

  `cfht/melissa_fix-->Dev-->master`. confirm unti test completed
- Update date/version/changelog. [Neil Cook]


0.4.088 (2019-03-09)
--------------------
- `SpirouLSD.py` - fix str to float bug. [Neil Cook]
- Test.run - update. [Neil Cook]
- `SpirouPOLAR.py` - fix string - float bug. [Neil Cook]
- `SpirouTelluric.py` -fix berv from string. [Neil Cook]
- SpirouRV - must have finite BERV value -- but should this be set to
  zero? [Neil Cook]
- `SpirouFITS.py` - undo hdr type fix. [Neil Cook]
- Update test.run. [Neil Cook]
- `SpirouBERV.py` - correct strings coming from header (BERV, BJD,
  `BERV_MAX)` [Neil Cook]
- Update test.run. [Neil Cook]
- Update test.run. [Neil Cook]
- `SpirouLOCOR.py` - fix bug with strings not being ints. [Neil Cook]
- `SpirouFITS.py` - fix problem with changing output type (should not
  change) [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - fix typo in updatewavesolution. [Neil Cook]
- `SpirouWAVE.py` - fix typo in new masknaems ordermask-->omask. [Neil
  Cook]
- `SpirouFITS.py` - fix values now as strings --> cast to ints/floats.
  [Neil Cook]
- Fix problem with mjd being a string. [Neil Cook]
- Fix problem with mjd being a string. [Neil Cook]
- `SpirouFITS.py` - allow NaNs into header by converting to string. [Neil
  Cook]
- `SpirouFITS.py` - allow NaNs into header by converting to string. [Neil
  Cook]
- `SpirouFITS.py` - allow NaNs into header by converting to string. [Neil
  Cook]
- `SpirouFITS.py` - allow NaNs into header by converting to string. [Neil
  Cook]
- `SpirouFITS.py` - allow NaNs into header by converting to string. [Neil
  Cook]
- `SpirouBERV.py` - fix bug when we don't need a BERV still need BERVHOUR
  in loc. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - fix typo BCHOUR --> BERVHOUR. [Neil Cook]
- `Cal_loc_RAW_spirou.py` - fix mistake in assigned QCV value. [Neil Cook]
- `Cal_loc_RAW_spirou.py` - fix mistake in assigned QCV value. [Neil Cook]


0.4.087 (2019-03-08)
--------------------
- Change AddKey --> AddKey1DList for QC names/values/logic. [Neil Cook]
- `Cal_preprocess_spirou.py` - correct qc missing from param dict. [Neil
  Cook]
- `SpirouKeywords.py` - fix missed comma in list. [Neil Cook]
- `SpirouBERV.py` - add BERVHOUR to loc (for saving to header) [Neil Cook]
- `SpirouBERV.py` - add BERVHOUR to loc (for saving to header) [Neil Cook]


0.4.086 (2019-03-08)
--------------------
- `SpirouBERV.py` - add BERVHOUR to loc (for saving to header) [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - add some more TODO's for sections that
  need work. [Neil Cook]
- `Cal_HC` - allow multiple files (need to update all files + add files to
  header) [Neil Cook]
- Add WMEANREF for AB and C to header. [Neil Cook]
- Add PID to output header files (so one can find the log file for each)
  [Neil Cook]
- Add Quality control header keys QC, QCV# (value), QCN# (name), QCL#
  (name) - and make sure these are not copied over from inputs + some
  pep8 fixes. [Neil Cook]
- `SpirouWAVE.py` - clean up the code (pep8) [Neil Cook]
- `SpirouFITS.py` - clean up the code (pep8) [Neil Cook]
- `SpirouBERV.py` - clean up the code (pep8) [Neil Cook]
- `SpirouPlot.py` - clean up the code (pep8) [Neil Cook]
- `SpirouConst.py` - clean up the code (pep8) [Neil Cook]
- `Cal_WAVE_NEW_E2DS_spirou.py` - clean up the code (pep8) [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - clean up the code (pep8) [Neil Cook]
- Merge branch `'melissa_fixes`' into dev. [Neil Cook]
- Merge pull request #551 from njcuk9999/cfht. [Neil Cook]

  Fixed lock timer bug and added barycorr retry.


0.4.085 (2019-03-07)
--------------------
- Fixed lock timer bug and added barycorr retry. [Chris Usher]


0.4.084 (2019-03-05)
--------------------
- Delete `wave_comp_night.py`. [melissa-hobson]
- Update `cal_WAVE_E2DS_EA_spirou.py`. [melissa-hobson]
- Merge pull request #547 from njcuk9999/melissa. [melissa-hobson]

  Melissa


0.4.083 (2019-02-28)
--------------------
- `SPlt.debug_locplot_finding_orders` pauses correctly after each plot;
  plot limit modified to improve visualization. [melissa-hobson]
- `SpirouBACK.measure_background_and_get_central_pixels`: removed
  duplicate call to `locplot_y_miny_maxy`. [melissa-hobson]


0.4.081 (2019-02-22)
--------------------
- Littrow check plot: ylimits added based on QCs and results. [melissa-
  hobson]
- `Cal_WAVE_NEW` gets HC catalog lines correctly. [melissa-hobson]
- Merge pull request #542 from njcuk9999/master. [melissa-hobson]

  update
- Merge pull request #541 from njcuk9999/dev. [Neil Cook]

  Dev --> Master
- Update date/version/changelog. [Neil Cook]
- Correct error estimation for `cal_WAVE_NEW`. [melissa-hobson]
- Merge pull request #538 from njcuk9999/master. [melissa-hobson]

  update


0.4.076 (2019-02-22)
--------------------
- `SpirouLOCOR.py` - fix problem with `locplot_im_sat_threshold` plot. [Neil
  Cook]


0.4.082 (2019-02-22)
--------------------
- `SpirouPlot.py` - fix problem with `locplot_im_sat_threshold` plot. [Neil
  Cook]
- `Cal_loc_RAW_spirou.py` - fix problem with `locplot_im_sat_threshold`
  plot. [Neil Cook]
- Merge remote-tracking branch 'origin/dev' into dev. [Neil Cook]
- Merge pull request #537 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date/version/changelog. [Neil Cook]


0.4.075 (2019-02-21)
--------------------
- `SpirouTelluric.py` - need to stop if not index files found. [Neil Cook]


0.4.073 (2019-02-19)
--------------------
- `Cal_validate_spirou.py` - fix bug it version checking (found by
  Melissa) [Neil Cook]
- Merge branch 'dev' into neil. [Neil Cook]
- `Cal_validate_spirou.py` - fix bug it version checking (found by
  Melissa) [Neil Cook]
- `SpirouWAVE.py` - add some more comments for resolution map. [Neil Cook]


0.4.074 (2019-02-19)
--------------------
- `SpirouTelluric.py` - remove hard coded number of orders. [njcuk9999]
- `Obj_mk_tellu_new.py` - comment out unused lines. [njcuk9999]


0.4.080 (2019-02-18)
--------------------
- Testing linear minimization FP wave sol fitting. [melissa-hobson]
- Merge branch 'master' into melissa. [Melissa Hobson]
- Merge pull request #536 from njcuk9999/neil. [Neil Cook]

  Neil --> Master. Confirm full tests complete.
- Update `date/version/changelog/update_notes`. [Neil Cook]
- Tests: -new version of Lovis method (fit n(x) for all lines, rather
  than linear interpolation) - wave sol comparison. [melissa-hobson]


0.4.072 (2019-02-13)
--------------------
- `Obj_mk_tellu_db.py` - need to only print errors if we have errors.
  [Neil Cook]
- `Obj_mk_tellu_db.py` - need to only print errors if we have errors.
  [Neil Cook]


0.4.071 (2019-02-12)
--------------------
- `Extract_trigger.py` - make sure `obj_fit_tellu` errors are stored. [Neil
  Cook]
- `Obj_mk_tellu_db.py` - keep track of errors and exceptions - only print
  at end. [Neil Cook]
- `Obj_mk_obj_template.py` - fix bug when filtering by snr (all columns of
  fits table must be same length) [Neil Cook]
- `SpirouPlot.py` - fix bug with HC plot (from added save of plotting)
  [Neil Cook]
- `Cal_preprocess_spirou.py` - remove rms printout and add values to QC
  errors. [Neil Cook]
- `SpirouPlot.py` - deal with TclError (with new call for `setup_figure)`
  [Neil Cook]
- `Cal_loc_RAW_spirou.py` - add p to call to plotting function. [Neil
  Cook]
- `SpirouPlot.py` - modify figure setup to try to catch TclError's and
  deal with them. [Neil Cook]
- `Extract_trigger.py` - modify printing to logfile (print input args)
  [Neil Cook]
- `Obj_mk_obj_template.py` - change number of tell files to info. [Neil
  Cook]
- `Obj_mk_obj_template.py` - fix typo in new snr constraint. [Neil Cook]
- `Obj_mk_obj_template.py` - fix typo in new snr constraint. [Neil Cook]
- `Obj_mk_obj_template.py` - fix typo in new snr constraint. [Neil Cook]
- `Obj_mk_obj_template.py` - fix typo in new snr constraint. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.070 (2019-02-12)
--------------------
- `SpirouFITS.py` - add UpdateWaveSolution `(update_wave_sol)` function to
  update correctly the HC and FP files. [Neil Cook]
- `Obj_mk_obj_template.py` - add criteria to check median SNR and remove
  any below half the median SNR (in specific order) [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - BUG FIX - hc and fp files have wrong
  headers when updating wave solution. [Neil Cook]


0.4.069 (2019-02-11)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py` - Big Bug FIX ASAP. [Neil Cook]
- `SpirouPlot.py` - update `wave_ea_plot_line_profiles` fig size. [Neil
  Cook]
- `SpirouImage.py` - pep8 correction to corruption test. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add second criteria for corrupt files.
  [Neil Cook]
- `Cal_preprocess_spirou.py` - update corruption tests. [Neil Cook]
- `SpirouImage.py` - adjust rms values (scaled by percentile) [Neil Cook]
- `Cal_preprocess_spirou.py` - move qc cuts to main code (from function)
  [Neil Cook]
- `SpirouImage.py` - update corruption test. [Neil Cook]
- `SpirouPlot.py` - update some plot parameters. [Neil Cook]
- `SpirouPlot.py` - enforce a default fig size on all plots + only save in
  png and pdf. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]

  Conflicts:
      INTROOT/SpirouDRS/spirouStartup/spirouStartup.py
- Merge remote-tracking branch `'origin/input_redo`' into neil. [Neil
  Cook]

  Conflicts:
      .gitignore
- DRS startup - need to make data/msg etc folders if they don't exist.
  [njcuk9999]


0.4.068 (2019-02-10)
--------------------
- `SpirouPlot.py` - make sure plots are unique. [njcuk9999]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - modifications to plotting changes.
  [njcuk9999]
- `Drs_reset.py` - add option to reset plot folder. [njcuk9999]
- `SpirouStartup.py` - deal with getting / setting / displaying plot
  level. [njcuk9999]
- `SpirouPlot.py` - add all functionality to support plotting to file.
  [njcuk9999]
- `SpirouConst.py` - add plot extensions and plot figsize to constants
  (for saving plots to file) [njcuk9999]
- Spirou modules - make all plot calls compatible with saving to file.
  [njcuk9999]
- Misc - make all plot calls compatible with saving to file. [njcuk9999]
- `Config.py` - make `DRS_PLOT` an int and change description of
  `DRS_INTERACTIVE`. [njcuk9999]
- Bin folder - modify all calls to plot to allow saving to file (all
  calls require "p" as an argument) [njcuk9999]


0.4.067 (2019-02-08)
--------------------
- `Cal_preprocess_spirou.py` - print out the corruption check value. [Neil
  Cook]
- `Cal_preprocess_spirou.py` - print out the corruption check value. [Neil
  Cook]
- `Cal_preprocess_spirou.py` - better message for corrupt file. [Neil
  Cook]
- `Cal_preprocess_spirou.py` - better message for corrupt file. [Neil
  Cook]
- `SpirouImage.py` - catch warning "RuntimeWarning: All-NaN slice
  encountered r = func(a, `**kwargs)`" [Neil Cook]
- `Cal_preprocess_spirou.py` - pep8 tidy up of QC. [Neil Cook]
- `SpirouImage.py` - add `get_full_flat`, `get_hot_pixels`,
  `test_for_corrupt_files` functions (for checking corruption in
  preprocessing) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add corrupt file constants. [Neil Cook]
- `Cal_preprocess_spirou.py` - add QC for corrupt files. [Neil Cook]
- `Extract_trigger.py` - update conditions for `mk_tellu` and `fit_tellu`.
  [Neil Cook]
- `Extract_trigger.py` - update conditions for `mk_tellu` and `fit_tellu`.
  [Neil Cook]
- `Obj_mk_obj_template.py` - make sure BigCube table in both BigCube and
  BigCube0. [Neil Cook]
- `Obj_mk_obj_tempalte.py` - fit BADFILE --> BADPFILE keyword. [Neil Cook]
- `SpirouKeywords.py` - update `KW_OBJECT` (was a typo) [Neil Cook]
- `Obj_mk_obj_template.py` - add the data type to ReadParams (otherwise
  tries to make them floats) [Neil Cook]
- `SpirouImage.py` - deal with keylook up and report better error (via
  keylookup) [Neil Cook]
- `Obj_mk_obj_template.py` - fix another typo since last update. [Neil
  Cook]
- `SpirouKeywords.py` - add keyword `KW_OBJECT`. [Neil Cook]
- `Obj_mk_obj_template.py` - fix type in previous changes. [Neil Cook]
- `Check_for_corrupt_files.py` - add an extra fix from Etienne. [Neil
  Cook]
- `Obj_mk_tellu_db.py` - fix typo in printout text. [Neil Cook]
- `Obj_mk_obj_template.py` - correct mistake in calling ReadParams (from
  most recent edit) [Neil Cook]
- `SpirouTelluric.py` - add a function to construct the big cube table
  (added as a second import to BigCube) [Neil Cook]
- `SpirouFITS.py` - add a `write_image_table` function to write a image and
  a table to single fits file. [Neil Cook]
- `Check_for_corrupt_files.py` - adjust with Etiennes changes. [Neil Cook]
- `Obj_mk_obj_template.py` - add fits table to big table with rows of file
  parameters (used in the big cube) [Neil Cook]
- `Check_for_corrupt_files.py` - fix bugs in the test. [Neil Cook]


0.4.066 (2019-02-07)
--------------------
- Update the leapseconds. [Neil Cook]
- `Check_for_corrupt_files.py` - worker code to check corrupt files
  functionality (before implementing into preprocessing) [Neil Cook]
- Update to only do `mk_tellu` and `fit_tellu`. [Neil Cook]
- Add  / get functions for recon file. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - qc snr for `mk_tellu` and `fit_tellu`. [Neil
  Cook]
- `Obj_mk_tellu_*.py` - distinguish between SNR cut in `fit_tellu` and
  `mk_tellu`. [Neil Cook]
- `Obj_fit_tellu.py` - add qc of SNR > 100 for order 33. [Neil Cook]
- `Check_objname.py` - pep9 remove blank lines. [Neil Cook]
- `Check_objname.py` - check objnames and dprtype for preprocessed files
  in a given directory. [Neil Cook]
- Update `extract_trigger` settings. [Neil Cook]
- Update telluric white/black lists. [Neil Cook]
- `Extract_trigger.py` - add a comment. [Neil Cook]
- `Check_calibdb_2.py` - check calibdb and sort and make "pernight" and
  "pertc" calibdb entries. [Neil Cook]
- `SpirouTelluric.__init__.py` - Add aliases to blacklist and whitelist
  functions. [Neil Cook]
- `Extract_trigger.py` - get whitelist from file. [Neil Cook]


0.4.065 (2019-02-06)
--------------------
- Add a note to locale README.md. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_table.py` - remove text to language database. [Neil Cook]


0.4.079 (2019-02-06)
--------------------
- `Cal_WAVE_NEW` corrected Littrow extrapolation for reddest orders.
  [melissa-hobson]


0.4.064 (2019-02-05)
--------------------
- `Drs_startup.py` - tweak display settings for interactive + debug mode
  in drs setup text. [Neil Cook]
- Update language database. [Neil Cook]
- `Drs_text.py` - tweak short codes and how length works with Entry(None)
  [Neil Cook]
- `Drs_exceptions.py` - tweak how exception work (and add string
  representation) [Neil Cook]
- Update language database. [Neil Cook]
- `Pseudo_const.py` - do not automatically write debug message language
  codes (only when debug >= 100) [Neil Cook]
- `Drs_startup.py` - continue editing how errors work. [Neil Cook]
- `Drs_recipe.py` - continue update to errors. [Neil Cook]
- `Drs_log.py` - do not use 'p' use params, update reporting (report all
  if debug >= 100) [Neil Cook]
- `Drs_file.py` - add extra param (pep8) [Neil Cook]
- `Drs_argument.py` - redo DrsArgument.exception and update `_display_info`.
  [Neil Cook]
- `Drs_text.py` - expand functionality of Entry classes `(__add__`,
  `__radd__`, `__len__`, `__iter__`, `__next__`, `__eq__`, `__ne__`, `__contains__)`
  and how .get() works. [Neil Cook]
- `Drs_exception.py` - add ArgumentException/Error/Warning. [Neil Cook]
- Update language database. [Neil Cook]
- `Param_functions.py` - get ArgumentError/Warning. [Neil Cook]
- `Drs_startup.py` - deal with changes to ErrorEntry (no "\n"
  automatically added now) [Neil Cook]
- `Drs_recipe.py` - move argument classes/functions to separate script +
  continue string moving to language database. [Neil Cook]
- `Drs_loy.py` - add comment that some strings cannot be moved to language
  database. [Neil Cook]
- `Drs_argument.py` - move argument classes/function to separate script.
  [Neil Cook]


0.4.063 (2019-02-04)
--------------------
- `Obj_mk_tellu_db.py` - do not reset tellu db in code (do it manually
  before) [Neil Cook]
- Update `extract_trigger.py` for `obj_mk_tellu_db.py`. [Neil Cook]
- Merge branch 'master' into neil. [Neil Cook]
- Merge branch 'master' into neil. [Neil Cook]
- `Extract_trigger.py` - add `obj_mk_tellu_db` to triggered files. [Neil
  Cook]
- Unit test runs - add `obj_mk_tellu_db` to runs. [Neil Cook]
- `SpirouTelluric.py` - fix bugs after moving functions here. [Neil Cook]
- Code to check the calibdb entries vs files. [Neil Cook]
- Add `obj_mk_tellu_db` to list of available unit tests. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.078 (2019-02-04)
--------------------
- `Cal_WAVE_NEW` update: no longer breaks if FP peak(s) next to reference
  line are missing. [melissa-hobson]


0.4.062 (2019-02-03)
--------------------
- `Port_database.py` - just try to open csv files as they are done in the
  drs -- hits problems here and not later. [njcuk9999]
- `Drs_text.py` - edit the way csv databases are loaded (to avoid encoding
  errors) [njcuk9999]
- `Drs_exceptions.py` - add errorobj as possible input to exceptions (and
  exctract message/level accordingly) [njcuk9999]
- Update language database. [njcuk9999]
- `Drs_recipe.py` - continue moving errors to database. [njcuk9999]
- `Drs_log.py` - continue moving errors to database. [njcuk9999]
- `Drs_file.py` - continue moving errors to database. [njcuk9999]


0.4.061 (2019-02-01)
--------------------
- Update language database. [Neil Cook]
- `Drs_file.py` - continue taking out error messages. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Add wiki plots. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Update langauge databases. [Neil Cook]
- `Drs_file.py` - continued error movement to database. [Neil Cook]


0.4.077 (2019-02-01)
--------------------
- `Cal_WAVE_NEW_E2DS` attempt to fix issues with FP line adjacent to
  reference peak being missing. [melissa-hobson]
- Merge branch 'master' into melissa. [Melissa Hobson]
- Merge pull request #534 from njcuk9999/dev. [Neil Cook]

  Dev --> Master
- `SpirouWAVE.py` - fix a deprecated WLOG message (found by Melissa) [Neil
  Cook]
- `SpirouLog.py` - must catch WLOG error before trying to do anything with
  p. [Neil Cook]
- `Cal_WAVE_NEW_E2DS`: added plot axis titles, littrow check and
  extrapolation, saving to files spirouConst: added functions for
  `cal_WAVE_NEW` spirouWAVE: corrected logging error. [melissa-hobson]
- Merge pull request #533 from njcuk9999/master. [melissa-hobson]

  update
- Merge pull request #531 from njcuk9999/master. [melissa-hobson]

  update melissa


0.4.060 (2019-01-31)
--------------------
- Update langauge databases. [Neil Cook]
- `Drs_file.py` - continue to take out error messages. [Neil Cook]
- `Recipe_definitions.py` - update location of locale module. [Neil Cook]


0.4.021 (2019-01-30)
--------------------
- `SpirouTelluric.py` - continue to write/upgrade new `mk_tellu` functions
  and functions for `mk_tellu_db`. [Neil Cook]
- `SpirouPlot.py` - add new `mk_tellu` plot. [Neil Cook]
- `SpirouConst.py` - add definition of whitelist file. [Neil Cook]
- `Tellu_whitelist.txt` - add a white list of all possible telluric star
  names. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add constants from new recipes. [Neil Cook]
- `Obj_mk_tellu_db.py` - move constants to constants files and functions
  to spirouTelluric. [Neil Cook]
- `Obj_mk_tellu_new.py` - move constants to constants file. [Neil Cook]


0.4.059 (2019-01-30)
--------------------
- `Obj_mk_tellu_new.py` - update code with Etienne's changes. [Neil Cook]
- `Obj_mk_tellu_db.py` - new wrapper script for `mk_tellu` + `fit_tellu` on
  tellurics -- creates the telluric database. [Neil Cook]


0.4.020 (2019-01-29)
--------------------
- Update .gitignore to ignore .npy files. [Neil Cook]
- `SpirouTelluric.py` - added aliases to two new `mk_tellu` functions. [Neil
  Cook]
- `SpirouTelluric.__init__.py` - added aliases to two new `mk_tellu`
  functions. [Neil Cook]
- `SpirouKeywords.py` - added two new keywords for new `mk_tellu` recipe.
  [Neil Cook]
- `SpirouConfig.py` - update bug in ConfigError (forced list) [Neil Cook]
- `Combine_tapas.py` - new `mk_tellu` recipe (original code from E.A.) [Neil
  Cook]
- `Obj_mk_tellu_new.py` - new `mk_tellu` recipe. [Neil Cook]


0.4.058 (2019-01-28)
--------------------
- Upgrade of language database. [Neil Cook]
- `Drs_lock.py` - continued upgrade of error entry. [Neil Cook]
- `Drs_recipe.py` - continued upgrade of error entry. [Neil Cook]
- `Drs_log.py` - continued upgrade of error entry. [Neil Cook]
- `Drs_file.py` - continued upgrade of error entry. [Neil Cook]
- `Drs_log.py` - fix bug in log and how exceptions are handled. [Neil
  Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge pull request #532 from njcuk9999/neil. [Neil Cook]

  Neil -> Master
- Update date/version/changelog. [Neil Cook]


0.4.017 (2019-01-28)
--------------------
- `SpirouLog.py` - fix a bug in logger (only a problem when log breaks)
  [Neil Cook]


0.4.057 (2019-01-26)
--------------------
- Modify test recipes with upgrades. [Neil Cook]
- Drsmodule.plotting - moved from drsmodule.plot. [Neil Cook]
- Drsmodule.locale - continue upgrade. [Neil Cook]
- Drsmodule.constants.io - continue upgrade. [Neil Cook]
- Drsmodule.constants.default - continue upgrade. [Neil Cook]
- Drsmodule.constants.core - continue upgrade. [Neil Cook]
- Drsmodule.config.instruments - continue upgrade. [Neil Cook]
- Drsmodule.config.core - continue upgrade. [Neil Cook]
- Update `DRS_VERSION` / `DRS_DATE` / `DRS_RELEASE`. [Neil Cook]
- Update `user_config.ini`. [Neil Cook]
- Update `user_config.ini`. [Neil Cook]


0.4.056 (2019-01-25)
--------------------
- `Drs_startup.py` - tweak the system information display section. [Neil
  Cook]
- `Drs_log.py` - separate print and log (and use default language for log)
  [Neil Cook]
- Backup language database. [Neil Cook]
- `Drs_text.py` - fill language database empty with 'N/A' [Neil Cook]
- Update language databases. [Neil Cook]


0.4.055 (2019-01-24)
--------------------
- Add READMEs to explain empty directories. [Neil Cook]
- Add instrument language packs and backup folder for language database.
  [Neil Cook]
- Drsmodule.locale - construct a readme. [Neil Cook]
- `Drsmodule.locale.__init__.py` - add `drs_exceptions` to internal imported
  modules. [Neil Cook]
- Drsmodule.locale.databases - update language databases. [Neil Cook]
- Drmodule.locale.core - move exceptions and make sure all are using
  basiclogger. [Neil Cook]
- Drsmodule.constants - update readme. [Neil Cook]
- Constants.default - make Const and Keywords have a source argument.
  [Neil Cook]
- Constants.core - change how exceptions work and where they are sourced
  from. [Neil Cook]
- Config.instruments.spirou - make copy have a source argument. [Neil
  Cook]
- Config.instruments.nirps - make copy have a source argument. [Neil
  Cook]
- `Drs_setup.py` - change how the exceptions work and where they are
  sourced from + continue to replace hard-coded text to text from
  database. [Neil Cook]
- `Drs_recipe.py` - carryon replacing text hard-coded to text in database.
  [Neil Cook]
- `Drs_log.py` - change how the exceptions work and where they are sourced
  from. [Neil Cook]


0.4.054 (2019-01-23)
--------------------
- Moved locale module to drsmodule root. [Neil Cook]
- Locale.databases - continued to add to databases. [Neil Cook]
- Locale.databases - continued to add to databases. [Neil Cook]
- .gitignore - added ignoring of .npy files and .~lock files. [Neil
  Cook]
- `Constants.default.pseudo_const.py` - added `REPORT_KEYS` method. [Neil
  Cook]
- `Constants.core.param_functions.py` - started added language / basic log
  functionality. [Neil Cook]
- `Constants.core.constants_functions.py` - added tracking of warnings (so
  they only print once) [Neil Cook]
- `Config.math.time.py` - added `get_hhmmss_now` function (for log) [Neil
  Cook]
- Removed locale folder from config folder to separate sub-module
  directory. [Neil Cook]
- `Instruments.spirou.recipe_definitions.py` - language implementation.
  [Neil Cook]
- `Instruments.nirps.recipe_definitions.py` - language implementation.
  [Neil Cook]
- `Instruments.nirps.pseudo_const.py` - format change. [Neil Cook]
- `Drs_startup.py` - language implementation. [Neil Cook]
- `Drs_recipe.py` - language implementation. [Neil Cook]
- `Drs_log.py` - language implementation. [Neil Cook]


0.4.053 (2019-01-22)
--------------------
- Added error.csv and "language.xls" - use language.xls to edit strings
  for each language (given a specific key) [Neil Cook]
- `Default_config.py` - updated options (now with ENG and FR allowed - ENG
  as default) [Neil Cook]
- Updated help.csv. [Neil Cook]
- Removed `recipe_descriptions.py` from config.locale.core. [Neil Cook]
- `Drs_text.py` - (formally text.py) - continued work on upgrade. [Neil
  Cook]
- `Recipe_definitions.py` - use HelpText to define strings (language
  support) [Neil Cook]
- `Drs_recipe.py` - `COLOURED_LOG` --> `DRS_COLOURED_LOG`. [Neil Cook]
- `Drs_log.py` - update WLOG to deal with ErrorEntry objects as WLOG
  messages. [Neil Cook]
- Use HelpText to define strings (language support) [Neil Cook]
- Update `user_config.ini` file. [Neil Cook]
- Update `user_config.ini` file. [Neil Cook]
- Add default help file. [Neil Cook]
- Change from ./configuration --> ./config. [Neil Cook]
- Change from ./configuration --> ./config. [Neil Cook]
- Added alias to new function `"get_file_names`" [Neil Cook]
- Adjusted path name ./configuration --> ./config. [Neil Cook]
- Started adding language support. [Neil Cook]
- Renamed drsmodule.configuration to drsmodule.config. [Neil Cook]


0.4.052 (2019-01-21)
--------------------
- Add source config file to error messages. [Neil Cook]
- Fixed printing of config errors in constants file. [Neil Cook]
- Added a test recipe for spirou and nirps. [Neil Cook]
- Added lock and table to drsmodule.io package. [Neil Cook]
- Added "getmodnames" to `drsmodule.constants.__init__` file. [Neil Cook]
- Continued upgrade to drsmodule.constants.default. [Neil Cook]
- Continued upgrade to drsmodule.constants.core. [Neil Cook]
- Added `__init__` file to drsmodule.configuration. [Neil Cook]
- Continued upgrade to drsmodule.configuration.instruments.spirou. [Neil
  Cook]
- Added a drsmodule.configuration.core.default folder (for default
  file/recipe descriptions) [Neil Cook]
- Continued upgrade to drsmodule.configuration.core. [Neil Cook]
- Default file definitions and recipe defintions. [Neil Cook]
- Add test default config for NIRPS. [Neil Cook]
- Add test user config for NIRPS. [Neil Cook]


0.4.051 (2019-01-19)
--------------------
- Add minor changes to `drs_recipe.py` and `drs_startup.py`. [Neil Cook]
- Add a test recipe to recipes.test. [Neil Cook]
- Added a plot module. [Neil Cook]
- Continued upgrade of constants.default packages. [Neil Cook]
- Added locale package. [Neil Cook]
- Continued update of instruments.spirou defintions. [Neil Cook]
- Adding `drs_recipe` + `drs_file`  to configuration.core modules. [Neil
  Cook]


0.4.050 (2019-01-18)
--------------------
- Move constants functions from package --> core (remove package module)
  [Neil Cook]
- Add init file for drsmodule (to be named something else eventually)
  [Neil Cook]
- Add configuration.instruments.spirou files. [Neil Cook]
- Remove the core.general package. [Neil Cook]
- Add init and README.md to constants module. [Neil Cook]
- Add a defaults folder (this has definitions of constants as well as
  default values) - sets up the classes for instruments to overwrite.
  [Neil Cook]
- Remove the const package (now "constants") [Neil Cook]
- Add a time module to the configurations.math module. [Neil Cook]
- Add a init file to configuration.instruments. [Neil Cook]
- Add spirou config files to configuration.instruments. [Neil Cook]
- Add logging to configuration.core. [Neil Cook]
- Add default user config files (will be commented out in future) [Neil
  Cook]
- `SpirouRecipe.py` - add "instrument" to attributes of spirouRecipe.py.
  [Neil Cook]
- `Files_spirou.py` - modify name and description docstring. [Neil Cook]
- `SpirouConst.py` - fix a bug in exit definition. [Neil Cook]


0.4.049 (2019-01-17)
--------------------
- Added additional file to INTROOT 2 (remanage) [Neil Cook]
- `Test_processing.py` - remove need for replacing '.py' [Neil Cook]
- `Recipes_spirou.py` - added instrument name (will be needed in the
  future) [Neil Cook]
- First draft of INTROOT remanage. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge pull request #529 from njcuk9999/neil. [Neil Cook]

  Neil --> Master
- Update date/version/changelog. [Neil Cook]
- `Test_processing.py` - modify code to return errors and timings (via
  multiprocessing.Manager) [Neil Cook]
- `SpirouRecipe.py` - modified the `generate_runs_from_filelist` function to
  fix when there is no directory from pos args. [Neil Cook]
- `SpirouFile.py` - added `read_header/read_data` functions and optimized
  (with todo comment) the read function. [Neil Cook]
- `Wavecompy.py` - added some comments. [Neil Cook]


0.4.048 (2019-01-16)
--------------------
- `Test_processing.py` - for now comment out main call (while testing)
  [Neil Cook]
- `SpirouRecipe.py` - reformat help printing, add required option to
  optional arguments (for when we do not have positional arguments) and
  rework the generation of runs from files (especially when we only have
  optional arguments) [Neil Cook]
- `Recipe_spirou.py` - add required keyword (for testing) [Neil Cook]
- `Wavecomp.py` - code to compare wavelength solutions (misc) [Neil Cook]


0.4.047 (2019-01-15)
--------------------
- `Drs_dependencies.py` - remove looking in the /misc/ folder for
  dependecies/code stats. [Neil Cook]
- `Test_recipe.py` - test self. [Neil Cook]
- `Test_processing.py` - upgrade to allow execution of recipes (in single
  and in parallel) [Neil Cook]
- `SpirouStartup2.py` - allow overwriting of `drs_params` when they are
  obtained via kwargs `(get_params)` [Neil Cook]
- `SpirouRecipe.py` - continued upgrade of `input_redo`. [Neil Cook]
- `Recipe_spirou.py` - continued upgrade of `input_redo`. [Neil Cook]


0.4.016 (2019-01-15)
--------------------
- `SpirouLog.py` - fixed an error with logging (if p not set crashes
  because there was no `DRS_DEBUG` key -- fixed now) [Neil Cook]
- `SpirouRV.py` - fixed bug found with part of correlbin - only affects
  spectra which have peaks with start/end different by +2 (rare?) but
  for now using the old correlbin which works for these. [Neil Cook]


0.4.046 (2019-01-11)
--------------------
- `Recipe_spirou.py` - change nomenclature require kwarg arguments have
  '-' optional have '--' [Neil Cook]
- `Test_recipe.py` - change comment to make clearer. [Neil Cook]
- `SpirouStartup2.py` - remove '-' in specials to allow them to work.
  [Neil Cook]
- `SpirouRecipe.py` - modify `_parse_args` to take into that we don't wont
  the '-' [Neil Cook]
- `Recipes_spirou.py` - testing file list as keyword arguments. [Neil
  Cook]
- `SpirouStartup2.py` - changed order of functions, modified display
  order, added functionality to deal with debug mode and other special
  keys. [Neil Cook]
- `SpirouRecipe.py` - continued upgrade (changes to parser handling of
  special arguments, check files + added debug as special argument)
  [Neil Cook]
- `SpirouFile.py` - small formatting changes in continued input redo.
  [Neil Cook]
- `Recipe_spirou.py` - remove references to debug (now a special command
  added to all recipes) [Neil Cook]
- `Recipe_descriptions.py` - remove unused help. [Neil Cook]
- `Files_spirou.py` - modify names to better suit input redo. [Neil Cook]


0.4.045 (2019-01-09)
--------------------
- `Test_recipe.py` - test on `cal_HC_E2DS_spirou.py`. [Neil Cook]
- `SpirouStartup2.py` - modified which argument display on setup (now only
  those that were entered at run time) [Neil Cook]
- `SpirouRecipe.py` - redone error reporting on header check. [Neil Cook]
- `SpirouFile.py` - continued upgrade of input redo. [Neil Cook]
- `Recipes_spirou.py` - added `cal_hc` definition. [Neil Cook]
- `Recipe_descriptions.py` - added `cal_hc` text. [Neil Cook]
- `Files_spirou.py` - updated names to better represent files (i.e. added
  fiber name) [Neil Cook]
- `SpirouRecipe.py` - make some methods/function private (protected) using
  the `"_`" character as a prefix. [Neil Cook]
- `Recipe_spirou.py` - add more argument defintions
  (blazefile/flatfile/wavefile), add `cal_hc` test. [Neil Cook]
- `Recipe_descriptions` - fix imports and define language in constants
  file. [Neil Cook]
- `SpirouConst.py` - add language constant (Not used yet) [Neil Cook]
- `SpirouStartup2.py` - modify `special_keys_present` function to look at
  altnames as well as names (i.e. DrsArgument.names instead of
  DrsArgument.name) [Neil Cook]
- `SpirouRecipe.py` - modify and add special actions (now: --help,
  --listing, --listall, --version, --info) [Neil Cook]
- `Recipe_spirou.py` - convert remaining descriptions/help to
  `recipe_descriptions` calls. [Neil Cook]
- `Recipe_descriptions.py` - continue to fill out recipe
  descriptions/examples/help. [Neil Cook]


0.4.044 (2019-01-08)
--------------------
- SpirouConst.py, spirouRecipe, `spirouStartup2.py` - move around the
  header --> into spirouConst.py. [Neil Cook]
- `SpirouStartup2.py` - add a check for special keys and do not display
  normal "splash" if found. [Neil Cook]
- `SpirouRecipe.py` - update listing, add version/ epilog and other small
  fixes to input redo. [Neil Cook]
- `Recipe_spirou.py` - continued work on recipe definitions (including
  references to `recipe_descriptions)` [Neil Cook]
- `Recipe_descriptions.py` - storage for longer text (allowing possibility
  of language support later) [Neil Cook]
- `SpirouConst.py` - added constant to define the maximum display limit
  for files/directorys (when showing an argument error) [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge pull request #528 from njcuk9999/neil. [Neil Cook]

  Neil --> Master
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Update the reset files for the calibDB and telluDB. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]

  Conflicts:
      INTROOT/SpirouDRS/spirouCore/spirouLog.py
- Merge pull request #527 from njcuk9999/neil. [Neil Cook]

  Neil --> Master. Confirmed unit tests completed successfully.


0.4.015 (2019-01-08)
--------------------
- `SpirouPOLAR.py` - fix dependence on `KW_ACQTIME_KEY_JUL` --> `KW_ACQTIME`.
  [Neil Cook]
- `SpirouCDB.py/spirouDB.py` - change all human times to be in format
  `YYYY-mm-dd_HH:MM:SS.f` for consistency. [Neil Cook]
- Test.run - update test.run to finish testing (start before last
  failure) [Neil Cook]
- `SpirouDB.py` - fix database definitions in modified `"get_database`"
  function. [Neil Cook]
- Updated version/date/changelog. [Neil Cook]
- Move old tests to `spirouUnitTests/old_tests`. [Neil Cook]


0.4.014 (2019-01-07)
--------------------
- `SpirouDB.py` - changed from reading human date to reading julian date,
  changed to use astropy.timea. [Neil Cook]
- `SpirouCDB.py` - reformatted calibDB functions to use spirouDB wherever
  possible, changed from reading human date to reading julian date,
  changed to use astropy.time. [Neil Cook]
- `SpirouDB.__init__.py` - moved location of `get_acqtime` (moved to
  spirouDB) [Neil Cook]
- `SpirouKeywords.py` - removed `KW_ACQTIME_KEY` and `KW_ACQTIME_KEY_JUL` in
  place of `KW_ACQTIME` (which is the modified julian date) - with
  supporting format in case of change (uses astropy.time) [Neil Cook]
- `SpirouConst.py` - removed the use of `ACQTIME_KEY_JUL` now uses
  `KW_ACQTIME` (which is the modified julian date by definition) [Neil
  Cook]
- `Cal_HC_E2DS_EA_spirou.py` - changed acqtime to ACQTIME (for
  consistency) [Neil Cook]


0.4.043 (2018-12-21)
--------------------
- `Test_processing.py` - continued work on `input_redo`. [Neil Cook]
- `SpirouRecipe.py` - continued work on `input_redo`. [Neil Cook]
- `Recipes_spirou.py` - continued work on `input_redo`. [Neil Cook]


0.4.013 (2018-12-19)
--------------------
- `SpirouLog.py` - fix for printlogandcmd now having argument "colour"
  [Neil Cook]
- `SpirouLog.py` - update of ipdb to allow magic commands. [Neil Cook]


0.4.042 (2018-12-19)
--------------------
- `SpirouRecipe.py` - continue input redo upgrade. [Neil Cook]
- `SpirouFile.py` - add some extra empty attributes to DrsInputFile and
  DrsFitsFile. [Neil Cook]
- `SpirouLog.py` - alias for embeded ipython (in ipdb type "ipython()")
  [Neil Cook]
- `Recipes_spirou.py` - update values during `input_redo` upgrade. [Neil
  Cook]
- `Test_processing.py` - script to test `input_redo` with processing. [Neil
  Cook]


0.4.041 (2018-12-18)
--------------------
- `Test_recipe.py` - continued update of input redo. [Neil Cook]
- `SpirouStartup2.py` - continued update of input redo. [Neil Cook]
- `SpirouStartup.py` - update from spirouStartup2.py. [Neil Cook]
- `SpirouRecipe.py` - continued update of input redo. [Neil Cook]
- `SpirouFile.py` - continued update of input redo. [Neil Cook]
- Merge branch 'neil' into `input_redo`. [Neil Cook]


0.4.012 (2018-12-18)
--------------------
- `SpirouStartup.py` - update display. [Neil Cook]
- `SpirouConst.py` - update colours and themes and Color Class. [Neil
  Cook]
- `SpirouLog.py` - add debug and custom colour modes to log messages.
  [Neil Cook]
- `SpirouLog.py` - add debug and custom colour modes to log messages.
  [Neil Cook]
- `SpirouConst.py` - update log constants. [Neil Cook]
- `Obj_mk_obj_template.py` - adjust log message to be more clear. [Neil
  Cook]
- Test codes for testing bug in BigCube/telluDB. [Neil Cook]
- `SpirouFile.sort_by_name` - return sort indices not array (so we can
  sort multiple arrays) [Neil Cook]
- `Obj_mk_obj_template.py` - fix bug in sorting files (wrong OBJNAME for
  filename) [Neil Cook]


0.4.040 (2018-12-17)
--------------------
- `SpirouRecipe.py` - continued work on input redo. [Neil Cook]
- `SpirouStartup2.py` - continued work on input redo. [Neil Cook]
- `SpirouRecipe.py` - continued work on input redo. [Neil Cook]
- `SpirouFile.py` - continued work on input redo. [Neil Cook]
- `Test_recipe.py` - continued update for `input_redo`. [Neil Cook]
- `SpirouRecipe.py` - continued update for `input_redo`. [Neil Cook]
- `SpirouFile.py` - continued update for `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]

  Conflicts:
      `INTROOT/SpirouDRS/spirouUnitTests/extract_trigger.py`


0.4.011 (2018-12-17)
--------------------
- `Obj_mk_obj_template.py` - fix bug when forcing calibDB from wave
  solution (calibDB needs to be re-read each time) [Neil Cook]
- `Obj_mk_obj_template.py` - fix bug when forcing calibDB from wave
  solution (calibDB needs to be re-read each time) [Neil Cook]
- `Obj_mk_obj_template.py` - fix bug when forcing calibDB from wave
  solution (calibDB needs to be re-read each time) [Neil Cook]
- `SpirouLog.py` - update log to allow option to be added (by default uses
  "RECIPE" or `"LOG_OPT`" or '') [Neil Cook]


0.4.010 (2018-12-16)
--------------------
- `Wave_sol_to_header.py` - code to update header of all e2ds/e2dsff
  (object and fpfps) in a `night_name` or all files. [Neil Cook]
- Merge pull request #525 from njcuk9999/dev. [Neil Cook]

  Melissa --> Dev --> Master. Confirm tested.
- Update `date/version/changelog/update_notes`. [Neil Cook]


0.4.039 (2018-12-15)
--------------------
- `SpirouFile.py` - continued work on input redo. [Neil Cook]
- `SpirouRecipe.py` - continued work on input redo. [Neil Cook]


0.4.009 (2018-12-14)
--------------------
- `Cal_CCF_E2DS_FP_spirou.py` - fix if `CCF_RV2` not in whdr. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - fix if `CCF_RV2` not in whdr. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - fix if `CCF_RV2` not in whdr. [Neil Cook]
- Test.run - update for current testing. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - fix crash bug Exception --> SystemExit.
  [Neil Cook]
- Test.run - change for continued test. [Neil Cook]
- Test.run - change for continued test. [Neil Cook]
- `SpirouTHORCA.py` - fudge factor fix --> `n_order_init` =
  `p['IC_LITTROW_ORDER_INIT_{0}'.format(1)]` [Neil Cook]
- `SpirouTHORCA.py` - test fix. [Neil Cook]
- `SpirouTHORCA.py` - fix for `n_order_init` (from init --> `init_1/init_2)`
  [Neil Cook]
- Update test.run - `cal_test.run` (from `cal_WAVE)` onwards. [Neil Cook]
- Merge branch 'melissa' into dev. [Neil Cook]
- `SpirouConst.py` - pep8 changes to `WAVE_FILE_EA_2`. [Neil Cook]
- `Cal_WAVE_NEW_E2DS_spirou.py` - pep8 changes. [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - few logic checks and pep8 changes. [Neil
  Cook]
- `Extract_trigger.py` - update run time parameters. [Neil Cook]
- `Extract_trigger.py` - fix incompatible version of `cal_shape` in
  reprocessing code. [Neil Cook]


0.4.038 (2018-12-14)
--------------------
- `SpirouRecipe.py` and `spirouStartup2.py` - continued update to input
  redo. [Neil Cook]
- `Extract_trigger.py` - fix incompatible version of `cal_shape` in
  reprocessing code. [Neil Cook]


0.4.037 (2018-12-13)
--------------------
- `SpirouRecipe.py` - update to check code (put into DrsRecipe class as
  methods) [Neil Cook]
- `SpirouRecipe.py` - update to check code (put into DrsRecipe class as
  methods) [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]


0.4.008 (2018-12-13)
--------------------
- `Constants_SPIROU_H4RG`: new constants for start/end littrow orders.
  [melissa-hobson]
- `Cal_WAVE_E2DS_EA`: littrow can now start and end at any order.
  Recalculation of littrow sigma handled for all cases. [melissa-hobson]
- `Extrapolate_littrow_sol`: correct initial littrow order. [melissa-
  hobson]
- `WAVE_FILE_EA_2` function adds fp filename to wavefilename. [melissa-
  hobson]
- `Cal_WAVE_NEW` shifted plots. [melissa-hobson]
- Merge pull request #523 from njcuk9999/master. [melissa-hobson]

  update
- Merge pull request #522 from njcuk9999/dev. [Neil Cook]

  Francois --> Dev --> Master
- Update date/version/changelog. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- Merge pull request #521 from njcuk9999/francois. [melissa-hobson]

  Francois
- Merge branch 'master' into francois. [Neil Cook]
- Merge pull request #520 from njcuk9999/master. [melissa-hobson]

  Update melissa from master


0.4.007 (2018-12-13)
--------------------
- `Extract_trigger.py` - changes to reprocessing code (correct order)
  [Neil Cook]
- Merge branch 'master' into dev. [Neil Cook]
- Merge pull request #519 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Code to check the telluric corrections. [Neil Cook]


0.4.006 (2018-12-12)
--------------------
- Add .idea to .gitignore. [Neil Cook]
- Re-do requirements files. [njcuk9999]
- Merge branch 'francois' into dev. [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - pep8 clean up of Francois branch. [Neil
  Cook]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - pep8 clean up of Francois branch. [Neil
  Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - pep8 clean up of Francois branch. [Neil
  Cook]
- Format of flux ratio set to .3f. [FrancoisBouchy]
- Compute the absolute CCF drift of the FP and save it in the wavelength
  solution file as CCFRV2. [FrancoisBouchy]
- Absolute CCF drift of FP is read from the wavelength solution file.
  The relative CCF drift takes into account this Absolute drift.
  [FrancoisBouchy]
- Merge remote-tracking branch 'origin/master' [Neil Cook]
- Update README.md. [Neil Cook]

  Update with recent changes
- Update requirements (barycorrpy required) [Neil Cook]
- Add a minimum requirements and current requirements (as .txt files)
  [Neil Cook]
- Merge pull request #518 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date/version/changelog/ update notes. [Neil Cook]


0.4.005 (2018-12-11)
--------------------
- `SpirouTable.py` - fix an error with missing end card. [Neil Cook]
- Update `extraction_trigger.py` run time parameters. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- `Cal_validate_spirou.py` - correct `cal_validate` for new wlog. [Neil
  Cook]


0.4.036 (2018-12-11)
--------------------
- `Cal_validate_spirou.py` - correct `cal_validate` for new wlog. [Neil
  Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]


0.4.004 (2018-12-10)
--------------------
- `SpirouConst.py` - undo change to global file. [Neil Cook]
- `SpirouFITS.py` - fix for lock file on non-fits files. [Neil Cook]


0.4.035 (2018-12-10)
--------------------
- `SpirouStartup2.py` - upgrade WLOG (requires `drs_params` to track pid)
  [Neil Cook]
- `SpirouRecipe.py` - upgrade WLOG (requires `drs_params` to track pid)
  [Neil Cook]
- `SpirouFile.py` - upgrade WLOG function (requires `drs_params` to track
  pid) [Neil Cook]
- `Recipes_spirou.py` - fix pep8 in helpstr. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge pull request #516 from `njcuk9999/dev_shape_redo`. [Neil Cook]

  Dev shape redo (confirmed testing on `cal_test`, `tellu_test` and `pol_test)`
- Update date/version/changelog. [Neil Cook]
- Merge branch 'master' into `input_redo`. [njcuk9999]


0.4.003 (2018-12-10)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py` - correct pep8 and add TODO's for problems.
  [Neil Cook]
- `Cal_WAVE_NEW_E2DS_spirou.py` - correct pep8 and WLOG changes. [Neil
  Cook]
- Merge branch 'dev' into `dev_shape_redo`. [Neil Cook]

  Conflicts:
      `INTROOT/misc/cal_WAVE_NEW_E2DS_spirou.py`
- Remove hard-coded initial wavelenth solution. [melissa-hobson]
- Merge pull request #515 from njcuk9999/master. [melissa-hobson]

  update melissa from master
- Add new CCF mask `(masque_sept18.mas)` [njcuk9999]
- Improvements to `fp_wavelength_sol_new` fp m value determination
  correction to fp line insertion into `all_lines` assorted tests for
  fitting HC lines. [melissa-hobson]
- Littrow: get total orders from `echelle_orders`, not `all_lines`; save
  orders of min/max deviation. [melissa-hobson]
- SpirouMath: calculates wave coeff from chebyshev polynomials
  spirouPlot: correct wavelengths for fitted lines in
  `wave_ea_plot_single_order`. [melissa-hobson]
- `Cal_WAVE_NEW_E2DS_EA` update (calculates wave sol, does Littrow)
  [melissa-hobson]
- `Cal_WAVE_EA` order information on Littrow QC fail. [melissa-hobson]
- Update timings for V0.4.001. [Neil Cook]
- `SpirouRV.py` - change an info log message to general log message (too
  many for CCF) [Neil Cook]
- `SpirouLSD.py` - remove some of the info logs and make them general
  logs. [Neil Cook]
- `Pol_spirou.py` - remove some of the info logs and make them general
  logs. [Neil Cook]
- Update date/version/changelog. [Neil Cook]


0.4.001 (2018-12-08)
--------------------
- `Unit_Test` runs - update test for run. [Neil Cook]
- `Extract_trigger.py` - update values for run time. [Neil Cook]
- `SpirouStartup.py` - define initial values for `log_opt` and program in
  Begin() [Neil Cook]


0.4.002 (2018-12-08)
--------------------
- `Constants_SPIROU_H4RG.py` - add `"fitsopen_max_wait`" time. [Neil Cook]
- `Cal_reset.py` - fix fake p (with real p) [Neil Cook]


0.3.077 (2018-12-07)
--------------------
- `SpirouTable.py` - add lock files around writing to fits file (avoids
  writing at the same time) [Neil Cook]
- `SpirouImage.__init__.py` - add links to check/close/open fits lock
  file. [Neil Cook]
- `SpirouFITS.py` - add fits file lock file (to avoid writing to same fits
  file at same time) [Neil Cook]
- `SpirouDB.py` - edit message and sleep time for waiting lock file. [Neil
  Cook]
- `Extract_trigger` - update to allow skipping of `mk_tellu` and `fit_tellu`
  files. [Neil Cook]
- `Obj_fit_tellu.py` - fix problems with WLOG update. [Neil Cook]
- `SpirouStartup.py` - add telluDB info to the start up printout/log.
  [Neil Cook]


0.3.076 (2018-12-05)
--------------------
- SpirouDRS/spirouUnitTest folder - major redo of logging system (to
  allow passing of process-id) [Neil Cook]
- SpirouDRS/spirouUnitTest folder - major redo of logging system (to
  allow passing of process-id) [Neil Cook]
- SpirouDRS/spirouTools folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouTHORCA folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouTelluric folder - major redo of logging system (to
  allow passing of process-id) [Neil Cook]
- SpirouDRS/spirouStartup folder - major redo of logging system (to
  allow passing of process-id) [Neil Cook]
- SpirouDRS/spirouRV folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouPOLAR folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouLOCOR folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouImage folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouFLAT folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouEXTOR folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouDB folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouCore folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouConfig folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- SpirouDRS/spirouBACK folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- `Spirou_drs/misc` folder - major redo of logging system (to allow
  passing of process-id) [Neil Cook]
- `Spirou_drs/bin` folder - major redo of logging system (to allow passing
  of process-id) [Neil Cook]
- `Spirou_drs/bin` folder - major redo of logging system (to allow passing
  of process-id) [Neil Cook]
- `Cal_extract_RAW_spirou.py` - remove the need to a TILT file is mode ==
  '4a' or '4b' [Neil Cook]
- `Cal_extract_RAW_spirou.py` - remove the need to a TILT file is mode ==
  '4a' or '4b' [Neil Cook]
- `SpirouConfigFile.py` - update comment to make it clear why two tests
  are needed. [Neil Cook]


0.3.075 (2018-12-04)
--------------------
- `SpirouImage.py` - adjust warning for getting `unix_time` from string
  (where time is not valid) - warning or error? [Neil Cook]


0.3.074 (2018-12-03)
--------------------
- `SpirouConst.py` - modify colour for white screen people. [Neil Cook]
- `SpirouKeywords.py` - update keys (must be shorter with addition of
  numbers) [Neil Cook]
- `SpirouKeywords.py` - update keys (must be shorter) [Neil Cook]
- `SpirouUnitRecipes.py` - remove `cal_SHAPE_spirou2`. [Neil Cook]
- `Extract_trigger.py` - update run arguments. [Neil Cook]
- `Unit_tests` - update test.run and `Pol_Test.run`. [Neil Cook]
- `SpirouStartup.py` - add functionality to assign process id (on begin)
  --> timestamp. [Neil Cook]
- `SpirouTable.py` - update comment to give some idea of the IDL command
  to open table. [Neil Cook]
- `SpirouLog.py` - start process of having individual logs for each
  instance. [Neil Cook]
- Recipe control - adjust inputs to `cal_SHAPE_spirou`. [Neil Cook]
- `Cal_SHAPE_spirou.py` - change name of `cal_SHAPE_spirou2.py` -->
  `cal_SHAPE_spirou.py`. [Neil Cook]
- `SpirouLSD.py` - modify output of LSD table to be a FIT BINARY Table.
  [Neil Cook]

  Note to open fits tables in IDL see here:
          `https://idlastro.gsfc.nasa.gov/ftp/pro/fits_table/aaareadme.txt`

          lookup:
              `ftab_print`, 'file.fits'
          read:
              tab = readfits('file.fits', hdr, /EXTEN)
              col1 = tbget(hdr, tab, 'COLUMN1')
- `Extract_trigger.py` - update `extract_trigger` run constants. [Neil Cook]
- `SpirouLSD.py` - change format of output to FITS table. [Neil Cook]
- `SpirouTable.py` - add option in `write_table` to accept header (hdict)
  [Neil Cook]
- `SpirouUnitRecipes.py` - remove reference to `cal_SHAPE_spirou2.py`. [Neil
  Cook]
- `Extract_trigger.py` - update run parameters (and slightly change order
  of constants) [Neil Cook]
- `Cal_SHAPE_spirou.py` - change reference to GetShapeMap2 -->
  GetShapeMap. [Neil Cook]
- `SpirouImage.py` - change `get_shape_map2` --> `get_shape_map` (change old
  `get_shape_map` --> `get_shape_map_old)` [Neil Cook]
- `Recipe_control.txt` - change `cal_SHAPE_spirou2` --> `cal_SHAPE_spirou`
  (remove old one) [Neil Cook]
- `Cal_SHAPE_spirou.py` - renamed from `cal_SHAPE_spirou2.py` (old code
  moved to ./misc) [Neil Cook]


0.3.073 (2018-11-30)
--------------------
- Update test.run. [njcuk9999]


0.3.072 (2018-11-28)
--------------------
- Changes to parallelisation (test) [njcuk9999]
- `Extract_trigger.py` - updates to extraction trigger. [njcuk9999]
- `Tellu_whitelist.txt` - a white list of telluric stars. [njcuk9999]


0.3.071 (2018-11-27)
--------------------
- `Extract_trigger.py` - correct problems with pre-processing automation.
  [njcuk9999]
- `Recipe_control.txt` - add some more options for `POL_STOKES_I`.
  [njcuk9999]
- Merge pull request #514 from `njcuk9999/dev_shape_redo`. [Neil Cook]

  Dev shape redo - tested on `Cal_test.run` and `Tellu_Test.run`


0.3.070 (2018-11-26)
--------------------
- Update test.run. [njcuk9999]
- `Run_off_listing.py` - fix errors in code. [njcuk9999]
- Update date/version/changelog. [njcuk9999]


0.3.069 (2018-11-26)
--------------------
- `Run_off_listing.py` - correct to try/except in `run_off_listing.py`.
  [njcuk9999]
- `Extract_trigger.py` - upgrades to extract trigger just do extractions.
  [njcuk9999]
- `Run_off_listing.py` - code to redo indexing. [njcuk9999]
- `SpirouStartup.py` - fix error with change to indexing (and old index
  files) [njcuk9999]
- `SpirouConst.py` - change `func_name` for `REDUC_OUTPUT_COLUMNS`.
  [njcuk9999]


0.3.068 (2018-11-24)
--------------------
- Update extraction trigger. [njcuk9999]
- `SpirouConst.py` - add MJDATE to index.fit. [njcuk9999]
- Merge branch 'master' into `dev_shape_redo`. [njcuk9999]

  Conflicts:
      INTROOT/SpirouDRS/spirouImage/spirouBERV.py
- Update spirouBERV.py. [Neil Cook]

  Correct error with `spriouBerv.get_earth_velocity_correction` - only calculate BERV for OBSTYPE = 'OBJECT' (an do not look for ra/dec etc in the headers - it wont be there for lab files)
- `Cal_SHAPE_spirou/spirou2` - correct mistakes found by unit test run.
  [njcuk9999]
- Update date/version/changelog. [njcuk9999]


0.3.067 (2018-11-24)
--------------------
- `Cal_Test.run` - add `cal_SHAPE_spirou2` to `Cal_Test.run`. [njcuk9999]
- Unit tests: add `cal_SHAPE_spirou2` to unit test definition. [njcuk9999]
- `SpirouImage.py` - update `get_shape_map2` and `get_offset_sp` in-line with
  Etienne's changes. [njcuk9999]
- `SpirouPlot.py` - update new shape plots in-ilne with Etiennes changes.
  [njcuk9999]
- `SpirouMath.py` - update `"gauss_fit_s`" (Etienne updated it) [njcuk9999]
- `SpirouKeywords.py` - add extra keys (for index.fits) and for wave-list
  in bigcubes. [njcuk9999]
- `SpirouConst.py` - update acquisition of filenames now we have "HCFILE"
  and "FPFILES" (not "HCFILES" and "FPFILE") [njcuk9999]
- `Constants_SPIROU_H4RG.py` - update constants inline with Etiennes
  changes. [njcuk9999]
- `Obj_mk_obj_template.py` - list wave files in header (along with file
  name and berv) for big cube. [njcuk9999]
- `Cal_SHAPE_spirou2.py` - continued work on shape upgrade + now 1 hcfile
  and multiple fp files. [njcuk9999]


0.3.066 (2018-11-23)
--------------------
- `SpirouFits.py` - fix bug with hdict being empty (possible on some
  writes) [njcuk9999]


0.3.065 (2018-11-22)
--------------------
- `SpirouTable.py` - updated the error outputs to include filename.
  [njcuk9999]
- `SpirouImage.py` - continued to modify `get_offset_sp` and `get_shape_file2`
  (for new SHAPE code) [njcuk9999]
- `SpirouPlot.py` - adjusted `slit_shape_angle_plot` and added
  `slit_shape_offset_plot` (for new SHAPE recipe) [njcuk9999]
- `SpirouMath.py` - adjusted problem in `gauss_fit_s` file "correction = (x
  - np.mean(x)) `*` slope" --> "correction = (x - x0) `*` slope" [njcuk9999]
- Updated the `catalogue_UNe.dat` file and added `cavity_length.dat` file
  (for new SHAPE code) [njcuk9999]
- `Master_tellu_SPIROU.txt` - updated the master calibdb with the new
  `MASTER_WAVE.fits`. [njcuk9999]
- `Master_calib_SPIROU.txt` - updated the master calibdb with the new
  `MASTER_WAVE.fits`. [njcuk9999]
- `Recipe_control.txt` - added `cal_SHAPE_spirou2` to the recipe control
  (with two arguments for `FP_FP` and `HC_HC` files - pp fits not e2ds!)
  [njcuk9999]
- `Constants_SPIROU_H4RG.py` - added new constants and modified constants
  changed by Etienne. [njcuk9999]
- `Cal_SHAPE_spirou2.py` - continued work on adapting Etiennes changes
  into `cal_SHAPE`. [njcuk9999]


0.3.064 (2018-11-21)
--------------------
- Add copy of old xt code (to compare with new one for changes)
  [njcuk9999]
- Add function: `read_cavity_length`, `get_shape_map2`, `get_offset_sp` for
  new shape code. [njcuk9999]
- `SpirouConst.py` - add new file definitions. [njcuk9999]
- `Output_keys.py` - add defintions for shape sanity check debug files.
  [njcuk9999]
- Notes on etiennes codes - no real changes just comments. [njcuk9999]
- `Constants_SPIROU_H4RG.py` - modify SHAPE constants to for new shape
  code. [njcuk9999]
- `Obj_mk_tellu.py` - fix copy of code - redundant. [njcuk9999]
- `Cal_SHAPE_spirou2.py` - modification of `cal_SHAPE_spirou.py` with
  changes to `cal_shape` needed. [njcuk9999]
- `SpirouBERV.py` - fix bug in berv code - non-objects should not look for
  star parameters. [njcuk9999]
- Update version/dates/changelog.txt. [njcuk9999]


0.3.063 (2018-11-20)
--------------------
- Add test files to misc. [njcuk9999]
- Add Etiennes files in misc folder. [njcuk9999]
- Runs - update the unit tests. [njcuk9999]


0.4.034 (2018-11-14)
--------------------
- `Test_recipe.py` - change permissions for file. [njcuk9999]


0.3.062 (2018-11-14)
--------------------
- `Fit_triplets` sigma-clip change. [melissa-hobson]
- `Cal_WAVE_E2DS_EA` - fix HC file being overwritten with FP data (fixes
  #513) [melissa-hobson]
- Merge pull request #512 from njcuk9999/master. [melissa-hobson]

  update Melissa
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]

  Conflicts:
      `INTROOT/bin/cal_WAVE_E2DS_EA_spirou.py`
- Merge pull request #509 from `njcuk9999/master_copy`. [melissa-hobson]

  update melissa
- Merge branch 'melissa' into `master_copy`. [melissa-hobson]
- Bug fix for `fit_gaussian` triplet (fixes #507) [melissa-hobson]


0.4.033 (2018-11-09)
--------------------
- Continued work on input redo. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge pull request #511 from njcuk9999/dev. [Neil Cook]

  Francois --> Dev, Neil--> Dev, Dev --> master


0.3.060 (2018-11-08)
--------------------
- `Cal_WAVE_EA` match to master. [melissa-hobson]


0.3.061 (2018-11-08)
--------------------
- Update date/version/changelog. [Neil Cook]


0.3.056 (2018-11-08)
--------------------
- `SpirouWAVE.py` - Melissa's fix for Issue #507 ->   "<" needs to be "<="
  [Neil Cook]
- Merge branch 'neil' into dev. [Neil Cook]
- Add hcone files for the `cal_DRIFTCCF_E2DS` recipe. [FrancoisBouchy]


0.4.032 (2018-11-07)
--------------------
- `SpirouFile.py` - continue to fill out drs file fits methods. [Neil
  Cook]


0.3.055 (2018-11-07)
--------------------
- New UrNe CCF mask based on lines used for the wavelength solution and
  to be used to compute DRIFT on hcone files. [FrancoisBouchy]


0.4.031 (2018-11-06)
--------------------
- `Test_recipe.py` - tested `cal_badpix_spirou.py`. [Neil Cook]
- `SpirouStartup2.py` - continue work on inputs update. [Neil Cook]
- `SpirouRecipe.py` - continue work on inputs update. [Neil Cook]
- `SpirouFile.py` - allow filename to be set in construction (via kwargs)
  [Neil Cook]
- `Recipes_spirou.py` - add and reformat options to set/take defaults.
  [Neil Cook]
- `SpirouConst.py` - add a variable that can globally update pp (for use
  when we don't have p) [Neil Cook]


0.4.030 (2018-11-05)
--------------------
- `Test_recipe.py` - tested `cal_FF_RAW_spirou.py` inputs. [Neil Cook]
- `SpirouStartup2.py` - modified code to line up with continued work on
  spirouRecipe. [Neil Cook]
- `SpirouRecipe.py` - continued to develop new recipe class. [Neil Cook]
- `SpirouFile.py` - filled out some attributes/methods. [Neil Cook]
- `Recipe_spirou.py` - added more definitions and started to fill out drs
  recipes (badpix --> extract) [Neil Cook]
- `Files_spirou.py` - updated call to spirouFile.DrsInput -->
  spirouFile.DrsInputFile. [Neil Cook]


0.4.029 (2018-11-04)
--------------------
- `SpirouRecipe.py` - move DrsInputs from here to spirouFile.py.
  [njcuk9999]
- `SpirouFile.py` - move DrsInputs from spirouRecipes to here. [njcuk9999]
- `Files_spirou.py` - update links to DrsInput: spirouRecipe -->
  spirouFile. [njcuk9999]


0.4.028 (2018-11-02)
--------------------
- `SpirouRecipes.py` - add todo. [Neil Cook]
- `SpirouStartup2.py` - pushed renaming of recipes --> `recipes_spirou` into
  code. [Neil Cook]
- `Recipes_spirou.py` - renamed from recipes.py. [Neil Cook]
- `Files_spirou.py` - renamed from spirouFiles.py. [Neil Cook]
- `SpirouRecipe.py` - add doc strings for new classes
  (DrsArgument/DrsRecipe/DrsInputFile/DrsFitsFile) [Neil Cook]
- `Test_receip.py` - update with new name for "ufiles"-->"filelist" [Neil
  Cook]
- `SpirouStartup2.py` - continue work on input code - update with changes
  to spirouRecipe.py. [Neil Cook]
- `SpirouRecipe.py` - define how DrsArgument, DrsRecipe and DrsInput
  (+DrsFitsFile) interact - continued testing of input redo. [Neil Cook]
- `SpirouFiles.py` - define all raw/pp/out files as instances of
  DrsFitsFile. [Neil Cook]
- `Recipes.py` - continue to test new inputs with `test_recipe` definition.
  [Neil Cook]


0.3.059 (2018-11-01)
--------------------
- Test of not using Littrow sols for `cal_WAVE_EA`. [melissa-hobson]


0.4.027 (2018-11-01)
--------------------
- `SpirouStartup2.py` - continue work on input code. [Neil Cook]
- `SpirouRecipe.py` - continue work on input code. [Neil Cook]
- `SpirouFiles.py` - define file types using new classes. [Neil Cook]
- `Recipe.py` - update recipe definitions based on changes. [Neil Cook]


0.3.058 (2018-10-31)
--------------------
- `Cal_WAVE_NEW` update. [melissa-hobson]


0.4.026 (2018-10-31)
--------------------
- `Recipe.py` - add new comment. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]


0.3.054 (2018-10-30)
--------------------
- `Test_wavsol.py` - fixed bugs and added STD for H band. [Neil Cook]
- `Test_wavsol.py` - added code to compare wave solutions from a calibDB
  (defined manually in the code) [Neil Cook]
- `HC_Test.run` - added run 47 back in (had been missed) [Neil Cook]


0.3.057 (2018-10-30)
--------------------
- `Cal_WAVE_NEW` update. [melissa-hobson]
- Updates to C. Lovis method. [melissa-hobson]
- Merge pull request #500 from njcuk9999/master. [melissa-hobson]

  update melissa


0.3.053 (2018-10-29)
--------------------
- Add `hc_test.run` back to unit tests. [Neil Cook]
- Merge pull request #501 from njcuk9999/neil. [Neil Cook]

  Neil --> Master - confirm unit tests
- Update date/version/changelog. [Neil Cook]


0.3.052 (2018-10-29)
--------------------
- Pep8 clean up. [Neil Cook]


0.3.051 (2018-10-26)
--------------------
- Pep8 clean up. [Neil Cook]
- Update TODO's, remove old H3RG dependencies and clean up. [Neil Cook]
- Merge pull request #497 from njcuk9999/dev. [Neil Cook]

  Dev --> Master (tested on `Cal_Test.run)`
- Update date/version/changelog/update-notes. [Neil Cook]


0.3.050 (2018-10-26)
--------------------
- `SpirouKeywords.py` - add separate set of header keys for the FP
  analysis. [Neil Cook]
- `SpirouConst.py` - add `CCF_FP` versions so files are separate (for now)
  [Neil Cook]
- `Output_keys.py` - add new keys for `CCF_FP`. [Neil Cook]
- `SpirouConfig.py` - define a copy function for ParamDict - copy all keys
  into new ParamDict. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - separate and keep separate the FP analysis
  (cp and cloc) - including header keys. [Neil Cook]
- Merge pull request #495 from njcuk9999/dev. [Neil Cook]

  Neil --> Dev, Francois --> Dev, Dev --> Master. Confirm unit tested
- Update test files - mistake in run018b. [Neil Cook]
- `Gl699_Aug05-A_B.run` - unit test run for A and B files. [Neil Cook]
- Update date/version/update notes/changelog. [Neil Cook]


0.3.049 (2018-10-25)
--------------------
- Tellurics2.run - add a second telluric run - to preprocess, extract
  and `mk_tellu` missed tellurics. [Neil Cook]
- Update test - only 1 telluric test + move others to `old_tests`. [Neil
  Cook]
- `SpirouTelluric.py` - template should be in MASTERWAVE frame not `WAVE_IT`
  frame. [Neil Cook]
- `SpirouPlot.py` - modify `tellu_fit_debug_shift_plot` to only plot one
  order. [Neil Cook]
- `Recipe_control.txt` - allow `cal_CCF_E2DS_FP_spirou` to use A, B files
  and `TELLU_CORRECTED/POL_` files. [Neil Cook]
- Update unit tests. [Neil Cook]
- `Obj_fit_telluy.py` - todo question about possibly broken plot. [Neil
  Cook]
- `SpirouFile.py` - better error message when wrong directory used for
  input files. [Neil Cook]
- New `unit_test` runs for maestria with missed Gl699 targets. [Neil Cook]


0.3.048 (2018-10-24)
--------------------
- `SpirouRV.py` - need to deal with the differing fibers (for now
  manually) [Neil Cook]
- `SpirouRV.py` - added function `"get_foberc_e2ds_name`" to deal with the
  different file types expected --> need E2DS AB file for C fiber. [Neil
  Cook]
- `SpirouPOLAR.py` - adjusted calls to headers to not be hard coded
  (should have been called from p --> spirouKeywords.py) [Neil Cook]
- `SpirouKeywords.py` - add MJEND keyword (for `pol_spirou.py)` - also
  changed naming to all upper case. [Neil Cook]
- `Obj_mk_tellu.py` - turn off debug plot. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - get correct filename for fiber C (E2DS
  file only) [Neil Cook]
- `Cal_validate_spirou.py` - add option to check (check=0 just prints
  paths) [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - correct imports and catch warnings (As
  with `cal_CCF_E2DS_spirou)` [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - correct link to header key in p. [Neil
  Cook]
- `SpirouKeywords.py` - make tellu header keys shorter. [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - load file C not from a telluric corrected
  spectrum but from the E2DS itself (using header) [Neil Cook]
- `SpirouExposeMeter.py` - fix some pep8 issues. [Neil Cook]
- `SpirouKeywords.py` - add header key definitions for options input in
  tellu. [Neil Cook]
- `Obj_fit_tellu.py` - add extra header keys to know how many components
  were fit in PCA etc. [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - fix some pep8 convension. [Neil Cook]
- Merge branch 'neil' into dev. [Neil Cook]
- Update unit test runs. [Neil Cook]
- `SpirouUnitRecipes.py` - update input name for `cal_exposure_meter` and
  `cal_wave_mapper`. [Neil Cook]
- `Cal_exposure_meter.py` - correct input name: "reffile" --> "flatfile"
  [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` + `spirouRV.py` - catch warnings for NaNs in mean
  and divide. [Neil Cook]
- `SpirouUnitRecipes.py` - add `cal_CCF_E2DS_FP_spirou` to unit tests. [Neil
  Cook]
- Update `date/version/update_notes/changelog`. [Neil Cook]


0.3.047 (2018-10-23)
--------------------
- `Cal_Test.run` - add `cal_wave_mapper` to tested recipes. [Neil Cook]
- `SpirouExoposureMeter.py` - use wave parameters instead of wave map +
  add normalisation option. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add constants for normalisation and
  `flat_correction`. [Neil Cook]
- `Cal_exposure_meter.py` - try rescale for the flux (Issue #490) [Neil
  Cook]
- `Cal_wave_mapper.py` - divide through by flat field (on request) and
  attempt to rescale flux (Issue #490) [Neil Cook]
- `SpirouExoposeMeter.py` - Issue #490 - add ability to not re-calculate
  order profile image (if already processed) + add shape as well as tilt
  (use shape if in calibDB) [Neil Cook]
- `SpirouKeywords.py` - add infilelist as keyword (For use for pushing
  input file list to header) [Neil Cook]
- `SpirouConst.py` - define a tmp file for the order profile map (Issue
  #490) [Neil Cook]
- `Cal_wave_mapper.py` - Issue #490 - add shape + fix badpixel function
  returns. [Neil Cook]
- `Cal_exposure_meter.py` - fix Issue #490 - use shape file + correct
  output of badpix mask. [Neil Cook]


0.3.046 (2018-10-22)
--------------------
- `Obj_mk_tellu.py` - make sure the NaNs do not propagate through to the
  convolution (NaN `*` 0.0 = NaN ---> need 0.0) [Neil Cook]
- `Obj_mk_tellu.py` - make sure the NaNs do not propagate through to the
  convolution (NaN `*` 0.0 = NaN ---> need 0.0) [Neil Cook]
- `Obj_mk_tellu.py` - catch warnings as sp now can have nans. [Neil Cook]
- `Obj_mk_obj_template.py` - change median to nan median and catch
  warnings with nanmedian of empty stack (all nans) [Neil Cook]
- `Obj_mk_tellu.py` - catch warnings in dev (nans allowed) [Neil Cook]
- `SpirouTelluric.py` - kernal resize. [Neil Cook]
- `Obj_mk_tellu.py` - shift data to master before (to match tapas) -
  instead of shifting transmission after. [Neil Cook]


0.3.045 (2018-10-22)
--------------------
- Updated permissions on spirouUnitTest files (chmod +x) [Neil Cook]
- `Tellu_Test.run` - added a test of `cal_CCF_E2DS_FP_spirou.py` (currently
  not working) [Neil Cook]
- `SpirouKeywords.py` - added `kw_DRIFT_RV` definition to keywords files
  (for use in `cal_CCF_E2DS_FP_spirou.py)` [Neil Cook]
- `Recipe_control.txt` - added `cal_CCF_E2DS_FP_spirou` to `recipe_control` -
  for fiber AB only (will only work with fiber AB) [Neil Cook]
- `Cal_CCF_E2DS_FP_spirou.py` - added changes to integrate into DRS. [Neil
  Cook]
- Merge branch 'francois' into dev. [Neil Cook]
- `Cal_CCF_E2DS` with simultaneous CCFDrift on FP fiber C.
  [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]
- New CCF mask for FP. [FrancoisBouchy]
- Merge pull request #491 from njcuk9999/neil. [Neil Cook]

  Melissa --> Neil --> Master (confirm unit tests)
- Update tests. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.3.043 (2018-10-19)
--------------------
- `Unit_test` runs - add maestria tests. [Neil Cook]
- Update `triggers/unit_tests` to catch and handle errors better. [Neil
  Cook]
- Update `triggers/unit_tests` to catch and handle errors better. [Neil
  Cook]
- Redo tests - comments where broken. [Neil Cook]
- `SpirouStartup.py` - remove print statement (was there to debug) [Neil
  Cook]
- `SpirouLog.py` - return useful message on sys.exit (after error log)
  [Neil Cook]
- `Error_test.py` - test catching errors for `trigger/unit_tests`. [Neil
  Cook]
- `SpirouWAVE.py` - make debug plot only show in debug mode (even with
  plotting on) [Neil Cook]
- Merge branch 'melissa' into neil. [Neil Cook]
- Merge branch 'master' into melissa. [Neil Cook]
- SpirouWAVE: plots will now appear in interactive mode only. [melissa-
  hobson]
- Merge pull request #487 from njcuk9999/master. [melissa-hobson]

  update melissa from master
- Update HC/WAVE test. [Neil Cook]
- `Unit_test.py` - better catching/recording of errors (for batch run that
  doesn't crash out) [Neil Cook]
- Update HC/WAVE test. [Neil Cook]
- Update HC/WAVE test. [Neil Cook]
- Update HC/WAVE test. [Neil Cook]
- Update HC/WAVE test. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #489 from njcuk9999/dev. [Neil Cook]

  Francois --> Dev, Neil --> Dev, Dev --> Master
- Update date/version/changelog. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- `Cal_DRIFTCCF_E2DS_spirou.py` - comment out saving of fits file - no
  loc['DRIFT'] defined. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- Merge branch 'neil' into dev. [Neil Cook]

  Conflicts:
      CHANGELOG.md
      INTROOT/SpirouDRS/spirouConfig/spirouConst.py
      VERSION.txt
- Fp.mas - added the fp mask to the `ccf_masks` folder (for `cal_driftccf)`
  [Neil Cook]
- Update HC/WAVE test. [Neil Cook]


0.3.042 (2018-10-18)
--------------------
- Update date/version/changelog. [Neil Cook]
- `Unit_test.py` - fix comment. [Neil Cook]
- TelluricsAll.run - add a list of all tellurics for maestria. [Neil
  Cook]
- `Constants_SPIROU_H4RG.py` - add quality control parameters for `mk_tellu`
  (RMS) [Neil Cook]
- `Obj_mk_tellu.py` - add an RMS cut to the QC parameters checked. [Neil
  Cook]
- `Obj_mk_obj_template.py` - turn multi fits into fits cubes. [Neil Cook]
- `Unit_test_parallel.py` - test of multiprocessing on unit tests - DRS
  not stable to use this yet! [Neil Cook]
- `Extract_trigger.py` - for now only do up to extraction of `HC_HC` and
  `FP_FP`. [Neil Cook]
- `Gl699_small.run` - just extract and fit those across one glitch. [Neil
  Cook]
- `Cal_HC/cal_WAVE` only copy over original file parameters if QC passed.
  [Neil Cook]
- `SpirouFITS.py` - fix bug in `check_wave_sol_consistency`. [Neil Cook]
- `Obj_mk_tellu.py` - add notes for new QC check (TODO's) [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - remove print statement. [Neil Cook]
- `Cal_SHAPE_spirou.py` - update permissions on `cal_SHAPE`. [Neil Cook]
- Update run list (for maestria runs) [Neil Cook]
- `Extract_trigger.py` - full calibration trigger test. [Neil Cook]
- `Extract_trigger.py` - update imports. [Neil Cook]
- `Extract_trigger.py` - use spirouUnitRecipes to run recipes. [Neil Cook]
- `Extract_trigger.py` - print the error. [Neil Cook]
- `Extract_trigger.py` - print output before running. [Neil Cook]
- `Extract_trigger.py` - changes to test run printing. [Neil Cook]
- `Extract_trigger.py` - fix for when there are no files found. [Neil
  Cook]
- `Extract_trigger.py` - turn off test run. [Neil Cook]
- `Extract_trigger.py` - add options to combine all files from a night and
  to limit the number of files used for a recipe. [Neil Cook]
- `Recipe_control.txt` - do not support `FLAT_DARK` and `DARK_FLAT` in `cal_FF`.
  [Neil Cook]


0.3.040 (2018-10-17)
--------------------
- `Extract_trigger.py` - add filters to allow only certain files to be
  process based on DPRTYPE. [Neil Cook]
- `Clean_calibDB` - custom script to remove all unwanted keys (set in the
  code) and remove files not in the calibDB and move all good files to
  new folder with a new master calibDB file. [Neil Cook]
- Reset the calibDB and telluDB with new MASTER wave solutions. [Neil
  Cook]
- `Extract_trigger.py` - make test run - with printing/storing of commands
  only and add/modify printing/logging statements. [Neil Cook]
- `Extract_trigger.py` - correct problem with preprocess trig. [Neil Cook]
- `Extract_trigger` - fix bugs. [Neil Cook]
- `Extract_trigger` - fix mistake. [Neil Cook]
- `Extract_trigger` - correct mistake in ask function. [Neil Cook]
- `Extract_trigger.py` - allow to skip pp and make function. [Neil Cook]
- `Extract_trigger.py` - first working version. [Neil Cook]
- `SpirouStartup.py` - fix bug with inputs (numpy array not allowed) [Neil
  Cook]
- `Extract_trigger.py` - start work on a simple calibration trigger (upto
  and including extraction) [Neil Cook]


0.3.041 (2018-10-17)
--------------------
- `SpirouStartup.py` - fixed problem when no column is present (set to
  None) [Neil Cook]
- `Extract_trigger.py` - start of a trigger that goes from pp -->
  extraction (including all calibrations) - [NOT FINISHED] [Neil Cook]
- `SpirouConst.py` - add DPRTYPE to index file for raw outputs. [Neil
  Cook]
- `SpirouFITS.py` - added `"check_wave_sol_consistency`" function to check
  and remap coefficients if incorrect from constants file
  `(IC_LL_DEGR_FIT)` [Neil Cook]
- `Cal_HC/` `cal_WAVE` - added check for consistent number of coefficients
  in wave solution - if wrong refitted onto new coefficients with
  correct number. [Neil Cook]
- `SpirouFile.py` - add function to sort by base name `(sort_by_name)` with
  alias SortByName. [Neil Cook]
- `Explore_headers.py` - code to explore headers of all files in given dir
  string (with wild cards) [Neil Cook]
- `Obj_mk_obj_stack.py` - for making stacks of images (Nobs x `Nb_xpix` x
  Nbo) [Neil Cook]
- `SpirouKeywords.py` - add new header keys to list + define them as
  keywordstores. [Neil Cook]
- `Obj_mk_obj_template.py` - sort template files by base file name. [Neil
  Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - add some header keys to help identify the
  source of output. [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - add some more header keys to enable
  identifying source of output files. [Neil Cook]


0.3.038 (2018-10-16)
--------------------
- Update version/date/changelog/update notes. [Neil Cook]
- `Cal_Test.run` - add `cal_DRIFTCCF_E2DS_spirou` to tested codes. [Neil
  Cook]
- `SpirouUnitRecipes.py` - add `cal_DRIFTCCF_E2DS_spirou` to unit recipe
  definitions. [Neil Cook]
- `SpirouKeywords.py` - add reference rv keyword and keywordstore
  definition. [Neil Cook]
- `SpirouConst.py` - fix tags in new DRIFTCCF file name definitions. [Neil
  Cook]
- `Recipe_control.txt` - add `cal_DRIFTCCF_E2DS_spiour` to the runable codes
  - for FP only. [Neil Cook]
- `Output_keys.py` - add `DRIFTCCF_E2DS_FITS_FILE` to output keys. [Neil
  Cook]
- `Constants_SPIROU_H4RG.py` - add driftccf constants to constants file.
  [Neil Cook]
- `Cal_DRIFTCCF_E2DS_spirou.py` - re-save driftfits to file. [Neil Cook]
- `Cal_DRIFTCCF_E2DS_spirou.py` - pep8 changes + load constants from file
  + add flux ratio + save reference RV to header. [Neil Cook]
- Merge branch 'francois' into dev. [Neil Cook]
- Merge pull request #488 from njcuk9999/dev. [Neil Cook]

  `spirouEXTOR.py` - undo debananafication all zeros check - does not work
- `SpirouEXTOR.py` - undo debananafication all zeros check - does not
  work. [Neil Cook]


0.3.039 (2018-10-16)
--------------------
- New recipe to compute the drift of simultaneous FP on Fiber C with
  fp.mas. [FrancoisBouchy]


0.3.044 (2018-10-16)
--------------------
- New function `DRIFTCCF_E2DS_TBL_FILE` to save driftccf file
  `DRIFTCCF_E2DS_FITS_FILE` still to be adapted. [FrancoisBouchy]


0.3.037 (2018-10-15)
--------------------
- `SpirouKeywords.py` - add the two new header keys for bigcube list.
  [Neil Cook]
- `Obj_mk_obj_template.py` - add file names and bervs for input files to
  big cube header. [Neil Cook]
- `Update_note.txt` - update with telluric changes. [Neil Cook]
- `SpirouConst.py` - add prefix and change filename. [Neil Cook]
- `Obj_fit_tellu.py` - save and remove abso save files - massive speed up.
  [Neil Cook]
- `SpirouTelluric.py` - catch more NaN warnings from `order_tapas`. [Neil
  Cook]
- `SpirouFile.py` - add `get_most_recent` function to get most recent unix
  time of list of files. [Neil Cook]
- `SpirouConst.py` - add `TELLU_ABSO_SAVE` file (for saving loaded trans
  files) [Neil Cook]
- `Obj_fit_tellu.py` - store abso unless there are new `trans_files`. [Neil
  Cook]
- `SpirouTelluric.py` - swap sign on dv. [Neil Cook]
- `SpirouFITS.py` - fix for new output of `read_tilt_file`. [Neil Cook]
- `SpirouFITS.py` - add reading a key 1D list from header. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add constants for quality control in
  `obj_mk_tellu`. [Neil Cook]
- `Obj_mk_tellu.py` - quality control SNR in order `QC_TELLU_SNR_ORDER`
  greater than `QC_TELLU_SNR_MIN`. [Neil Cook]
- `Obj_mk_obj_tellu.py` - only use unique filenames for tellu files. [Neil
  Cook]
- `Obj_fit_tellu.py` - only use unique filenames from trans files. [Neil
  Cook]


0.3.036 (2018-10-14)
--------------------
- `SpirouEXTOR.py`  - fix bug where whole order is zeros - will break
  spline. [Neil Cook]
- Merge pull request #486 from njcuk9999/dev. [Neil Cook]

  Melissa --> Dev --> Master (Confirm test on `Cal_Test.run`, `Tellu_Test.run`, `Tellu_Test2.run`, `Pol_Test.run)`
- Update changelog and test.run. [Neil Cook]
- `SpirouTelluric.py` - catch known warnings and disregard. [Neil Cook]
- Update notes and changelog. [Neil Cook]


0.3.035 (2018-10-12)
--------------------
- Update unit test runs. [Neil Cook]
- `SpirouTelluric.py` - modify `get_molecular_tell_lines` to use master
  wavelength solution, rename functions to better describe
  functionality, use relativistic dv correction function. [Neil Cook]
- `SpirouTDB.py` - rename functions to better describe functionality.
  [Neil Cook]
- `SpirouDB.__init__.py` - rename aliases to better describe functions.
  [Neil Cook]
- `SpirouPlot.py` - add `tellu_fit_debug_shift_plot` - Issue #478. [Neil
  Cook]
- `SpirouMath.py` - add `relativistic_waveshift` function. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - turn off the fit derviative part for
  principle components - Issue #478. [Neil Cook]
- `Obj_mk_obj_template.py` - further fixes for wavelength shift addition -
  Issue #478. [Neil Cook]
- `Obj_fit_tellu.py` - further fixes for wavelength shift addition - Issue
  #478. [Neil Cook]
- `Obj_fit_tellu.py` - fix bugs in shifting wavelength (Issue #478) [Neil
  Cook]
- `Cal_extract/FF_RAW_spirou.py` - catch warnings from extraction process.
  [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - currently only supports one `FP_FP` and one
  `HC_HC` (due to file updating) - added check to error if more used.
  [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - currently only supports one `FP_FP` and one
  `HC_HC` (due to file updating) - added check to error if more used.
  [Neil Cook]
- `SpirouTelluric.py` - change bad mask from 0.999 to 0.5 to avoid NaN
  fringing - Issue #478. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]
- `SpirouWAVE.py` - small pep8 and visual changes / simplifications. [Neil
  Cook]
- `SpirouPlot.py` - bring new plot in-line with other plots + pep8
  changes. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - small pep8 fixes to constants. [Neil Cook]
- Merge branch 'master' into melissa. [Melissa Hobson]
- Merge pull request #485 from njcuk9999/dev. [Neil Cook]

  Eder --> Dev --> Master
- Update `unit_tests`. [Neil Cook]
- `Unit_test.py` - make sure all plots are closed. [Neil Cook]
- `Cal_WAVE_EA`: moved plot of single HC order + fitted lines to
  spirouPlot constants: added `cal_WAVE_EA` constants spirouWAVE:
  improvements to FP line identification. [melissa-hobson]
- SpirouPlot: moved plot of single HC order + fitted lines here from
  `cal_WAVE_EA`. [melissa-hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- `Find_hc_gauss_peaks`: added log message when found lines are read from
  table, reporting the table file. [melissa-hobson]


0.3.034 (2018-10-11)
--------------------
- `Unit_test.py` - make sure all plots are closed. [Neil Cook]
- `SpirouEXTOR.__init__.py` - add alias for `compare_extraction_modes`
  (CompareExtMethod) - Issue #481. [Neil Cook]
- `SpirouEXTOR.py` - add `compare_extraction_mode` function to test
  difference between flat and e2ds extraction modes (#481) [Neil Cook]
- `Cal_FF_RAW_spirou.py` - save extraction method to header (like
  `cal_extract)` [Neil Cook]
- `Cal_extract_RAW_spirou.py` - get flat header, compare flat extraction
  to extraction type  (Issue #481) [Neil Cook]
- `SpirouFITS.py` - return header for flat file so we can get extraction
  type for the flat (Issue #481) [Neil Cook]
- `Unit_tests` - do not currently test `cal_WAVE_E2DS_EA_spirou.py` -
  comment out. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]
- `SpirouLSD.py` - add a few outstanding TODO comments and fix error print
  (filename may not be defined) [Neil Cook]
- `SpirouPOLAR.__init__.py` - chagen polarHeader --> PolarHeader (for
  convention) [Neil Cook]
- `Pol_spirou.py` - Update to alias for convention polarHeader -->
  PolarHeader. [Neil Cook]
- Merge branch 'master' into eder. [Neil Cook]
- Merge pull request #484 from njcuk9999/neil. [Neil Cook]

  Neil --> Master (confirm test on `Cal_Test.run`, `Tellu_Test.run` and `Tellu_Test2.run)`
- Update date/version/timings/changelog/update notes. [Neil Cook]
- Merge branch 'master' into eder. [Eder]
- Changed parameters for LSD analysis. [Eder]
- Implemented selection of CCFFILE in LSD analysis matching closest
  temperature to source observed. [Eder]
- Updated keyworks BERV, BJD, and MJD of polar products by central
  values calculated in the module. Also updated keyword EXPTIME by the
  sum of all EXPTIME values from individual exposures. [Eder]
- Updated keyworks BERV, BJD, and MJD of polar products by central
  values calculated in the module. Also updated keyword EXPTIME by the
  sum of all EXPTIME values from individual exposures. [Eder]
- Merge branch 'master' into eder. [Eder]
- Tuned parameters to improve LSD analaysis and added new statistical
  quantities calculated from LSD analysis. [Eder]
- Added new keywords in polar products, mainly the BJD time calculated
  at center of observations. Also fixed small bugs. [Eder]
- Added new keywords in polar products, mainly the BJD time calculated
  at center of observations. Also fixed small bugs. [Eder]
- Added new keywords in polar products, mainly the BJD time calculated
  at center of observations. Also fixed small bugs. [Eder]
- Added new keywords in polar products, mainly the BJD time calculated
  at center of observations. Also fixed small bugs. [Eder]
- Added new keywords in polar products, mainly the BJD time calculated
  at center of observations. Also fixed small bugs. [Eder]
- Merge branch 'master' into eder. [Eder]
- Merge branch 'master' into eder. [Eder]
- Resolved merging conflicts. [Eder]


0.3.032 (2018-10-11)
--------------------
- `Unit_tests` - update `tellu_test2` and test. [Neil Cook]
- `SpirouFITS.py` - fix output of wavelength solution - Issue #483. [Neil
  Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #482 from njcuk9999/neil. [Neil Cook]

  Neil --> master - tested on `Cal_Test.run`, `Tellu_Test.run`, `Tellu_Test2.run`
- `SpirouConst.py` - after reading default config file must look for a
  user config file (parameters depend on it) [Neil Cook]
- `SpirouConfigFile.py` - moved `get_user_config` to here (to allow
  accessing from spirouConst.py) [Neil Cook]
- `SpirouConfig.py` - move `get_user_config` to `spirouConfigFile.py` -
  (needed to fix not obtaining constants from user config file) [Neil
  Cook]
- `SpirouLog.py` - add a possibility to debug in ipython. [Neil Cook]
- `SpirouFITS.py` - fix error - now if image is not defined tries to get
  dimensions from header before giving error - Issue #483. [Neil Cook]
- Update date/version/update notes and changelog. [Neil Cook]


0.3.031 (2018-10-10)
--------------------
- `Tellu_Test2.run` - add additional test to test different wavelength
  solutions in telluric recipes. [Neil Cook]
- SpirouUnitTests/Runs - fix the units test with new recipes/names.
  [Neil Cook]
- `SpirouUnitRecipes.py` - fix for the change of name of
  `obj_mk_tell_template` --> `obj_mk_obj_template`. [Neil Cook]
- `SpirouWAVE.py` - Etienne's fix for `cal_HC` stability in
  `"fit_gaussian_triplets`" [Neil Cook]
- `SpirouFITS.py` - add a quiet mode (to not duplicate log) and fix bug in
  getting wavemap from header (from wave params) [Neil Cook]
- `SpirouConst.py` - add filenames for `obj_mk_obj_template`. [Neil Cook]
- `Master_calibDB_SPIROU.txt` - no longer need AB wave solutions and shape
  - only AB and C needed / shape generated online. [Neil Cook]
- `Output_keys.py` - add `obj_mk_obj_template` filenames to output keys +
  `recipe_control`. [Neil Cook]
- `Constnats_SPIROU_H4RG.py` - turn off force calibDB for wave solution +
  add HC parameters (Etienne's fix) [Neil Cook]
- `Obj_mk_obj_template` - renamed from `obj_mk_tell_template.py` + fixed for
  wavelength grid shift - Issue #478. [Neil Cook]
- `Obj_mk_tell_template.py` - update with shifted wavelength grid - Issue
  #478. [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - correct bug that wavelength solution
  parameters were not saved to header correctly. [Neil Cook]
- `Recipe_control.txt` - add `DARK_FP` to drift and driftpeak allowed inputs
  - Issue #475. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add `dark_fp` to the drift peak allowed
  constants (to all in use for drift/driftpeak) - Issue #475. [Neil
  Cook]
- `Recipe_control.txt` - add `OBJ_DARK` to allowed files used in
  `cal_DARK_spirou.py` (Issue #479) [Neil Cook]
- `Cal_DARK_spirou.py` - all use of skydarks and push SKYDARK to calibDB
  if used (Issue #479) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add key `"use_skydark_correction`" to allow
  SKYDARKs to be use (and take presence over DARK in calibDB) [Neil
  Cook]
- `SpirouTelluric.py` - shift templates if they are not created at runtime
  from mastergrid to current wavelength grid - Issue #478. [Neil Cook]
- `SpirouTelluric.py` - fix bug with `convolve_files` (should not be re-
  copied into telluDB) [Neil Cook]
- `SpirouImage.py` - allow SKYDARK to be used (if present in calibDB) if
  `USE_SKYDARK_CORRECTION` = True - Issue #479. [Neil Cook]
- `Obj_mk_tellu.py` - fix headers in saved file (now wavelength is
  shifted) - Issue #478. [Neil Cook]
- `Obj_fit_tellu.py` - fix bug with shifting PCA components (Issue #478)
  [Neil Cook]
- `Pol_spirou.py` + all recipes use GetWaveSolution - force fiber A and B
  to use wave solution AB (Issue #480) [Neil Cook]
- All recipes using GetWaveSolution - force fiber A and B to use AB wave
  solution. [Neil Cook]


0.3.030 (2018-10-09)
--------------------
- `SpirouUnitRecipes.py` - remove the moved HC/WAVE recipes from import
  (no longer in bin folder) [Neil Cook]
- SpirouTelluric - add function wave2wave to shift an image from one
  wavelength grid to another (Issue #478) [Neil Cook]
- `SpirouFITS.py` - allow wave solution to be obtained quietly. [Neil
  Cook]
- SpirouTDB - add `get_database_master_wave` to get the master wavelength
  grid from TelluDB (Issue #478) [Neil Cook]
- `Recipe_control.txt` - Allow sky objects for `cal_DARK_spirou` (Issue
  #479) [Neil Cook]
- `Master_tellu_SPIROU.py` + file - modify master telluric database to
  have a `MASTER_WAVE` key - containing the master wavelength grid
  [unfinished] - Issue #478. [Neil Cook]
- `Wave2wave.py` - backup of Etiennes function to shift images from one
  wavelength grid to another - Issue #478. [Neil Cook]
- HC/WAVE recipes - move all (older) recipes to misc folder - can still
  be used when in this directory - cannot currently be used with unit
  tests. [Neil Cook]
- `Obj_mk_tellu.py` - add code to shift transmission map [unfinished] -
  Issue #478. [Neil Cook]
- `Obj_fit_tellu.py` - add code to shift pca components and template
  components [unfinished] - Issue #478. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - fix bug with extraction method 4a and 4b -
  data2 shallow copied - shouldn't be! (Issue #477) [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.4.025 (2018-10-06)
--------------------
- `Input_file.txt` - update list of inputs (Issue #475) [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]


0.3.029 (2018-10-06)
--------------------
- `Cal_FF_RAW_spirou.py` - update extraction to deal with different
  outputs. [Neil Cook]
- `SpirouFile.py` - made sure pre-procesing always adds DPRTYPE even if
  file not recognised (#Issue 475) [Neil Cook]
- `SpirouEXTOR.py` - for modes 3c, 3d, 4a, 4b add the e2dsll extraction
  type. [Neil Cook]
- `SpirouConst.py` - add file definition for e2dsll. [Neil Cook]
- `Recipe_control.txt` - added and corrected `dark_fp`, `dark_flat` and
  `obj_obj`. [Neil Cook]
- `Output_keys.py` - added output type `extract_e2dsll_file`. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - added "un-sum" extraction output (E2DSLL)
  to see what the extraction is doing. [Neil Cook]
- Merge pull request #476 from `njcuk9999/extract_redo`. [Neil Cook]

  Extract redo --> Merge `(cal_WAVE_E2DS_EA_spirou` not working with new extraction)


0.3.028 (2018-10-05)
--------------------
- `Update_note.txt` - update with note about setting extraction to 4b
  (default = 3d) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - set `extraction_type` back to 3d for now -
  until 4a/4b tested. [Neil Cook]
- Update - version/date/changelog/update notes. [Neil Cook]


0.3.027 (2018-10-05)
--------------------
- Timings.txt - update timings with new runs. [Neil Cook]
- `Cal_Test.run` - comment out `cal_WAVE_E2DS_EA_spirou` - not working with
  extraction 4b? [Neil Cook]
- `SpirouTHORCA.__init__.py` - add alias to `generate_res_files`
  (GenerateResFiles) [Neil Cook]
- `SpirouWAVE.py` - add `generate_res_files` functions to generate
  arrays/header dictionary in correct format for wave resolution line
  profile map file. [Neil Cook]
- `SpirouConst.py` - add `WAVE_RES_FILE_EA` to file definitions. [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - add saving of wavelength resolution line
  profiles to file. [Neil Cook]
- `Output_keys.py` - added `"WAVE_RES`" to output keys (for wave solution
  res map) [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - added saving of resolution map and line
  profiles to file. [Neil Cook]
- `SpirouUnitTest.py` - up date title of log timings. [Neil Cook]
- `Recipe_control.txt` - hide `dark_fp` `dark_flat` for now (test later) [Neil
  Cook]
- `SpirouFITS.py` - allow fiber-forcing in getting wave solution
  (otherwise when calibDB is used, uses p['FIBER']) [Neil Cook]
- `Off_listing_RAW_spirou.py` - correct mistake with `off_listing` (rawloc
  should be a list) [Neil Cook]
- `SpirouFITS.py` - make sure the source of the wavelength solution is
  reported (Issue #468) [Neil Cook]
- Update date/version/update notes and changelog. [Neil Cook]


0.3.026 (2018-10-05)
--------------------
- `Cal_Test.run` - add `cal_SHAPE_spirou.py` to unit test. [Neil Cook]
- `SpirouUnitsRecipes.py` - add `cal_HC_E2DS_EA_spirou`, `cal_SHAPE_spirou`,
  `cal_WAVE_E2DS_EA_spirou` to unit tests. [Neil Cook]
- `Recipe_control.txt` - add `cal_SHAPE_spirou` (copy of `cal_SLIT_spirou)`
  [Neil Cook]
- `Cal_SHAPE_spirou.py` - change `__NAME__` (after recipe control
  integration) [Neil Cook]
- `SpirouImage.py` - optimisation - moved a few things out of loop to
  speed up process. [Neil Cook]
- `SpirouPlot.py` - corrected type in constant name
  `(slit_shape_angle_plot)` [Neil Cook]
- `Constants_SPIROU_H4RG.py` - move `cal_SHAPE_spirou.py` constants to
  constants file. [Neil Cook]
- `Cal_SHAPE_spirou.py` - move constants to constants file. [Neil Cook]


0.3.025 (2018-10-04)
--------------------
- `SpirouFITS.py` - get shape file from header. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add shape file to header (if mode 4a/4b)
  [Neil Cook]
- `Cal_SHAPE_spirou.py` - fix type - should be SHAPE file not TILT file.
  [Neil Cook]
- `SpirouImage.__init__.py` - add alias to `get_shape_map` (GetShapeMap)
  [Neil Cook]
- `SpirouImage.py` - move `get_shape_map` to spirouImage functions (And add
  imports as required) [Neil Cook]
- `SpirouPlot.py` - add slit shape plot. [Neil Cook]
- `SpirouKeywords.py` - add `kw_SHAPEFILE` to output keys. [Neil Cook]
- `SpirouConst.py` - add `SLIT_SHAPE_FILE` filename definition. [Neil Cook]
- `Output_keys.py` - add `slit_shape_file` output key. [Neil Cook]
- `New_bananarama.py` - fix to work with DRS. [Neil Cook]
- `Cal_SLIT_spirou.py` - replace old path function with new and correct
  small typo. [Neil Cook]
- `Cal_SHAPE_spirou.py` - add plotting, filesaving, calibDB movement and
  move functions to spirouImage (finally runs) [Neil Cook]
- `Cal_SHAPE_spirou.py` - added plotting, file saving and adding to
  calibDB. [Neil Cook]
- `Cal_SHAPE_spirou.py` - fix bugs that now produce identical results to
  `new_bananarama` code. [Neil Cook]


0.3.024 (2018-10-03)
--------------------
- `Cal_SHAPE_spirou.py` - fix typo dx[iw] = coeffs[1] --> dx[iw] =
  gcoeffs[1] [Neil Cook]
- `New_bananarama.py` - added TODO questions for Etienne. [Neil Cook]
- `Cal_SHAPE_spirou.py` - more changes to update with Etiennes
  `new_bananarama` code. [Neil Cook]
- Merge branch 'master' into `extract_redo`. [Neil Cook]
- `Cal_Test.run` - must test HC/WAVE EA recipes - added to runs. [Neil
  Cook]
- `Cal_HC_E2DS_EA_spirou.py` - fix bug flatfile in header should be
  blazefile. [Neil Cook]
- `Cal_SHAPE_spirou.py` - updated code [unfinished/not working] [Neil
  Cook]
- Copy of etiennes shap finding code. [Neil Cook]
- Merge branch 'master' into `extract_redo`. [Neil Cook]

  Conflicts:
      .gitignore
      INTROOT/SpirouDRS/spirouImage/spirouFITS.py
- Merge pull request #473 from njcuk9999/neil. [Neil Cook]

  Neil --> Master
- Update timings and update notes. [Neil Cook]
- Test code for one target. [Neil Cook]
- Update version/date/changelog/update notes. [Neil Cook]
- Unit tests - remove some extractions (not needed for minimum test)
  [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Unit tests - add full telluric test for TC3. [Neil Cook]
- `SpirouImage.py` - `WAVE_FILE` is now WAVEFILE. [Neil Cook]
- `Dark_test.py` - test of the values supplied in the dark header file
  (for specific files + `night_name)` [Neil Cook]
- `Visu_E2DS_spirou.py` - readblazefile now need p returned. [Neil Cook]
- `Obj_fit_tellu.py` - re-add loc['WAVE'] (used for plotting) +
  `loc['WAVE_IT']` need filename returned. [Neil Cook]
- `Cal_wave_mapper.py` - remove flat file (not used or obtained) from
  header. [Neil Cook]
- `Cal_exposure_meter.py` - remove flatfile (not used or obtained) [Neil
  Cook]
- Update spirouImage.py. [Neil Cook]

  `spirouImage.py` - fix for bug in itable dtype being bytes not string (certain python installations only)
- Merge pull request #470 from njcuk9999/neil. [Neil Cook]

  Neil --> master
- `Cal_SHAPE_spirou.py` - working on integrating nuxtract from EA. [Neil
  Cook]
- Update gitignore to ignore misc folder. [Neil Cook]
- Sync file - not used. [Neil Cook]
- `Cal_SHAPE_spirou.py` - first commit [unfinished] [Neil Cook]
- `Reset_calibDB` file - add shape map file (placeholder - will be
  generated in new `cal_SLIT` code) [Neil Cook]
- .gitignore - remove unneeded ignore. [Neil Cook]
- `SpirouUnitRecipes.py` - remove references to `cal_extract_RAW_spirouAB`
  and C. [Neil Cook]
- `SpirouFITS.py` - add `read_shape_file` function to get shape file from
  calibDB. [Neil Cook]
- `SpirouEXTOR.__init__.py` - add aliases and remove old commented
  aliases. [Neil Cook]
- `SpirouEXTOR.py` - modify extraction wrapper function to accept new
  arguments of shape extraction functions, fill out shape extraction
  functions and add "debananafication" function. [Neil Cook]
- `SpirouCDB.py` - fix typo in error message. [Neil Cook]
- `Master_calib_SPIROU.txt` - add SHAPE file for reset (until new `cal_SLIT`
  code is running) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - update normal method to 4b. [Neil Cook]
- `Cal_extract_RAW_spirou`: add modifications required for extraction
  methods 4a and 4b. [Neil Cook]
- `Cal_extract_EA_test`: update test for EA changes 2018-09-20. [Neil
  Cook]
- Misc - backup old files. [Neil Cook]
- `SpirouEXTOR.py` - add todo and comment to remind to move afterwards.
  [Neil Cook]
- `SpirouEXTOR.py` - add shape extract method to test methods. [Neil Cook]
- `Cal_Extract_EA_test.py`: add test code to experiment with extraction
  methods. [Neil Cook]
- `Constants_SPIROU_H4RG`: add extra extraction types to allowed types.
  [Neil Cook]


0.3.023 (2018-10-02)
--------------------
- `Cal_CCF_E2DS_spirou.py` - fix order out GetWaveSolution outputs (Issue
  #464) [Neil Cook]
- `Cal_Test.run` - change over `(cal_exposure_meter` last) [Neil Cook]
- `SpirouTelluric.py` - modify functions to allow filename saved to p -
  for insertion into header at hdict creation (Issue  #471) [Neil Cook]
- `SpirouLOCOR.py` - modify functions to allow filename save to p - for
  insertion into header at hdict creation (Issue  #471) [Neil Cook]
- `SpirouImage.py` - modify functions to allow filename to be saved to p -
  to insert into header at hdict creation (Issue  #471) - fix bug with
  mask2 (in getting drift files function) [Neil Cook]
- `SpirouFITS.py` - mmodify read functions to save the filename to p - to
  inject into header at hdict creation (Issue  #471) [Neil Cook]
- SpirouFLAT - add filenames to headers (Issue  #471) [Neil Cook]
- `SpirouKeywords.py` - add the keywords for each file (that will go in
  the header) - Issue  #471. [Neil Cook]
- `Obj_mk_tellu.py` - add filenames to headers (Issue  #471) [Neil Cook]
- `Obj_mk_tellu_template.py` - add filenames to headers (Issue  #471)
  [Neil Cook]
- `Obj_fit_tellu.py` - add filenames to headers (Issue  #471) [Neil Cook]
- `Cal_wavE_mapper.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_[WAVE_E2DS]_spirou.py` - add filenames to headers (Issue  #471)
  [Neil Cook]
- `Cal_SLIT_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_loc_RAW_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_HC_E2DS_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_HC_E2DS_EA_spirou.py` - add filenames to headers (Issue  #471)
  [Neil Cook]
- `Cal_FF_RAW_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_extract_RAW_spirou.py` - add filenames to headers (Issue  #471)
  [Neil Cook]
- `Cal_exposure_meter.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - add filenames to headers (Issue  #471)
  [Neil Cook]
- `Cal_DRIFT_E2D.py` - add filenames to headers (Issue  #471) [Neil Cook]
- `Cal_DARK_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- `Cal_BADPIX_spirou.py` - add filenames to headers (Issue  #471) [Neil
  Cook]
- Update date/version/changelog. [Neil Cook]
- SpirouWAVE - replace `get_e2ds_ll` (Issue #468) [Neil Cook]
- `SpirouFITS.py` - allow header return. [Neil Cook]
- `SpirouPlot.py` - fix bug `plot_style` cannot be None - now '' when empty.
  [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - fix bug - swap wave and param. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - add header to wave solution returns. [Neil
  Cook]


0.3.022 (2018-10-01)
--------------------
- `SpirouTHORCA.__init__.py` - remove use of GetE2DSll - use
  GetWaveSolution (Issue #468) [Neil Cook]
- `SpirouTHORCA.py` - remove use of GetE2DSll - use GetWaveSolution (Issue
  #468) [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - remove use of GetE2DSll - use GetWaveSolution
  (Issue #468) [Neil Cook]
- `SpirouTHORCA.py` - re-work the obtaining of wave solution (Issue #468)
  [Neil Cook]
- `SpirouFITS.py` - re work wave solution functions (Issue #468) [Neil
  Cook]
- `SpirouImage.__init__.py` - remove old wave sol functions (Issue #468)
  [Neil Cook]
- `Cal_DRIFT_RAW_spirou.py` - work on wave solution functions (Issue #468)
  [Neil Cook]
- `Pol_spirou.py` - work on wave solution functions (Issue #468) [Neil
  Cook]
- `Cal_extract_RAW_spirou.py` - work on wave solution functions (Issue
  #468) [Neil Cook]
- `Visu_[ALL]_spirou.py` - work on wave solution functions (Issue #468)
  [Neil Cook]
- `Obj_[fit/mk]_tellu.py` - work on wave solution functions (Issue #468)
  [Neil Cook]
- `Cal_wave_mapper.py` - work on wave solution functions (Issue #468)
  [Neil Cook]
- `Cal_HC_E2DS_EA_spirou.py` - work on wave solution functions (Issue
  #468) [Neil Cook]
- `Cal_WAVE_[ALL].py` - work on wave solution functions (Issue #468) [Neil
  Cook]
- `Cal_exposure_meter.py` - work on wave solution functions (Issue #468)
  [Neil Cook]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - work on wave solution functions (Issue
  #468) [Neil Cook]
- `Cal_DRIFT_E2DS_spirou.py` - work on wave solution functions (Issue
  #468) [Neil Cook]
- `SpirouImage.py` - modify `get_all_similar_files` to add check of fiber
  for `OBJ_FP` `OBJ_HCONE` etc (i.e. only allow on fiber C) and return
  filetype to show user which `DRS_EXTOUT` were allowed (Issue #464) [Neil
  Cook]
- `SpirouImage.__init__.py` - update alias to better represent what we are
  doing `get_all_similar_files` --> GetSimilarDriftFiles. [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add constant to check which fiber is being
  used (for `OBJ_FP` and `OBJ_HCONE` etc should only work on fiber C)  -
  Issue #464. [Neil Cook]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - fix code to allow `FP_FP` and `OBB_FP` (and
  report back on allowed types) - Issue #464. [Neil Cook]
- `Cal_DRIFT_E2DS_spirou.py` - fix code to allow `FP_FP` and `OBB_FP` (and
  report back on allowed types) - Issue #464. [Neil Cook]
- Teset.run - update tested files. [Neil Cook]
- Re-add misc folder to github sync. [Neil Cook]
- `SpirouImage.py` - change how `get_all_similar_files` works (now look for
  `kw_OUTPUT` based on `"DRIFT_PEAK_ALLOWED_OUTPUT`" - Issue #464. [Neil
  Cook]
- `Constnats_SPIROU_H4RG.py` - Issue #464 - add definitions for which
  outputs are allowed for "fp" and "hc" [Neil Cook]
- Add misc backup files. [Neil Cook]
- Removed problematic `fitgaus.py` from fortran (conflicts with fitgaus.f)
  and removed fitgaus.f from spirouTHORCA. [Neil Cook]
- `SpirouImage.py` - Issue #464 - `get_all_similar_files` - modify to run
  indexing if no index.fits exists. [Neil Cook]
- `Off_listing_REDUC_spirou.py` - Issue #464 - allow `off_listing` to run in
  quiet mode. [Neil Cook]


0.3.021 (2018-09-26)
--------------------
- `SpirouWAVE.py` - adapt to allow force creating of linelist. [Neil Cook]
- `SpirouPlot.py` - adapt to be able to use different style. [Neil Cook]
- `SpirouConst.py` - add plot style (for alternate plotting) [Neil Cook]
- `Constants_SPIROU_H4RG.py` - add control to force linelist re-
  computation. [Neil Cook]


0.3.020 (2018-09-25)
--------------------
- `SpirouPlot.py` - pass font changes for all graphs (via matplotlib.rc)
  [Neil Cook]
- SpirouConst - add descriptions for plot font functions. [Neil Cook]
- `SpirouConst.py` - add plot pseudo constants (to enable changing plot
  fontsize easily - for all plots) [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - add inputs for `ccf_rv_ccf_plot` (modified
  inputs for plot title) [Neil Cook]
- Merge pull request #466 from njcuk9999/neil. [Neil Cook]

  fix typo in last commit
- Merge pull request #465 from njcuk9999/neil. [Neil Cook]

  Neil --> Master (Fixes for issue #464)


0.3.019 (2018-09-24)
--------------------
- `Cal_DRIFTPEAK_E2DS_spirou.py` - fix typo bug with
  `drift_peak_allowed_types`. [Neil Cook]
- `Recipe_control.txt` - add `HCTWO_HCTWO` and `OBJ_FP` to `cal_DRIFT` and
  `cal_DRIFTPEAK` recipes - Issue #464. [Neil Cook]
- `Constnats_SPIROU_H4RG.py` - added new constant to control with files
  (with header key `KW_EXT_TYPE)` are associated with fp and hc (for
  setting other constants) - Issue #464. [Neil Cook]
- `Cal_extract_RAW_spirou.py` - note from Etienne to Francois re: negative
  fluxes to zero after background correction. [Neil Cook]
- `Cal_DRIFTPEAK_E2DS_spirou.py` - modified the lamp parameter to get from
  constants (for easier addition of different types) - Issue #464. [Neil
  Cook]
- Merge pull request #463 from njcuk9999/dev. [Neil Cook]

  Dev


0.3.018 (2018-09-21)
--------------------
- Update timings. [Neil Cook]
- Update date/version/changelog/timings. [Neil Cook]


0.3.017 (2018-09-21)
--------------------
- `SpirouTHORCA.py` - fix code to not have min/max of `HC/FP_N_ORD`
  START/FINAL for cal WAVE/cal HC. [Neil Cook]
- `Cal_WAVE_E2DS_spirou.py` - fix code to not have min/max of `HC/FP_N_ORD`
  START/FINAL for cal WAVE. [Neil Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - fix code to not have min/max of
  `HC/FP_N_ORD` START/FINAL for cal WAVE. [Neil Cook]
- `Cal_HC_E2DS_spirou.py` - fix code to not have min/max of `HC/FP_N_ORD`
  START/FINAL for cal HC. [Neil Cook]


0.3.016 (2018-09-21)
--------------------
- Remove user specific ignore (should not be needed) [Neil Cook]
- Update .gitignore to ignore misc folder. [Neil Cook]
- `SpirouWAVE.py` - Merge changes from Dev into Melissa. [Neil Cook]
- `SpirouTHORCA.py` - Merge changes from Dev into Melissa. [Neil Cook]
- `SpirouRV.py` - Merge changes from Dev into Melissa. [Neil Cook]
- `SpirouPlot.py` - Merge changes from Dev into Melissa (Issue #460) [Neil
  Cook]
- `Constants_SPIROU_H4RG.py` - Merge changes from Dev into Melissa. [Neil
  Cook]
- `Cal_WAVE_E2DS_EA_spirou.py` - Merge changes from Melissa. [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - full header added to `"CCF_FITS_FILE`" [Neil
  Cook]
- Merge pull request #459 from njcuk9999/dev. [Neil Cook]

  Dev --> master
- Update version/changelog/date/update notes. [Neil Cook]


0.3.015 (2018-09-19)
--------------------
- `Unit_tests`: fix bug in run names. [Neil Cook]


0.3.012 (2018-09-19)
--------------------
- `Unit_tests`: add `cal_CCF` test to `Tellu_Test.run`. [Neil Cook]
- `Unit_tests`: update unit test with new hc files (from 2018-08-05) [Neil
  Cook]
- `Recipe_control.txt` - remove duplicate line in `cal_CCF` definition.
  [Neil Cook]
- `Cal_CCF_E2DS_spirou.py` - update comments and remove extra spaces.
  [Neil Cook]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]
- Update date/version/changelog. [Neil Cook]


0.3.013 (2018-09-19)
--------------------
- New CCF mask provided by Xavier on 2018 Sept 19. [FrancoisBouchy]
- Add `E2DS_FF` for `cal_CCF_E2DS` recipe. [FrancoisBouchy]
- Adaptation for telluric corrected spectra. [FrancoisBouchy]


0.3.011 (2018-09-19)
--------------------
- `Recipe_control.txt` - add e2dsff files to `cal_drift` codes and `cal_ccf`.
  [Neil Cook]
- `Cal_DRIFTPEAK_E2DS_spirou`: fix obtaining of lamp type with `hc_hc`
  `(ext_type` == `"HCONE_HCONE`" or `"HCTWO_HCTWO")` [Neil Cook]
- `Cal_extract_RAW_spirou.py`: better error message for no DPRTYPE in
  header (Issue #456) [Neil Cook]


0.4.024 (2018-09-18)
--------------------
- `Test_recipe.py` - continue work on getting new input method to work.
  [Neil Cook]
- `SpirouStartup2.py` - continue work on getting new input method to work.
  [Neil Cook]
- `SpirouRecipe.py` - continue work on getting new input method to work.
  [Neil Cook]
- `Recipes.py` - add test recipe to test new definition method. [Neil
  Cook]
- SpirouConst.py: fix pep8 issue - brackets not needed. [Neil Cook]
- Merge branch 'master' into `input_redo`. [Neil Cook]


0.3.010 (2018-09-18)
--------------------
- `Tellu_test.run`: add actual non-hot stars to telluric test. [Neil Cook]
- `Tellu_test.run`: add actual non-hot stars to telluric test. [Neil Cook]
- `Tellu_test.run`: reset for full test. [Neil Cook]


0.3.009 (2018-09-17)
--------------------
- Test runs: update `tellu_test.run`. [Neil Cook]
- Update `cal_test.run`. [Neil Cook]
- SpirouStartup.py: extra check for no outputs in indexing (fixes crash)
  [Neil Cook]
- SpirouPlot: fix telluric plots (labels, titles, limits) [Neil Cook]
- `Obj_mk_tellu`: save SP to loc. [Neil Cook]
- `Obj_fit_tellu`: fix bug (blaze must be normalised to fit telluric)
  [Neil Cook]


0.4.023 (2018-09-17)
--------------------
- `Test_recipe`: todo's added. [Neil Cook]


0.4.022 (2018-09-14)
--------------------
- Input update: `spirouStartup.__init__.py` aliases / imports to
  spirouStartup2 (temporary) [Neil Cook]
- Input update: `recipes.py` - holder for recipe definitions. [Neil Cook]
- Input update: `spirouRecipe.py` - holder for new recipe classes. [Neil
  Cook]
- Input update: `spirouStartup2.py` - holder for new spirouStartup. [Neil
  Cook]
- Input update: `test_recipe.py` - test recipe to test new input
  functions. [Neil Cook]
- Input update: add `input_files.txt` - definition of input files. [Neil
  Cook]
- Merge pull request #453 from `njcuk9999/V0.3_Cand`. [Neil Cook]

  V0.3 cand --> master. Confirm unit tests successful.


0.3.008 (2018-09-13)
--------------------
- Version.txt: update/check dependencies. [Neil Cook]
- `Drs_dependencies.py`: fix for python 2 path. [Neil Cook]
- Update date/version/changelog. [Neil Cook]
- Timings.txt: For Neil reference only `unit_test` timings. [Neil Cook]


0.3.007 (2018-09-13)
--------------------
- `Drs_changelog.py`: undo pep8 name change (and redo properly) [Neil
  Cook]
- `Update_notes.txt`: add unit tests to update (files and some
  explanation) [Neil Cook]
- `Pol_spirou.py`: fix error with new input/output to WriteImageMulti.
  [Neil Cook]
- SpirouWAVE.py: hide testing "print" statements. [Neil Cook]
- `Unit_tests`: update unit test + add polarisation test. [Neil Cook]
- SpirouCDB.py: fix bad call to `DATE_FMT_HEADER` (p not required) [Neil
  Cook]
- `Cal_reset.py`: exit script `has_plots=False`. [Neil Cook]
- SpirouWAVE.py: fix issue with pep8 update `(ll_prev` defined in wrong
  place) [Neil Cook]
- `SpirouWAVE.py` (Issue #452): `wave_catalog` is now initialised as a NaN
  array (instead of an array of zeros) [Neil Cook]


0.3.006 (2018-09-12)
--------------------
- `Off_listing.py`: fix bug and add to index (if prompted by user) [Neil
  Cook]
- SpirouStartup.py: added Y/N question function. [Neil Cook]
- `Off_listing.py`: fix to bug in code (rawloc --> list) [Neil Cook]
- `Off_listing.py`: generic off listing that takes any directory as only
  input (no night name) and read's index.fits / `_pp` fits file headers to
  get off listing for that directory. [Neil Cook]
- SpirouStartup.py: fix for not requiring night name in `load_arguments`.
  [Neil Cook]
- SpirouConst.py: Added general off listing columns. [Neil Cook]
- Made spirouTools executable. [Neil Cook]
- Fix bad pep8 updates. [Neil Cook]
- Pep8 updates. [Neil Cook]


0.3.005 (2018-09-11)
--------------------
- Pep8 updates. [Neil Cook]
- `Update_notes.txt`: update with new unit tests. [Neil Cook]
- Unit tests: update unit test --> add `"Tellu_Test.run`" and modify
  `"Cal_Test.run`", remove `test_tellu.run`. [Neil Cook]
- `Recipe_control.txt` --> add telluric and polarisation cases for
  `visu_E2DS_spirou`. [Neil Cook]
- `Obj_fit_tellu`, `obj_mk_tell_template`, `obj_mk_tellu`: fix writing outputs
  to file. [Neil Cook]
- Update date/version/changelog/update notes. [Neil Cook]


0.3.033 (2018-09-11)
--------------------
- Added BJD# and MEANBJD to header of polar products. [Eder]
- Minor changes. [Eder]
- Minor changes. [Eder]
- Minor changes. [Eder]


0.3.004 (2018-09-11)
--------------------
- `Recipe_control.txt` --> add cases (for fiber) for `visu_E2DS_spirou`.
  [Neil Cook]
- `SpirouFile.py` - fix bad error output {0} --> {1} [Neil Cook]
- `Cal_test.run`: fix errors (typos ...f --> ...a) [Neil Cook]
- Update recipe control for `visu_RAW` and `visu_E2DS` recipes. [Neil Cook]
- Update notes with not done/finished. [Neil Cook]
- SpirouWAVE - re-add dict() --> OrderedDict() [Neil Cook]
- Config - merge fix - do NOT upload own config! [Neil Cook]
- `Cal_WAVE_E2DS_EA` - extra imports. [Neil Cook]
- Merge branch 'dev2' into melissa2. [Neil Cook]

  Conflicts:
      `INTROOT/SpirouDRS/data/constants/recipe_control.txt`
      INTROOT/SpirouDRS/spirouConfig/spirouConst.py
      INTROOT/SpirouDRS/spirouTHORCA/spirouWAVE.py
      `INTROOT/bin/cal_WAVE_E2DS_EA_spirou.py`
- `Cal_exposure_meter.py`: fix bad call to `get_telluric` (p, loc --> loc)
  [Neil Cook]
- Updated changelog/date/version/update notes. [Neil Cook]
- Update unit tests. [Neil Cook]
- SpirouUnitTests: fix outputs of `manage_run` (post H2RG removal) [Neil
  Cook]
- SpirouTelluric.py: fix kind when reading TAPAS file (was FLAT now
  TAPAS) [Neil Cook]
- SpirouStartup.py: fix indexing of files (add `"LAST_MODIFIED`" column)
  [Neil Cook]
- `SpirouStartup.__init__.py`: fix aliases. [Neil Cook]
- SpirouTable - increase width of table (now 9999) [Neil Cook]
- SpirouExoposeMeter.py: update where TAPAS file is taken from (now from
  telluDB) [Neil Cook]
- SpirouConst.py: update reduced output columns (need date and utc for
  drift) [Neil Cook]
- Update `master_calib_SPIROU.txt` for reset - now we don't need H2RG or
  TAPAS input. [Neil Cook]
- `Off_listing_RAW/REDUC_spirou` - fix bug in adding unix time - now
  called `"last_modified`" (to be more specific) [Neil Cook]
- `Cal_FF_RAW_spirou`: fix bug in H2RG removal. [Neil Cook]
- `Cal_exposure_meter/cal_wave_mapper` - update location of telluric ref
  file (TAPAS) now via telluDB. [Neil Cook]


0.3.003 (2018-09-10)
--------------------
- Update notes - update. [Neil Cook]
- Unit test .run files - update after removing H2RG dependency. [Neil
  Cook]
- SpirouUnitTests.py: remove H2RG dependency (comparison not needed)
  [Neil Cook]
- `Unit_test.py`: replace dict() --> OrderedDict() + remove H2RG
  dependency. [Neil Cook]
- SpirouUnitTests.py: replace dict() --> OrderedDict() + remove H2RG
  dependency. [Neil Cook]
- SpirouUnitRecipes.py: remove H2RG dependency (no comparison needed) +
  replace dict() --> OrderedDict() [Neil Cook]
- `SpirouUnitTests.__init__.py`: remove H2RG dependency (remove `check_type`
  and `set_comp)` [Neil Cook]
- `Drs_tools`: replace dict() --> OrderedDict() [Neil Cook]
- `Drs_documentation`: replace dict() --> OrderedDict() [Neil Cook]
- `Drs_dependencies`: replace dict() --> OrderedDict() [Neil Cook]
- `Drs_changelog`: replace dict() --> OrderedDict() [Neil Cook]
- `Calc_berv`: replace dict() --> OrderedDict() and remove H2RG
  dependency. [Neil Cook]
- SpirouWAVE: replace dict() --> OrderedDict() [Neil Cook]
- SpirouTHORCA.py: remove H2RG dependency. [Neil Cook]
- SpirouTelluric.py: remove unused line (norm) [Neil Cook]
- SpirouStartup.py: remove H2RG dependency and add "UNIX" file column.
  [Neil Cook]
- SpirouRV.py: remove H2RG dependency. [Neil Cook]
- SpirouPOLAR.py: replace dict() --> OrderedDict() [Neil Cook]
- SpirouLOCOR.py: remove H2RG dependency. [Neil Cook]
- SpirouImage.py: remove H2RG dependency. [Neil Cook]
- SpirouFITS.py: remove H2RG dependency + replace dict() -->
  OrderedDict() [Neil Cook]
- SpirouBERV.py: remove H2RG dependency. [Neil Cook]
- SpirouEXTOR: replace dict() --> OrderedDict() [Neil Cook]
- SpirouDB: replace dict() --> OrderedDict() [Neil Cook]
- SpirouPlot.py: remove H2RG dependency. [Neil Cook]
- SpirouConst.py: update reduced output columns (remove obs date and utc
  from reduced products) [Neil Cook]
- SpirouConfig.py: replace dict() --> OrderedDict() [Neil Cook]
- `Main_drs_trigger`: remove H2RG dependency. [Neil Cook]
- `Constants_SPIROU_H2RG`: remove H2RG dependency (Delete file) [Neil
  Cook]
- `Off_listing_REDUC_spirou` - add column for last modified (unix time)
  [Neil Cook]
- `Cal_wave_mapper`: replace dict() --> OrderedDict() [Neil Cook]
- `Cal_SLIT_spirou`: remove H2RG dependency. [Neil Cook]
- `Cal_preprocess_spirou`: remove H2RG dependency. [Neil Cook]
- `Cal_loc_RAW_spirou`: remove H2RG dependency. [Neil Cook]
- `Cal_FF_RAW_spirou`: remove H2RG dependency. [Neil Cook]
- `Cal_extract_RAW_spirou`: remove H2RG dependency. [Neil Cook]
- `Cal_exposure_meter`: replace dict() --> OrderedDict() [Neil Cook]
- `Cal_DARK_spirou.py`: remove H2RG dependency. [Neil Cook]
- `Cal_CCF_E2DS_spirou.py`: replace dict() --> OrderedDict() [Neil Cook]


0.3.002 (2018-09-07)
--------------------
- Added an `all_order` plot of fitted gaussians (as discussed in #442)
  Saved additional values to loc in spirouWAVE functions that were
  required for `cal_WAVE_E2DS_EA`. [melissa-hobson]
- `Fit_emi_line`: added check to not fit on lines with more than one zero-
  value (fix for #393) [melissa-hobson]


0.3.000 (2018-09-06)
--------------------
- Issue #418 `spirouStartup.py` - Make directory for `NIGHT_NAME` in
  `TMP_DIR`, index.fits saves to `TMP_DIR`, files are now checked for RAW in
  `TMP_DIR`. [Neil Cook]
- Issue #418 spirouFile.py: obtaining tmppath and tmpfile to check for
  raw files (instead of rawpath which now throws error when used) [Neil
  Cook]
- Issue #418 spirouConfig: added `TMP_DIR` definition (as `DRS_DATA_WORKING`
  dir) [Neil Cook]
- Issue #418 `cal_preprocess_spirou.py`: made pp target raw folder but
  save to tmp dir. [Neil Cook]
- Updated notes. [Neil Cook]
- Updated the update notes. [Neil Cook]
- Added Update Notes. [Neil Cook]
- Update `20180805_test1.run` to extract FP sequences and run DRIFT
  recipes (with extracted FPs) [Neil Cook]
- Update 20180409 test to include `off_listing_RAW/REDUC` and not include
  `pol_spirou` (do not have the raw files needed) [Neil Cook]
- `Unit_test.py`: Move Reset after set up (so errors reported before reset
  questions) [Neil Cook]
- Issue #429: spirouUnitRecipes.py: modify the outputs of `off_listing`
  recipes (distinguish between RAW and REDUCED listing) [Neil Cook]
- Issue #429: `calc_berv` - modify input/output of WriteImage (for
  handling p['OUTPUTS']) [Neil Cook]
- Issue #429: `spirouStartup.py` modify `"main_end_script`" to index outputs
  or pre-processing - via functions `"index_pp`", `"index_outputs`",
  "indexing" and `"sort_and_save_outputs`" [Neil Cook]
- Issue #429: `spirouStartup.__init__.py`: alias `sort_and_save_outputs` to
  SortSaveOutputs. [Neil Cook]
- Issue #429: spirouLSD - modify WriteImage to accept new input/output
  for writing p['OUTPUTS'] [Neil Cook]
- Issue #429: spirouTable: Add ways of making, reading and writing fits
  table (via astropy.table.Table) - functions added = `make_fits_table`,
  `read_fits_table`, `write_fits_table`. [Neil Cook]
- Issue #429: spirouImage.py: replace `"get_all_similar_files`" function
  to look at header keys instead of file name (for `cal_DRIFT` recipes)
  [Neil Cook]
- SpirouFITS: modify `write_image` and `write_image_multi` to deal with
  writing output dict to p (via new function `"write_output_dict")` [Neil
  Cook]
- SpirouFile: add `DRS_TYPE` to identify RAW and REDUCED recipes (and pass
  to output processing later) [Neil Cook]
- `SpirouImage.__init__`: add aliases for `make_fits_table`, `read_fits_table`
  and `write_fits_table`. [Neil Cook]
- SpirouMath: reformat exception on timestamp (to print the input -->
  helps with debugging) [Neil Cook]
- SpirouConst: add `OFF_LISTING_RAW_FILE`, `OFF_LISTING_REDUC_FILE`,
  `INDEX_OUTPUT_FILENAME`, `OUTPUT_FILE_HEADER_KEYS`, `RAW_OUTPUT_COLUMNS`,
  `REDUC_OUTPUT_COLUMNS` functions. [Neil Cook]
- Modify `unresize.py` with the output to WriteImage (outputs management)
  [Neil Cook]
- Update `cal_drift_raw` for outputs (but not file list) [Neil Cook]
- Re-work `off_listing` recipes to look at the index files first (Much
  faster) - and to update the index files. [Neil Cook]
- Modify `cal_preprocess_spirou` to sort out outputs and to skip index
  file. [Neil Cook]
- Issue #429 - Re-work "listfiles" to get files from the headers (and
  index files) + deal with outputs. [Neil Cook]
- Issue #429 - ReWork "WriteImage" to save to p['OUTPUTS'] and deal with
  spirouStartup.End dealing with outputs. [Neil Cook]


0.2.128 (2018-09-06)
--------------------
- SpirouPlot: updated `wave_ea_plot_per_order_hcguess`: - plots stay open
  until manually closed - each plot shows only the gaussian fits
  corresponding to the order (Fixes #442) [melissa-hobson]


0.2.124 (2018-09-05)
--------------------
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data), and added
  the obtaining of DPRTYPE to add  `EXT_TYPE` key to header (extraction
  output id key --> giving DPRTYPE for extracted files) [Neil Cook]
- Added a new log output to split up files to help see progress. [Neil
  Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - re-worked file identification only using header keys (no
  filename identification) [Neil Cook]
- Issue #429 - added `kw_OUTPUT` and `kw_EXT_TYPE` definitions for saving
  output header id and extraction output header id. [Neil Cook]
- Issue #429 - added TAGFOLDER and TAGFILE functions and modified all
  fits-file definition functions to accept tags. [Neil Cook]
- Issue #429 - added `get_tags` function. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Issue #429 - re-work `recipe_control.txt` to take into account added
  output keys (and check keys on start up) [Neil Cook]
- Issue #429 - definition of output header keys (based on output
  filename in spirouConst.py) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]
- Issue #429 - add output header key to identify output files
  `(KW_OUTPUT)` - defined in `output_keys.py` (SpirouDRS/data) [Neil Cook]


0.2.125 (2018-09-05)
--------------------
- `Cal_WAVE_E2DS_EA_spirou`: updated HC section from
  `cal_HC_E2DS_EA_spirou.py`. [melissa-hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- `Visu_E2DS_spirou`, `recipe_control`: fiber is now obtained from file.
  [melissa-hobson]
- `Visu_E2DS_spirou`, `recipe_control`: fiber is now obtained from file
  (Fixes #437) [melissa-hobson]
- Commit local changes. [Melissa Hobson]
- Merge pull request #441 from `njcuk9999/master_copy`. [melissa-hobson]

  update melissa from Master copy
- Merge branch 'melissa' into `master_copy`. [melissa-hobson]
- Merge pull request #439 from njcuk9999/dev2. [Neil Cook]

  Dev2
- Merge remote-tracking branch 'origin/dev2' into dev2. [Neil Cook]
- Merge pull request #438 from njcuk9999/dev2. [Neil Cook]

  Dev2 --> Master (unit test complete and verified)
- Update version/changelog and date. [Neil Cook]


0.2.126 (2018-09-05)
--------------------
- Commit local changes. [Melissa Hobson]


0.2.127 (2018-09-05)
--------------------
- SpirouRV (for `cal_DRIFTPEAK_E2DS_spirou)` - Fix repetition of warning
  messages in while loop. [njcuk9999]


0.2.123 (2018-09-04)
--------------------
- Move `cal_HC_E2DS_EA` constants to here. [Neil Cook]
- Prep `cal_HC_E2DS_EA` for recipe run (add main function, move constants
  etc) [Neil Cook]
- Updated date/version/changelog. [Neil Cook]


0.2.121 (2018-09-04)
--------------------
- Add placeholder marker for the new `cal_HC_E2DS_EA_spirou` work. [Neil
  Cook]
- Modify `generate_resolution_map` --> fixes for integrating etiennes
  hcpeak functions. [Neil Cook]
- Enter todo to rename variable. [Neil Cook]
- Add plot for `cal_HC_E2DS_EA_spirou` `(wave_ea_plot_line_profiles)` and
  worker function `(remove_first_last_ticks)` [Neil Cook]
- Modify the `gauss_fit_s` function `(cal_HC_EA_E2DS` usuage) [Neil Cook]
- Separate input and output filename pseudo constant functions, added EA
  versions of `cal_HC` output filename definitions. [Neil Cook]
- Update leapsec log. [Neil Cook]
- Update to `cal_HC_E2DS_EA_spirou` - finish work on integrating Etienne's
  work. [Neil Cook]
- Fix for S1D spectra - there may be occasions when we cannot convert to
  S1D - print a warning if this is the case. [Neil Cook]
- Merge pull request #434 from njcuk9999/neil. [Neil Cook]

  Neil --> Dev 2


0.2.122 (2018-09-03)
--------------------
- Manually incorporated possibility to read wavelength solution from
  calibDB (from dev2) [melissa-hobson]
- `Cal_WAVE_E2DS_EA_spirou.py`: incorporated FP lines into solution,
  corrected checks spirouWAVE.py: corrections to new FP functions.
  [melissa-hobson]


0.2.120 (2018-08-31)
--------------------
- Update date and version. [Neil Cook]
- Script to manually add file to calibDB (from file in reduced folder)
  [Neil Cook]
- Update change log/version and date. [Neil Cook]
- Update master calibDB for reset. [Neil Cook]
- Reset `cal_CCF` set NaNs to zeros (Issue #389) [Neil Cook]


0.2.117 (2018-08-31)
--------------------
- Added new wavelength solution and deleted files in `data_example` (not
  needed - run `cal_reset` or `cal_validate)` [Neil Cook]
- Merge pull request #432 from njcuk9999/melissa-hobson-patch-1. [Neil
  Cook]

  TC3 initial wavelength solution


0.2.116 (2018-08-30)
--------------------
- Add `off_listing_REDUC_spirou` to recipes available for testing. [Neil
  Cook]
- Write a test for 18BQ01-Aug05 test files `(20180805_test1.run)` - Issue
  #400. [Neil Cook]
- Fix micro seconds = 1e-6 not 1e-3. [Neil Cook]
- Fix bug with PATH in bashrc file. [Neil Cook]
- Add the resolution map (work-in-progress) [Neil Cook]
- Fix bugs with `cal_HC_E2DS_EA`. [Neil Cook]
- Fix bug with timestamp in logging. [Neil Cook]
- Add writing of file for `off_listing`. [Neil Cook]


0.2.114 (2018-08-29)
--------------------
- Added fixes to triplet fitting function. [Neil Cook]
- Added alias for the `get_night_dirs` function (GetNightDirs) [Neil Cook]
- Fixed number of `night_name` dirs displayed on error. [Neil Cook]
- Added `night_name` display limit (for when `NIGHT_NAME` is not an
  argument) [Neil Cook]
- Fix to bad copy and paste in spirouPlot. [Neil Cook]
- Improvements to having no FOLDER name - now displays all available
  folders. [Neil Cook]
- Improvements to `off_listing` - having no `night_name` argument now
  displays all available `night_names`. [Neil Cook]
- Improvements to `off_listing` - having no `night_name` argument now
  displays all available `night_names`. [Neil Cook]
- Added `off_listing_REDUC_spirou` to allow listing of reduced folders.
  [Neil Cook]
- Issue #428 - force calibDB wave solution - modify `get_wave_keys`. [Neil
  Cook]
- Issue #428 - force calibDB wave solution - modify `get_wave_solution`.
  [Neil Cook]
- Issue #428 - force calibDB wave solution - add constant switch. [Neil
  Cook]
- `Cal_HC_E2DS_EA` - Set up for local running. [Neil Cook]


0.2.115 (2018-08-29)
--------------------
- TC3 initial wavelength solution. [melissa-hobson]


0.2.113 (2018-08-28)
--------------------
- First commit - Etienne's `cal_HC` - added functions for `cal_hc_ea`. [Neil
  Cook]
- First commit - Etienne's `cal_HC` - added call to spirouMath. [Neil
  Cook]
- First commit - Etienne's `cal_HC` - moved `lin_mini` to spirouMath. [Neil
  Cook]
- First commit - Etienne's `cal_HC` - ReadTable/WriteTable/MakeTable
  correction when no formats. [Neil Cook]
- First commit - Etienne's `cal_HC` - `wave_ea_plots`. [Neil Cook]
- First commit - Etienne's `cal_HC` - gauss functions and `lin_mini`. [Neil
  Cook]
- First commit - Etienne's `cal_HC` - filename definition. [Neil Cook]
- First commit - Etienne's `cal_HC`. [Neil Cook]
- Merge pull request #427 from njcuk9999/melissa. [Neil Cook]

  Melissa --> Dev
- Merge branch 'dev2' into melissa. [Neil Cook]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Neil
  Cook]
- Set `pixel_shift_inter` and `pixel_shift_slope` back to zero (Issue #411)
  [Neil Cook]


0.2.118 (2018-08-27)
--------------------
- Issue #399 - copied in extra files `(FILE_B` and read me files) required
  by iers (but not currently linked to) [njcuk9999]
- Issue #399 - modification to iers to make offline (hopefully) given
  testing offline. [njcuk9999]
- Issue #399 - fix `astropy_iers_dir` to be the actual directory.
  [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #426 from njcuk9999/neil. [Neil Cook]

  Neil --> master (confirm tested on 20180409all.run and `test_tellu.run)`
- Merge pull request #424 from njcuk9999/neil. [Neil Cook]

  Neil --> Master


0.2.119 (2018-08-27)
--------------------
- Added location to save astropy iers file (Issue #389) [Neil Cook]
- Possible fix for Issue #389: from @cusher - import
  astropy.utils.iers and set `iers_table` [Neil Cook]
- Issue #399: barycorrpy offline file. [Neil Cook]


0.2.112 (2018-08-27)
--------------------
- Updated date, version and changelog. [Neil Cook]


0.2.107 (2018-08-27)
--------------------
- Updated date, version and changelog. [Neil Cook]
- Issue with changelog (Version.txt not updating) --> corrected. [Neil
  Cook]


0.2.106 (2018-08-27)
--------------------
- Set `pixel_shift_inter` and `pixel_shift_slope` back to zero (Issue #411)
  [Neil Cook]


0.2.105 (2018-08-24)
--------------------
- Fix for Issue #406 - `cal_CCF` does not accept StokesI or e2dsff -
  fixed. [Neil Cook]
- Fix for issue #406 - CCF recipe does not accept Stokes I spectra -->
  replace `'_A.fits`' with `'_AB_StokesI.fits`' [Neil Cook]
- Fix for Issue #406 -CCF recipe does not accept stokes I spectra -->
  replace `'_A.fits`' with `'_AB_StokesI.fits`' [Neil Cook]
- Fix for Issue #423 - `cal_reset` fails if folder does not exist. [Neil
  Cook]
- Changed blacklist functino to look at objnames (Issue #419) [Neil
  Cook]
- Changed blacklist file to object names (Issue #419) [Neil Cook]
- Moved blacklist check to after we have the OBJNAME (Issue #419) [Neil
  Cook]


0.2.104 (2018-08-23)
--------------------
- Add `check_blacklist` and `get_blacklist` functions (Issue #419) [Neil
  Cook]
- Add alias to check black list function (Issue #419) [Neil Cook]
- Add alias to raw text file function (Issue #419) [Neil Cook]
- Add blacklist filename (Issue #419) [Neil Cook]
- Add code to read raw text file (Issue #419) [Neil Cook]
- Add code to check for blacklisted file (Issue #419) [Neil Cook]
- Add blacklist file (Issue #419) [Neil Cook]
- Issue #389 - NaN values vauses error to be raised (Needs to be fixed
  properly) [Neil Cook]
- Update date version and changelog. [Neil Cook]


0.2.110 (2018-08-23)
--------------------
- Update `cal_HC_E2DS_spirou.py`. [Neil Cook]

  correct indentation error
- Update spirouMath.py. [Neil Cook]

  update pep8


0.2.103 (2018-08-23)
--------------------
- Re-write of `median_one_over_f_noise` function (Issue #420) [Neil Cook]
- New alias for function re-write (Issue #420) [Neil Cook]
- Using new function (re-write) from issue #420. [Neil Cook]


0.2.111 (2018-08-23)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py` update. [melissa-hobson]


0.2.109 (2018-08-22)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: moved FP solution to spirouWAVE. [melissa-
  hobson]


0.2.108 (2018-08-21)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: - check to remove double-fitted or
  spurious FP peaks - incorporation of FP lines (now working with no
  jumps) [melissa-hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- Removed test prints. [melissa-hobson]
- SpirouMATH.py, spirouTHORCA.py: redo pixel shift implementation.
  [melissa-hobson]
- `Cal_HC_E2DS_spirou.py`: changed start and end orders of second pass to
  be min (max) of FP and HC start (end) orders. spirouWAVE.py: correctly
  defined orders for inserting FP lines to `all_lines_2` Fixes #411.
  [melissa-hobson]
- Merge pull request #414 from njcuk9999/master. [melissa-hobson]

  update melissa
- Update changelog. [njcuk9999]


0.2.102 (2018-08-18)
--------------------
- Issue #411: reset `cal_wave` changes from Melissa (not working with
  `unit_test` 20180409all.run. [njcuk9999]
- Merge pull request #413 from njcuk9999/dev. [Neil Cook]

  Dev
- Update version. [njcuk9999]
- Update date version and changelog. [njcuk9999]


0.2.099 (2018-08-18)
--------------------
- Fix to file name (allow e2ds and e2dsff by only replaceing `"_A.fits`"
  [njcuk9999]
- Allow LSD process (now it is fixed) [njcuk9999]
- Merge remote-tracking branch 'origin/dev' into dev. [njcuk9999]
- Merge pull request #412 from njcuk9999/eder. [Neil Cook]

  Eder
- Merge branch 'master' into eder. [Eder]
- Merge pull request #410 from njcuk9999/melissa. [Neil Cook]

  Merge Melissa's branch with dev (for testing)
- Merge pull request #409 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date, version, changelog. [njcuk9999]


0.2.101 (2018-08-18)
--------------------
- Update spirouMath.py. [Neil Cook]

  fix pep8


0.2.096 (2018-08-18)
--------------------
- Issue #382 - added a position to check for FLATFILE and DARKFILE (must
  agree with `recipe_control.txt)` [njcuk9999]


0.2.095 (2018-08-17)
--------------------
- Issue #401 - Added check that number of `TELLU_MAP` files > number of
  PCA components. [njcuk9999]
- Issue #392 change "PPVERSION" to "PVERSION" - header key too long.
  [njcuk9999]
- Issue #405 - add message when reset userinput is not "yes" [njcuk9999]


0.2.098 (2018-08-17)
--------------------
- Fixed memory issue by avoiding direct use of an nxn S^2 matrix. [Eder]


0.2.094 (2018-08-16)
--------------------
- Issue #392: added per-processed version keyword. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Issue #392: added version to outputs. [njcuk9999]
- Entries prepared ready to fix issues #394 and #406. [njcuk9999]
- Issue #407: fix bug where split lines not all printed to log file
  (only to screen) [njcuk9999]


0.2.097 (2018-08-16)
--------------------
- NaN-to-zero change moved from `obj_fit_tellu` to `cal_CCF` - warning
  printed if there are NaNs in the e2ds input to `cal_CCF` - Ref: #389,
  #390. [melissa-hobson]
- Pixel shift incorporated to all wavelength solutions - added to
  constants file - read from constants for `cal_WAVE_E2DS_EA_spirou.py` -
  added to `spirouMATH.get_ll_from_coefficients` (and calls to it in
  spirouTHORCA) - warning is printed if the pixel shift is not zero.
  [melissa-hobson]
- SpirouFITS.py: removed `write_s1d`. [melissa-hobson]
- Merge pull request #408 from njcuk9999/master. [melissa-hobson]

  update Melissa
- Merge pull request #404 from njcuk9999/dev. [Neil Cook]

  Dev - tested against unit tests 20180409all.run and `test_tellu.run`
- Updated date, changelog and version. [njcuk9999]


0.2.093 (2018-08-15)
--------------------
- Update telluric unit test. [njcuk9999]
- Add `obj_mk_tellu` and `obj_fit_tellu` to the unit tests. [njcuk9999]
- Turn off the LSD analysis (until problem fixed) [njcuk9999]
- Added a telluric test (based on Neil's files) [njcuk9999]
- Fix to issue #398: The first time running `obj_mk_tellu` fails with an
  I/O problem - `convolve_file` was being saved to the wrong location (and
  hence `put_file` was failing to copy it to telluDB) [njcuk9999]
- Updated descriptions (from Etienne) [njcuk9999]
- Updated date, changelog and version. [njcuk9999]
- Fixed import issue. [njcuk9999]
- Merge pull request #403 from njcuk9999/melissa. [Neil Cook]

  Merge Melissa's branch into Dev branch
- Merge pull request #402 from njcuk9999/eder. [Neil Cook]

  Merge Eder branch into Dev branch
- Update spirouConst.py. [Neil Cook]

  fix pep8 on doc string
- Merge pull request #396 from njcuk9999/cfht. [Neil Cook]

  Fixed `__NAME__` of `obj_fit_tellu`


0.2.092 (2018-08-15)
--------------------
- Update config.py. [Neil Cook]

  Revert `config.py` (Copying over a custom `config.py` file )
- Update spirouFITS.py. [Neil Cook]

  Todo added to remove `write_s1d` this should not be used - but keeps coming up in Melissa's branch
- Delete vcs.xml. [Neil Cook]

  should be ignored by github


0.2.089 (2018-08-14)
--------------------
- Implemented Least Squares Deconvolution (LSD) Analysis to polar
  module. [Eder]
- Merge branch 'master' into eder. [Eder]
- Implemented Least Squares Deconvolution (LSD) Analysis to polar
  module. [Eder]


0.2.090 (2018-08-14)
--------------------
- `Obj_fit_tellu.py`: re-add blaze, set NaNs to zero in final e2ds
  (UNTESTED), as per #389, #390. [melissa-hobson]
- `SpirouLOCOR.py` now prints name of localization file (Discussed in
  #387) [melissa-hobson]
- SpirouStartup.py: removed lines that caused exit if `DRS_PLOT` was not
  set even when `DRS_INTERACTIVE` was set. Fixes #395. [melissa-hobson]


0.2.091 (2018-08-14)
--------------------
- Fixed `__NAME__` of `obj_fit_tellu`. [Chris Usher]


0.2.088 (2018-08-13)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: began incorporation of FP lines (work in
  progress) [melissa-hobson]


0.2.087 (2018-08-09)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: incorporated extrapolation of Littrow
  solution for last two orders; added save to calibDB of good solutions.
  [Melissa Hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]

  Conflicts:
      INTROOT/SpirouDRS/spirouCore/spirouPlot.py
      INTROOT/SpirouDRS/spirouImage/spirouBERV.py
      INTROOT/SpirouDRS/spirouImage/spirouImage.py
      INTROOT/SpirouDRS/spirouTHORCA/spirouWAVE.py
      `INTROOT/bin/cal_FF_RAW_spirou.py`
      `INTROOT/bin/cal_SLIT_spirou.py`
      `INTROOT/bin/cal_WAVE_E2DS_EA_spirou.py`
      `INTROOT/bin/cal_extract_RAW_spirou.py`
      `INTROOT/bin/cal_loc_RAW_spirou.py`
      `INTROOT/config/constants_SPIROU_H4RG.py`
- Merge pull request #386 from njcuk9999/cfht. [Neil Cook]

  Proposed fixes for minor issues
- Merge pull request #388 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date, version and change log. [njcuk9999]


0.2.083 (2018-08-08)
--------------------
- Update spirouFITS.py. [Neil Cook]

  Made the warning handling more readable and added TODO, this should be handled properly not just ignored (i..e header cards should be corrected) - TODO will remind of this!


0.2.072 (2018-08-08)
--------------------
- Correctioned some constants and added value to loc. [njcuk9999]
- Added definitions from FP files and EA wave files. [njcuk9999]
- Updated `cal_WAVE_E2DS` files to check for. [njcuk9999]
- Part2 test and updated/corrected some constants. [njcuk9999]
- Added background subtraction. [njcuk9999]
- Title to the plots + action TODO to find the right FIBER type.
  [njcuk9999]
- Refinement of the cut of the left edge of blue orders for localisation
  - merge from @FrancoisBouchy. [njcuk9999]
- Use only the part of E2DS > 0 to build the S1D spectra. [njcuk9999]
- Read the OBSTYPE before computing BERV - OBSTYPE should be OBJECT to
  derive the BERV (i.e. not for calibrations) - merge from
  @FrancoisBouchy. [njcuk9999]
- Some cosmetic / improvement for plot display - merged from
  @FrancoisBouchy. [njcuk9999]
- Updated constants + new definition for the blue window on DARK -
  `uc_fracminblaze` = 16, new param to restrict the wings of spectral
  orders with flux lower than `flux_at_blaze` / 16, spectral order 0 is
  not taken into account. [njcuk9999]
- Correction of center of the blaze window - put to zero edge of the
  spectra hwere flux is too low (less than `flux_at_blaze/`
  `IC_FRACMINBLAZE)` - merged from @FrancoisBouchy. [njcuk9999]
- Put to zero part of spectra where the blaze is not defined.
  [njcuk9999]
- Add the background subtraction - from @FrancoisBouchy. [njcuk9999]
- @melissa-hobson correct call to GetLampParams. [njcuk9999]


0.2.084 (2018-08-08)
--------------------
- Added fiber position identification from fiber type. [njcuk9999]
- First version `cal_WAVE` developed by @eartigau, adapted to DRS format
  by @melissa-hobson added informational printouts - fixed figures -
  fixed asymmetry that allowed lines to be found in two windows - added
  `all_lines` data structure, Littrow check and uncertainty calclulation
  added possibility to set a pixel shift. [njcuk9999]


0.2.085 (2018-08-08)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: - added possibility to have a linear pixel
  shift when getting the initial wavelength solution (needed for TC2-TC3
  change) - added QC - implemented storing of wavelength solution and
  tables (tables TBC) spirouConst.py: defined specific wave file names
  for outputs of `cal_WAVE_E2DS_spirou.py` and `cal_WAVE_E2DS_EA_spirou.py`.
  [Melissa Hobson]


0.2.086 (2018-08-08)
--------------------
- Suppress warnings about truncating FITS comments. [Chris Usher]
- Prevent `measure_background_flatfield` from throwing error. [Chris
  Usher]
- Fixed scrambled FITS headers. [Chris Usher]


0.2.082 (2018-08-07)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: added posibility to set a pixel shift
  `recipe_control.txt`: put correct DPRTYPE for `cal_WAVE` checks. [Melissa
  Hobson]


0.2.081 (2018-08-03)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: - added informational printouts - fixed
  figures - fixed asymmetry that allowed lines to be found in two
  windows - added `all_lines` data structure, Littrow check, and
  uncertainty calculation. [Melissa Hobson]

  `cal_WAVE_E2DS_spirou.py`: test updates

  `visu_WAVE_spirou.py`: lines in adjacent orders are now plotted alternately in magenta or purple for visibility

  `constants_SPIROU_H4RG.py`: increased fit degrees, adjusted FP values

  spirouPlot.py: changed Littrow plot to rainbow colours to improve distinguishing x cuts

  spirouWAVE.py: small improvements
- Merge pull request #381 from njcuk9999/francois. [melissa-hobson]

  update Melissa from Francois


0.2.080 (2018-08-01)
--------------------
- `Cal_WAVE_E2DS_EA_spirou.py`: first version of `cal_WAVE` developed by
  @eartigau, adapted to DRS format. [Melissa Hobson]
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- Merge pull request #379 from njcuk9999/master. [melissa-hobson]

  update melissa
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- Merge pull request #377 from njcuk9999/master. [melissa-hobson]

  update melissa
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]
- Merge pull request #365 from njcuk9999/master. [melissa-hobson]

  Melissa
- Merge remote-tracking branch 'origin/melissa' into melissa. [Melissa
  Hobson]

  Conflicts:
      INTROOT/SpirouDRS/spirouTHORCA/spirouTHORCA.py


0.2.079 (2018-07-27)
--------------------
- Title to the plots + Action TODO to find the right FIBER type.
  [FrancoisBouchy]
- Refinement of the Cut of the left edge of blue orders for
  localisation. [FrancoisBouchy]
- Use only the part of E2DS > 0 to build the S1D spectra.
  [FrancoisBouchy]
- Read the OBSTYPE Before computing BERV OBSTYPE should be OBJECT to
  derive the BERV (not for Calibrations) [FrancoisBouchy]
- Some cosmetic / improvemtn for plot display. [FrancoisBouchy]
- New definition for the blue window on DARK `ic_fracminblaze` = 16 -->
  New parameter to restrict the wings of spectral orders with flux lower
  than `flux_at_blaze` / 16 Spectral order 0 is not taken into account for
  QC of the Flat QC of Flat can be reduce to 5% [FrancoisBouchy]
- Add the background correction. [FrancoisBouchy]
- Correction of center of the blaze window Put to zero edge of the
  spectra where flux is too low (less than `flux_at_blaze` /
  `IC_FRACMINBLAZE`. [FrancoisBouchy]
- Put to zero part of spectra where the blaze is not define.
  [FrancoisBouchy]


0.2.077 (2018-07-25)
--------------------
- Improvement for the localisation. [FrancoisBouchy]
- Adaptation parameters for localisation. [FrancoisBouchy]
- Add the background subtraction. [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]

  Conflicts:
      `INTROOT/SpirouDRS/data/ccf_masks/gl581_july18_clean_rec2.mas`
      INTROOT/SpirouDRS/spirouBACK/spirouBACK.py
      `INTROOT/SpirouDRS/spirouImage/__init__.py`
      INTROOT/SpirouDRS/spirouImage/spirouImage.py
      `INTROOT/bin/cal_FF_RAW_spirou.py`
      `INTROOT/bin/cal_extract_RAW_spirou.py`
      `INTROOT/bin/visu_WAVE_spirou.py`
      `INTROOT/config/constants_SPIROU_H4RG.py`


0.2.078 (2018-07-25)
--------------------
- Inserted filename, MJD, and MJDEND keywords from expsoures in polar
  sequence to the header of polarimetry products. [Eder]
- Merge branch 'master' into eder. [Eder]
- Merge pull request #378 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date/changelog/version. [njcuk9999]
- Merge branch 'master' into eder. [Eder]
- Merge branch 'master' into eder. [Eder]
- Removed small comment -- nothing really. [Eder]
- Fixed formatting of doc strings. [Eder]
- Merge branch 'eder' of `https://github.com/njcuk9999/spirou_py3` into
  eder Removing function duplicated function `calculate_stokes_I`. [Eder]


0.2.071 (2018-07-20)
--------------------
- Update test run. [njcuk9999]
- Misc functions. [njcuk9999]
- Fixed call to earth velocity correction function. [njcuk9999]
- Move `get_good_object_name` function. [njcuk9999]
- Add aliases for getting obj name and airmass. [njcuk9999]
- Fix acquisition time naming. [njcuk9999]
- Added file iteration to plot. [njcuk9999]
- Fix acquitision time naming (julian not unix) [njcuk9999]
- Add tellu template file definition. [njcuk9999]
- Remove extra recipe control key. [njcuk9999]
- Move objname and airmass to functions. [njcuk9999]
- Fix naming conversion time is julian not unix. [njcuk9999]
- Correct filename bug. [njcuk9999]
- Fixed bug with convolve file not being read correctly. [njcuk9999]
- Fxied bug with `get_param`. [njcuk9999]
- Fxied bug with `get_param`. [njcuk9999]
- Fxied bug with `get_param`. [njcuk9999]
- Fix bug in `get_wave_solution`. [njcuk9999]
- Fixed but with header key too long (9 > 8) [njcuk9999]
- Fix bug in assigned WAVEFILE. [njcuk9999]
- Fix bug in `get_param` call. [njcuk9999]


0.2.070 (2018-07-19)
--------------------
- Add telluric database reset to `cal_validate`. [njcuk9999]
- Tellu recipes - bug fix for plot. [njcuk9999]
- Fix bug with timestamp (telluDB only) [njcuk9999]
- Integrate telluric recipes with test runs: compressed + binned
  `tapas_all_sp` file. [njcuk9999]
- Integrate telluric recipes with test runs: updated after test runs.
  [njcuk9999]
- Integrate telluric recipes with test runs: updated error message in
  `get_param`. [njcuk9999]
- `Cal_preprocess` - DPRTYPE = None  rows of `recipe_control` should not be
  used to ID files. [njcuk9999]
- Integrate telluric recipes with test runs: fixes afer test runs.
  [njcuk9999]
- Integrate telluric recipes with test runs: updated aliases.
  [njcuk9999]
- Integrate telluric recipes with test runs: updated `TELL_MOLE` file
  (.gz) [njcuk9999]
- Integrate telluric recipes with test runs: fixes afer test runs.
  [njcuk9999]
- Integrate telluric recipes with test runs: fixes afer test runs.
  [njcuk9999]
- Integrate telluric recipes with test runs: fixes afer test runs.
  [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]


0.2.069 (2018-07-18)
--------------------
- Integrate telluric recipes with test runs: updated after test runs.
  [njcuk9999]
- Integrate telluric recipes with test runs: added `get_wave_keys`
  function. [njcuk9999]
- Integrate telluric recipes with test runs: updated aliases.
  [njcuk9999]
- Integrate telluric recipes with test runs: test run only. [njcuk9999]
- Integrate telluric recipes with test runs: updated plots (corrected)
  [njcuk9999]
- Integrate telluric recipes with test runs: resorted `use_keys` + added
  wave and telluric keys. [njcuk9999]
- Updated filename `(TELLU_FIT_OUT_FILE)` [njcuk9999]
- Integrate telluric recipes with test runs: added constants from
  Etienne and corrected bug in `tell_lambda_max`. [njcuk9999]
- Integrate telluric recipes with test runs: update after running
  `fit_tellu`. [njcuk9999]
- Integrate telluric recipes with test runs: update after running
  `fit_tellu`. [njcuk9999]
- Integrate telluric recipes with test runs: test run only. [njcuk9999]
- Modified `cal_extract` to save wavefile name and wave file dates (for
  telluric) [njcuk9999]


0.5.038 (2018-07-17)
--------------------
- Merge pull request #376 from njcuk9999/neil. [Neil Cook]

  Neil
- Update date/version/changelog. [njcuk9999]
- Copy (same) [njcuk9999]
- Update tellu recipes: fix bug with file name. [njcuk9999]
- Update tellu recipes: drs telluDB reset now resets telluDB not calibDB
  (fix typos) [njcuk9999]
- Update tellu recipes: fix after test run FWHM is function not object.
  [njcuk9999]
- Update tellu recipes: fix after test run - telluDB get database values
  are already split on spaces. [njcuk9999]
- Update tellu recipes: fix after test run - fix bug (needed
  enumerate(lines)) [njcuk9999]
- Update tellu recipes: fix after test run - add alias to
  `update_datebase_tell_temp`. [njcuk9999]
- Possible bug fix: tried to separate out interactive options in
  `end_interactive_session` function. [njcuk9999]
- Possible bug fix: tried to reduce repetition of displayed warnings.
  [njcuk9999]
- Update tellu recipes: added AIRMASS header key. [njcuk9999]
- Bug fix: fix file name `'_s1d_{0}.fits`' -->
  `'_s1d_{0}.fits'.format(p['FIBER'])` [njcuk9999]
- Update tellu recipes: add required line in master telluDB. [njcuk9999]
- Update tellu recipes: add `obj_mk_tell_template` to recipe control.
  [njcuk9999]
- Update tellu recipes: move `obj_mk_tell_template` constantsto here and
  correct some bugs after test run. [njcuk9999]
- Update tellu recipes: fix after test run. [njcuk9999]
- Update tellu recipes: fix after test run. [njcuk9999]
- Updated date/changelog/version. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- Merge pull request #375 from njcuk9999/neil. [Neil Cook]

  Neil
- Telluric integration: bug fixes (after move of functions) [njcuk9999]
- Updated call to plot. [njcuk9999]
- Moved debug plot back to main code. [njcuk9999]
- Updating integration of tellu files: added functions -
  `interp_at_shifted_wavelengths`, `calc_recon_abso`,
  `calc_molecular_absorption` and `lin_mini`. [njcuk9999]
- Updating integration of tellu files: added new function aliases.
  [njcuk9999]
- Updating integration of tellu files: added plot function
  `"tellu_fit_recon_abso_plot`" [njcuk9999]
- Updating integration of tellu files: Added abso output keyword.
  [njcuk9999]
- Updating integration of tellu files; Added filename pseudo constants.
  [njcuk9999]
- Updating integration of tellu files: added constants (need
  commenting!) [njcuk9999]
- Updating integration of tellu files. [njcuk9999]
- Updating integration of tellu files. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- Merge pull request #374 from njcuk9999/neil. [Neil Cook]

  add new mask from Xavier
- Updated date and veresion and changelog. [njcuk9999]


0.2.066 (2018-07-15)
--------------------
- Add new mask from Xavier. [njcuk9999]
- Merge pull request #373 from njcuk9999/neil. [Neil Cook]

  Neil - runs with H4RG set up in data from 2018-04-09
- Changed encoding (copy/paste/revert) -- ignore. [njcuk9999]
- Fixed log to not wrap this text - ONLY. [njcuk9999]
- Changed name of sub-module. [njcuk9999]
- Fixed cyclic imports (new sub-module - spirouBERV) [njcuk9999]
- Fixed cyclic imports. [njcuk9999]
- Added `character_log_length` pseudo constant. [njcuk9999]
- Added maximum log length (wraps to new row with a tab) wraps words but
  still problem with long filenames. [njcuk9999]
- Fixed typo in Merge from @FrancoisBouchy. [njcuk9999]
- Fixed cyclic importing and typos in keyword assignment. [njcuk9999]
- Fixed cyclic importing. [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Bring S1D `(cal_extract)` in-line with rest of DRS (Fixing merges from
  @FrancoisBouchy) [njcuk9999]
- Added spirouTelluric to modules list. [njcuk9999]
- Fix pep8 issues (in-line comment should have at least two spaces
  between code and comment. [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Merge @FrancoisBouchy changes - still need fixing (PEP8 and
  integration) [njcuk9999]
- Fix needed commented code (commented for testing) --> uncommented now.
  [njcuk9999]
- Updated `construct_convolution_kernal2` function. [njcuk9999]
- Added teullric aliases. [njcuk9999]
- Added `tellu_fit_tellu_spline_plot` function. [njcuk9999]
- Update ConstructConvKernel2 function. [njcuk9999]
- Continued to merge Etiennes code. [njcuk9999]


0.2.065 (2018-07-13)
--------------------
- Add functions: `calculate_absorption_pca`, `get_berv_value`. [njcuk9999]
- Add telluric aliases. [njcuk9999]
- Add functions `get_database_tell_template`, `update_database_tell_temp`.
  [njcuk9999]
- Continue to integrate functions. [njcuk9999]
- Correct duplication of header is None. [njcuk9999]
- Added telluric alias. [njcuk9999]
- Added telluric pca plot. [njcuk9999]
- Corrected bad function call to GetNormalizedBlaze and duplicated call
  to loc=ParamDict() [njcuk9999]
- Moved getting berv to spirouTelluric. [njcuk9999]
- First attempt at integrating code (unfinished) [njcuk9999]
- Add keys defined in functions. [njcuk9999]
- Add new TDB aliases. [njcuk9999]
- Correct access to telluric database and update telluric database.
  [njcuk9999]
- First commit - direct integration of `mk_template.py` from Etienne.
  [njcuk9999]
- First commit - blank. [njcuk9999]
- Updated where we get the telluric molecular file (now from database)
  [njcuk9999]
- Added getting of absolute path for telluric files. [njcuk9999]
- Added switch between telluricand calibration databases. [njcuk9999]
- Added aliases from TDB. [njcuk9999]
- Added get and update functions (wrapping generic functions in
  spirouDB) [njcuk9999]
- Added todo's to make general. [njcuk9999]
- First commit - generic functions for database management. [njcuk9999]


0.2.076 (2018-07-13)
--------------------
- New correlation Mask made by XD. [FrancoisBouchy]
- Background correction and set negative values to zero Read Blaze
  function Compute S1D spectra and archive it. [FrancoisBouchy]
- Background correction and negative values set to zero.
  [FrancoisBouchy]
- Typo correction to read the fitted lines. [FrancoisBouchy]
- New constant parameters for background correction and e2dstos1d.
  [FrancoisBouchy]
- Adaptation of function to measure the global background in the image.
  [FrancoisBouchy]
- Add the two new functions e2dstos1d and `write_s1d`. [FrancoisBouchy]
- New function to write S1D spectra with the same format than HARPS.
  [FrancoisBouchy]
- New function to build S1D spectra. [FrancoisBouchy]


0.2.064 (2018-07-12)
--------------------
- First commit - added `obj_mk_tellu` functions. [njcuk9999]
- Added spirouTelluric aliases. [njcuk9999]
- Added wave param aliases. [njcuk9999]
- Added read andget wave param functions. [njcuk9999]
- Added plot for `obj_mk_tellu`. [njcuk9999]
- Added file name definitions for `obj_mk_tellu`. [njcuk9999]
- Added `obj_mk_tellu` to recipe control. [njcuk9999]
- Added `obj_mk_tellu` constants. [njcuk9999]
- Integrated `obj_mmk_tellu` into spirou drs (rea/write/constants etc)
  [njcuk9999]
- Added saving of wave parameters to header of E2DS. [njcuk9999]
- Remove. [njcuk9999]
- Copy of etiennes raw `mk_tellu` code. [njcuk9999]
- Added imports to python local namespace (for embeded run after code
  finish) [njcuk9999]
- Blank files for telluric functions. [njcuk9999]
- First commit of the spirou visu GUI. [njcuk9999]
- First commit of `obj_mk_tellu` - processing the telluric files and
  adding them to telluDB. [njcuk9999]


0.2.063 (2018-07-11)
--------------------
- Add `master_tellu_spirou` file. [njcuk9999]
- Add `cal_wave_mapper` to recipe control file. [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Add reset tellu to `drs_reset` functions. [njcuk9999]
- Adde `dcal_wave_mapper` to recipe list (and unit recipe) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) + added printing of tilt/wave/blaze/flat file used.
  [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Fixed bug: `hdr['KW_X']` --> `hdr[p['KW_X'][0]]` [njcuk9999]
- Add telluDB constants. [njcuk9999]
- Add telluDB (for now a copy of spirouCDB - but will change)
  [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Update `cal_wave_mapper` (as main function with returns to local)
  [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]
- Rename calibDB module: spirouCDB --> spirouDB (to add telluric
  database) [njcuk9999]


0.2.062 (2018-07-10)
--------------------
- Added filename functions `(WAVE_MAP_SPE_FILE` and `WAVE_MAP_SPE0_FILE)`
  [njcuk9999]
- Added filenames in spirouConfig. [njcuk9999]
- Define todos. [njcuk9999]
- Fix bug: `night_name` should only be a string (could be a int)
  [njcuk9999]
- Update to accept multiple fibers AB and C or A B and C or any
  combination. [njcuk9999]
- Change the files tested. [njcuk9999]
- Fix to a bug `ll_line_cat` --> `ll_line_fit`. [njcuk9999]
- E2ds back projection - first commit. [njcuk9999]
- Fix for choice of fiber(s) [njcuk9999]


0.2.061 (2018-07-09)
--------------------
- Removed berv calculation from RV module. [njcuk9999]
- Added `print_full_table` function. [njcuk9999]
- Updated aliases and `__all_` [njcuk9999]
- Updated aliases and `__all_` [njcuk9999]
- Updated aliases and `__all_` [njcuk9999]
- Moved earth barycentric correction here. [njcuk9999]
- Test fitting versus interpolation. [njcuk9999]
- Updated test to only show "good" orders. [njcuk9999]
- Fixed a comment and updated the berv variable. [njcuk9999]
- Fixed logging all analysed files and printing to screen. [njcuk9999]
- Fixed `off_listing` printing only a few rows (now prints all)
  [njcuk9999]
- Moved berv calculation to extraction. [njcuk9999]
- Moved berv calculation to extraction. [njcuk9999]


0.2.060 (2018-07-05)
--------------------
- Fix and test of `find_lines`. [Neil Cook]


0.5.033 (2018-07-04)
--------------------
- Merge pull request #372 from njcuk9999/neil. [Neil Cook]

  Neil
- Update changelog/date/version. [Neil Cook]


0.2.059 (2018-07-04)
--------------------
- Update change log. [Neil Cook]
- Update change log. [Neil Cook]
- The output changelog. [Neil Cook]
- Added functionality to update VERSION.txt and the version in the
  `spirouConst.py` file. [Neil Cook]
- DRS version added to VERSION.txt. [Neil Cook]
- Recipe to get/update change log (moved to spirouTools - final
  location) [Neil Cook]
- Recipe to get/update change log. [Neil Cook]
- Output: the change log (backup) [Neil Cook]
- Recipe to update change log. [Neil Cook]
- Merge pull request #371 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.074 (2018-07-04)
--------------------
- Removed duplicated function `calculate_stokes_I` in spirouPOLAR.py.
  [Eder]


0.2.058 (2018-07-03)
--------------------
- Add generic change log (not used but for history) [Neil Cook]
- Make sure object name is "good" with function: `get_good_object_name`.
  [Neil Cook]
- Correct typo. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Remove change log. [Neil Cook]
- Add `user_dir` and `cal_reset` constants. [Neil Cook]
- Add pp mode variable. [Neil Cook]
- Update using the DRS with H4RG example. [Neil Cook]
- Update todo list (remove done + add new) [Neil Cook]
- Update quick installation. [Neil Cook]
- Update output keywords (not finished) [Neil Cook]
- Update installation. [Neil Cook]
- Update input keywords. [Neil Cook]
- Update date architecture. [Neil Cook]
- Removed old change log. [Neil Cook]
- Add `pp_mode` (the way to switch on/off) file type suffix adding. [Neil
  Cook]
- Add output files to p (and thus sent back to main() function call)
  [Neil Cook]
- Update commentation. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #370 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #369 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge remote-tracking branch 'origin/dev' into dev. [Neil Cook]
- Updated doc strings to be consistent with rest of DRS. [Neil Cook]
- Merge pull request #368 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed runs + some very minor fixes to pep8
- Update `pol_spirou.py`. [Neil Cook]

  fix to pep8
- Update spirouPOLAR.py. [Neil Cook]

  fix to pep8
- Merge pull request #367 from njcuk9999/eder. [Neil Cook]

  Eder
- Update spirouPlot.py. [Neil Cook]

  pep 8 fixes
- Improved polar continuum routine. [Eder]
- Improved polar continuum routine. [Eder]
- Swap exposure 3 and 4 to agree with actual SPIRou sequence, and added
  doc string to spirouPolar functions. [Eder]
- Swap exposure 3 and 4 to agree with actual SPIRou sequence, and added
  doc string to spirouPolar functions. [Eder]
- Fixed bugs in plot and added new keywords to polar products. [Eder]
- Fixed bugs in plot and added new keywords. [Eder]
- Updated module definitions in spirouPOLAR. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and version. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Added variable definitions to wave solution section and qulaity
  control section. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated date and version. [Neil Cook]


0.5.031 (2018-06-29)
--------------------
- Merge pull request #366 from njcuk9999/neil. [Neil Cook]

  Neil - just document changes and some code clean up.
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Added variabels to `cal_hc/cal_wave` variable definitions. [Neil Cook]
- Added more `cal_hc/cal_wave` variable definitions. [Neil Cook]
- Removed old `cal_hc` constants. [Neil Cook]
- Removed old `cal_hc` code. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Update version, date and module root definitions. [Neil Cook]
- Update variable definitions. [Neil Cook]


0.5.030 (2018-06-28)
--------------------
- Merge pull request #364 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.057 (2018-06-28)
--------------------
- Updated date and version and added new recipes. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added more variable definitions. [Neil Cook]
- Update to variables - adding new ones. [Neil Cook]
- Update to comment. [Neil Cook]
- Tried to speed up plotting + fixed a bug with call to
  spirouTHORCA.GetLampParams (now requires header) [Neil Cook]
- Fix python 2/python 3 incompatibility with numpy change. [Neil Cook]
- Fix call to `fiber_params` change (from circular import bug) [Neil Cook]
- Doc string update - requires spirouPOLAR command. [Neil Cook]
- Fix circulate import bug --> move `fiber_params` from spirouLOCOR to
  spirouFile and update calls accordingly. [Neil Cook]


0.2.075 (2018-06-28)
--------------------
- `Visu_WAVE_spirou.py`: correct call to GetLampParams. [melissa-hobson]


0.2.056 (2018-06-27)
--------------------
- First commit of spirouPOLOAR module tex file. [Neil Cook]
- Update main init. [Neil Cook]
- Add spirouPOLAR to aliases. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Move functions around and add todo/fixme. [Neil Cook]
- Doc string update. [Neil Cook]
- Update date and version. [Neil Cook]
- Rebuild pdf after doc string update. [Neil Cook]
- Update date and versions. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Doc string update. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #361 from njcuk9999/neil. [Neil Cook]

  Neil
- Added new tool to calculate barycentric velocity and add it to the
  header of the input file. [Neil Cook]
- Added a skip check to `check_file`. [Neil Cook]


0.2.055 (2018-06-26)
--------------------
- Added `cal_hc` and `cal_wave` to unit test definitions. [Neil Cook]
- Fix to `cal_HC` and `cal_WAVE` added to unit test runs. [Neil Cook]
- Added printout of max time for calibDB. [Neil Cook]
- Added `cal_HC`, `cal_WAVE` (and setup for `cal_WAVE_NEW)` to all run. [Neil
  Cook]
- We have FIBER therefore use FIBER not `FIB_TYP`, modified error
  reporting give we use header keys. [Neil Cook]
- Fixed bug that allows reduced files to be None (should be found by
  file name or generate error) [Neil Cook]
- Added e2dsff files to recipe control for `cal_HC` and `cal_WAVE`, added
  `cal_WAVE_NEW` files (same as `cal_WAVE)` [Neil Cook]
- Fixed typo (bug?) [Neil Cook]
- Updated to work with odometer identification (like rest of DRS) [Neil
  Cook]
- Merge pull request #360 from njcuk9999/melissa. [Neil Cook]

  Melissa
- Update spirouTHORCA.GetLampParams to identify lamp type from fiber
  position header key Update all functions using GetLampParams `(cal_HC`,
  `cal_WAVE`, `cal_WAVE_NEW)` `visu_WAVE)` to pass the header. [melissa-
  hobson]
- `Visu_WAVE_spirou`: higher base level for lines. [melissa-hobson]
- Update for `visu_WAVE_spirou.py` - now working. [melissa-hobson]
- `Cal_HC_E2DS_spirou.py`: added fiber position identification from fiber
  type `spirouTHORCA.decide_on_lamp_type`: - changed to identify lamp from
  fiber position (for use w/odometer names) - previous version moved to
  `decide_on_lamp_type_old`. [melissa-hobson]
- `Cal_HC_E2DS_spirou.py`: added fiber position identification from fiber
  type `spirouTHORCA.decide_on_lamp_type`: - changed to identify lamp from
  fiber position (for use w/odometer names) - previous version moved to
  `decide_on_lamp_type_old`. [melissa-hobson]
- Update for use with e2dsff files as well as e2ds files. [Neil Cook]
- Merge pull request #357 from njcuk9999/neil. [Neil Cook]

  Neil
- Fixed bug in header key `berv_max`. [Neil Cook]
- Add calibDB setup to `cal_validiate`. [Neil Cook]
- Add BERV corrections to header. [Neil Cook]
- Update `pol_spirou.py`. [Neil Cook]

  code duplicated in bad merge @edermartioli
- Merge pull request #356 from njcuk9999/eder. [Neil Cook]

  Eder
- Reset config.py. [Eder]
- Merging changes. [Eder]
- Merge branch 'master' into eder. [Eder]
- Updates from master. [Eder]
- Update output name without `_A`, save errors to output using
  WriteImageMulti. [Eder]
- Update output name without `_A`, save errors to output using
  WriteImageMulti. [Eder]
- Update output name without `_A`, save errors to output using
  WriteImageMulti. [Eder]
- Merged master and resolved conflict in `pol_spirou`. [Eder]
- Implemented total flux (Stokes I) calculation. [Eder]
- Merge branch 'master' into eder. [Eder]
- Merge pull request #354 from njcuk9999/neil. [Neil Cook]

  Neil - confirmed test of H4RG
- Added `cal_preprocess`, `off_listing`, `visu_raw`, `visa_e2ds` and `pol_spirou`
  to the unit testing. [Neil Cook]
- Modified a warning message to be slightly more descriptive. [Neil
  Cook]
- Merge pull request #353 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #351 from njcuk9999/dev. [Neil Cook]

  Dev
- Revert changes to get wave solution from calibDB (errors were due to
  badly set up calibDB) [Neil Cook]
- Merged changes from @edermartioli: added alias to `calculate_stokes_I`
  and added aliases to `__all__` [Neil Cook]
- Merged changes from @edermartioli: Update output name with `_A`, save
  errors to output using WriteImageMulti, Implemented total flux (Stokes
  I) calculation, implemented polarimetric error calculation. [Neil
  Cook]
- Merged changes from @edermartioli: aqdded stokesI plot, spelling
  correction + polarisation is now percentage (bug was missing in
  conversion) [Neil Cook]
- Merged changes from @edermartioli: Update output name with `_A`, save
  errors to output using WriteImageMulti, Implemented total flux (Stokes
  I) calculation, implemented polarimetric error calculation. [Neil
  Cook]
- Added warning in `config.py` to not change PATHs here (todo in docs)
  [Neil Cook]
- Merged changes from @edermartioli: Update output name with `_A`, save
  errors to output using WriteImageMulti, Implemented total flux (Stokes
  I) calculation, implemented polarimetric error calculation. [Neil
  Cook]
- Merge pull request #350 from njcuk9999/neil. [Neil Cook]

  Neil
- Issue #348 - fixed definition of WLOG in spirouPlot ("sometimes"
  causes a crash sometimes doesn't) [Neil Cook]
- Update date and version. [Neil Cook]
- Undo bad merge by @melissa-hobson. [Neil Cook]
- `Cal_HC_E2DS_spirou.py`: added fiber position identification from fiber
  type `spirouTHORCA.decide_on_lamp_type`: - changed to identify lamp from
  fiber position (for use w/odometer names) - previous version moved to
  `decide_on_lamp_type_old`. [melissa-hobson]
- Update date and version. [Neil Cook]
- Fix for loggers being out of range. [Neil Cook]


0.2.073 (2018-06-26)
--------------------
- `Cal_HC_E2DS_spirou.py`: added fiber position identification from fiber
  type `spirouTHORCA.decide_on_lamp_type`: - changed to identify lamp from
  fiber position (for use w/odometer names) - previous version moved to
  `decide_on_lamp_type_old`. [Melissa Hobson]
- `Cal_HC_E2DS_spirou.py`: added fiber position identification from fiber
  type `spirouTHORCA.decide_on_lamp_type`: - changed to identify lamp from
  fiber position (for use w/odometer names) - previous version moved to
  `decide_on_lamp_type_old`. [Melissa Hobson]
- Log calibDB match method. [melissa-hobson]
- `Cal_WAVE_NEW_E2DS_spirou.py`: first version (untested) [melissa-hobson]
- Merge pull request #347 from njcuk9999/master. [melissa-hobson]

  Melissa
- Merge pull request #345 from njcuk9999/neil. [Neil Cook]

  Neil - confirmed tested on H4RG files
- Fixed to run with new setup. [Neil Cook]
- Fix for warninglogger. [Neil Cook]
- Log handled exits! [Neil Cook]
- Fixed setup for badpix. [Neil Cook]
- Fix set up changes. [Neil Cook]
- Update set up begin function. [Neil Cook]
- Updated setup (use of spirouStartup.Begin) [Neil Cook]
- Dealt with recipe name handling better. [Neil Cook]
- Fix program with recipe name instead of sys.argv (unless not present)
  [Neil Cook]
- Fix recipe setup. [Neil Cook]
- Updated master time. [Neil Cook]
- Fixed system exit quitting automated run. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Now cleaning WLOG in `run_begin` (via `WLOG.clean_log())`, and added
  `main_end_script` (to push logging to p and run `clean_log)` [Neil Cook]
- Added function `write_image_multi` (aliased to WriteImageMulti) to save
  multiple extensions to filename - for @edermartioli and the `pol_spirou`
  code specifically. [Neil Cook]
- Defined logger function into class (allows storage or any
  errors/warnings/info and piping back into p at the end of recipe. Must
  clear WLOG at start and end of recipes! [Neil Cook]
- Fix for issue #337 - add e2dsff as well as e2ds (defaults to e2dsff if
  present) and added `log_storage_keys` pseudo variable. [Neil Cook]
- Updated trigger to add error and logger values to HISTORY.txt. [Neil
  Cook]
- Updated recipes main end script (to allow piping of logging into p -
  thus accessible outside via `ll['p']['LOGGING_ERROR']` for example.
  [Neil Cook]
- `Cal_WAVE_NEW_E2DS_spirou.py`: first version (untested) [melissa-hobson]
- Merge pull request #344 from njcuk9999/master. [melissa-hobson]

  Update
- Merge pull request #343 from njcuk9999/neil. [Neil Cook]

  Neil
- Fix to print out. [Neil Cook]
- Updated files for reset. [Neil Cook]
- Added new wavesolution to cal reset. [Neil Cook]
- Merge pull request #342 from njcuk9999/neil. [Neil Cook]

  Work on Issue #338
- Work on Issue #338 - added possibility to enter debug mode and added
  the table printed to screen. [Neil Cook]
- Update date and version. [Neil Cook]
- Merge pull request #341 from njcuk9999/neil. [Neil Cook]

  fix - spirouUnitRecipes.wrapper requires true python strings
- Fix - spirouUnitRecipes.wrapper requires true python strings. [Neil
  Cook]
- Merge pull request #340 from njcuk9999/dev. [Neil Cook]

  Dev
- Added catch of warnings with polyfit. [Neil Cook]
- Added catch warning for polyfit, fixed bug with `lamp_type` in
  `decide_on_lamp_type`. [Neil Cook]
- Added missing plot function `(wave_fp_wavelength_residuals)`, added
  iteration number to plots for `wave_littrow_check_plot` and
  `wave_plot_final_fp_order`. [Neil Cook]
- Added doc string to `cal_HC` main function. [Neil Cook]
- Merge pull request #339 from njcuk9999/francois. [Neil Cook]

  Merge Francois to Dev
- Work on issue #337: modified `decide_on_lamp_type` function to accept
  `ic_lamps` values as lists (and iterate through) - still must only have
  one of the two. [Neil Cook]
- Updated constants in H2RG to match H4RG. [Neil Cook]
- Work on issue #337: changed `ic_lamps` values to be lists + cleaned up
  constants (pep8) [Neil Cook]
- Work on Issue #337: slight clean up of @FrancoisBouchy changes.
  Renamed part1b to part2 and commented out old part 2. [Neil Cook]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]
- Merge pull request #336 from njcuk9999/neil. [Neil Cook]

  Neil
- Part 1b created as a copy of Part 2 and Modified Part 1b repeats the
  Littrow extrapolation for the second pass The second Littrow
  extrapolation is used for to join orders Part 2 is no more useful and
  we do not need CCF. [FrancoisBouchy]
- Adaptation of all the parameters for `cal_HC` `ic_lamps` still need to be
  adapted for hc1 and hcone exposures. [FrancoisBouchy]
- Change e2ds with e2dsff to define the wave filename but it will be
  useful to keep both possibility (e2ds and e2dsff) Correction on the
  format of the wave filename. [FrancoisBouchy]
- Define `ord_start` and `ord_final` for the first guess solution Compute
  correctly E2DS orders from echelle orders for the display LOG Display
  the right number of good lines Count the total number of good lines
  Add possibility to change Littrow fit degree for the two iterations
  For second iteration the initial catalog is used again Let the
  possibility to join extrapolated orders in the blue `ll_free-span` set
  as a list of two parameters in COnstante File Require at least 4
  points to fit a Gaussian Order limits are define with min and max of
  `ll_lines`. [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]

  Conflicts:
      INTROOT/SpirouDRS/spirouEXTOR/spirouEXTOR.py
      `INTROOT/bin/off_listing_RAW_spirou.py`
- Merge pull request #334 from njcuk9999/master. [melissa-hobson]

  update branch
- `Cal_WAVE_NEW_E2DS_spirou.py`: first version (untested) [melissa-hobson]
- Merge pull request #328 from njcuk9999/master. [melissa-hobson]

  Update Melissa branch
- Fitgaus - python version. [melissa-hobson]

  Python version of the fitgaus.f functions.
  - contains two versions of Gauss-Jordan algorithm, an exact copy of the fortran code with all loops `(gaussj_fortran)` and an attempt to make it more efficient via numpy (gaussj, but is currently slower).
  - function covstr was omitted as it does nothing in our use case.
- Merge pull request #321 from njcuk9999/master. [melissa-hobson]

  Update branche
- Merge pull request #286 from njcuk9999/master. [melissa-hobson]

  update
- Merge pull request #273 from njcuk9999/master. [melissa-hobson]

  update melissa
- Merge pull request #269 from njcuk9999/master. [melissa-hobson]

  update melissa


0.2.052 (2018-06-21)
--------------------
- Implemented polarimetric errors calculation. [Eder]
- Implemented polarimetric errors calculation. [Eder]
- Changed polarimetry stuff to adapt changes made by Neil. [Eder]
- Config.py. [Eder]
- Merge branch 'eder' of `https://github.com/njcuk9999/spirou_py3` into
  eder. [Eder]

  No big changes, just testing a few things


0.2.051 (2018-06-20)
--------------------
- No main file. [Neil Cook]
- Must use unit test to run recipes. [Neil Cook]
- Undo print test. [Neil Cook]
- Updated chmod. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #335 from njcuk9999/neil. [Neil Cook]

  Neil
- Fixes to main raw trigger. [Neil Cook]
- Corrected bug where `OFF_LISTING_FILE` was missing. [Neil Cook]
- Corrected bug where no night name does give good error. [Neil Cook]
- Fixed bug that `arg_night_name` and files not checked any more. [Neil
  Cook]
- Fixed bug with no DRPTYPE assigned. [Neil Cook]
- Modified recipe control (added order and detector validity) [Neil
  Cook]
- Fisrt commit - raw file trigger `(cal_dark` to `cal_extract)` [Neil Cook]
- Merge pull request #333 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.049 (2018-06-19)
--------------------
- Corrected bug in `night_name` error reporting. [Neil Cook]
- Updated documentation (function definitions) [Neil Cook]
- Improved functionality in reset (allow reset of calibDB or reduced or
  log or all via user input) [Neil Cook]
- Improved reporting of bad night name. [Neil Cook]
- Removed old misc files. [Neil Cook]
- Add obj name to raw files if no other suffix added (for objects) [Neil
  Cook]
- Added preprocessed trigger (for automating pre-processing on
  `DRS_RAW_DATA` directory) [Neil Cook]
- Fixed bug with processed suffix. [Neil Cook]


0.2.050 (2018-06-19)
--------------------
- Changed config to my local paths. [Eder]
- Put config back. [Eder]
- Non. [Eder]
- Merge pull request #332 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #331 from njcuk9999/neil. [Neil Cook]

  Neil
- Update config.py. [Neil Cook]

  removed master need for user config file


0.2.048 (2018-06-18)
--------------------
- Rebuilt pdfs. [Neil Cook]
- Updated doc strings. [Neil Cook]
- Updated author list. [Neil Cook]
- Udpated date and version and added spirouFile command. [Neil Cook]
- Updated some function descriptions. [Neil Cook]
- Issue #330 - fixed comment description. [Neil Cook]
- Issue #330 - fix WLOG message. [Neil Cook]
- Issue #330 - add `pol_spirou` to recipe control. [Neil Cook]
- Issue #330 - fix entry value, set sources keys, and float(nexp) -->
  int(nexp) [Neil Cook]
- Issue #330 - change scatter --> plot. [Neil Cook]
- Issue #330 - add keyword `kw_CMMTSEQ`. [Neil Cook]
- Issue #330 - fix constant value (run tested correction) [Neil Cook]
- Issue #330 - fix setup and a few other minor (run tested correction)
  [Neil Cook]
- Fix bug and cleanup the imports. [Neil Cook]
- Renamed and chmod files. [Neil Cook]
- Renaming file. [Neil Cook]
- Rename file. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]

  Conflicts:
      INTROOT/SpirouDRS/spirouConfig/spirouConst.py
- Merge pull request #329 from njcuk9999/dev. [Neil Cook]

  Dev
- Issue #330 - Adding plots for polarimetry. [Neil Cook]
- Issue #330 - alaises for spirouPOLAR. [Neil Cook]
- Issue #330 - re-write of SPIROU polarimetry module (for DRS
  compatibility class --> functions) [Neil Cook]
- Issue #330 - Adding keywords for polarimetry. [Neil Cook]
- Updated date and version. [Neil Cook]
- Issue #330 - Adding file name definitions for polarimetry. [Neil Cook]
- Issue #330 - Adding constants for polarimetry. [Neil Cook]
- Issue #330: integrating `pol_spirou` from @edermartioli into DRS format.
  [Neil Cook]


0.2.046 (2018-06-15)
--------------------
- Fixed hidden bug (formats should be allowed to be None - chosen by
  astropy. [Neil Cook]
- Fixed hidden bug. [Neil Cook]
- Added extra check for bad key in WLOG (dev issue only) [Neil Cook]
- Added some keys (OBJNAME, `SBCDEN_P)` [Neil Cook]
- Updated date and version and added `OFF_LISTING_FILE` function. [Neil
  Cook]
- @FrancoisBouchy - Added commit: Creation of `off_listing_RAW_spirou` -
  modified to conform with DRS standards + functions + keywords +
  parameters. [Neil Cook]
- @FrancoisBouchy - Added commit: Flux ratio display with 3 digit. [Neil
  Cook]
- @FrancoisBouchy - Added commit: Background correction of the ref file.
  [Neil Cook]
- @FrancoisBouchy - Added commit: Correction to avoid division by zero.
  [Neil Cook]
- Merge pull request #327 from njcuk9999/neil. [Neil Cook]

  verified - tested all recipes on H2RG and H4RG (except `cal_HC`, `cal_WAVE` - which just run through to end - untested + unverified)


0.2.047 (2018-06-15)
--------------------
- Flux ratio display with 3 digit. [FrancoisBouchy]
- Background correction of the ref file. [FrancoisBouchy]
- #300 Bug on the `fit_ccf` on individual orders to investigate.
  [FrancoisBouchy]
- Correction to avoid division by zero. [FrancoisBouchy]


0.2.045 (2018-06-14)
--------------------
- Work on Issue #155 - fix for new single file return. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #326 from njcuk9999/neil. [Neil Cook]

  Neil
- Work on issues #167, #176 and #231 - first commmit spirouWAVE file
  with `cal_WAVE` (only) functions. [Neil Cook]
- Work on issues #167, #176 and #231 - renamed 'DATA' to 'HCDATA', moved
  `get_ll`, `get_dll` to spirouMath. [Neil Cook]
- Work on Issue #155 - modified `multi_file_setup` function and return of
  `single_file_setup` work on issues #167, #176 and #231 - modified custom
  getting of `args/load_arguments` to help with `cal_wave`. [Neil Cook]
- Moved `get_dll` to spirouMath. [Neil Cook]
- Work on issues #167, #176 and #231 - added `read_hcref`, fixed bug with
  NBFRAMES `append_source` --> `set_source`. [Neil Cook]
- Work on Issue #155 - fixing bugs for multi file setup (custom) [Neil
  Cook]
- Added aliases. [Neil Cook]
- Added aliases. [Neil Cook]
- Renamed `correct_flat` to `get_flat`. [Neil Cook]
- Added aliases. [Neil Cook]
- Work on issue #167, #176, #231 - added `wave_plot_instrument_drift`,
  `wave_plot_final_fp_order`, `wave_local_width_offset_plot`, and
  `wave_fp_wavelength_residuals`. [Neil Cook]
- Moved `get_ll_from_coefficients` and `get_dll_from_coefficients` here.
  [Neil Cook]
- Added aliases. [Neil Cook]
- Updated date and version. [Neil Cook]
- Modified comment. [Neil Cook]
- Work on Issue #176, #167, #231 - added constants. [Neil Cook]
- Work on Issue #176, #167, #231. [Neil Cook]
- Work on Issue #155 - modified return of recipe. [Neil Cook]
- Work on Issue #155 - modified return of recipe. [Neil Cook]
- Work on Issue #155 - modified return of recipe. [Neil Cook]
- Work on Issue #155 - modified return of recipe. [Neil Cook]


0.2.044 (2018-06-13)
--------------------
- Modified run order. [Neil Cook]
- Work on issue #176 - changes from variable names (in line with other
  recipes) [Neil Cook]
- Work on issue #155 - modified `initial_file_setup`, added
  `single_file_setup` and `multi_file_setup`, set todo's to remove now
  obsolete functions, added new `get_file` function. [Neil Cook]
- Added aliases. [Neil Cook]
- Added rotate function, fix non pre-processed files function. [Neil
  Cook]
- Work on issue #155 - finished id checking functions. [Neil Cook]
- Added aliases. [Neil Cook]
- Updated date and version, shortened `log_opt` (no suffix just program
  name) [Neil Cook]
- Shorterned calibration --> cal. in log messages (for copying/not
  copying cal files) [Neil Cook]
- Work on issue #155 - added more files to control. [Neil Cook]
- Updated constant name. [Neil Cook]
- Added constants (preprocessing, exposuremeter, `cal_hc`, `cal_wave)` [Neil
  Cook]
- Fix for non pre-processed files. [Neil Cook]
- Fixed bug in gfkwargs. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for non pre-processed
  files. [Neil Cook]
- Made rotation a function based on a given rotation from constant.
  [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for non pre-processed
  files. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for non pre-processed
  files, added H2RG compatibility fix. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for non pre-processed
  files. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for non pre-processed
  files. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for H2RG
  compatibility, added H4RG kw objects needed for berv calculation.
  [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via SingleFileSetup + MultiFileSetup) [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via SingleFileSetup) [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via SingleFileSetup) [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via InitialFileSetup), fix for H2RG
  compatibility. [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via SingleFileSetup) [Neil Cook]
- Work on issue #155 - modified set up to accommodate checks via
  filename and header (via SingleFileSetup) [Neil Cook]


0.2.043 (2018-06-12)
--------------------
- Work on issue #155 - added recipe control file. [Neil Cook]
- Work on issue #155 - (un-finished) added new `initial_file_setup` and
  get file (now use `single_file_setup)` [Neil Cook]
- Work on issue #155 - modified `read_header` to optionally return
  comments. [Neil Cook]
- Work on issue #155 - added ID functions. [Neil Cook]
- Work on issue #155 - reworked aliases and `__ALL__` [Neil Cook]
- Work on issue #155 - updated DPRTYPE comment. [Neil Cook]
- Work on issue #155 - added some required keywords. [Neil Cook]
- Work on issue #155 - rearranged some constants, added data constant
  directory. [Neil Cook]
- Work on issue #155 - changed import to deal with change in location of
  spirouFile. [Neil Cook]
- Work on issue #155 - test of ID-ing files. [Neil Cook]
- Work on issue #155 - added section to ID files and modify the header
  accordingly (based on filename OR header keys) [Neil Cook]
- Merge pull request #325 from njcuk9999/neil. [Neil Cook]

  updated date and version
- Merge pull request #324 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.041 (2018-06-11)
--------------------
- Updated date and version. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added two masks for `cal_HC`.
  [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - updated keywords, renamed some
  loc variables (for clarity) [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added some fixes to
  coravelation (to accommodate `cal_hc)` [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added merge table and added
  some fixes to small bugs. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added alias to
  `spirouTable.merge_table` (MergeTable) [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added FWHM calculation (from
  sigma) [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added keywords for `cal_hc`.
  [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added wave file output
  filename definitions. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added constants. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - output to file + ccf
  calculation (from `cal_CCF` mainly) [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - fixed value of FWHM from
  sigma. [Neil Cook]


0.2.039 (2018-06-08)
--------------------
- Continued work on `cal_HC` (Issue #176) - test of fit gauss functions.
  [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - modified
  `first_guess_at_wave_solution`, `detect_bad_lines`, `fit_1d_solution`,
  `calculate_littrow_sol`, `extrapolate_littrow_sol`,
  `second_guess_at_wave_solution`. Added `join_orders`. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added alias to
  `spirouTHORCA.join_orders` (JoinOrders) [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added `wave_littrow_check_plot`
  and corrected `wave_littrow_extrap_plot`. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - corrected imports and a bug in
  fitgaussian functions. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added how to compile fortran.
  [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - python version of fitgaus by
  @melissa-hobson. [Neil Cook]
- Continued work on `cal_HC` (Issue #176) - added new constants. [Neil
  Cook]
- Continued work on `cal_HC` (Issue #176) - added new constants. [Neil
  Cook]
- Continued work on `cal_HC` (Issue #176) [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- Merge pull request #323 from njcuk9999/dev. [Neil Cook]

  Dev


0.2.036 (2018-06-07)
--------------------
- Find lines test `(cal_HC` test) [njcuk9999]
- Continued work on `cal_HC` - aliases for new THORCA functions.
  [njcuk9999]
- Continued work on `cal_HC` - wave littrow plot. [njcuk9999]
- Continued work on `cal_HC` - experimentation with fitting. [njcuk9999]
- Continued work on `cal_HC`. [njcuk9999]
- Continued work on `cal_HC` - constants for `cal_HC`. [njcuk9999]
- Continued work on `cal_HC`. [njcuk9999]


0.2.037 (2018-06-07)
--------------------
- Added default user config path. [Neil Cook]
- Added my path. [Neil Cook]
- Merge pull request #322 from njcuk9999/dev. [Neil Cook]

  Dev
- @FrancoisBouchy changes - merge confirmed, added some pe8 and comments
  and simplifications. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed + added `ff_rms_plot`
  function. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed + added
  `ff_rms_plot_skip_orders`. [Neil Cook]
- Added `ff_rms_plot_skip_orders` (blank for H2RG) [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed, moved plotting to
  spirouPlot. [Neil Cook]
- @FrancoisBouchy changes - merge confirmed, some pep8 and commenting.
  [Neil Cook]
- @FrancoisBouchy changes - merge confirmed. [Neil Cook]


0.2.035 (2018-05-29)
--------------------
- Fix matplotlib bug. [njcuk9999]
- Fix small bug. [njcuk9999]
- Update date and version. [njcuk9999]
- Merge pull request #319 from njcuk9999/neil. [Neil Cook]

  Neil
- Update config.py. [njcuk9999]
- Re-added BERV correction just for H4RG. [njcuk9999]
- Added masks to correct folder. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- Merge pull request #318 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #317 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #316 from njcuk9999/cfht. [Neil Cook]

  new masks added on data
- New masks added on data. [Spirou DRS]
- Added new SpirouDRS data directories. [njcuk9999]
- Added new SpirouDRS data directories. [njcuk9999]
- Added new SpirouDRS data directories. [njcuk9999]
- Added new SpirouDRS data directories. [njcuk9999]
- Sorted SpirouDRS data folder. [njcuk9999]
- Barycorrpy leap sec files (moved to drs) [njcuk9999]
- Added constant for berv (ccf) [njcuk9999]
- Updated ccf function. [njcuk9999]
- Edited ccf. [njcuk9999]


0.2.034 (2018-05-28)
--------------------
- Updated for `cal_hc`. [njcuk9999]
- Removed redundant comment. [njcuk9999]
- Added test from old drs. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]
- Merge pull request #314 from njcuk9999/neil. [Neil Cook]

  updated date and version number
- Merge pull request #313 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #312 from njcuk9999/neil. [Neil Cook]

  Update `cal_CCF_E2DS_spirou.py`
- Update value for speed of light, added `invert_1ds_ll_solution`.
  [njcuk9999]
- Added new trial method to newbervmain (using barycorrpy) [njcuk9999]


0.2.033 (2018-05-26)
--------------------
- Updated date and version number. [njcuk9999]
- Update tests with CCF test. [njcuk9999]
- Update h2rg constant file (to be same as h4rg) [njcuk9999]
- Fix typos. [njcuk9999]
- Fix runtime errors on ccf test (set order to empty) [njcuk9999]
- Added ee. [njcuk9999]
- Removed fortran code. [njcuk9999]
- Update unit tests. [njcuk9999]
- Update fortran codes. [njcuk9999]
- Updated script doc string. [njcuk9999]
- Update unit tests `(cal_FF_raw` needs `flat_flat)` [njcuk9999]
- Synced h2rg and h4rg. [njcuk9999]
- Correct the comments and indentation of the background. [njcuk9999]
- Merge branch 'francois' into neil. [njcuk9999]

  Conflicts:
      INTROOT/SpirouDRS/spirouConfig/spirouKeywords.py
      INTROOT/SpirouDRS/spirouRV/spirouRV.py
      `INTROOT/bin/cal_CCF_E2DS_spirou.py`
      `INTROOT/bin/cal_FF_RAW_spirou.py`
      `INTROOT/config/constants_SPIROU_H4RG.py`
- First wavelength solution added to SpirouDRS/data. [FrancoisBouchy]
- Telluric mask added on SpirouDRS/data. [FrancoisBouchy]
- Fortran module for BERV computation : Require f2py -c -m newbervmain
  --noopt --quiet newbervmain.f. [FrancoisBouchy]
- Update of `cal_CCF_E2DS` with target parameters and BERV computation
  from the fortran module newbervmain. [FrancoisBouchy]
- Update of `cal_DRIFT_E2DS_spirou`. Results now comparable to
  `cal_DRIFTPEAK_E2DS_spirou`. [FrancoisBouchy]
- Background correctionis now an option. [FrancoisBouchy]
- `Cal_FF_RAW_spirou` must run on `flat_flat` and provide flat and blaze for
  A, B, AB and C fibers. [FrancoisBouchy]
- New recipes to display the full spectral range of an E2DS file.
  [FrancoisBouchy]
- Typo on the name corrected. [FrancoisBouchy]
- Added CFHT parameters and option for background correction on
  `cal_DRIFT`. [FrancoisBouchy]
- Add targets keywords + Date of observations for `cal_CCF_E2DS_spirou`.
  [FrancoisBouchy]
- All wavelength are in nm. [FrancoisBouchy]
- #300 Bug on the `fit_ccf` on individual orders to investigate.
  [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]

  Conflicts:
      INTROOT/SpirouDRS/spirouCore/spirouPlot.py
      `INTROOT/bin/cal_DARK_spirou.py`
      `INTROOT/bin/cal_DRIFTPEAK_E2DS_spirou.py`
      `INTROOT/bin/cal_extract_RAW_spirou.py`
      `INTROOT/bin/visu_RAW_spirou.py`
      `INTROOT/config/constants_SPIROU_H4RG.py`
- @FrancoisBouchy change (merged by @njcuk9999) - why comment out this
  line? [njcuk9999]
- @FrancoisBouchy change (merged by @njcuk9999) - plot labels should be
  in nm not angstrom. [njcuk9999]
- @FrancoisBouchy change (merged by @njcuk9999) - added new required
  input HEADER keywords. [njcuk9999]
- @FrancoisBouchy change (merged by @njcuk9999) [njcuk9999]
- @FrancoisBouchy change (merged by @njcuk9999) [njcuk9999]
- @FrancoisBouchy change (merged by @njcuk9999) [njcuk9999]
- Update H2RG dependency flag. [njcuk9999]
- @ Francois Bouchy - fixed changes `dark_flat/flat_dark` --> `flat_flat`.
  [njcuk9999]


0.2.029 (2018-05-25)
--------------------
- Update of `cal_DRIFT_E2DS_spirou`. Results now comparable to
  `cal_DRIFTPEAK_E2DS_spirou`. [FrancoisBouchy]

  (cherry picked from commit 86ee03b)
- @FrancoisBouchy added `earth_velocity_correction`, newbervmain functions
  and modified coravelation. [njcuk9999]
- @FrancoisBouchy - added alias to `earth_velocity_correction`.
  [njcuk9999]
- @FrancoisBouchy added read star parameters and earth velocity
  calculation. [njcuk9999]
- Merge remote-tracking branch 'origin/neil' into neil. [njcuk9999]


0.2.030 (2018-05-25)
--------------------
- Worked on `fit_1d_solution` (complete?), added to doc strings (gparams)
  [njcuk9999]
- Added alias to `fit_1d_solution` (Fit1DSolution) [njcuk9999]
- Added new `cal_hc` variables. [njcuk9999]
- Change FirstGuessSolution mode to new (to avoid needing fortran
  fitgaus code) [njcuk9999]


0.2.031 (2018-05-25)
--------------------
- Update `cal_CCF_E2DS_spirou.py`. [melissa-hobson]

  Changed filetype to accept all E2DS files.
- Merge pull request #311 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.026 (2018-05-18)
--------------------
- Update readme. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Fixed bug when config files only have one or zero lines. [Neil Cook]
- Reset constant back to default. [Neil Cook]
- Fix to Issue #232 - added `cal_exposure_meter` to unit tests. [Neil
  Cook]
- Fix to Issue #232 - added `cal_exposure_meter` to unit tests. [Neil
  Cook]
- Fix to Issue #232 - add file names for `cal_exposure_meter`. [Neil Cook]
- Fix to Issue #232 - add different outputs. [Neil Cook]
- Fix to Issue #232 - add different outputs. [Neil Cook]
- Fix to Issue #232 - bug in applying badpixmask. [Neil Cook]
- Commented out work-in-progress function. [Neil Cook]
- Fix to Issue #232 - added `get_badpixel_map` and modified
  `correct_for_badpix` functions. [Neil Cook]
- Fix to Issue #232 - added exposure-meter functions to new sub-module
  in spirouImage. [Neil Cook]
- Fix to Issue #232 - added alias to `get_badpixel_map` function
  (GetBadPixMap) [Neil Cook]
- Fix to Issue #232 - added output keywords to spirouKeywords. [Neil
  Cook]
- Fix to Issue #232 - added telluric exposure meter maps to calibDB.
  [Neil Cook]
- Fix to Issue #232 - added expsoure-meter constants. [Neil Cook]
- Fix to Issue #232 - produce expsoure-meter recipe (compatible with
  H2RG and H4RG) [Neil Cook]
- Work on `cal_HC` (restore from bad merge) [Neil Cook]
- Merge pull request #310 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Added wavelength solution file for H4RG. [Neil Cook]
- Added H4RG wavelength solution files to the calib DB default files
  (for reseting) [Neil Cook]
- @FrancoisBoucy - 4 digit to diplay the dark statistics. [Neil Cook]
- @FrancoisBouchy - new lower limit in dark level plot (with H2RG
  compatibility) [Neil Cook]
- Fix error message in `get_database` (calibDB) [Neil Cook]
- Update default `master_calib_spirou` file (with H2RG and H4RG default
  wave solutions) [Neil Cook]
- Update date and version. [Neil Cook]
- @FrancoisBouchy - update to dark constants. [Neil Cook]
- @FrancoisBouchy - `visu_RAW_spirou` adapted for preprocessed files.
  [Neil Cook]
- @FrancoisBouchy - Use the wavelength solution from the calibDB, set
  all negative pixels to zero and update `ext_sorder_fit` upper limit.
  [Neil Cook]
- @FrancoisBouchy - Use the wavelength solution from the calibDB. [Neil
  Cook]
- @FrancoisBouchy - Quality control of the dark level on the blue part
  of the detector. [Neil Cook]
- Added recipe to reset (while in development only) [Neil Cook]


0.2.027 (2018-05-18)
--------------------
- 4 digit to diplay the dark statistics. [FrancoisBouchy]
- Range adjusted to display Dark frame Blue window displayed in White
  Cut parameter added in extract plotting function Wavelength solution
  used in extract plotting function. [FrancoisBouchy]
- Dark constant and Dark quality control adjusted. [FrancoisBouchy]
- `Visu_RAW_spirou` adapted for preprocessed files. [FrancoisBouchy]
- Negative pixels are set to zero Read wavelength solution on calibDB
  Set the cut to `max_signal/10` to display the order location.
  [FrancoisBouchy]
- Use the first wavelength solution from the calibDB
  `spirou_wave_H4RG_v0.fits`. [FrancoisBouchy]
- Quality control of the dark level on the blue part of the detector.
  [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]
- Merge pull request #307 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]
- Merge pull request #305 from njcuk9999/master. [FrancoisBouchy]

  Update README.md
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]

  Conflicts:
      INTROOT/SpirouDRS/spirouEXTOR/spirouEXTOR.py
      INTROOT/SpirouDRS/spirouImage/spirouImage.py
      `INTROOT/bin/cal_BADPIX_spirou.py`
      `INTROOT/bin/cal_DRIFTPEAK_E2DS_spirou.py`
      `INTROOT/bin/cal_extract_RAW_spirou.py`
      `INTROOT/config/constants_SPIROU_H4RG.py`


0.2.025 (2018-05-17)
--------------------
- Fix to Issue #227 - added `cal_drift` and drift peak to tests. [Neil
  Cook]
- Fix to Issue #227 - added `cal_drift` and drift peak to tests. [Neil
  Cook]
- Fix to Issue #227 - added `cal_drift` and drift peak to tests. [Neil
  Cook]
- Work on issue #176 - Attempt to get First Guess solution working and
  detection of badlines. [Neil Cook]
- Work on issue #176 - Attempt to get First Guess solution working and
  detection of badlines (aliases) [Neil Cook]
- Work on issue #176 - added three `cal_HC` constants. [Neil Cook]
- Work on issue #176 - Attempt to get First Guess solution working and
  detection of badlines. [Neil Cook]


0.2.024 (2018-05-16)
--------------------
- Removed dependency on `cal_drift_raw`. [Neil Cook]
- Updated test.run. [Neil Cook]
- Fix to Issue #227 - dealt with warnings for `cal_driftpeak`. [Neil Cook]
- Updated date and version. [Neil Cook]
- Fake file comments added. [Neil Cook]
- Added fake `fp_fp` files for drift (copies of `fp_fp_001)` [Neil Cook]
- Fix to Issue #227 - removed support for `cal_drift_raw_spirou`. [Neil
  Cook]
- Fix to Issue #227 - removed `cal_DRIFT_RAW_spirou`. [Neil Cook]
- Fix to Issue #227 - refactored warnlog. [Neil Cook]
- Fix to Issue #227 - added `cal_drift` and drift peak to tests. [Neil
  Cook]
- Fix to Issue #227 - deal with warnings. [Neil Cook]
- Fix to Issue #227 - refactor warnlog (+ fix bug) [Neil Cook]
- Update date and version. [Neil Cook]
- Fix to Issue #227 - refactor warnlog. [Neil Cook]
- Fix to Issue #227 - apply H4RG fixes to drift codes. [Neil Cook]
- Enchancement - compare function gets `ARG_NIGHT_NAME` from ll, prints
  old and new file locations (for extra confirmation) [Neil Cook]
- Update oldpath (don't include path) [Neil Cook]
- Updated test run. [Neil Cook]
- Fix for bug when HEADER time not string (should always be string but
  can be interpreted as number and thus break function) [Neil Cook]
- Fix - removed unneeded comment. [Neil Cook]
- Merge pull request #306 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]


0.2.023 (2018-05-15)
--------------------
- Updated run. [Neil Cook]
- Fixed typo. [Neil Cook]
- Added runname to comparison table. [Neil Cook]
- Added run name to comparison table (to name table) [Neil Cook]
- Corrected bug with unit test (files were duplicated in list i.e. file1
  file1 file2 file3. [Neil Cook]
- Tool file - clear out cached .pyc files (useful when rebuilding) [Neil
  Cook]
- H2RG compatibility - fitsfilename = `arg_file_names[-1]` and only adding
  SNR keys and EXTM/FUNC for H4RG, p returned to call. [Neil Cook]
- Fixed pep8 in `smoothed_box_mean_image1` function. [Neil Cook]
- Updated date and version + rebuild pdfs. [Neil Cook]
- Updated date and version. [Neil Cook]
- H2RG compatibility - fitsfilename = `arg_file_names[-1]` and only adding
  SNR keys and EXTM/FUNC for H4RG. [Neil Cook]
- H2RG compatibility - fitsfilename = `arg_file_names[-1]` [Neil Cook]
- True on comparison in H2RG run. [Neil Cook]
- Fix to calling from python (bug introduced in last update) [Neil Cook]
- Fix to `unit_test` comparison table. [Neil Cook]
- Fix to `unit_test` comparison table. [Neil Cook]
- Fix to `unit_test` comparison table. [Neil Cook]


0.2.022 (2018-05-14)
--------------------
- Update README.md. [Neil Cook]
- Merge pull request #304 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #303 from njcuk9999/neil. [Neil Cook]

  Neil
- Updated date and versions. [Neil Cook]
- Fix for issue #296 - was mistake in argument to `test_suffix` =
  suffix.format  - called dictionary incorrectly. [Neil Cook]
- Fix for issue #302 - `IC_COSMIC_THRES` --> `IC_COSMIC_THRESH`. [Neil Cook]
- Updated test run. [Neil Cook]
- Fix for issue #302 - added `IC_COSMIC_SIGCUT` and `IC_COSMIC_THRES`. [Neil
  Cook]
- Fix for issue #302 - added `IC_COSMIC_SIGCUT` and `IC_COSMIC_THRES`. [Neil
  Cook]
- Fix to Issue #296 - added alias (CheckPreProcess) for
  `spirouStartup.check_preprocess`. [Neil Cook]
- Fix to Issue #296 - added `IC_FORCE_PREPROCESS` and added all other
  preprcess constants to constants file. [Neil Cook]
- Fix to #296 - added .fits to suffix. [Neil Cook]
- Fix to Issue #296 - added call to CheckPreProcess - check for
  preprocessed files. [Neil Cook]
- Fix to #296 - added `check_preprocess` function. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #301 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #293 from njcuk9999/neil. [Neil Cook]

  Neil
- Fix to `unit_test` - bug in logic when file does not exist --> True to
  False. [Neil Cook]
- Fix to issue #292 - `get_fiber_type` modified to accept and require
  suffix to get fiber type. [Neil Cook]


0.2.021 (2018-05-12)
--------------------
- Fix to issue #300 - added `correct_for_badpix` function. [Neil Cook]
- Fix to issue #300 - alias to `correct_for_badpix` function. [Neil Cook]
- Fix to issue #298 - exit script should deal with new `DRS_INTERACTIVE`
  parameter. [Neil Cook]
- Fix to issue #298 - `DRS_INTERACTIVE` should be set to 1 by default.
  [Neil Cook]
- Fix to bug identified - no exit script in AB or C. [Neil Cook]
- Fix to issue #298 - set `DRS_PLOT` to zero if `DRS_INTERACTIVE` == 0 and
  if `DRS_INTERACTIVE` == 0 do not prompt user at the end of recipes about
  exiting and plotting. [Neil Cook]
- Fix to issue #298 - set `DRS_PLOT` to zero if `DRS_INTERACTIVE` == 0 and
  if `DRS_INTERACTIVE` == 0 do not prompt user at the end of recipes about
  exiting and plotting. [Neil Cook]
- Fix to issue #298 - added `DRS_INTERACTIVE` to config.py. [Neil Cook]
- Fix to issue #297 - Unit test to display current files if no argument.
  [Neil Cook]
- Fixes to `unit_tests` for internal bugs and to correct for issue #295.
  [Neil Cook]
- Fix to issue #294 - H2RG needs to return "bstats2" too (set to zero)
  [Neil Cook]
- Fix to Issue #295 - complete reworking of wrapper function (which is
  now called from recipes) [Neil Cook]
- Fix to Issue #295 - updated alias functions. [Neil Cook]
- Fix to Issue #295 - added `E2DS_EXTM` and `E2DS_FUNC` HEADER keys to
  report extract type and extract function. [Neil Cook]
- Fix for Issue #295 - removed `EXTRACT_E2DS_ALL_FILES` - not needed any
  more. [Neil Cook]
- Fix to Issue #295 - change the way extraction is managed - modified
  `IC_EXTRACT_TYPE` and added `IC_FF_EXTRACT_TYPE`. [Neil Cook]
- Fix to Issue #295 - change the way extraction is managed - now type
  `IC_FF_EXTRACT_TYPE`. [Neil Cook]
- Fix to Issue #295 - change the way extraction is managed - now type 2.
  [Neil Cook]
- Fix to Issue #295 - change the way extraction is managed - now type 2.
  [Neil Cook]
- Fix to Issue #295 - change the way extraction is managed. [Neil Cook]
- Fix to Issue #294 - stats for `bad_pixel_map_2` in `cal_BADPIX_spirou`.
  [Neil Cook]
- Fix to Issue #294 - stats for `bad_pixel_map_2` in `cal_BADPIX_spirou`.
  [Neil Cook]
- Start of fix to issue #295 - Switch between extraction routines in
  `constants_SPIROU` file - unfinished. [Neil Cook]
- Fix to issue #294 - stats for `bad_pixel_map_2` in `cal_BADPIX_spirou`.
  [Neil Cook]
- Fix imports for python 2 and make runs sorted (again for python 2)
  [Neil Cook]
- Fix imports for python 2. [Neil Cook]
- Update units tests with new run names (sortable) - python 2 safe.
  [Neil Cook]
- Fix unit test import (should be inner call to function) [Neil Cook]
- Fix typo. [Neil Cook]
- Fix for typo. [Neil Cook]
- Fix to import statements (for python 2 compatibility) [Neil Cook]
- New `extraction_tilt_weight2cosm` with cosmic correction. Mode=2 is by
  default this new extraction. [Neil Cook]
- Display of bad pixels with 4 digits. [Neil Cook]
- `Ic_blake_fitn` set to 7 `ic_ext_sigdet` set to -1. [Neil Cook]
- ConvertToADU convert from ADU/s to ADU (not e-) Faction of dead pixels
  display with 4 digits Display the number of cosmic rays (bad pixels)
  detected by the extraction. [Neil Cook]
- Fake wavelength solution to run without WAVE fiel in the calibDB.
  [Neil Cook]
- Correction of the display of the image size. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #290 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #288 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.019 (2018-05-09)
--------------------
- Fitgaus fortan code (for testing only) [Neil Cook]
- Example in ipynb and tex format. [Neil Cook]
- Modified test run unit test. [Neil Cook]
- Added new unit test runs (all and minimum required) [Neil Cook]
- Removed old unit test runs. [Neil Cook]
- Added `cal_extract_RAW_spirou` AB and C to unit tests. [Neil Cook]
- Fix problem with reset = False. [Neil Cook]
- Fix so wrapper extractions work with `unit_tests` (and can be called
  from python) [Neil Cook]
- `Ic_ext_sigdet` should be -1. [Neil Cook]
- Fix to Issue #289 - was a problem with WLOG message (argument missing
  from format) [Neil Cook]


0.2.020 (2018-05-09)
--------------------
- Faction of dead pixels display with 4 digits Display the number of
  cosmic rays (bad pixels) detected by the extraction. [FrancoisBouchy]
- Fake wavelength solution due to missing WAVE in calibDB.
  [FrancoisBouchy]
- Display of the format of the resized image. [FrancoisBouchy]
- Merge remote-tracking branch 'origin/francois' into francois.
  [FrancoisBouchy]

  Conflicts:
      `INTROOT/bin/cal_BADPIX_spirou.py`
      `INTROOT/bin/cal_DRIFTPEAK_E2DS_spirou.py`
      `INTROOT/bin/cal_extract_RAW_spirou.py`
- New `extraction_tilt_weight2cosm` with cosmic correction. Mode=2 is by
  default this new extraction. [FrancoisBouchy]
- Display of bad pixels with 4 digits. [FrancoisBouchy]
- `Ic_blake_fitn` set to 7 `ic_ext_sigdet` set to -1. [FrancoisBouchy]
- ConvertToADU convert from ADU/s to ADU (not e-) Faction of dead pixels
  display with 4 digits Display the number of cosmic rays (bad pixels)
  detected by the extraction. [FrancoisBouchy]
- Fake wavelength solution to run without WAVE fiel in the calibDB.
  [FrancoisBouchy]
- Correction of the display of the image size. [FrancoisBouchy]
- Merge pull request #271 from njcuk9999/master. [Neil Cook]

  update to master


0.2.018 (2018-05-07)
--------------------
- Fix to latex format. [Neil Cook]
- Fix to install (cal validate from cmd line needs .py) [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added retrun possibility to `list_modules`, and added
  `find_all_missing_modules` wrapper function. [Neil Cook]
- Completed doc string. [Neil Cook]
- Corrected `__all__` [Neil Cook]
- Added missing doc strings. [Neil Cook]
- Added missing doc strings. [Neil Cook]
- Added missing functions from tex files. [Neil Cook]
- Added tex and pdf versions of the examples (auto-generated from
  notebooks) [Neil Cook]
- Added unit tests and tools to SpirouDRS `__all__` list (and imported)
  [Neil Cook]
- Example 10 in html format. [Neil Cook]
- Example 10 - how to use spirou tools. [Neil Cook]
- Fixed bug in `display_calibdb` (use LoadMinimum not LoadArguments) [Neil
  Cook]
- Updated date and version. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated variables (added CCF variables and missed `cal_BADPIX`
  variabels) [Neil Cook]
- Update to `ic_ext_tilt_bord` description. [Neil Cook]
- H4RG by default. [Neil Cook]
- Update to `unit_test` file (post `unit_test` changes) [Neil Cook]
- Fix to issue #287 - extra issue log statements with errors inside -
  print warnings first then internal errors after - set key after too
  (avoids printing errors inbetween warnings) [Neil Cook]
- Fix to issue #287 - extra issue of crash before config loads
  `(IC_IMAGE_TYPE)` missing from needed spirouKeyword `USE_PARAMS`. [Neil
  Cook]
- Fix to issue #287 - deal with `DRS_UCONFIG` warning printing. [Neil
  Cook]
- Update README.md. [Neil Cook]
- Merge pull request #285 from njcuk9999/neil. [Neil Cook]

  updated date and versions
- Merge pull request #284 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.017 (2018-05-04)
--------------------
- Updated date and versions. [Neil Cook]
- Merge remote-tracking branch 'origin/neil' into neil. [Neil Cook]
- Merge pull request #283 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #282 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #275 from njcuk9999/neil. [Neil Cook]

  pep8 update all ParamDict constants to capitals
- Merge pull request #274 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #270 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #268 from njcuk9999/neil. [Neil Cook]

  Neil
- `Unit_test` fix - add total time to `log_timings` print out. [Neil Cook]
- Fix to Issue #278 - make `cal_extract_RAW_spirouAB` and
  `cal_extract_RAW_spirouC` work again. [Neil Cook]
- Fix to Issue #278 - make `cal_extract_RAW_spirouAB` and
  `cal_extract_RAW_spirouC` work again. [Neil Cook]
- Fix to issue #281 - small function to deal with some extensions being
  corrupted (will still crash if all extensions bad) and will assume
  first valid extension (i.e. with shape) is the image to be used. [Neil
  Cook]
- Fix to issue #277 - check "files" and if it is a string force it into
  a length=1 list, if not string or list throw error. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]
- Fix to issue #277 - added doc string to main functions to make it
  clear what inputs are expected. [Neil Cook]


0.2.016 (2018-05-03)
--------------------
- Pep8 update all ParamDict constants to capitals. [Neil Cook]
- `Unit_test` - added additional run files. [Neil Cook]
- `Unit_test` fix - `DRS_Reset` modification, loading arguments modification
  and `set_type` --> `check_Type` change. [Neil Cook]
- `Unit_test` fix - `set_type` doesn't work - just check type instead (and
  throw error) [Neil Cook]
- `Unit_test` fix - rename `set_type` to `check_type`. [Neil Cook]
- `Unit_test` fix - alias to `load_minimum`. [Neil Cook]
- `Unit_test` fix - `reset_confirmation` modification and log successful
  completion. [Neil Cook]
- `Unit_test` fix - do not require `night_name`. [Neil Cook]


0.2.015 (2018-05-02)
--------------------
- Notebook additions - conversion to html. [Neil Cook]
- Notebook additions - added a quiet mode for notebooks (no user input
  needed) [Neil Cook]
- Notebook additions - added `unit_test` alias to init file (for loading
  up from python) [Neil Cook]
- Notebook additions - test unit test for notebooks. [Neil Cook]
- Notebook additions - example 9 - unit tests. [Neil Cook]
- Notebook additions - example 8 - wlog. [Neil Cook]
- Notebook additions - code to convert. [Neil Cook]


0.2.014 (2018-05-01)
--------------------
- Rebuild pdfs. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Redefining unit tests - example run files (for unit test) [Neil Cook]
- Redefining unit tests - first commit - slight changes (logging) [Neil
  Cook]
- Redefining unit tests - first commit - new recipe for unit test. [Neil
  Cook]
- Redefining unit tests - first commit - new functions for unit test.
  [Neil Cook]
- Redefining unit tests - first commit - new recipe definitions for unit
  tests. [Neil Cook]
- Redefining unit tests - added new function aliases. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - moved old. [Neil Cook]
- Redefining unit tests - allowing silent reset (not advised) [Neil
  Cook]
- Updating versions. [Neil Cook]
- Redefining unit tests - add function alias. [Neil Cook]


0.2.012 (2018-04-30)
--------------------
- Regarding issue #264 - change no longer needed - revert to earlier
  version. [Neil Cook]
- Fix to issue #267 - SNR saved in the headers - added keys to E2DS
  header. [Neil Cook]
- Fix to issue #267 - SNR saved in the headers - added new keyword to
  list. [Neil Cook]
- Fix to code dependency. [Neil Cook]
- Merge pull request #266 from njcuk9999/francois. [Neil Cook]

  Francois
- Update `cal_FF_RAW_spirou.py`. [Neil Cook]

  keep compatibility with H2RG version
- Update spirouLOCOR.py. [Neil Cook]

  keep compatibility with H2RG


0.2.013 (2018-04-30)
--------------------
- Update constant parameters for localization, flat-field and blaze.
  [FrancoisBouchy]
- Plot the central column threshold for `DRS_DEBUG=0`. [FrancoisBouchy]
- Add the plot of the central column with miny and maxy for `DRS_DEBUG=0`.
  [FrancoisBouchy]
- Plot values of e2ds>0 and values of blaze>1. [FrancoisBouchy]
- Force the curvature of orders in case of no detection.
  [FrancoisBouchy]
- Merge pull request #265 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #260 from njcuk9999/neil. [Neil Cook]

  manually adding francois changes


0.2.009 (2018-04-27)
--------------------
- Fix to issue #264 - spirouFLAT.MEasurEBlazeForOrder now requires p
  (for H2RG dependency) [Neil Cook]
- Fix to issue #264 - stop blaze setting zero or negative values to 1.
  [Neil Cook]
- Update? [Neil Cook]
- Issue #263 and Issue #262 - tilt borders added and mask for negative
  pixel added to all functions. [Neil Cook]
- Added function to extract valid order numbers from `constants_SPIROU`
  (via ParamDict) [Neil Cook]
- Added function to extract valid order numbers from `constants_SPIROU`
  (via ParamDict) [Neil Cook]
- Added function to extract valid order numbers from `constants_SPIROU`
  (via ParamDict) [Neil Cook]
- Addressing issues #225 and #226 - compatability with both H2RG and
  H4RG by adding "method" (switch between average and median), pep8
  fixes. [Neil Cook]
- Pep8 fixes and Issue #226 - compatibility with both H2RG and H4RG.
  [Neil Cook]
- Issue #263 - allowed tilt border to be changed in constants and first
  and last order to be selected. [Neil Cook]
- Issue #250 - average --> median and dependency with H2RG. [Neil Cook]
- Allowed valid orders to be changed in constants. [Neil Cook]
- Dealt with dependency of H2RG (Issue #266) and allowed valid orders to
  be changed in constants. [Neil Cook]
- Merge pull request #261 from njcuk9999/francois. [Neil Cook]

  Francois


0.2.010 (2018-04-27)
--------------------
- Update constant parameters for flat-field and blaze. [FrancoisBouchy]
- Modification of spirouPLot to Display all orders with correct NBFIB
  parameter. [FrancoisBouchy]
- Start extraction from order 4th in `cal_extract_RAW_spirou`.
  [FrancoisBouchy]
- Start extraction from order 4th in `cal_FF_RAW_spirou`. [FrancoisBouchy]
- Merge pull request #259 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.011 (2018-04-27)
--------------------
- Manually adding francois changes. [njcuk9999]
- Manually adding francois changes. [njcuk9999]
- Merge pull request #258 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #256 from njcuk9999/revert-254-francois. [Neil
  Cook]

  Revert "Francois"
- Revert "Francois" [Neil Cook]
- Merge pull request #255 from njcuk9999/revert-254-francois. [Neil
  Cook]

  Revert "Francois"
- Revert "Francois" [Neil Cook]
- Merge pull request #254 from njcuk9999/francois. [Neil Cook]

  update accepted.
- Update config.py. [Neil Cook]
- Update `visu_RAW_spirou.py`. [Neil Cook]

  call to plt should come via sPlt i.e.:
  instead of:
  python
  import matplotlib.pyplot as plt
  

  use

  python
  from SpirouDRS.spirouCore import sPlt
  plt = sPlt.plt
  

  This avoids all errors with matplotlib backends.
- Change. [njcuk9999]
- Change. [njcuk9999]
- Update vcs.xml. [Neil Cook]
- Cleaning up files. [njcuk9999]
- Removed cached files. [njcuk9999]
- Reset to master. [njcuk9999]


0.2.008 (2018-04-26)
--------------------
- Reset paths to defaults (shouldn't have overwritten) [Neil Cook]
- Merge pull request #249 from njcuk9999/francois. [Neil Cook]

  Francois
- Merge branch 'dev' into francois. [Neil Cook]
- Merge pull request #248 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #247 from njcuk9999/neil. [Neil Cook]

  Neil
- Add files via upload. [Neil Cook]

  Added francois files manually (via direct upload)
- Add files via upload. [Neil Cook]

  Added francois files via direct upload


0.2.007 (2018-04-25)
--------------------
- Fix to `cal_badpix` to allow use with H2RG (required bool mask for
  `bad_pixel_mask2)` [Neil Cook]
- Merge pull request #246 from njcuk9999/melissa. [Neil Cook]

  Melissa


0.2.0097 (2018-04-25)
---------------------
- `Cal_DARK`: increased decimals shown `constants_SPIROU_H4RG`: adjusted
  dark cut limit `spirou_PLOT`: added labels and titles to figures;
  changed histograms to normalised frequency `spirou_IMAGE.measure_dark`:
  changed histograms to density histograms, increased decimals.
  [melissa-hobson]
- Merge pull request #245 from njcuk9999/master. [melissa-hobson]

  update
- Merge pull request #244 from njcuk9999/neil. [Neil Cook]

  Neil
- Updated order of `cal_BADPIX_spirou` in the unit test functions. [Neil
  Cook]
- Fix for Issue #229 - added alias to `spirouImage.locate_bad_pixels_full`
  (LocateFullBadPixels) [Neil Cook]
- Code to un-resize and un-flip the image (for back processing files
  created by the DRS) [Neil Cook]
- Fix for Issue #229 - full flat detector image from engineering data
  (required for badpix fit) [Neil Cook]
- Fix for Issue #229 - wrote `locate_bad_pixel_full` to workout threshold
  from full flat engineering data. [Neil Cook]
- Fix for Issue #229 - added parameters to `constants_spirou` file. [Neil
  Cook]
- Fix for Issue #229 - added parameters to `constants_spirou` file. [Neil
  Cook]
- Fix to Issue #193 - try statement to import matplotlib and error
  output via WLOG (does not fix but catches exceptions) [Neil Cook]
- Fix for Issue #229 - added call to
  spirouImage.LocateFullBadPixels, plotted graph, added resizing
  and flipping the image to match other recipes. [Neil Cook]
- Merge pull request #243 from njcuk9999/master. [melissa-hobson]

  update branch
- Merge pull request #242 from njcuk9999/neil. [Neil Cook]

  Neil
- Re-built pdfs. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Updated version in readme. [Neil Cook]
- Added alias to `load_other_config_file` (LoadOtherConfig) - used in
  tools. [Neil Cook]
- Fixed bug in `__all__` statement. [Neil Cook]
- Update to style. [Neil Cook]
- New tool - drs documentation - doc functions useful for keeping the
  docs up-to-date. [Neil Cook]
- Added % comments to doc (in variables) - needed to know which are
  missing. [Neil Cook]
- Fix to suggestion in Issue #229 - changed argument order around to
  avoid confusion. [Neil Cook]
- Merge pull request #241 from njcuk9999/neil. [Neil Cook]

  Neil
- Changed plot colour to `"gist_gray`" and linetype to "red" to help ID
  fits better (pink on rainbow was bad) [Neil Cook]
- Updated preporecess for use with H2RG. [Neil Cook]
- Fix for issue #220 - added alias to InterpolateBadRegions (call to
  `spirouImage.interp_bad_regions)` [Neil Cook]
- Fix for issue #220 - added `interp_bad_regions` function and added doc
  strings for other new functions. [Neil Cook]
- Fix for issue #220 - added `bad_region` constants. [Neil Cook]
- Fix for issue #220 - added call to spirouImage.InterpolateBadRegions.
  [Neil Cook]
- Merge pull request #238 from njcuk9999/master. [Neil Cook]

  update to master


0.2.006 (2018-04-23)
--------------------
- Corrected order of inputs in `cal_BADPIX` main definition. [melissa-
  hobson]
- Merge pull request #240 from njcuk9999/master. [melissa-hobson]

  Update branch
- Merge pull request #239 from njcuk9999/dev. [Neil Cook]

  Merge pull request #237 from njcuk9999/master
- Merge pull request #237 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #236 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #234 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #233 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #217 from njcuk9999/master. [melissa-hobson]

  Update branch melissa from master
- Merge pull request #216 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #213 from njcuk9999/master. [melissa-hobson]

  Update branch from master
- Merge pull request #211 from njcuk9999/dev. [Neil Cook]

  Merge pull request #207 from njcuk9999/master
- Merge pull request #207 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #210 from njcuk9999/melissa. [Neil Cook]

  Merge pull request #206 from njcuk9999/master
- Merge pull request #206 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #209 from njcuk9999/neil. [Neil Cook]

  Neil


0.2.005 (2018-04-20)
--------------------

Fix
~~~
- Exit script should only ask to close graphs if we have plots (see
  `"has_plots`" keyword) [Neil Cook]

Other
~~~~~
- Fix for issue #235 - added TODO to remove from `cal_DARK` eventually.
  [Neil Cook]
- Fix for issue #235 changed BADPIX to `BADPIX_OLD` for calibDB key. [Neil
  Cook]
- Added the `has_plots=False` to exit script. [Neil Cook]
- Fix to issue #176 (unfinished) - avoids the importing of `cal_HC` in
  unit tests running the code (currently doesn't have .main() for ease
  of debugging) [Neil Cook]
- Fix to issue #212 - `night_name` now is allowed a backslash at the end
  and now gives error if incorrectly defined (before wasn't checked
  specifically) fix to issue regarding type of custom argument (was
  incorrect - big bug fixed - customarg recipes will now be able to run
  again) [Neil Cook]
- Updated date and versions. [Neil Cook]
- Fix for issue #218 - threshold in `find_order_centers` should be in
  constnats file - also updated documentation with new constant. [Neil
  Cook]
- Issue #219 - Added PP function aliases to spirouImage (called in
  `cal_preprocess_spirou)` [Neil Cook]
- Issue #219 - pre-processing add Etienne's code to recipe- added
  functions `"ref_top_bottom`", `"median_filter_dark_amp`",
  `"median_one_over_f_noise`" [Neil Cook]
- Issue #219 - pre-processing add Etienne's code to recipe. [Neil Cook]
- Issue #219 - Add Etiennes pre-processing code to recipe. [Neil Cook]


0.2.004 (2018-04-19)
--------------------
- Fix to handling of custom arguments to accept only a list of
  filenames. [Neil Cook]
- New way to handle files (with wildcards built in) [Neil Cook]
- Dealing with Issue #219 - pre-processing - unfinished. [Neil Cook]


0.2.003 (2018-04-18)
--------------------
- Fix to Issue #215 - spirouImage.WriteImage do not use dtype='float64'
  [Neil Cook]
- Fix to Issue #215 - spirouImage.WriteImage do not use dtype='float64'
  [Neil Cook]


0.2.001 (2018-04-17)
--------------------
- Continuation of Issue #176 - writing `cal_HC` - very stuck on replacing
  fitgaus.fitgaus. [Neil Cook]
- Fix for Issue #183 - now checks module and version. [Neil Cook]
- Merge pull request #208 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #205 from njcuk9999/neil. [Neil Cook]

  Neil
- Change to doc logo size. [Neil Cook]
- Change to doc logo size. [Neil Cook]
- Edit - test version needed main. [Neil Cook]
- Merge pull request #204 from njcuk9999/dev. [Neil Cook]

  Merge pull request #201 from njcuk9999/master
- Merge pull request #201 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #203 from njcuk9999/melissa. [Neil Cook]

  Merge pull request #202 from njcuk9999/master
- Merge pull request #202 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #200 from njcuk9999/neil. [Neil Cook]

  Neil
- Updated documentation and added example custom configs to config
  folder. [Neil Cook]
- Issue # 193 - matplotlib dependency. [Neil Cook]
- Merge pull request #199 from njcuk9999/master. [Neil Cook]

  merge
- Merge pull request #197 from njcuk9999/neil. [Neil Cook]

  Neil
- Issue # 194 - Fix to python version string parsing failing if format
  isn't as expected. [Neil Cook]
- Merge pull request #196 from njcuk9999/import-fixes. [Neil Cook]

  Import fixes
- Update spirouPlot.py. [Neil Cook]

  added `__test_smoothed_boxmean_image` temporarily to spirouPlot.py
- Update spirouLOCOR.py. [Neil Cook]

  remove `__test_smoothed_boxmean_image` from here (isn't needed)
- Update spirouPlot.py. [Neil Cook]


0.2.002 (2018-04-17)
--------------------
- Copied the matplotlib backend fix into spirouLOCOR.py. [Chris Usher]
- Only import IPython when it will be used. [Chris Usher]
- Prevent failed import for missing matplotlib backends. [Chris Usher]
- Merge pull request #192 from njcuk9999/revert-191-melissa. [Neil Cook]

  Revert "Melissa"
- Revert "Melissa" [Neil Cook]
- Merge pull request #191 from njcuk9999/melissa. [Neil Cook]

  Melissa - updated to master
- Merge branch 'master' into melissa. [Neil Cook]
- Merge pull request #190 from njcuk9999/isabelle. [Neil Cook]

  Merge pull request #188 from njcuk9999/master
- Merge pull request #188 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #189 from njcuk9999/francois. [Neil Cook]

  Merge pull request #187 from njcuk9999/master
- Merge pull request #187 from njcuk9999/master. [Neil Cook]

  update to master
- Merge pull request #182 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #181 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #180 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #179 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #178 from njcuk9999/neil. [Neil Cook]

  Merge pull request #177 from njcuk9999/master
- Preprocessing script (currently does rotation only) [melissa-hobson]


0.1.037 (2018-04-16)
--------------------
- Spirou tools addition - compare two files (plot images and diff in a
  user-friendly manner) [Neil Cook]
- Issue #176 - continued development of `find_lines`. [Neil Cook]
- Issue #176 - Added FirstGuessSolution alias to init. [Neil Cook]
- Issue #176 - continued to build `cal_HC_E2DS`. [Neil Cook]
- Fix for bug introduced in last build - `night_name` now set in
  `arg_file_names`. [Neil Cook]
- Merge from Melissa - H4RG `constants_SPIROU` file (values set from
  Melissa) [Neil Cook]
- Merge from Melissa - update `constants_SPIROU_H2RG` with pep8 styling.
  [Neil Cook]
- Merge from Melissa - switch between constants in H2RG and H4RG now
  `constants_SPIROU.py` is different for both. [Neil Cook]
- Merge from Melissa - pre-processing script for H4RG images (currently
  only rotation) [Neil Cook]


0.1.036 (2018-04-13)
--------------------
- Issue #176 - Added catalogue line lists to SpirouDRS data folder.
  [Neil Cook]
- Issue 176 - continued update of `first_guess_solution` (unfinished),
  added `find_lines` function (unfinished), added `fit_emi_line`
  (unfinished) [Neil Cook]
- Fit gaussian moved to spirouCore.spirouMath. [Neil Cook]
- Read table modified to display numbe rof columns on error. [Neil Cook]
- Issue #176 - read line list function modified. [Neil Cook]
- Added overwrite to hdu.writeto function in spirouFits.writeimage
  function. [Neil Cook]
- Issue #176 - alias for ReadLineList. [Neil Cook]
- Moved fit gaussian to spirouMath. [Neil Cook]
- Issue #185 and #186 - `kw_ACQTIME_KEY` and `kw_ACQTIME_KEY_UNIX` are
  different between H2RG and H4RG. [Neil Cook]
- Issue #185 and #186 - `DATE_FMT_HEADER` now requires p to function.
  [Neil Cook]
- Issue #185 and #186 - `DATE_FMT_HEADER` now requires p to function.
  [Neil Cook]
- Issue #186 - added `"ic_image_type`", Issue #176 - modified `ic_lamp`
  types. [Neil Cook]
- Issue #186 - modified `DRS_UCONFIG` for H2RG/H4RG configs. [Neil Cook]
- Issue #176 - modified to allow running without function (temporarily)
  [Neil Cook]


0.1.035 (2018-04-12)
--------------------
- Issue #176 - added `get_lamp_parameters`, `fiirst_guess_at_wave_soltuion`
  (unfinished), and `decide_on_lamp_type` functions. [Neil Cook]
- Issue #176 - added GetLampParams alias. [Neil Cook]
- Issue #176 - renamed `cdata_folder`. [Neil Cook]
- Issue #176 - created a `read_line_list` function (unfinished) [Neil
  Cook]
- Issue #176 - modified GetFile call (with required key) [Neil Cook]
- Issue #176 - added `correct_flat` function. [Neil Cook]
- Issue #176 - added CorrectFlat. [Neil Cook]
- Issue #176 - renamed cdata folder - make it more clear it is a
  relative path. [Neil Cook]
- Issue #176 - modifications to `get_file_name`. [Neil Cook]
- Issue #176 - added some `cal_HC` params. [Neil Cook]
- Issue #176 - added fiber getting, application of flat and start of
  first guess at solution. [Neil Cook]
- Update to version ready for new alpha release 0.1.035. [Neil Cook]
- Update to version ready for new alpha release 0.1.035. [Neil Cook]
- Update to version ready for new alpha release 0.1.035. [Neil Cook]
- Update to version ready for new alpha release 0.1.035. [Neil Cook]
- Update to version ready for new alpha release 0.1.035. [Neil Cook]


0.1.0349 (2018-04-11)
---------------------
- Added unit test for `cal_HC_E2DS_spirou`. [Neil Cook]
- Added hcone extraction to unit test. [Neil Cook]
- Replacement of rawfile with `p['ARG_FILE_DIR']` [Neil Cook]
- Replacement of rawfile with `p['ARG_FILE_DIR']` [Neil Cook]
- Place holder function for flat correction. [Neil Cook]
- Replacement of rawfile with `p['ARG_FILE_DIR']` [Neil Cook]
- Replacement of rawfile with `p['ARG_FILE_DIR']` [Neil Cook]
- Fix to issue #176 - in progress - updating `cal_HC_E2DS`. [Neil Cook]


0.1.0348 (2018-04-09)
---------------------
- Fix to issue #152 - User/Custom `config.py` file - rebuilt pdfs. [Neil
  Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file - rebuilt pdfs. [Neil
  Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file - updated
  documentation. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Fix to issue #152 - User/Custom `config.py` file. [Neil Cook]
- Merge pull request #177 from njcuk9999/master. [Neil Cook]

  merge with master
- Merge pull request #175 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #172 from njcuk9999/neil. [Neil Cook]

  Neil
- Merge pull request #153 from njcuk9999/francois. [Neil Cook]

  Merge pull request #151 from njcuk9999/dev
- Merge pull request #151 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #150 from njcuk9999/dev. [Neil Cook]

  same?
- Merge pull request #149 from njcuk9999/dev. [Neil Cook]

  removed new constant (test)


0.1.0346 (2018-04-06)
---------------------
- Fix to issue #173 - Need a versioned text file. [Neil Cook]
- Fix to issue #174 - License required. [Neil Cook]
- Fixed call to python (was python3 now python) [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #170 - PYTHONPATH in installation - what happens if not
  defined? [Neil Cook]
- Fix issue #165 - `cal_extract` plotting issue with bounding edges. [Neil
  Cook]
- Fix issue #163 - `cal_ff` plot fit edges error. [Neil Cook]
- Fix issue #161 - `cal_SLIT` plot wrong offse - offset is now corrected.
  [Neil Cook]
- Fixed plots closing automatically in an interactive session --> now
  user is asked. [Neil Cook]
- Fix to issue #159 - updated fix giving several allowed backends. [Neil
  Cook]
- Fix to issue #159 - matplotlib plots freeze on macOSX. [Neil Cook]


0.1.0344 (2018-04-05)
---------------------
- Fixed typo in call to `deal_with+prefixes` (requires filename if p not
  defined) and fixed `__NAME__` [Neil Cook]
- Removed call to calibDB (note needed) [Neil Cook]
- Added quick mention of startswith, contains and endswith method to
  documentation. [Neil Cook]
- Added contains and endswith methods to ParamDict. [Neil Cook]
- Moved blank recipe to spirouTools. [Neil Cook]
- Wrote some generic tools: list raw/reduced/calib files (with filter),
  display calibDB (with date filter) [Neil Cook]
- DRS reset moved to spirouTools. [Neil Cook]
- Dependencies corrected and moved to SpirouTools. [Neil Cook]
- Moved tools to separate package. [Neil Cook]
- Updated change log with changes to calibdb. [Neil Cook]
- Added quiet modes for `run_begin` and `load_arguments`. [Neil Cook]
- CalibDB now also contains humantime and unixtime accessible from
  dictionary call. [Neil Cook]
- Updated module descriptions (based on changes) [Neil Cook]
- Fix of issue #156 - Parameter dictionary source dictionary not case
  insensitive. [Neil Cook]
- Fix of issue #162 - `cal_SLIT` save TILT to file using Add1Dlist -
  slight change. [Neil Cook]
- Fix of issue #162 - `cal_SLIT` save TILT to file using Add1Dlist. [Neil
  Cook]
- Fix of issue #171 - fixed `cal_validate_spirou` -->
  `cal_validate_spirou.py`. [Neil Cook]
- Fix of issue #168 - Documentation: chapter installation weird <PATH>
  variable #168. [Neil Cook]
- Fix of issue #166 - `cal_DRIFTPEAK` should accept hc or fp. [Neil Cook]
- Fix of issue #164 - `cal_extract` kind is incorrect. [Neil Cook]
- Fix of issue #160 - too many decimal places in quality control -
  fixed. [Neil Cook]
- Fix of issue #157 (Unix time doesn't match human time for UT) bug was
  only in "fake" wave solution files. [Neil Cook]
- Fixed Issue #154 (Installation type update to config.txt and
  `constants_SPIROU.txt` (now `.py` files) [Neil Cook]
- Same? [Neil Cook]


0.1.0342 (2018-03-28)
---------------------
- Removed new constant (test) [Neil Cook]
- Merge pull request #147 from njcuk9999/dev. [Neil Cook]

  added new constant
- Added new constant. [Neil Cook]
- Merge pull request #146 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #145 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #144 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #143 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #142 from njcuk9999/dev. [Neil Cook]

  Dev


0.1.034 (2018-03-25)
--------------------
- New unit test (not comp full run) [Neil Cook]
- Updated date and version. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added new test full run no compare. [Neil Cook]


0.1.033 (2018-03-22)
--------------------
- New example 7. [Neil Cook]
- New example 6. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated versions and dates. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Moved examples to subfolder. [Neil Cook]
- Spelling check. [Neil Cook]
- Spelling check. [Neil Cook]
- Spelling check. [Neil Cook]
- Spelling check. [Neil Cook]
- Updates to comments. [Neil Cook]
- Spelling check. [Neil Cook]
- Fixed error in call. [Neil Cook]
- Updates to comments. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Update date and versions. [Neil Cook]
- Spell check. [Neil Cook]
- Spell check. [Neil Cook]
- Spell check. [Neil Cook]
- Spell check. [Neil Cook]
- Spell check. [Neil Cook]
- Page split. [Neil Cook]
- Added parameters to record file. [Neil Cook]
- Added `return_filename` for added functionality. [Neil Cook]
- Improvements to telluric file - added header keys. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated edit date and versions. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]


0.1.032 (2018-03-19)
--------------------
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Corrected spelling. [Neil Cook]
- Merge pull request #141 from njcuk9999/dev. [Neil Cook]

  Dev
- Examples 5 convert to html. [Neil Cook]
- First commit - common python 3 functions different from old python 2.
  [Neil Cook]
- Merge pull request #140 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #139 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #138 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #137 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #136 from njcuk9999/dev. [Neil Cook]

  Dev


0.1.031 (2018-03-14)
--------------------
- Updated image size. [Neil Cook]
- Update readme. [Neil Cook]


0.1.030 (2018-03-13)
--------------------
- Conversion to html. [Neil Cook]
- First commit - using custom arguments. [Neil Cook]
- Update date and version. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated docs for GetCustomFromRuntime function. [Neil Cook]
- Added spacer. [Neil Cook]
- Reformatted customargs (to be like `cal_CCF)` for consistency. [Neil
  Cook]
- Example3 in html format. [Neil Cook]
- First commit - the debugger. [Neil Cook]
- Rerun code. [Neil Cook]


0.1.029 (2018-03-07)
--------------------
- Ipython notebooks converted to html. [Neil Cook]
- First commit: ipython notebook example: "What is a parameter
  dictionary?" [Neil Cook]
- First commit ipython notebook example1: "Calling recipes from python"
  [Neil Cook]
- Added blank template file. [Neil Cook]
- Updated date and version. [Neil Cook]
- Modified `read_config_file` to be able to return just filename. [Neil
  Cook]
- Rebuilt pdfs. [Neil Cook]
- Set `config_file` name so sources are correct. [Neil Cook]
- Updated date and version. [Neil Cook]
- Set debug to 0. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]
- Updated exit message. [Neil Cook]


0.1.028 (2018-03-06)
--------------------
- Added note about using texteidter and smart speechmarks. [Neil Cook]
- Fixed importing issues. [Neil Cook]
- Fixed importing issues. [Neil Cook]
- Fixed importing issues. [Neil Cook]
- Fixed importing issues. [Neil Cook]
- Updated date and version. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated dependencies. [Neil Cook]
- Added a test of text file having bad (illegal) characters (non
  letters, punctuation, whitespace, digits) as defined by python string
  module. [Neil Cook]
- Added `.bash_profile` for mac install. [Neil Cook]
- Added `.bash_profile` for mac install. [Neil Cook]
- Test of bad characters. [Neil Cook]
- Added a run time debug option and reformatted logging. [Neil Cook]
- Merge remote-tracking branch 'origin/master' [Neil Cook]
- Merge pull request #135 from njcuk9999/dev. [Neil Cook]

  Merge pull request #134 from njcuk9999/master
- Merge pull request #134 from njcuk9999/master. [Neil Cook]

  sync
- Merge pull request #133 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #132 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #131 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #130 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #129 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #128 from njcuk9999/dev. [Neil Cook]

  pep8 fixes + suppress known-required exceptions
- Merge pull request #127 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #126 from njcuk9999/dev. [Neil Cook]

  Dev - confirm docs built and code runs
- Merge pull request #125 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #124 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #123 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #122 from njcuk9999/dev. [Neil Cook]

  major changes to code
- Merge pull request #121 from njcuk9999/dev. [Neil Cook]

  Dev
- Updated unit test - py2 error is valueerror not importerror. [Neil
  Cook]
- Updated unit test - py2 error is valueerror not importerror. [Neil
  Cook]
- Updated unit test - py2 error is valueerror not importerror. [Neil
  Cook]
- Updated unit test - py2 error is valueerror not importerror. [Neil
  Cook]


0.1.027 (2018-03-01)
--------------------
- Rebuilt pdfs. [Neil Cook]
- Updated tabbing in TOC. [Neil Cook]
- Updated versions and dates. [Neil Cook]
- Modified `initial_file_setup` to include a "contains" keyword, to make
  sure all files `(arg_file_names)` contain this substring if contains is
  not None. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added description. [Neil Cook]
- Added chagnes to `initial_file_steup`. [Neil Cook]
- Added placeholder sections and added setup and exit sections. [Neil
  Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Modified recipe description. [Neil Cook]
- Updated pep8 fixes + added sys info. [Neil Cook]
- Updated `display_title` and `display_system_info` doc strings. [Neil Cook]
- Added DisplayTitle and DisplaySysInfo aliases in `__init__` [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated dependencies with python versions. [Neil Cook]
- Added DisplayTitle and DisplaySysInfo to spirouStartup public
  functions. [Neil Cook]
- Twaeked import. [Neil Cook]


0.1.026 (2018-02-27)
--------------------
- Changed printing in function + added warning that user will reset all
  processed files. [Neil Cook]
- Changed printing in function. [Neil Cook]
- Changed `display_title` function. [Neil Cook]
- Modified printlog function and added printcolour function. [Neil Cook]
- Added printlog and printcolour aliases. [Neil Cook]
- Added dependencies and updated latest versions of py modules. [Neil
  Cook]
- Added printlog and printcolour functions. [Neil Cook]
- Tweaked display title. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Fixed bug: `set_souce` -> `set_source`. [Neil Cook]
- Updated date and version. [Neil Cook]
- Minor text change. [Neil Cook]
- Corrected `cal_loc` example and call. [Neil Cook]
- Update date and version. [Neil Cook]
- Add `get_folder_name` function and fix file name of comparison results
  file (name it by input program) [Neil Cook]
- Update test comparison dir. [Neil Cook]
- Update test comparison dir. [Neil Cook]
- Same? [Neil Cook]
- First commit - get dependencies for the drs (and current versions)
  [Neil Cook]
- Added source to `arg_file_names`, nbframes and fitsfilename. [Neil Cook]
- Corrected BIG bug (NBframes not redefined when `arg_file_names`
  redefined) [Neil Cook]
- Corrected error statement (format missing) [Neil Cook]
- Support astropy < 2.0.1 bug in astro.io.fits hdu.scale (this fixes it)
  [Neil Cook]
- Updated plot imshow should not take True and False array (convert to
  ints) [Neil Cook]
- Removed use of tqdm (unnecessary dependency) [Neil Cook]
- Added new page preak for TOC. [Neil Cook]
- Example - slight change to format. [Neil Cook]


0.1.025 (2018-02-26)
--------------------
- Small fixes to refix pep8 across module/suppressing known and required
  pep8 exceptions. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes + doc strings. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated date and version. [Neil Cook]
- Added summary of properties and graphs section. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]
- Pep8 fixes. [Neil Cook]


0.1.024 (2018-02-23)
--------------------
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Cal ccf figure 3. [Neil Cook]
- Cal ccf figure 2. [Neil Cook]
- Cal ccf figure 1. [Neil Cook]
- First commit of cal ccf recipe doc (unfinished) [Neil Cook]
- Updated reffile to e2ds file. [Neil Cook]
- Updated date and version. [Neil Cook]
- First commit - new faster version of telluric mask generation - using
  polyderivatives. [Neil Cook]
- Updated telluric 2d mask. [Neil Cook]
- Updated date and version. [Neil Cook]
- Added ccf filenames to variables. [Neil Cook]
- Added calccf recipe to inputs. [Neil Cook]
- Changed reffile to e2dsfile. [Neil Cook]
- Take some things out loop to speed up. [Neil Cook]
- Fixes to tilt above and below central fit (untested) [Neil Cook]
- Moved setting of fitsfilename and `arg_file_names` (when files is not
  None) to a separate function to deal with run time vs call. [Neil
  Cook]
- Moved some constants outside a loop. [Neil Cook]
- Added cal driftpeak figure. [Neil Cook]
- Added cal driftpeak figure. [Neil Cook]
- Added cal driftpeak figure. [Neil Cook]
- Added cal driftpeak figure. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated the versions and date. [Neil Cook]
- Updated the versions and date. [Neil Cook]
- Updated examples and interactive mode figures. [Neil Cook]


0.1.023 (2018-02-21)
--------------------
- Cal drift raw plot files for docs. [Neil Cook]
- Cal drift raw plot files for docs. [Neil Cook]
- Cal drift e2ds plot files for docs. [Neil Cook]
- Cal drift e2ds plot files for docs. [Neil Cook]
- First commit - cal drift recipe (unfinished) [Neil Cook]
- Updated quick todo list. [Neil Cook]
- Moved the `arg_file_name/fitsfilename` setting when we have custom args
  to after we read from runtime. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Added drift filenames. [Neil Cook]
- Updated todo list. [Neil Cook]
- Input the caldrift section. [Neil Cook]
- Fix for loadcalibdb. [Neil Cook]
- Fix for loadcalibdb. [Neil Cook]


0.1.022 (2018-02-20)
--------------------
- Major changes to code. [Neil Cook]


0.1.021 (2018-02-19)
--------------------
- Rebuilt pdfs. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added extract figure. [Neil Cook]
- Added extract figure. [Neil Cook]
- Added extract figure. [Neil Cook]
- First commit of verify recipe section. [Neil Cook]
- First commit of extract recipe section. [Neil Cook]
- Added ReadBlazeFile. [Neil Cook]
- Updated doc strings and minor code fixes (for no header in writeimage)
  [Neil Cook]
- Updated date and versions. [Neil Cook]
- Added function to convert waveimage to interpretted spectrum. [Neil
  Cook]
- Updated date and version. [Neil Cook]
- Added extract file variables. [Neil Cook]
- Changed order + added input for extract and validate. [Neil Cook]
- Changes to example code run. [Neil Cook]
- Changes to example code run. [Neil Cook]
- Fixed cmdbox typo. [Neil Cook]
- Changed some doc strings. [Neil Cook]
- Changed comment. [Neil Cook]


0.1.020 (2018-02-16)
--------------------
- Update README.md. [Neil Cook]
- Merge pull request #120 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed tested and all run
- Rebuilt pdfs. [Neil Cook]
- Added current default files (for reset) [Neil Cook]
- First commit - a reset switch - setting DRS back to default. [Neil
  Cook]
- Added mainfitsdir for when we are using custom arguments, resorted
  functions, added `get_custom_arg_files_fitsfilename` to deal with
  setting `arg_file_names` and fitsfilename with custom arguments. [Neil
  Cook]
- Fixed problem with plot `(wave_ll` only for CCF - so use x instead)
  normally want "wave" [Neil Cook]
- Moved `log_file_name` getting to constants file. [Neil Cook]
- Added `log_file_name` to constants. [Neil Cook]
- Fixed bug for `arg_file_names` from custom args. [Neil Cook]
- Updated doc string. [Neil Cook]
- Added mainfitsdir for custom loadarguments. [Neil Cook]
- Merge pull request #119 from njcuk9999/dev. [Neil Cook]

  Dev
- Rebuilt pdf. [Neil Cook]
- Readded `cal_slit` plots for interactive sessions (accidentally
  overwritten) [Neil Cook]
- Readded `cal_FF_raw` plots for interactive sessions. [Neil Cook]
- Added `cal_FF_raw` plots for interactive sessions. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added `cal_FF_raw` file definitions. [Neil Cook]
- Updated `cal_FF_raw` change log. [Neil Cook]
- Fixed errors in default recipe. [Neil Cook]
- Added paths for example files, fixed example run. [Neil Cook]
- Added paths for example files. [Neil Cook]
- Added all sections (previously empty) [Neil Cook]
- Added paths for example files. [Neil Cook]
- Added path for example file. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated date and version. [Neil Cook]
- Replace use of `log_opt` (not valid in `load_arguments)` with DPROG
  (Defaults to sys.argv[0]) [Neil Cook]
- Renamed GetKwValues to GetKeywordValues. [Neil Cook]
- Renamed GetKwValues to GetKeywordValues. [Neil Cook]
- Renamed GetKwValues to GetKeywordValues. [Neil Cook]
- Added blaze to calibDB. [Neil Cook]
- Merge pull request #118 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #117 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #116 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #115 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #114 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed untested
- Merge pull request #113 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed docs only and docs build
- Merge pull request #112 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #111 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #110 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #109 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #108 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #107 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #106 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #105 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #104 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #103 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #102 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #101 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #100 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #99 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #98 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #97 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #96 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #95 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #94 from njcuk9999/dev. [Neil Cook]

  added test data link
- Merge pull request #93 from njcuk9999/dev. [Neil Cook]

  link to logo change


0.1.019 (2018-02-15)
--------------------
- Corrected need for mainfitsfile to define `arg_file_names` and
  fitsfilename. [Neil Cook]
- Corrected doc string typo. [Neil Cook]
- Added `return_header/return_shape` options to readdata function,
  corrected readrawdata function. [Neil Cook]
- First commit of telluric mask file (currently a pseudo-recipe) [Neil
  Cook]
- Updated doc strings. [Neil Cook]
- Changed typo and updated some doc strings. [Neil Cook]
- Fixed needing mainfitsfile for custom files. [Neil Cook]
- Fixed needing mainfitsfile for custom files. [Neil Cook]
- Updated edit date and version. [Neil Cook]
- Updated edit date and version. [Neil Cook]
- Added calff. [Neil Cook]
- First commit - blank `cal_ff` recipe. [Neil Cook]
- Added package descriptions (from CTAN) [Neil Cook]
- Updated keys (missed `order_profile)` [Neil Cook]


0.1.018 (2018-02-14)
--------------------
- `Cal_slit` graphs. [Neil Cook]
- `Cal_slit` graphs. [Neil Cook]
- `Cal_slit` graphs. [Neil Cook]
- First commit - recipe for `cal_slit_spirou`. [Neil Cook]
- Added labels to slit plot (were missed before) [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and version info. [Neil Cook]
- Updated date and version info. [Neil Cook]
- Commented TOC separator (may use later to clean up) [Neil Cook]
- Removed TOC separator. [Neil Cook]
- Removed use of caption in favour of capt-of (screwdriver vs hammer)
  [Neil Cook]
- Added some named labels, fixed typo namdlabels --> namedlabels. [Neil
  Cook]
- Added calslit include. [Neil Cook]
- Added labels to sections. [Neil Cook]
- Corrected errors in windows sections (ref links) [Neil Cook]
- Addede Interactive mode section. [Neil Cook]
- Fixed program call typo and ref to \calDARK. [Neil Cook]
- Fixed subsection title and some paths. [Neil Cook]


0.1.017 (2018-02-13)
--------------------
- Cal loc figures. [Neil Cook]
- Windows environment figures. [Neil Cook]
- Display system info, moved header bar to a constant. [Neil Cook]
- Modified logger to accept printonly and logonly inputs. [Neil Cook]
- Updated version and date. [Neil Cook]
- Changed the windows installation section. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Modified end of code section to reflect changes. [Neil Cook]
- Modified doc string for logger. [Neil Cook]
- Updated shebang, added `exit_script` dealing with interactive sessions
  in `__main__` call. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]
- Updated shebang and `__main__` exiting. [Neil Cook]


0.1.016 (2018-02-12)
--------------------
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Updated date and versions. [Neil Cook]
- Fix for only one file name in `readimage_and_combine`. [Neil Cook]
- Changed rawfits to orderpfile (name change) [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Change back to doc class comment. [Neil Cook]
- Change to doc class? [Neil Cook]
- Made cmdboxprintspecial breakable. [Neil Cook]
- Added some named labels and some new file names. [Neil Cook]
- Input calloc. [Neil Cook]
- Edited receipe. [Neil Cook]
- Edited receipe. [Neil Cook]
- Edited receipe. [Neil Cook]
- Edited receipe. [Neil Cook]


0.1.015 (2018-02-09)
--------------------
- Rebuilt pdfs. [Neil Cook]
- Moved calibration database loading to separate function (for custom
  arg recipes), tweaked functions accordingly, added getting of multi
  arguments (as last param) + wrapper around `get_file` `(get_files)` [Neil
  Cook]
- Added new aliases. [Neil Cook]
- Tweaked `readimage_and_combine` and `math_controller` to be more generic.
  [Neil Cook]
- Removed Config Error from messages (shouldn't be an error unless
  error=error) [Neil Cook]
- Added to custom arg section + added setup summary. [Neil Cook]
- Added/edited section. [Neil Cook]
- Rewrote section. [Neil Cook]
- Edited/updated doc strings. [Neil Cook]
- Edited/updated doc strings. [Neil Cook]
- Designed basic layout (setup + sections) [Neil Cook]
- Updated ghost template. [Neil Cook]
- Added loading of calibDB. [Neil Cook]
- Update date and version numbers. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated TILT and WAVE fixes (with todo) [Neil Cook]
- Updated todolist. [Neil Cook]
- Added indents to minipages, added alias/internal function definition.
  [Neil Cook]
- Added titles to some code boxes. [Neil Cook]
- Added titles to some code boxes. [Neil Cook]
- Added titels to some code boxes, changes paths for print outputs.
  [Neil Cook]
- Added some new packages to dependencies, added that custom args can be
  added to code boxes. [Neil Cook]
- Added recipe and module reference sections and some titles for calibDB
  text file examples. [Neil Cook]
- Changed a bashbox to a cmdbox. [Neil Cook]
- Added example of addition to calibration database. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]
- Updated indentation of minipages. [Neil Cook]


0.1.014 (2018-02-07)
--------------------
- First commit - move recipe to individual file. [Neil Cook]
- First commit - move recipe to individual file. [Neil Cook]
- First commit - move recipe to individual file. [Neil Cook]
- First commit - move recipe to individual file. [Neil Cook]
- First commit - move recipe to individual file. [Neil Cook]
- Updated date and version. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated the highlight parameters for doc string. [Neil Cook]
- Moved individual recipes to indivudal files. [Neil Cook]


0.1.013 (2018-02-06)
--------------------
- First commit module description for thorca. [Neil Cook]
- First commit module description for startup. [Neil Cook]
- Updated doc strings with p and loc descriptions. [Neil Cook]
- Updated doc strings with p and loc descriptions. [Neil Cook]
- Updated doc strings with p and loc descriptions. [Neil Cook]
- Updated wave to `wave_ll`. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Added startup and THORCA. [Neil Cook]
- Added doc strings to RV tex file. [Neil Cook]
- Changed wave to `wave_ll` in loc. [Neil Cook]


0.1.012 (2018-02-05)
--------------------
- Added spirouRV and spirouTHORCA imports to init. [Neil Cook]
- Started updating doc strings (p and loc) [unfinished] [Neil Cook]
- Started updating doc strings (p and loc) [unfinished] [Neil Cook]
- Updated date and version. [Neil Cook]
- Started module writing (incomplete) [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Added inputs. [Neil Cook]
- Updated imports. [Neil Cook]
- Removed unneeded comment for alias. [Neil Cook]
- Modified some doc strings. [Neil Cook]
- Refactored "imageLocSuperimp" --> "ImageLocSuperimp" [Neil Cook]
- Modified comments for several functions (more concise) [Neil Cook]
- Modified `doc_string` for writeimage. [Neil Cook]
- Modified `doc_string` for warninglogger. [Neil Cook]
- Added to `__all__` [Neil Cook]
- Modified `get_keywords` `doc_string`. [Neil Cook]
- Added doc strings for ConfigError methods. [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- First commit - added doc strings + sub-module func descriptions (based
  on spirouBLANK.tex) [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Changed subsection and section size in nav bar menu. [Neil Cook]
- Added spirouCore and spirouFLAT to constants , modified paths for
  WLOG, ParamDict and ConfigError (to module file) [Neil Cook]
- Added blue to the special cmd colours. [Neil Cook]
- Added introduction. [Neil Cook]
- Added doc strings. [Neil Cook]
- Changed default module tex file template. [Neil Cook]
- Refactor imageLocSuperimp --> ImageLocSuperimp. [Neil Cook]


0.1.011 (2018-02-02)
--------------------
- First commit - module tex file. [Neil Cook]
- First commit - module tex file. [Neil Cook]
- First commit - module tex file. [Neil Cook]
- First commit - module tex file. [Neil Cook]
- Edited doc string. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Changed size of subsubsection. [Neil Cook]
- Added new package. [Neil Cook]
- Added docstring tcbox. [Neil Cook]
- Changing format input module tex files. [Neil Cook]
- Updated doc strings with parameter dictionary descriptions. [Neil
  Cook]
- Updated doc strings with parameter dictionary descriptions. [Neil
  Cook]
- Updated date and version. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Updated latest edit and version. [Neil Cook]
- Updated some constants descriptions. [Neil Cook]


0.1.010 (2018-02-01)
--------------------
- Updated doc strings with parameter dictionary descriptions. [Neil
  Cook]
- Updated doc strings with parameter dictionary descriptions. [Neil
  Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated date and version. [Neil Cook]
- Add res to loc (for `debug_locplot_fit_residual)` [Neil Cook]
- Update doc string (p and loc) [Neil Cook]
- Update doc string (p and loc) [Neil Cook]
- Update doc string (p and loc) [Neil Cook]
- Updated doc strings. [Neil Cook]
- Update doc string (p and loc) [Neil Cook]


0.1.009 (2018-01-31)
--------------------
- Updated doc strings. [Neil Cook]
- Updated doc strings. [Neil Cook]
- Updated doc strings. [Neil Cook]
- Removed doc strings + added `__all__` functions. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Removed doc strings. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Updated date and version. [Neil Cook]
- Updated todo list. [Neil Cook]
- Cosmetic change to comment. [Neil Cook]


0.1.008 (2018-01-30)
--------------------
- Added spacing. [Neil Cook]
- Edit of doc string (unfinished) [Neil Cook]
- Create `DEFAULT_LOG_OPT()` from sys.argv[0] [Neil Cook]
- Replace sys.argv[0] in logs with
  `spirouConfig.Constant.DEFAULT_LOG_OPT()` [Neil Cook]
- Added doc strings, moved gaussian function and added some error
  handling. [Neil Cook]
- Moved gaussian function here. [Neil Cook]
- Added doc strings. [Neil Cook]
- Added doc strings. [Neil Cook]
- Corrected error `"mean_background`" --> `"mean_backgrd`" [Neil Cook]
- Updated back to my data folder. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Updated version. [Neil Cook]
- Updated `doc_strings` and error handling. [Neil Cook]
- Updated `doc_strings` and error handling. [Neil Cook]
- Updated `doc_strings`. [Neil Cook]
- Updated version and date. [Neil Cook]
- Updated version and date. [Neil Cook]
- Added `badpix_norm_percentile` constant constant. [Neil Cook]
- Added `badpix_norm_percentile` constant constant. [Neil Cook]


0.1.007 (2018-01-29)
--------------------
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Updated versions + dates. [Neil Cook]
- Updated versions + dates. [Neil Cook]
- Updated versions + dates. [Neil Cook]
- Doc strings and error handling (unfinished) [Neil Cook]
- Doc strings and error handling (unfinished) [Neil Cook]
- Doc strings and error handling. [Neil Cook]
- Updated doc strings [unfinished] [Neil Cook]


0.1.006 (2018-01-26)
--------------------
- Added test help file - for `cal_DARK_spirou`. [Neil Cook]
- Updated todo list with help files that are needed. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc string. [Neil Cook]
- Update doc strings + help file management. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc strings, remove `__main__` [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc strings. [Neil Cook]
- Update doc. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Update todo list with man files need writing. [Neil Cook]
- Modified MANUAL FILE (corrected) [Neil Cook]
- Updated date and version. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Updated the date and version numbers. [Neil Cook]
- Added/corrected some cal drift variables. [Neil Cook]
- Added descriptions. [Neil Cook]
- Added doc string for sPlt. [Neil Cook]
- Added constant for drift peak. [Neil Cook]
- Fixed plotting function calls. [Neil Cook]
- Updated descriptions (UNFINISHED) [Neil Cook]
- Updated descriptions and unix/string time getting. [Neil Cook]
- Updated descriptions and unix/string time getting. [Neil Cook]
- Added doc strings + math time functions. [Neil Cook]
- Added more formats (defaults + log), removed main code. [Neil Cook]
- Updated config error. [Neil Cook]
- Updated descriptions and unix/string time getting. [Neil Cook]


0.1.005 (2018-01-24)
--------------------
- Update versions + date. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Version + date update. [Neil Cook]
- Updated `__all__` [Neil Cook]
- Added to warninglogger (funcname), changed end card colour. [Neil
  Cook]
- Added warnlog alias. [Neil Cook]
- Better error handling + reporting. [Neil Cook]
- Better error handling + reporting. [Neil Cook]
- Better error handling + reporting. [Neil Cook]
- Better error handling + reporting. [Neil Cook]
- Better error handling. [Neil Cook]
- Doc strings added. [Neil Cook]
- Doc strings added. [Neil Cook]
- Warnings added, better error handling. [Neil Cook]
- Update of code. [Neil Cook]
- Config param change (debug mode active) [Neil Cook]
- Submodule clean up and doc string writing. [Neil Cook]
- First commit of quick install guide. [Neil Cook]
- Added `DARK_CUTLIMIT` to keyword used variables, added a hack to avoid
  not having config file `ICDP_NAME` (will complain elsewhere) [Neil Cook]
- Added `DARK_CUTLIMIT` to keyword used variables, added a hack to avoid
  not having config file `ICDP_NAME`. [Neil Cook]
- Added logic for quick install guide (false) [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Fixed installDIR. [Neil Cook]
- Sorted out environment paths. [Neil Cook]
- Sorted out environment paths. [Neil Cook]
- Fixed debug mode. [Neil Cook]
- Fixed comment. [Neil Cook]
- Fixed init `__all__` call. [Neil Cook]
- Editted log to print message even if we cannot log to file. [Neil
  Cook]
- Updated version and latest edit date. [Neil Cook]
- Added additional way to read config file (slow using python open) or
  give good error message if cannot open. [Neil Cook]
- Allowed ConfigError "message" to take list as input. [Neil Cook]
- Streamlined config strings. [Neil Cook]
- Streamlined config strings. [Neil Cook]
- Fixed error with `DRS_NAME`, `DRS_VERSION`. [Neil Cook]


0.1.004 (2018-01-22)
--------------------
- Added test data link. [Neil Cook]
- Link to logo change. [Neil Cook]
- Merge pull request #92 from njcuk9999/dev. [Neil Cook]

  Merge pull request #91 from njcuk9999/master
- Merge pull request #91 from njcuk9999/master. [Neil Cook]

  merge
- Merge remote-tracking branch 'origin/master' [Neil Cook]
- Merge pull request #90 from njcuk9999/dev. [Neil Cook]

  Merge pull request #89 from njcuk9999/master
- Merge pull request #89 from njcuk9999/master. [Neil Cook]

  master to dev
- Rebuilt pdfs. [Neil Cook]
- Updated version. [Neil Cook]
- Added spacing to constants. [Neil Cook]
- Changed the cmd code boxes. [Neil Cook]
- Added a general section. [Neil Cook]
- Removed definevariablecmd variables. [Neil Cook]
- Added some namedlabels. [Neil Cook]
- Fixed typo in log message. [Neil Cook]
- Updated readme. [Neil Cook]
- Updated date and rebuilt. [Neil Cook]
- Added quick install chapter. [Neil Cook]
- Updated date + version. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Updated version. [Neil Cook]
- Unchanged. [Neil Cook]
- Updated dirs. [Neil Cook]
- Fixed errors. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated log colourring. [Neil Cook]
- Updated paths. [Neil Cook]
- Added readme files. [Neil Cook]
- Added example data readme files. [Neil Cook]
- Added calibDB minimum files. [Neil Cook]
- Restructure of drs file. [Neil Cook]
- Merge pull request #88 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #87 from njcuk9999/dev. [Neil Cook]

  Merge pull request #86 from njcuk9999/master
- Rebuilt pdfs. [Neil Cook]
- Updated version. [Neil Cook]
- Added spacing to constants. [Neil Cook]
- Changed the cmd code boxes. [Neil Cook]
- Added a general section. [Neil Cook]
- Removed definevariablecmd variables. [Neil Cook]
- Added some namedlabels. [Neil Cook]
- Fixed typo in log message. [Neil Cook]
- Updated readme. [Neil Cook]
- Updated date and rebuilt. [Neil Cook]
- Added quick install chapter. [Neil Cook]
- Updated date + version. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Updated version. [Neil Cook]
- Unchanged. [Neil Cook]
- Updated dirs. [Neil Cook]
- Fixed errors. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated log colourring. [Neil Cook]
- Updated paths. [Neil Cook]
- Added readme files. [Neil Cook]
- Added example data readme files. [Neil Cook]
- Added calibDB minimum files. [Neil Cook]
- Restructure of drs file. [Neil Cook]
- Updated version and date. [Neil Cook]
- Updated version and date. [Neil Cook]
- Merge pull request #86 from njcuk9999/master. [Neil Cook]

  merge


0.1.003 (2018-01-16)
--------------------
- Update README.md. [Neil Cook]
- Merge pull request #85 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed update
- Updated to alpha 0.1. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated to alpha 0.1. [Neil Cook]
- Merge pull request #84 from njcuk9999/dev. [Neil Cook]

  rotated speed table + rebuild pdf
- Rotated speed table + rebuild pdf. [Neil Cook]
- Merge pull request #83 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed doc + version updates
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated python module versions. [Neil Cook]
- Updated readme (quick manual out of date and useless - use pdfs) [Neil
  Cook]
- Updated dates and version. [Neil Cook]
- Updates architecture. [Neil Cook]
- Merge pull request #82 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed testing and doc
- `Cal_ccf` fitting difference graph. [Neil Cook]
- `Cal_dark` graph 3. [Neil Cook]
- `Cal_dark` graph 2. [Neil Cook]
- `Cal_dark` graph 1. [Neil Cook]
- Changed reporting of errors to "differences" [Neil Cook]
- First commit unit test including all current recipes (with comparison)
  + `cal_drift_raw` and `cal_driftpeak_e2ds`. [Neil Cook]
- Updated name of unit test 3. [Neil Cook]
- Updated name of unit test 2. [Neil Cook]
- Added new and old methods for calulating badpix normalisation constant
  (for testing purposes) [Neil Cook]
- Changed location of TOC page break. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Commented conflicting text (do not use memoir captions) [Neil Cook]
- Added new packages. [Neil Cook]
- Added new constants. [Neil Cook]
- Added named labels to some constants. [Neil Cook]
- Added calibdb section (unfinished) [Neil Cook]
- Updated todo list. [Neil Cook]
- Added caldark to recipes. [Neil Cook]
- Updated versions. [Neil Cook]
- Updated change log and moved around sections. [Neil Cook]
- Updated imports in placeholder file. [Neil Cook]
- Updated imports in placeholder file. [Neil Cook]
- Added reffilename to paramdict. [Neil Cook]
- Added to log printing in qc. [Neil Cook]
- Allowed norm median flat to be old or new method. [Neil Cook]
- Merge pull request #81 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #80 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed run and tested
- Merge pull request #79 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed doc changes
- Merge pull request #78 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed - `cal_ccf` now runs
- Merge pull request #77 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed changes
- Merge pull request #76 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed tested
- Merge pull request #75 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed run
- Merge pull request #74 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed untested
- Merge pull request #73 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed `cal_ccf` completed but not tested
- Merge pull request #72 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed `cal_CCF` stuff
- Merge pull request #71 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed unfinished and untested
- Merge pull request #70 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #69 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #68 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #67 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #66 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #65 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #64 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #63 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #62 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed checked for consistency and that codes run
- Merge pull request #61 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed `cal_drift_e2ds` not working
- Merge pull request #60 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed untested `cal_badpix`
- Merge pull request #59 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed pdf build
- Merge pull request #58 from njcuk9999/dev. [Neil Cook]

  Dev - documentation edits: confirm pdf builds
- Merge pull request #57 from njcuk9999/dev. [Neil Cook]

  readme link update
- Merge pull request #56 from njcuk9999/dev. [Neil Cook]

  doc change - pdfs build correctly
- Merge pull request #55 from njcuk9999/dev. [Neil Cook]

  image change
- Merge pull request #54 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #53 from njcuk9999/dev. [Neil Cook]

  added pdf manuals to readme
- Merge pull request #52 from njcuk9999/dev. [Neil Cook]

  added pdf manuals to readme
- Merge pull request #51 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed documentation and cosmetic changes only
- Merge pull request #50 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #49 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #48 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #47 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #46 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #45 from njcuk9999/dev. [Neil Cook]

  Added latex gitignore
- Merge pull request #44 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #43 from njcuk9999/dev. [Neil Cook]

  updated links in table of contents
- Merge pull request #42 from njcuk9999/dev. [Neil Cook]

  Dev
- Delete fits2ramp.py. [eartigau]
- Add files via upload. [eartigau]

  latest version of fits2ramp
- Merge pull request #41 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #40 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #39 from njcuk9999/dev. [Neil Cook]

  Dev - confirm run
- Merge pull request #38 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed cosmetic only
- Merge pull request #37 from njcuk9999/dev. [Neil Cook]

  Dev - confirm runs
- Merge pull request #36 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #35 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #34 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed checked runs and consistency
- Merge pull request #33 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed codes run + bug fixes are correct
- Merge pull request #32 from njcuk9999/dev. [Neil Cook]

  Dev - confirmed cosmetic nature - extract still not working (unfinished)
- Merge pull request #31 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #30 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #29 from njcuk9999/dev. [Neil Cook]

  readme update - confirmed
- Merge pull request #28 from njcuk9999/dev. [Neil Cook]

  confirmed consitency
- Merge pull request #27 from njcuk9999/dev. [Neil Cook]

  Confirm check of consistency
- Merge pull request #26 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #25 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #24 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #23 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #22 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #21 from njcuk9999/dev. [Neil Cook]

  added to general section, `cal_dark` section and `cal_loc` section
- Merge pull request #20 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #19 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #18 from njcuk9999/dev. [Neil Cook]

  confirmed runs and consistent
- Merge pull request #17 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #16 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #15 from njcuk9999/dev. [Neil Cook]

  cosmetic changes only - confirmed running
- Merge pull request #14 from njcuk9999/dev. [Neil Cook]

  Check runs and consistent (visually)
- Merge pull request #13 from njcuk9999/dev. [Neil Cook]

  checked they still run
- Merge pull request #12 from njcuk9999/dev. [Neil Cook]

  Tested consistency
- Merge pull request #11 from njcuk9999/dev. [Neil Cook]

  Confirmed still runs and same output
- Merge pull request #10 from njcuk9999/dev. [Neil Cook]

  Confirmed agrees with original code
- Merge pull request #9 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #8 from njcuk9999/dev. [Neil Cook]

  Tested and verified as consistent
- Merge pull request #7 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #6 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #5 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #4 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #3 from njcuk9999/dev. [Neil Cook]

  Dev
- Merge pull request #2 from njcuk9999/dev. [Neil Cook]

  push to master
- Merge pull request #1 from njcuk9999/dev. [Neil Cook]

  Commit to Master


0.1.002 (2018-01-12)
--------------------
- Updated progress. [Neil Cook]
- Rebuilt pdf file. [Neil Cook]
- Updated todo list. [Neil Cook]
- Added fortran python conversion (for test purposes only) [Neil Cook]
- Unignore fitgaus.so. [Neil Cook]
- Added fitgaus.f (for test purposes only) [Neil Cook]
- Added comparison + tests + nanstats in order to pass or fail found
  errors. [Neil Cook]
- Set a threshold for order of magnitude difference (in comparison)
  [Neil Cook]
- Added a `test_fit_ccf` to compare "fortran fit" with "python fit" [Neil
  Cook]
- Cosmetic comment fix. [Neil Cook]
- Added writeimage dtype fix. [Neil Cook]
- Added `kw_drs_QC` keyword. [Neil Cook]
- Cosmetic fixes. [Neil Cook]
- Moved qc and fixed header bugs. [Neil Cook]
- Fixed badpixelfits error. [Neil Cook]
- Added logs. [Neil Cook]
- Fixed header error. [Neil Cook]


0.1.001 (2018-01-11)
--------------------
- Updated progress. [Neil Cook]
- Fixed list not appending. [Neil Cook]
- First commit - comparison functions for old vs new test. [Neil Cook]
- Added ability to test outputs. [Neil Cook]
- Added aliases to utc. [Neil Cook]
- Added fiber definition to fiber loop. [Neil Cook]
- First commit `unit_Test3` - testing the outputs. [Neil Cook]
- Added output assignment to all unit tests. [Neil Cook]
- Added output filename functions, reordered functions for better
  clarity. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Removed output filenaming to spirouConfig.spirouConst. [Neil Cook]
- Added a question re fiber type for wave file. [Neil Cook]
- Updated version. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Modified date and version. [Neil Cook]
- Added `cdata_folder` constant. [Neil Cook]
- Added spirouTHORCA placeholder section. [Neil Cook]
- Added `cal_CCF` section. [Neil Cook]


0.1.000 (2018-01-10)
--------------------
- Readded `cal_CCF` to unit test 2. [Neil Cook]
- Moved UrNe.mas to data folder. [Neil Cook]
- Added a `locate_mask` function - to local file if filename is not a
  valid path and found by os.path.exists, make `ic_debug` `drs_debug==2`.
  [Neil Cook]
- Make `ic_debug` `drs_debug==2`. [Neil Cook]
- Corrected typo in debug plot. [Neil Cook]
- Added `CDATA_FOLDER` constant. [Neil Cook]
- Added `get_relative_folder` function. [Neil Cook]
- Added aliases to init. [Neil Cook]
- Added removal of lockfile in generated error. [Neil Cook]
- Make `ic_debug` `drs_debug==2`. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Added spaces to some commands. [Neil Cook]
- Added listing style and tcolorbox to print out cmd prompt in colours
  red/yellow/green. [Neil Cook]
- Added to variables. [Neil Cook]
- Added to todo. [Neil Cook]
- Added coloured log section. [Neil Cook]
- Change log updated (ccf update needs doing) [Neil Cook]
- Debug mode explained in comments. [Neil Cook]
- Moved file. [Neil Cook]
- Make `ic_debug` `drs_debug==2`. [Neil Cook]
- Remove template logging (moved into spirouRv.GetCCFMask function.
  [Neil Cook]
- Removed `ic_debug` and replaced with `drs_debug`. [Neil Cook]
- Removed `ic_debug` (replaced with `drs_debug)` [Neil Cook]
- Added an option in `debug_start` to allow no coloured text. [Neil Cook]
- Changed order to allow reading of config file (to access certain
  parameters without running recipe) [Neil Cook]
- First commit - config file reading (base level no drs imports allowed)
  [Neil Cook]
- Moved config file reading to new code. [Neil Cook]
- Removed `ic_debug` (now `drs_debug)` [Neil Cook]
- Added input keyword chapter for user. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Removed devguide if statements. [Neil Cook]
- Created named label command (to allow linking to individual text via
  phantom sections) [Neil Cook]
- Changed label to namedlabel. [Neil Cook]
- Changed label to namedlabel. [Neil Cook]
- Removed typo. [Neil Cook]
- Changed label to namedlabel. [Neil Cook]
- Changed label to named label. [Neil Cook]
- Made links to modules only for dev guide. [Neil Cook]
- Modified variables. [Neil Cook]
- Made most of input keywords section devguide only. [Neil Cook]
- Removed `ic_debug` constant. [Neil Cook]
- Added `drs_debug` and `coloured_log` constants. [Neil Cook]
- Removed `ic_debug` and replaced with `drs_debug`. [Neil Cook]
- Removed `ic_debug` and replaced with `drs_debug`. [Neil Cook]


0.0.048 (2018-01-09)
--------------------
- Fixed import and removed `cal_CCF` (problem with code) from unit tests.
  [Neil Cook]
- Fixed import. [Neil Cook]
- Reformatted multi-line error message. [Neil Cook]
- Fixed comments. [Neil Cook]
- Better dealing with calibDB file. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Overlhaul of define variable function. [Neil Cook]
- Readded `qc_max_signal`, added `calib_db_match` constant. [Neil Cook]
- Placeholder for `cal_WAVE`. [Neil Cook]
- Placeholder for `cal_HC`. [Neil Cook]
- Moved wave into fiber loop (now needs fiber) [Neil Cook]
- Added calibdb prefix (from update to V48) [Neil Cook]


0.0.046 (2018-01-08)
--------------------
- Updated text for conversion from .txt to `.py` config files. [Neil Cook]
- Added `return_locals` for debugging purposes. [Neil Cook]
- Added aliases for `unit_test_functions`. [Neil Cook]
- Added/modified renamed functions for setup, changed errors that span
  multiple lines to list argument for logger. [Neil Cook]
- Added/modified renamed functions for setup. [Neil Cook]
- Removed call to unused constant (update to V48) [Neil Cook]
- Corrected change for update to V48. [Neil Cook]
- Updated text for config files from .txt to `.py` conversion. [Neil Cook]
- Allow list log messages, coloured log messages, and launch debugger in
  DEBUG mode on error. [Neil Cook]
- Updated text for change of .txt config to .py. [Neil Cook]
- Added colour levels and debug pseudo constants. [Neil Cook]
- Fixed error with getting dictionaries from config files. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Added qc constants. [Neil Cook]
- Converts to py file (but still read as text file) + added some qc
  constants. [Neil Cook]
- Converts to py file (but still read as text file) [Neil Cook]
- Moved exit function to top, changed startup alias. [Neil Cook]
- Updated for V48 of old code. [Neil Cook]
- Updated for V48 of old code. [Neil Cook]
- Updated for V48 of old code. [Neil Cook]
- Modified startup functions. [Neil Cook]
- Modified startup functions. [Neil Cook]
- Modified startup functions. [Neil Cook]
- Modified startup functions. [Neil Cook]
- Added date and release type to codes for modules. [Neil Cook]
- Added date and release type to codes for recipes. [Neil Cook]
- Rebuilt pdfs after variables changes. [Neil Cook]
- Unit test 2 now uses `unit_test_functions`. [Neil Cook]
- Unit test 1 now uses `unit_test_functions`. [Neil Cook]
- Moved argument definitions of unit tests to functions file (can call
  from multiple files without having to update all) [Neil Cook]
- Modified `create_drift_file` (V48 update) [Neil Cook]
- Added fiber to 'WAVE' calib key (V48 update) [Neil Cook]
- Added `drift_peak_plot_llpeak_amps` function (V48 update) [Neil Cook]
- Added `calib_prefix` const function. [Neil Cook]
- Updated descriptions of `drift_peak` variables. [Neil Cook]
- Added and updated `drift_peak` constants. [Neil Cook]
- Added 'ALL' fiber type option and error if `fiber_type` is not
  understood. [Neil Cook]
- Updated to version 48 (untested) [Neil Cook]
- Updated to version 48 (untested) [Neil Cook]


0.0.045 (2017-12-21)
--------------------
- Added coravelation and sub functions, added ccf fit functions and misc
  functions. [Neil Cook]
- Added aliases for coravelation and fitccf. [Neil Cook]
- Added ccf plots. [Neil Cook]
- Added ccf keywords. [Neil Cook]
- Added ccf table and fits pseudo constants. [Neil Cook]
- Added ccf constants. [Neil Cook]
- Unchanged. [Neil Cook]
- Unchanged. [Neil Cook]
- Unchanged. [Neil Cook]
- Added correlation sections - code finished but untested. [Neil Cook]
- What. [Neil Cook]


0.0.044 (2017-12-20)
--------------------
- Temporarily put mask in bin folder (where does it go?) [Neil Cook]
- Corrected mistakes in `get_e2ds_ll`. [Neil Cook]
- Added aliases for getll and getdll. [Neil Cook]
- Added to coravelation function (not finished), added `calculate_ccf`
  function (not finished), added `raw_correlbin` function, added correlbin
  function (not finished) [Neil Cook]
- Added to coravelation function (not finished), added `calculate_ccf`
  function (not finished), added `raw_correlbin` function, added correlbin
  function (not finished) [Neil Cook]
- Fixed error in `read_table` (with colnames != None) [Neil Cook]
- Added keyword. [Neil Cook]
- Updated configerror error message. [Neil Cook]
- Added constants. [Neil Cook]
- Added data to loc. [Neil Cook]


0.0.043 (2017-12-19)
--------------------
- Need to finish code. [Neil Cook]
- Redefined wave getting (GetE2DSll) and added a micron mask checking
  section. Code unfinished. [Neil Cook]
- First commit added `get_e2ds_ll`, `get_ll_from_coeffiecients`, and
  `get_dll_from_coefficients` functions. [Neil Cook]
- First commit added GetE2DSll alias. [Neil Cook]
- Need to finish coravelation function. [Neil Cook]
- Added `get_ccf_mask` function, added coravelation function (not
  finished) [Neil Cook]
- Added to `write_table`, added `read_table` function, added `update_docs`
  function and call to function at end. [Neil Cook]
- Modified `read_wave_file`. [Neil Cook]
- Added ReadTable alias. [Neil Cook]
- Added keywords to use list. [Neil Cook]
- Added `cal_CCF` keywords (input from `WAVE_AB)` [Neil Cook]
- Added GetKwValues alias to `get_keyword_values_from_header`. [Neil Cook]
- Cosmetic changes to comments. [Neil Cook]


0.0.042 (2017-12-18)
--------------------
- First commit (similar to `cal_drift_e2ds)` -- currently unfinished.
  [Neil Cook]
- Modified `get_custom_from_run_time_Args` function (Added for function
  arguments) to allow more functionality, commented old function. [Neil
  Cook]
- Added start of `get_ccf_mask` function (not finished) [Neil Cook]
- Added alias to `get_ccf_mask` (GetCCFMask) [Neil Cook]
- Added ability to define x and y in `drift_plot_Selected_wave_ref`. [Neil
  Cook]
- Added two `cal_CCF` constants. [Neil Cook]
- Added dividers between sections 2.7 - 2.10. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Updated progress. [Neil Cook]


0.0.041 (2017-12-14)
--------------------
- Rebuilt pdf. [Neil Cook]
- Updated `drift_peak_exp_width` function calls. [Neil Cook]
- Changed hardcoded width to width from constant in `get_drift()` [Neil
  Cook]
- Rebuilt pdf. [Neil Cook]
- Added TOC page divider. [Neil Cook]
- Added caldriftpeak command. [Neil Cook]
- Added drift peak section and constants. [Neil Cook]
- Updated constants. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Deep copy on speref in `create_drift_file` function, other modifications
  to correct errors. [Neil Cook]
- Corrected errors in `drift_peak_plot_dtime_against_drift`. [Neil Cook]
- Added to change log. [Neil Cook]
- Added drift-peak constants. [Neil Cook]
- Fixes to `cal_drift-peak` - now works in gaussfit and non-gaussfit mode.
  [Neil Cook]


0.0.040 (2017-12-13)
--------------------
- Rebuild pdf. [Neil Cook]
- Updated todo list. [Neil Cook]
- Updated progress in readme. [Neil Cook]
- Added drift-peak plot to documentation figures. [Neil Cook]
- Added RV aliases. [Neil Cook]
- Corrected some code, added warning catch, added `sigma_clip` function,
  added `drift_per_order` and `drift_all_orders` functions. [Neil Cook]
- Added `drift_peak` plot, `drift_plot_correlation_comp` and working
  function. [Neil Cook]
- Added `drift_peak` constants. [Neil Cook]
- Cosmetic change to logging. [Neil Cook]
- Cosmetic change to logging. [Neil Cook]
- Added many sections (code finished - untested) [Neil Cook]


0.0.039 (2017-12-12)
--------------------
- Corrected `cal_drift_e2ds` test (file was wrong) [Neil Cook]
- First commit - copy of `cal_drift_e2ds` - in process of modifying - not
  tested. [Neil Cook]
- Added global c constant, added `create_drift_file`, `gauss_function`,
  `remove_wide_peaks`, `remove_zero_peaks`, `get_drift`, `pearson_rtest`
  functions (not tested) [Neil Cook]
- Rearranged function aliases, added `drift_peak` function aliases. [Neil
  Cook]
- Change MeasureMinMax function name. [Neil Cook]
- Added `append_source`, `append_sources`, `append_all` methods to ParamDict.
  [Neil Cook]
- Changed doc string of `measure_box_min_max`. [Neil Cook]
- Added drift constants. [Neil Cook]
- Change MeasureMinMax function name. [Neil Cook]
- Change MeasureMinMax function name. [Neil Cook]
- Cosmetic changes. [Neil Cook]
- Cosmetic changes. [Neil Cook]


0.0.038 (2017-12-11)
--------------------
- Updated readme progress. [Neil Cook]
- First commit unit test 2. [Neil Cook]
- Updated latest edit date. [Neil Cook]
- Updated todo list. [Neil Cook]
- Removed unneeded comment. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]
- Checked against old versions and updated edit date, added badpix key.
  [Neil Cook]
- Checked against old versions and updated edit date. [Neil Cook]


0.0.037 (2017-12-08)
--------------------
- Rebuild pdfs. [Neil Cook]
- Updated readme. [Neil Cook]
- Updated readme. [Neil Cook]
- Added description of some variables. [Neil Cook]
- Added to changelog. [Neil Cook]
- Fixed fibertype function (now got from constants) [Neil Cook]
- Fixed bug with `LOC_FILE` not being used. [Neil Cook]
- Added root to copy root keys - now works as supposed to (only copies
  keys with root not all keys) [Neil Cook]
- Moved ww calc to function and calculating for all unique combinations
  (up to 4) of ww0 and ww1 (caused by rounding) [Neil Cook]
- Added closeall funciton, modified ext and drift functions. [Neil Cook]
- Changed `root_drs` keywords (now used in code) [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Updated date. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Added DRIFT-E2DS and changed rootdrs keywords. [Neil Cook]
- Updated todo list. [Neil Cook]
- Removed duplicate sections (i.e. drifts should all be in one section
  etc), renamed placeholder sections. [Neil Cook]
- Added new extract and drift constants, added spacing. [Neil Cook]
- Added new extract and drift keywords. [Neil Cook]
- Added `fiber_types`, reworked extract and drift constants. [Neil Cook]
- Added return locals. [Neil Cook]
- Added return locals. [Neil Cook]
- Added return locals. [Neil Cook]
- Added return locals. [Neil Cook]
- Added return locals, added extra input to make like old extractrawC.
  [Neil Cook]
- Added return locals, added extra input to make like old extractrawAB.
  [Neil Cook]
- Added return locals, fixed changes from old to new. [Neil Cook]
- Added return locals, fixed minor differences. [Neil Cook]
- Added return locals, fixed minor differences between old and new code.
  [Neil Cook]
- Added return locals. [Neil Cook]
- Returned locals. [Neil Cook]


0.0.036 (2017-12-07)
--------------------
- Added `get_fiber_type` function. [Neil Cook]
- Added Get Fiber type function. [Neil Cook]
- Modified `get_all_similar_files`. [Neil Cook]
- Added readdata function and modified readimage, added `read_flat_file`
  function. [Neil Cook]
- Added MakeTable and WriteTable to init. [Neil Cook]
- Made sure we dont get filename unless we need it in
  `get_acquision_time`. [Neil Cook]
- Added extra drift constants. [Neil Cook]
- Updated. [Neil Cook]
- First commit (no working) [Neil Cook]
- Changed `__main__` to main() in sources. [Neil Cook]
- Updated readme with badpix section. [Neil Cook]
- Corrected typo in wmed - in `normalise_median_flat` function
  `(flat_median_width` to `badpix_flat_med_wid)` [Neil Cook]
- Corrected type (comma) in `USE_KEYS`. [Neil Cook]
- Rebuild pdfs. [Neil Cook]
- Added numbered pdf bookmarks + contents to bookmarks. [Neil Cook]
- Added TOC commands to change spacing in TOC. [Neil Cook]
- Added tocloft package. [Neil Cook]
- Added calbadpix constant. [Neil Cook]
- Added badpix section. [Neil Cook]
- Updated todo section. [Neil Cook]
- Added badpix section. [Neil Cook]
- Added badpix section. [Neil Cook]
- Added badpix constants. [Neil Cook]
- Fixed badpixelfits construction. [Neil Cook]


0.0.035 (2017-12-06)
--------------------
- Moved `unit_Test1` to unit test module. [Neil Cook]
- First commit if unit test init file. [Neil Cook]
- Modified `run_time_custom_args` (now works and tested), added
  `get_custom_from_run_time_args` and `get_file` functions, modified
  `display_custom_args` function. [Neil Cook]
- Added GetCustomFromRuntime and GetFile aliases. [Neil Cook]
- Added `normalise_median_flux` and `locate_bad_pixel` functions. [Neil
  Cook]
- Added functionality to readimage. [Neil Cook]
- Added LocateBadPixels and NormMedianFlat aliases. [Neil Cook]
- Added badpix keywords. [Neil Cook]
- Added startswith function to ParamDict. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Cosmetic changes to commenting. [Neil Cook]
- Commented packages. [Neil Cook]
- Updated to-do list. [Neil Cook]
- Added placeholder module sections. [Neil Cook]
- Added badpix constants. [Neil Cook]
- Fixed Addkey not assigning to hdict. [Neil Cook]
- First commit `cal_BADPIX`. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Added to question. [Neil Cook]
- First commit to do list chapter. [Neil Cook]
- First commit documentation chapter. [Neil Cook]
- Added todolist and documentation chapters to main tex. [Neil Cook]
- Added package ulem (For strikethrough) removed duplicate packages.
  [Neil Cook]
- Removed visibility level from pseudoparamentry. [Neil Cook]
- Added latexbox (and latexbox1) [Neil Cook]
- Removed visibility level for pseudo code (should be all private) [Neil
  Cook]
- Added new code sections. [Neil Cook]
- Added latex code example. [Neil Cook]


0.0.034 (2017-12-05)
--------------------
- First commit of `output_keywords` chapter (filled and completed) [Neil
  Cook]
- Added `output_keywords` chapter. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Added keyword aliases. [Neil Cook]
- Added keywordentry command (similar to parmeterentry) [Neil Cook]
- Added escaping to inline python text. [Neil Cook]
- Added text. [Neil Cook]
- Readme link update. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuild pdf. [Neil Cook]
- Cosmetic change. [Neil Cook]
- Added `EXIT_LEVELS` definition. [Neil Cook]
- Changed exit vairable to `log_exit_type`. [Neil Cook]
- Added main init paramdict commands and move mac command. [Neil Cook]
- Changed title size to tiny. [Neil Cook]
- Changed title size to tiny. [Neil Cook]
- Modified sections. [Neil Cook]
- Added section. [Neil Cook]
- Removed sections added intro paragraph. [Neil Cook]


0.0.033 (2017-12-04)
--------------------
- Image change. [Neil Cook]
- Image change. [Neil Cook]
- Added pdf manuals to readme. [Neil Cook]
- Added pdf manuals to readme. [Neil Cook]
- Added pdf manuals to readme. [Neil Cook]
- Added pdf manuals to readme. [Neil Cook]
- Cosmetic changes only. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Removed `.py` from recipe command added more hskips for module commands.
  [Neil Cook]
- Added psuedoparamentry command. [Neil Cook]
- Added blank pythonbox tcblisting. [Neil Cook]
- Added sections. [Neil Cook]
- Changed note to dev note. [Neil Cook]
- Wrote section (from readme) [Neil Cook]


0.0.032 (2017-12-01)
--------------------
- Rebuilt pdf. [Neil Cook]
- Corrected syntax errors and line breaking. [Neil Cook]
- Rebuilt pdf files. [Neil Cook]
- Changed coi to `os_fac` and called from `ic_tilt_coi`. [Neil Cook]
- Added getting `DRS_NAME` and `DRS_VERSION` from spirouConfig.Constants.
  [Neil Cook]
- Moved the internal hyperlink setup out of preamble. [Neil Cook]
- Moved the internal hyperlink setup out of preamble. [Neil Cook]
- Added module aliases, added hslip 0pt for long variable names (so they
  can split on line break) [Neil Cook]
- Moved colour definitions to commands, modified ParameterEntry to add
  called from form (for devguide only) [Neil Cook]
- Moved colour definitions to commands. [Neil Cook]
- Reformated ParameterEntry (added call from for devguide), added many
  new variables (still not complete) [Neil Cook]
- Added error if calibDB file does not exist (and proper exception +
  log/print message) [Neil Cook]
- Corrected typo. [Neil Cook]
- Added sources for some constants, renamed coi to `ic_tilt_coi`. [Neil
  Cook]
- Added source for `fib_type`. [Neil Cook]


0.0.031 (2017-11-30)
--------------------
- Cosmetic change to spacing. [Neil Cook]
- Added placeholder sections. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Changed the user manual from yellow to red (and updated the margin
  label) [Neil Cook]
- Changed the level of green on the dev margin. [Neil Cook]
- Added new constants. [Neil Cook]
- Modified ParameterEntry command. [Neil Cook]
- Added a python inline style. [Neil Cook]
- Added variable file locations section, image variable section, fiber
  variable section, dark calibration section. [Neil Cook]
- Minor spelling changes to comments. [Neil Cook]
- Rebuilt pdfs. [Neil Cook]
- Now getting `DRS_NAME` and `DRS_VERSION` from spirouConfig.Consants. [Neil
  Cook]
- Added a NAME function constant. [Neil Cook]
- Added spirouCONSt and spirouKeywords constants. [Neil Cook]
- Added minipage to parameter definition (to force items on one page)
  [Neil Cook]
- Modified `drs_name` and `drs_version` - only in dev version. [Neil Cook]
- Removed `drs_name` and `drs_version` from config.txt (now in spirouConst)
  [Neil Cook]


0.0.030 (2017-11-29)
--------------------
- Rebuilt pdf files. [Neil Cook]
- Renamed preample to preamble. [Neil Cook]
- First commit of preamble file. [Neil Cook]
- First commit of packages file. [Neil Cook]
- First commit of merged variables file. [Neil Cook]
- First commit of merged recipes file. [Neil Cook]
- First commit of merged intro file. [Neil Cook]
- Updated folder path for figures in readme. [Neil Cook]
- Rebuilt pdf files. [Neil Cook]
- Moved bulk of same code to packages file and preample file, added
  ifdevguide (to distinguish between dev and user) added coloured
  border, moved chapters around after merges. [Neil Cook]
- Added masterclibddbfile, configtxtfile, acqtimekey, folderdateformat
  constants. [Neil Cook]
- Added paraeter command and devnote devsection (all dependent on
  devguide or userguide) [Neil Cook]
- Attempted breakable tcolorbox. [Neil Cook]
- First full commit - wrote section. [Neil Cook]
- Corrected spelling and added command in place of filename. [Neil Cook]
- Added from old manual. [Neil Cook]
- Added more sections. [Neil Cook]
- Deleted (not used) [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]
- Deleted and merged dev and user. [Neil Cook]


0.0.029 (2017-11-28)
--------------------
- First commit of user version of `data_architecture` (not to be kept -
  use if statements?) [Neil Cook]
- First commit of dev version of `data_architecture` (not to be kept - use
  if statements?) [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Rebuilt pdf. [Neil Cook]
- Added packages, modified abstract (noindent) [Neil Cook]
- Added packages, modified abstract (noindent) [Neil Cook]
- Ignored .listing files. [Neil Cook]
- Added recipe constants. [Neil Cook]
- Added a definevariablecmd function (cyan instead of blue for
  definevariable) [Neil Cook]
- Complete redo of code formatting (using newtcblistings) [Neil Cook]
- Updated label for chapter. [Neil Cook]
- Updated label for chapter. [Neil Cook]
- Updated label for chapter. [Neil Cook]
- Added code blocks section. [Neil Cook]
- Added code block sections. [Neil Cook]
- Updated notes to environment, code to code environments. [Neil Cook]
- Added folder layout section, installation root dir section, bin dir
  section, spirou module directory section. [Neil Cook]
- Renamed `cal_validate_drs` to `cal_validate_spirou`. [Neil Cook]


0.0.028 (2017-11-27)
--------------------
- Added latex gitignore. [Neil Cook]
- Memoir chapter styles (for pdf building) [Neil Cook]
- First commit dev guide. [Neil Cook]
- First commit user guide. [Neil Cook]
- Added logo to figures. [Neil Cook]
- Added constants first commit. [Neil Cook]
- Added commands (from old manual) [Neil Cook]
- Added coding formats (using new styles) [Neil Cook]
- Added installation process (first commit) for linux+mac and windows.
  [Neil Cook]
- What. [Neil Cook]
- Added placeholder first commit tex files (empty other than title)
  [Neil Cook]
- Updated progress in readme (with documentation needs) [Neil Cook]
- Added a function to check write level, corrected bug in logging (was
  `print_level` needed to be `log_level)` [Neil Cook]
- Added logo to documentation files. [Neil Cook]
- Edited comments. [Neil Cook]
- Added validation code (to test imports and display user setup) [Neil
  Cook]
- Updated links in table of contents. [Neil Cook]


0.0.027 (2017-11-24)
--------------------
- Updated section naming in readme. [Neil Cook]
- Added installation process to readme. [Neil Cook]
- Added `ic_ext_all` constant. [Neil Cook]
- Added timing to debug run. [Neil Cook]
- Added posibility to save all extraction types to file (simple, tilt,
  tiltweight, weight) [Neil Cook]
- Added timed unit tests sections. [Neil Cook]
- Corrected unit test. [Neil Cook]


0.0.026 (2017-11-23)
--------------------
- Made unit test compatible with python 2 (ordered dict) [Neil Cook]
- Updated progress in readme. [Neil Cook]
- Added to table of contents, added section 2.3 (to be filled out like
  section 2.2) [Neil Cook]
- Imported division from `__future` (to make sure all division is float
  division not int), cleaned up code, applied pep8 convensions. [Neil
  Cook]
- Removed debug timing stuff. [Neil Cook]
- Update readme with `cal_extract` and `cal_drift` sections, added unit test
  timing section. [Neil Cook]
- Renamed `run_inital_startup` to `run_initial_startup`. [Neil Cook]
- Wrapper around `cal_extract_RAW_spirou` to allow `fiber_type` defined as
  'C' [Neil Cook]
- Wrapper around `cal_extract_RAW_spirou` to define AB as the fiber type.
  [Neil Cook]
- First commit - unit test for all tested files (with timings) [Neil
  Cook]
- Modified `run_inital_startup` function to allow `night_name` and files
  arguments to be passed from main function calls. [Neil Cook]
- Moved `measure_dark` function here from `cal_DARK_spirou`, added
  'human'/'unix' time to `get_acqtime`. [Neil Cook]
- Added alias to MeasureDark function. [Neil Cook]
- Cosmetic change to `__all__` [Neil Cook]
- Added `drift_plot_dtime_Against_mdrift` function. [Neil Cook]
- Added `kw_ACQTIME_KEY_UNIX`. [Neil Cook]
- Modified `ARG_FILE_NAMES` and `ARG_NIGHT_NAME` to accept value already in
  p (from function call over command line arguments) [Neil Cook]
- Added human/unix acqtime getting. [Neil Cook]
- Added `ic_drift_n_order_max` parameter, cosmetic changes (spaces between
  sections increased) [Neil Cook]
- Moved `__main__` code to main function. [Neil Cook]
- Moved `__main__` code to main function. [Neil Cook]
- Moved `__main__` code to main function. [Neil Cook]
- Moved `__main__` code to main function. [Neil Cook]
- Moved `__main__` code to main function, added rv properties section,
  added plot section, added save drift values to file section. [Neil
  Cook]
- Moved `__main__` code to main function. [Neil Cook]


0.0.025 (2017-11-22)
--------------------
- Cosmetic changes to layout. [Neil Cook]
- Fixed some bugs, added compute cosmic+renorm section, added calculate
  RV drift section. [Neil Cook]
- Changed mask1 and mask to flag in `delta_v_rms_2d`, added
  `renormalise_cosmic2d` and `calculate_RV_drifts_2D` functions. [Neil Cook]
- Added aliases for ReNormCosmic2D and CalcRVdrift2D. [Neil Cook]
- Fixed error in `get_all_similar_files` (filelist not returned) [Neil
  Cook]
- Fixed error in `drift_plot_photon_uncertainty` `('number_orders`' in loc
  not p) [Neil Cook]
- Added `ic_drift_cut`, renamed `ic_dv_maxflux` and `ic_dv_boxsize`. [Neil
  Cook]


0.0.024 (2017-11-21)
--------------------
- Modified readme with change in plot function. [Neil Cook]
- Added imports, added startup section, read ref image section, get
  basic ref props section, resize ref image section, get loc/tilt/wave
  sections, merge coeffs section, extract ref section, computer dvrms
  section, plot ref section, get all files section, started all file
  loop (not finished) [Neil Cook]
- First commit, added `delta_v_rms_2d` function. [Neil Cook]
- Added `get_all_similar_files` function, modified `correct_for_dark`
  function (now can return dark for use later), modified `get_exptime`,
  `get_gain`, `get_sigdet`, `get_param`, added `get_acqtime`. [Neil Cook]
- Redefined readimage (no combining) and added `readimage_and_combine` (to
  do reading and combining), updated readimage functions throughout.
  [Neil Cook]
- Updated `__all__` [Neil Cook]
- Added GetAllSimilarFiles, GetAcqTime, ReadImage and
  ReadImageAndCombine functions. [Neil Cook]
- Modified extract functions to have and look for keywords in function
  calls before using defaults (allows customisation) [Neil Cook]
- Renamed plots for clarity, added `drift_plot_selected_wave_ref`,
  `drift_plot_photo_uncertainty`. [Neil Cook]
- Added filename arg to `get_acquisaion_time` and code to deal with it.
  [Neil Cook]
- Added `ic_ext_d_range_fpall`, `ic_drift_noise`, `ic_dv_maxflux`,
  `ic_dv_boxsize`, `drift_nlarge`, `drift_file_skip`, modified
  `ic_ext_range_fpall`. [Neil Cook]
- Renamed ReadImage to ReadImageAndCombine for clarity and renamed
  plotting functions (for clarity) [Neil Cook]
- Renamed ReadImage to ReadImageAndCombine for clarity and renamed
  plotting functions (for clarity) [Neil Cook]
- Renamed ReadImage to ReadImageAndCombine for clarity, changed fiber to
  p['fiber'], and renamed plotting functions (for clarity) [Neil Cook]
- Renamed ReadImage to ReadImageAndCombine for clarity. [Neil Cook]
- Renamed ReadImage to ReadImageAndCombine for clarity. [Neil Cook]


0.0.023 (2017-11-20)
--------------------
- Updated progress section. [Neil Cook]
- Added function `copy_root_keys` function, modified `read_header` function.
  [Neil Cook]
- Added alias for CopyRootKeys to init and `__all__` [Neil Cook]
- Modified `extract_AB_order`, `extract_order`, `extract_tilt_order`,
  `extract_tilt_weight_order`, `extract_tilt_weight_order2`,
  `extract_weight_order`, `extract_const_range`,
  `extract_const_range_fortran`, `extract_const_range_wrong` and
  `extract_wrapper` added code for `extract_tilt`, `extract_weight`,
  `extract_tilt_weight2`, `extract_tilt_weight`, extract, `check_for_none`,
  `get_tilt_matrix`. [Neil Cook]
- Updated `__all__` [Neil Cook]
- Added alias to ExtractTiltWeightOrder2. [Neil Cook]
- Added `cal_extract` plot functions. [Neil Cook]
- Moved EXIT definition to constants. [Neil Cook]
- Added `kw_LOCO_FILE` keyword. [Neil Cook]
- Added EXIT function (to return exit statement based on `log_exit_type()`
  [Neil Cook]
- Added `ic_ext_range_fpall`, modified `ic_ff_plot_all_orders`, added
  `ic_extmeanzone` constants. [Neil Cook]
- Renamed extracttiltweightorder function to extracttiltweightorder2.
  [Neil Cook]
- Added timing to extraction comparison, corrected noise calculation,
  added plot section, added saving e2ds to file. [Neil Cook]


0.0.021 (2017-11-17)
--------------------
- Added p to spiouCDB.GetDatabase (for `max_time` constants) [Neil Cook]
- Added p to spiouCDB.GetDatabase (for `max_time` constants), added read
  out of `max_time` in error (helps to identify why error was caused)
  [Neil Cook]
- Fixed call to spirouEXTOR.ExtractABOrder, added p to
  spiouCDB.GetDatabase (for `max_time` constants) [Neil Cook]
- Fixed error in `add_key_2d_list`. [Neil Cook]
- Fixed `selected_order_fit_and_edges`, added function
  `all_order_fit_and_edges`. [Neil Cook]
- Added stringtime2unixtime and unixtime2stringtime functions (fixed
  from spirouCDB) [Neil Cook]
- Added `DATE_FMT_HEADER` and `DATE_FMT_CALIBDB` constants. [Neil Cook]
- Added `ic_ff_plot_all_orders` constant, fixed `loc_file_fpall` and
  `orderp_file_fpall`. [Neil Cook]
- Fixed acqtime key error, fixed time getting error (inconsistent
  times), made check that times are consistent, added `max_time_human` and
  `max_time_unix` to p. [Neil Cook]
- Added due test mode. [Neil Cook]
- Added due test mode, added plot all orders (instead of just selected)
  - slower, added flat to calibDB. [Neil Cook]
- Modified imports, added version/author from constants. [Neil Cook]
- Modified imports, added version/author from constants, and added
  `__all__` function. [Neil Cook]
- Modified imports, added version/author from constants, changed lloc to
  loc, added functions for `extract_order`, `extract_order_0`,
  `extract_tilt_order`, `extract_weight_order` (None currently working) -
  will need to edit `extract_wrapper` to make work. [Neil Cook]
- Modified imports, added version/author from constants and interactive
  plot constant. [Neil Cook]
- Modified imports, added version/author from constants, added `TRIG_KEY`,
  `WRITE_LEVEL`, EXIT and WARN from constants, added `CONFIG_KEY_ERROR`
  warning. [Neil Cook]
- Added constants PACKAGE(), VERSION(), AUTHORS(), `LATEST_EDIT()`,
  CONFIGFOLDER(), CONFIGFILE(), `INTERACTIVE_PLOT_ENABLED()`,
  `LOG_TRIG_KEYS()`, `WRITE_LEVEL()`, `LOG_EXIT_TYPE()`,
  `LOG_CAUGHT_WARNINGS()`, `CONFIG_KEY_ERROR`, add set version and author
  from constants. [Neil Cook]
- Modified imports, added version/author from constants, added package
  `config_file`, configfolder and trig key from Constants. [Neil Cook]
- Modified imports, added version/author from constants. [Neil Cook]
- Modified imports, added version/author from constants. [Neil Cook]
- Modified imports, added version/author from constants. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases, added printing of sub-package names. [Neil Cook]
- First commit, modified imports, added version/author from constants,
  added `__all__` aliases, moved RunInitialStartup and RunStartup here
  (from SpirouCore) [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases, added aliases for different extraction types. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases, moved RunInitialStartup and RunStartup to spirouStartup
  module. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases. [Neil Cook]
- Modified imports, added version/author from constants, added `__all__`
  aliases. [Neil Cook]
- Editted comments for `ic_extopt`. [Neil Cook]
- Modified imports, moved spirouStartup to own module, added calls to
  extract functions. [Neil Cook]
- Modified imports, moved spirouStartup to seperate module. [Neil Cook]
- Modified `get_loc_coefficients` to look for keyword `'LOC_FILE`' [Neil
  Cook]
- Added key to arguments of `read_tilt_file` function, added
  `read_wave_file` function, modified `read_order_profile_superposition` to
  look for keyword `'ORDERP_FILE`' [Neil Cook]
- Added ReadWaveFile alias. [Neil Cook]
- Added A and B to fiber type parameters, added `loc_fil` and `orderp_file`
  parameters. [Neil Cook]
- Moved dprtype from header getting section, added fiber A B and AB
  replacement for AB (in merging coefficients) [Neil Cook]
- Added read image section, added basic image properties section, added
  correction of dark, added resize image, added the logging of dead
  pixels, added minmax `max_signal` section, added background computation
  section, added tilt reading section, added wave solution reading
  section, added localaization coefficient getting section, added order
  profile getting section, added order loop, added noise/flux/SNR
  calculation, added saturation warning section, added quality control
  section. [Neil Cook]


0.0.020 (2017-11-16)
--------------------
- Add calibDB to p in startup if calibdb required (should be faster than
  reloading it each time) [Neil Cook]
- Corrected `cal_ff` extractiltweightorder spelling mistake. [Neil Cook]
- Added check for calibDB in p. [Neil Cook]
- Added check for 'calibDB' in p. [Neil Cook]
- Moved `forbidden_copy_keys` to constants, added `get_type_from_header`
  function, added `read_raw_header` function. [Neil Cook]
- Added GetTypeFromHeader alias to init. [Neil Cook]
- Added dealing with customargs and added `run_time_custom_args` +
  `display_custom_args` functions. [Neil Cook]
- Added `kw_DPRTYPE`. [Neil Cook]
- Added `FORBIDDEN_COPY_KEYS` constant. [Neil Cook]
- Added tests for calibDB in p. [Neil Cook]
- Reformatted comments on variables. [Neil Cook]
- Added dprtype find from header, modified test code. [Neil Cook]
- Added dprtype find from header, modified test code. [Neil Cook]
- Added dprtype find from header, modified test code. [Neil Cook]
- Added dprtype find from header, added test code, added `__NAME__`, added
  setup section. [Neil Cook]
- Added dprtype find from header, added test code. [Neil Cook]


0.0.019 (2017-11-15)
--------------------
- Added `cal_FF_RAW` summary of changes section, updated progress. [Neil
  Cook]
- Added `add_key_1d_list` function, updated `add_key_2d_list` to be more
  generic (with header comment) [Neil Cook]
- Added AddKey1DList alias to init. [Neil Cook]
- Added `selected_order_fit_and_edges`,
  `selected_order_tilt_adjusted_e2ds_blaze` and `selected_order_flat` plot
  functions. [Neil Cook]
- Added `kw_EXTRA_SN` and `kw_FLAT_RMS`. [Neil Cook]
- Added `ic_ff_order_plot` constant. [Neil Cook]
- Cosmetic change. [Neil Cook]
- Added plot section, added saving blaze and flat field section. [Neil
  Cook]


0.0.018 (2017-11-14)
--------------------
- Added `convert_to_adu` function, fixed `get_gain/get_sigdet/get_param`
  functions. [Neil Cook]
- Removed reducedfolder call and fixed `order_profile` key. [Neil Cook]
- Added ConvertToADU alias to init. [Neil Cook]
- First commit `spirouFLAT.py` added `measure_blaze_for_order` function.
  [Neil Cook]
- First commit spirouFLAT init (added MeasureBlazeForOrder alias) [Neil
  Cook]
- Modified `extract_tilt_weight_order` and `extract_wrapper` functions,
  added `extract_tilt_weight` function and `extract_tilt_weight_old`
  function. [Neil Cook]
- Fixed error in gain/exptime keyword. [Neil Cook]
- Fixed hard coded key in `get_file_name` function. [Neil Cook]
- Cosmetic change. [Neil Cook]
- Added `ic_ff_sigdet`, `ic_extfblaz`, `ic_blaze_fitn` constants. [Neil Cook]
- Added storage set up for extraction, added extract with tilt+weight
  loop, added skip for `max_signal` QC. [Neil Cook]


0.0.017 (2017-11-13)
--------------------
- First commit, added some well used constants (constants but need input
  and functions so not formed from basic string/int/float/list) [Neil
  Cook]
- Reworked `fiber_params` to get dictionaries of constants with particular
  suffix, added more logging to `get_loc_coefficients`, added
  `merge_coefficients` function. [Neil Cook]
- Added mergecoefficients alias. [Neil Cook]
- Added masterfile constant, added `get_gain`, `get_sigdet`, `get_param`
  functions. [Neil Cook]
- Moved bulk of getting file name from calibDB to spirouCDB, added
  `read_order_profile_superposition` function. [Neil Cook]
- Added GetSigdet, GetExptime, GetGain and ReadOrderProfile aliases to
  init. [Neil Cook]
- Added `extract_tilt_weight_order` function (not finished), added
  `extract_tilt_weight` skeleton code, changed `extraction_wrapper` to fit
  changes of other functions. [Neil Cook]
- Added ExtractTiltWeightOrder alias to init file. [Neil Cook]
- Added reduced folder constant, fixed `calibd_dir` path on line 150 (now
  149) [Neil Cook]
- Fixed logging to file (date wasn't working) [Neil Cook]
- Added sigdet, exptime and gain keywords, moved acqtime to "required
  header keys" section. [Neil Cook]
- Added `extract_dict_params` function. [Neil Cook]
- Added ExtractDictParam to init. [Neil Cook]
- Added raw and reduced dir constants, added new function `get_file_name`,
  added `lock_file` and master file constants. [Neil Cook]
- Added GetFile command to init. [Neil Cook]
- Chagned fiber param variables to dictionaries. [Neil Cook]
- Changed getting sigdet, exptime and gain to functions, added reduced
  folder constant, added new fiber params command. [Neil Cook]
- Changed getting sigdet, exptime and gain to functions, added reduced
  folder constant. [Neil Cook]
- Changed getting sigdet, exptime and gain to functions, added reduced
  folder constant, added read tilt slit angle, added start of fiber
  extract loop (not finished) [Neil Cook]
- Changed getting sigdet, exptime and gain to functions, added reduced
  folder constant. [Neil Cook]
- Added pep8 cosmetic corrections. [Neil Cook]
- Added pep8 cosmetic corrections. [Neil Cook]
- Added filename option to readimage function, added `read_tilt_file`
  function. [Neil Cook]
- Added ReadTiltFile to init. [Neil Cook]
- Added image to doc string for `extract_AB_order`. [Neil Cook]
- Added `ic_tilt_nbo` constant. [Neil Cook]
- Added space between comma. [Neil Cook]
- Added read tilt slit angle section. [Neil Cook]


0.0.016 (2017-11-10)
--------------------
- Added `fib_type` to fiber types constants, added `cal_ff` params, added a
  qc param. [Neil Cook]
- Moved `measure_box_min_max` and
  `measure_background_and_get_central_pixels` to spirouBACK. [Neil Cook]
- Added `measure_background_and_get_central_pixels`, `measure_box_min_max`
  to spirouBACK `measure_background_flatfield` (not finished) to init.
  [Neil Cook]
- Moved `measure_background_and_get_central_pixels`, `measure_box_min_max`
  to spirouBACK, added `measure_background_flatfield` (not finished) [Neil
  Cook]
- Moved `measure_background_and_get_central_pixels`, `measure_box_min_max`
  to spirouBACK. [Neil Cook]
- Moved MeasureBkgrdGetCentPixs to spirouBACK. [Neil Cook]
- Added setup section, added read image section, added correction of
  dark section, added resize image section, , added `max_signal` section.
  [Neil Cook]
- Chnaged ccdsigdet to sigdet, added test (no need to specific files)
  [Neil Cook]


0.0.015 (2017-11-09)
--------------------
- Added `cal_slit` section. [Neil Cook]
- Stricked done progress. [Neil Cook]
- Added hlines. [Neil Cook]
- Edit table of contents, added back to top, added future sections.
  [Neil Cook]
- Added table of contents. [Neil Cook]
- Section numbering. [Neil Cook]
- Added WLOG update. [Neil Cook]
- Added WLOG update, and configError update. [Neil Cook]
- Added jpg py3 logo. [Neil Cook]
- Added picture as jpg. [Neil Cook]
- Changed path for plot. [Neil Cook]
- Correlation with a box test plot. [Neil Cook]
- Change test function for `smoothed_boxmean_image`. [Neil Cook]
- Added to general section, `cal_dark` section and `cal_loc` section. [Neil
  Cook]
- Moved `kw_TILT` to own section. [Neil Cook]
- Edited description of slit param. [Neil Cook]


0.0.014 (2017-11-08)
--------------------
- Added doc string for extract and added ExtractABorder alias to init.
  [Neil Cook]
- Added FitTilt and GetTilt to init. [Neil Cook]
- Moved `extract_AB_order` here (from `cal_SLIT_spirou)` [Neil Cook]
- Removed `get_tilt` and `fit_filt` functions (to spirouImage) [Neil Cook]
- Moved `get_tilt` and `fit_filt` functions here. [Neil Cook]
- Added doc strings for slit plotting functions. [Neil Cook]
- Updated `USE_KEYS` list formatting. [Neil Cook]
- Updated readme. [Neil Cook]
- Reworked `get_tilt` function, added extract AB order function and fit
  filt function, added plotting section, added tilt calculation section,
  added todo quality control section, added update calibDB section.
  [Neil Cook]
- Added coi `ic_tilt_fit` and `ic_slit_order_plot` constants. [Neil Cook]
- Added `kw_TILT` keyword. [Neil Cook]
- Added slit plotting functions: `selected_order_plot` and
  `slit_tilt_angle_and_fit_plot`. [Neil Cook]
- Added doc string for `extract_wrapper`, `extract_const_range`, added test
  functions `extract_const_range_fortran` and moved `extract_const_range` to
  `extract_const_range_wrong` (updates former) [Neil Cook]
- Changed plt.ion to sPlt controller function. [Neil Cook]


0.0.013 (2017-11-07)
--------------------
- Added doc for `get_loc_coefficients`, `initial_order_fit`,
  `sigmaclip_oder_fit` and `image_localization_superposition` added
  `calcualte_location_fits` function. [Neil Cook]
- First commit - added extract wrapper alias. [Neil Cook]
- First commit - added extract wrapper and first attempt at extract
  code. [Neil Cook]
- First commit - added fast polyval function. [Neil Cook]
- Added doc string comments for all functions. [Neil Cook]
- Edited `kw_loco_ctr_coeff` and `kw_loco_fwhm_coeff`. [Neil Cook]
- Allowed `max_time` to be None and get `max_time` from p['fitsfilename']
  [Neil Cook]
- Added some slit parameters. [Neil Cook]
- Added extract function. [Neil Cook]
- Added test via sys.argv. [Neil Cook]
- Added `get_loc_coefficients` function. [Neil Cook]
- Added GetCoeffs to init. [Neil Cook]
- Called GetAcqTime in `correct_for_dark` function. [Neil Cook]
- Added `read_header`, `read_key` and `read_key_2d_list` functions. [Neil
  Cook]
- Added ReadHeader, ReadKey, Read2Dkey to init. [Neil Cook]
- Added CopyCDBfiles call to `run_startup` function. [Neil Cook]
- Added `get_acquision_time` and `copy_files` function. [Neil Cook]
- Added CopyCDB and GetAcqTime to init. [Neil Cook]
- Updates `cal_SLIT` with `__NAME__` and new functions, updated startup
  section, added read image section, correction of dark section, resize
  image section, get coefficients section. [Neil Cook]
- Removed unused cocde from `cal_loc_RAW`. [Neil Cook]


0.0.012 (2017-11-03)
--------------------
- Updated comments in `constants_SPIROU`. [Neil Cook]
- Added a label to `locplot_order`. [Neil Cook]
- Changed splt to sPlt. [Neil Cook]


0.0.011 (2017-11-02)
--------------------
- Added timer, moved plots to spirouPlots, moved functions to
  spirouLOCOR, updated AddNewKey --> AddKey, added quality control
  section and add to calibDB section. [Neil Cook]
- Added timer, moved plots to spirouPlots, updated AddNewKey--> Addkey,
  [Neil Cook]
- Added `__getitem__`, `__contains`, `__delitem__` functions, forced all keys
  to uppercase (now ParamDict is case-insensitive), added `source_keys`,
  `__capitalise_keys__`, `__capitalise__key__` functions, added list to set
  of evaluate allowed types. [Neil Cook]
- Reloaded keywords `USE_KEYS`, added ParamDict call, added `kw_LOC_` keys,
  added source to overwritten warning. [Neil Cook]
- Renamed AddNewKey to AddKey. [Neil Cook]
- Added wrapper function for `add_new_key` `(add_new_keys)`, [Neil Cook]
- Renamed `image_localazation_superposition` to
  `image_localization_superposition`. [Neil Cook]
- Added functions from `cal_loc` --> spirouLOCOR, added
  `image_localazation_superposition` function. [Neil Cook]
- Added functions from `cal_loc` --> spirouLOCOR to init. [Neil Cook]
- Moved fiber variables to own section, added qc for `cal_loc`. [Neil
  Cook]
- Changed keys as now param dict all uppercase. [Neil Cook]
- First commit - all plotting functions moved here. [Neil Cook]


0.0.010 (2017-11-01)
--------------------
- `Set_source` for param dicts. [Neil Cook]
- `Set_source` for param dicts. [Neil Cook]
- Renamed `set_source` function to `set_source_for_defaulting_statements`
  (to avoid confusion) [Neil Cook]
- Added `set_source`. [Neil Cook]
- Added documentation to ConfigException, added new class ParamDict
  (custom dictionary), added `set_source` to param dicts and a `set_source`
  function for dealing with default values from `check_params()` [Neil
  Cook]
- Added ParamDict to init. [Neil Cook]
- Added set source + `c_Database` --> ParamDict. [Neil Cook]
- Added set source + fparam --> ParamDict. [Neil Cook]
- Added set source + updated keywords to match spirouKeywords. [Neil
  Cook]


0.0.009 (2017-10-31)
--------------------
- Modified `measure_background_and_get_central_pixels` to accept and
  return loc made a copy of data2  (data2o) for localisation with 0 on
  fit data dump added code for "Save and record of image of localization
  with order center and keywords" section added code for "Save and
  record of image of sigma" section placeholder code for "Save and
  Record of image of localization" section. [Neil Cook]
- Added empty holder for `image_localazation_super` function (not
  finished) [Neil Cook]
- Updated call for `ACQTIME_KEY` to `kw_ACQTIME_KEY`. [Neil Cook]
- Moved functions into sections added function `"add_new_key`" and
  `"add_key_2d_list`" [Neil Cook]
- Updated init file. [Neil Cook]
- Updated call to spirouConfig moved `check_params` moved
  `load_other_config_file` (kept wrapper function for logging) [Neil Cook]
- Removed log constants (to spirouConfig) [Neil Cook]
- Updated spirouCore init. [Neil Cook]
- First commit moved from config/keywords. [Neil Cook]
- Moved some constants to here `(TRIG_KEY`, `WRITE_LEVEL`, EXIT) added
  config exception class added config error class moved
  `load_config_from_file` from startup functions to spirouConfig added doc
  for `check_config` moved `check_params` from startup to spirouConfig
  created `get_default_config_file` function. [Neil Cook]
- First commit for spirouConfig ini - moved config and keyword function
  calls to here. [Neil Cook]
- Added `ic_locfitp`, `ic_loc_delta_width`, `ic_locopt1` to config file. [Neil
  Cook]
- Added `SPECIAL_NAME` back to config. [Neil Cook]
- Updated function calls. [Neil Cook]
- Updated function calls. [Neil Cook]
- Added call to AddNewKey. [Neil Cook]


0.0.008 (2017-10-30)
--------------------
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- Tmp file for keyword args? - sort this out. [Neil Cook]
- File migration and new imports plot order num against rms. [Neil Cook]
- File migration and new imports. [Neil Cook]
- File migration and new imports. [Neil Cook]
- Reordered files. [Neil Cook]


0.0.007 (2017-10-27)
--------------------
- Reworked fit order into "initial order fit" and `"sigmaclip_order_fit`"
  added and tested order fitting sections. [Neil Cook]
- Added some more location parameters. [Neil Cook]
- Updated locate center order position into two functions. [Neil Cook]
- Return header from last "added" fits and set fitsfilename to last file
  (as in original code) - not sure it this is wanted but it is how it
  is. [Neil Cook]
- Changed `locate_center_order_positions` to two functions one for center
  finding one for center + width of individual (subtle differences)
  [Neil Cook]


0.0.006 (2017-10-26)
--------------------
- Revert "added example of BoxSmoothedImage with mode 'convolve' vs
  'manual'" This reverts commit f7637bf. [Neil Cook]
- Changed the logged to exit via sys.exit. [Neil Cook]
- Added a minimum width requirement and return widths in
  `"locate_center_order_position`" functions. [Neil Cook]
- Closed the hdu and added a header extension argument (default = 0)
  [Neil Cook]
- Changed name of `locate_central_position` alias. [Neil Cook]
- Added constants from `cal_loc_RAW_spirou`. [Neil Cook]
- Added to position and width finding (incomplete + untested) [Neil
  Cook]
- Fixed formatting. [Neil Cook]
- Reformatted BoxSmoothedimage and LocateCentralPosition descriptions in
  change log. [Neil Cook]
- Wrapped for `locate_order_positions` to go between manual and convolve
  versions. [Neil Cook]
- Added more documentation for `smoothed_boxmean_image`. [Neil Cook]
- Added BoxSmoothedImage 'convolve' vs 'manual' change to change log.
  [Neil Cook]
- Added BoxSmoothedImage with mode 'convolve' vs 'manual' [Neil Cook]


0.0.005 (2017-10-25)
--------------------
- Added `locate_central_positions` function. [Neil Cook]
- Added some code for locating central positions. [Neil Cook]
- Removed sys.exit (now in WLOG for key='error') add a warning that
  parameter dictionary key is duplicated and overwrite when loading
  other config file. [Neil Cook]
- Added keys argument to `write_file_to_master` added log statement to log
  updated calibDB. [Neil Cook]
- Moved `smoothed_boxmean_image` function to spirouLOCOR added function
  `measure_box_min_max`. [Neil Cook]
- Moved `smoothed_boxmean_image` function to spirouLOCOR. [Neil Cook]
- Corrected typo 'Adding' --> 'ADD' [Neil Cook]
- Updates init with boxsmoothedminmax moved boxsmoothed image to
  spirouLOCOR. [Neil Cook]
- Added config readme at top added some `cal_loc` variables added -[code]
  tag to comments to show where constant is used (currently) [Neil Cook]
- Added measure background function and `plot_y_miny_maxy` and
  `plot_min_ycc_loc_threshold` updated data2 to be a copy of
  `order_profile`. [Neil Cook]
- Changed updatemaster key to variable instead of hardcoded string.
  [Neil Cook]
- Added `cal_loc_RAW_spirou` section to changelog. [Neil Cook]
- First commit of spirouLOCOR (empty) [Neil Cook]
- Added `flip_image`, `convert_to_e`, and `smoothed_boxmean_image` functions.
  [Neil Cook]
- Added 'BoxSmoothedImage, ConvertToE and FlipImage functions. [Neil
  Cook]
- Added `loc_box_size` constant and localisation parameters section. [Neil
  Cook]
- Added construct image `order_profile` section and write `order_profile` to
  file/calibDB sections. [Neil Cook]
- Updated comment with spelling correction. [Neil Cook]


0.0.004 (2017-10-24)
--------------------
- Set out plan for code. [Neil Cook]
- Move config file. [Neil Cook]
- Add warning logger and remove sys.exit from all but logger. [Neil
  Cook]


0.0.003 (2017-10-16)
--------------------
- Added nbframes as a parameter to get in `run_startup` function. [Neil
  Cook]
- Changed `ACQTIME_KEY` to getting from config file added checks for
  `ACQTIME_KEY`. [Neil Cook]
- Allow `math_controller` arg "framemath" to be None --> pass straight
  through. [Neil Cook]
- Added `correct_for_dark` function changed raise value errors to WLOG +
  sys.exit(1) [Neil Cook]
- Added CorrectForDark to init. [Neil Cook]
- Added `ACQTIME_KEY` constant. [Neil Cook]
- Added read image file section added call to CorrectForDark function
  added resize image section. [Neil Cook]
- Added rotation and conversion to e- (commented out currently) [Neil
  Cook]
- Added `fiber_params` function added startup.RunInitialStartup call added
  custom startup.RunStartup call (with parameters to add for each prefix
  case) [Neil Cook]
- Added a requirement that calibdb is defined in `run_startup` function.
  [Neil Cook]
- Updated the README with summary of changes to `cal_DARK_spirou.py`.
  [Neil Cook]


0.0.002 (2017-10-13)
--------------------
- Added check for reduced directory (and make if needed) added check
  from calib directory (and make if needed) [Neil Cook]
- First commit added `update_datebase` and `put_file` functions added
  `get_check_lock_file`, `wriite_files_to_master`, and time2unixtime
  functions. [Neil Cook]
- Added PutFile and UpdateMaster functions. [Neil Cook]
- Added writeimage and `copy_original_keys` functions. [Neil Cook]
- Added readimage and writeimage function to init. [Neil Cook]
- Added dark quality control parameters added calibDB parameters. [Neil
  Cook]
- Added short name to `measure_dark` function added `dadead_{0}` to
  parameter dictionary (p) added comments dictionary from ReadImage
  added quality control section added save dark to fits section added
  save bad pixel mask added calibDB update. [Neil Cook]
- Added more TODO's regarding user defined config file. [Neil Cook]
- Added `DRS_PLOT` variable. [Neil Cook]
- Added image region plot added datacut plot added histogram plot. [Neil
  Cook]
- Added dark histogram variables. [Neil Cook]
- Added measure dark function changed pp --> p added dark measurement
  section added identification of bad pixels section. [Neil Cook]


0.0.001 (2017-10-12)
--------------------
- Added evaluate value function to try to interpret the value in a
  config file (i.e. set to float/int/bool before setting to a string)
  [Neil Cook]
- Added line separator. [Neil Cook]
- Added `__version__` [Neil Cook]
- Added keyslookup function added numpy import. [Neil Cook]
- First commit added resize function. [Neil Cook]
- Added GetKeys + ResizeImage function to init added `__version__` [Neil
  Cook]
- Added `ic_cc(x/y)_(blue/red)_(low/high)` variables added `qc_dark_Time`
  variable. [Neil Cook]
- Added read image and resize iamge sections. [Neil Cook]
- Modified `run_startup` to deal with no fitfilename file. [Neil Cook]
- Updated `DRS_ROOT` path. [Neil Cook]
- Added `readimage+read_raw_Data` documentation and
  `keylookup+math_controller` function. [Neil Cook]
- Added ReadImage and GetKey to init. [Neil Cook]
- Added ReadImage functions and got keys from header. [Neil Cook]
- Added initial files, added readimage and `read_raw_data` functions.
  [Neil Cook]
- Added initial files. [Neil Cook]
- Updated title of readme. [Neil Cook]


