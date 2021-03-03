# The Run file README

Note: Please do not change the example run files (these will be overwritten on reset)

Last updated: 2020-03-21

### Using APERO processing recipe

`apero_processing.py` can be used in a few different ways but always requires the following

1) The instrument (`SPIROU`)

2) The run file to execute

i.e.
```
tools/bin/apero_processing.py SPIROU mini_run.ini
```

#### The processing run files ( `{RUN_FILE}`)

These are located in the `{DRS_DATA_RUNS}` (default=`/data/runs/`) directory. They can be used in two ways

##### 1) Process automatically

By default it processes every night and every file that can be found in the `{DRS_DATA_RAW}` (default=`/data/raw/`)  directory.
One can turn on specific nights to process in several ways 
(a) setting the `NIGHT_NAME` in the selected `{RUN_FILE}`
(b) adding a night to the `EXCLUDE_OBS_DIRS` (exclude list = reject) or `INCLUDE_OBS_DIRS` (include list = keep)
(c) adding an extra argument to `apero_processing.py` (`--obs_dir`, `--exclude_obs_dirs`, `--inculde_obs_dirs`) 

One can also just process a single file by adding an extra argument to `apero_processing.py` (`--filename`)

One can also tell the recipe to only process specific targets 
(when the recipes can accept targets -- i.e. extraction, telluric fitting, CCF) 
by changing the `TELLURIC_TARGETS` key for tellurics or the `SCIENCE_TARGETS` key for science objects in the `{RUN_FILE}`

For processing automatically `id00000` should be set to one of the sequence names (see below) 
-- note that the id number should always be unique.

Note one can turn on/off recipes in a sequence by setting `RUN_{RECIPE}` to False, or skip files that already exist by 
setting `SKIP_{RECIPE}` to False - these will only be affected if `{RECIPE}` is in the sequence.

Note that all found filenames will be processed in parallel if `CORES` set to a number greater than 1.


##### 2) Process a set of specific instructions

One can also define a specific set of instructions (similar to just running recipes individually), but batch them
and parallize them (if `CORES` set to a number greater than 1). They will be processed in the order given by the id number
-- note that the id number should always be unique.

i.e. 
```
id00001 = cal_ccf_spirou.py 2018-08-05 2295651o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00002 = cal_ccf_spirou.py 2018-08-05 2295652o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00004 = cal_ccf_spirou.py 2018-08-05 2295653o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00005 = cal_ccf_spirou.py 2018-08-05 2295654o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
```

#### The available sequences

Sequences are defined in the `apero/core/instruments/{INSTRUMENT}/recipe_definitions.py` script.
These enable the user to quickly process sets of data in specific orders based on their needs.

Note these can be combined in any order the user wants but some assume others have been completed first (in terms of files needed).
i.e. 

```
id00001 = master_seq
id00002 = calib_seq
id00003 = tellu_seq
id00004 = science_seq
```

Currently defined sequences are:

##### 1. `full_seq`

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.


| recipe                                                          | SHORT_NAME |
| --------------------------------------------------------------- | ---------- | 
| cal_preprocessing                                               | PP         |
| cal_dark_master                                                 | DARKM      |
| cal_badpix [master obs dir]                                     | BADM       |
| cal_loc [DARK_FLAT; master obs dir]                             | LOCM       |
| cal_loc [FLAT_DARK; master obs dir]                             | LOCM       |
| cal_shape_master                                                | SHAPEM     |
| cal_shape [master obs dir]                                      | SHAPELM    |
| cal_ff [master obs dir]                                         | FLATM      |
| cal_leak_master [master_night]                                  | LEAKM      |
| cal_thermal [DARK_DARK_INT; master obs dir]                     | THIM       |
| cal_thermal [DARK_DARK_TEL; master obs dir]                     | THTM       |
| cal_wave_master                                                 | WAVEM      |
|                                                                 |            |
| cal_badpix [every night]                                        | BAD        |
| cal_loc [DARK_FLAT; every night]                                | LOC        |
| cal_loc [FLAT_DARK; every night]                                | LOC        |
| cal_shape [every night]                                         | SHAPE      |
| cal_ff [every night]                                            | FF         |
| cal_thermal [DARK_DARK_INT; every night]                        | THERMAL    |
| cal_thermal [DARK_DARK_TEL; every night]                        | THERMAL    |
| cal_wave_night [every night]                                    | WAVE       |
| cal_extract [OBJ_DARK + OBJ_FP; every night; ALL OBJECTS]       | EXTALL     |
| cal_leak [OBJ_FP; every night; ALL OBJECTS]                     | LEAKALL    |
| obj_mk_tellu_db                                                 | MKTELLDB   |
| obj_fit_tellu_db                                                | FTELLDB    |
| cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night]              | CCF        |


##### 2. `limited_seq`

Similar to `full_seq` but uses the `{TELLURIC_TARGETS}` and `{SCIENCE_TARGETS}` 
to filter the objects processed

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_preprocessing                                                   | PP         |
| cal_dark_master                                                     | DARKM      |
| cal_badpix [master obs dir]                                         | BADM       |
| cal_loc [DARK_FLAT; master obs dir]                                 | LOCM       |
| cal_loc [FLAT_DARK; master obs dir]                                 | LOCM       |
| cal_shape_master                                                    | SHAPEM     |
| cal_shape [master obs dir]                                          | SHAPELM    |
| cal_ff [master obs dir]                                             | FLATM      |
| cal_leak_master [master_night]                                      | LEAKM      |
| cal_thermal [DARK_DARK_INT; master obs dir]                         | THIM       |
| cal_thermal [DARK_DARK_TEL; master obs dir]                         | THTM       |
| cal_wave_master                                                     | WAVEM      |
|                                                                     |            |
| cal_badpix [every night]                                            | BAD        |
| cal_loc [DARK_FLAT; every night]                                    | LOC        |
| cal_loc [FLAT_DARK; every night]                                    | LOC        |
| cal_shape [every night]                                             | SHAPE      |
| cal_ff [every night]                                                | FF         |
| cal_thermal [DARK_DARK_INT; every night]                            | THERMAL    |
| cal_thermal [DARK_DARK_TEL; every night]                            | THERMAL    |
| cal_wave_night [every night]                                        | WAVE       |
| cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]      | EXTTELL    |
| cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]       | EXTOBJ     |
| cal_leak [OBJ_FP; every night; TELLURIC_TARGETS]                    | LEAKTELL   |
| cal_leak [OBJ_FP; every night; SCIENCE_TARGETS]                     | LEAKOBJ    |
| obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]     | MKTELLU1   |
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]    | MKTELLU2   |
| obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]  | MKTELLU3   |
| obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]     | MKTELLU4   | 
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]     | FTELLU1    |
| obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]   | FTELLU2    |
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]     | FTELLU3    |
| cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night]                  | CCF        |


##### 3. preprocessing runs

Only run the preprocessing recipe


###### 3a: `pp_seq`

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_preprocessing                                                   | PP         |


###### 3b: `pp_seq_opt`

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                                   | SHORT_NAME |
| ------------------------------------------------------------------------ | ---------- | 
| cal_preprocessing [OBJ_DARK + OBJ_FP; every night; OBJECT="Calibration"] | PP_CAL     |
| cal_preprocessing [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]      | PP_SCI     |
| cal_preprocessing [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]     | PP_TEL     |




##### 4. `master_seq`

Only run the master recipes

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_dark_master                                                     | DARKM      |
| cal_badpix [master obs dir]                                         | BADM       |
| cal_loc [DARK_FLAT; master obs dir]                                 | LOCM       |
| cal_loc [FLAT_DARK; master obs dir]                                 | LOCM       |
| cal_shape_master                                                    | SHAPEM     |
| cal_shape [master obs dir]                                          | SHAPELM    |
| cal_ff [master obs dir]                                             | FLATM      |
| cal_leak_master [master_night]                                      | LEAKM      |
| cal_thermal [DARK_DARK_INT; master obs dir]                         | THIM       |
| cal_thermal [DARK_DARK_TEL; master obs dir]                         | THTM       |
| cal_wave_master                                                     | WAVEM      |



##### 5. `calib_seq`

Only run the nightly calibration sequences and make a complete calibration database.
(assumes that the master run is done i.e. `master_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_badpix [every night]                                            | BAD        |
| cal_loc [DARK_FLAT; every night]                                    | LOC        |
| cal_loc [FLAT_DARK; every night]                                    | LOC        |
| cal_shape [every night]                                             | SHAPE      |
| cal_ff [every night]                                                | FF         |
| cal_thermal [DARK_DARK_INT; every night]                            | THERMAL    |
| cal_thermal [DARK_DARK_TEL; every night]                            | THERMAL    |
| cal_wave_night [every night]                                        | WAVE       |



##### 5. `tellu_seq`

Only run the steps required to process `{TELLURIC_TARGETS}` and make the telluric database.
(assumes that calibrations have been done i.e. `calib_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]      | EXTTELL    |
| cal_leak [OBJ_FP; every night; TELLURIC_TARGETS]                    | LEAKTELL   |
| obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]     | MKTELLU1   |
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]    | MKTELLU2   |
| obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]  | MKTELLU3   |
| obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]     | MKTELLU4   | 



##### 6. `science_seq`

Only run the steps required to process `{SCIENCE_TARGETS}` 
(assumes that calibrations and tellurics have been done i.e. `calib_seq` and `tellu_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]       | EXTOBJ     |
| cal_leak [OBJ_FP; every night; SCIENCE_TARGETS]                     | LEAKOBJ    |
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]     | FTELLU1    |
| obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]   | FTELLU2    |
| obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]     | FTELLU3    |
| cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night]                  | CCF        |




##### 7. `eng_seq`

This is full of engineering sequences that probably will only be used with most options turned off.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| cal_extract [HCONE_HCONE; every night]                              | EXTHC1     |
| cal_extract [FP_FP; every night]                                    | EXTFPFP    |
| cal_extract [DARK_FP; every night]                                  | EXTDFP     |



---

# APERO run order
[Back to top](#apero---a-pipeline-to-reduce-observations)

As mentioned above this depends on what sequence you wish to use but as
an overview the steps are as follows

## 1) Choose a master observation directory

(i.e. 2018-09-25)

If using the processing script one must set this in that file else
when choosing arguments one must use them from the master observation directory
choosen.

Note one has to run `cal_badpix` and `cal_loc` calibrations for the master 
observation directory in order to run the shape master recipe.

2) Run all the preprocessing

Note one must preprocess ALL nights for the master to work) - it will only 
combine darks(for the master dark) and fps (for the master shape) from 
preprocessed data (i.e. use sequence `pp_seq`)



3) Run the master sequence (i.e. use sequence `master_seq`)
i.e. 
```
cal_dark_master
cal_badpix [master observation directory]
cal_loc [DARK_FLAT; master observation directory]
cal_loc [FLAT_DARK; master observation directory]
cal_shape_master
cal_shape [master observation directory
cal_ff [master observation directory]
cal_leak_master
cal_thermal [DARK_DARK_INT; master observation directory]
cal_thermal [DARK_DARK_TEL; master observation directory]
cal_wave_master
```


Note if any step in the master sequence fails you cannot continue with the
night runs.


4) Run the night sequences

These must be in this order but could be night-by-night or
all of one then all of the other) - the order here only matters when a file is 
missed/corrupt or does not pass quality control. If all badpix are run first
then the loc will have the best chance at having bad pixel correction from a
night close to it. If one runs night by night then the next step will only 
have access to calibrations from nights already processed.

Note again one should extract all telluric stars and run the telluric sequence
(to create a telluric database) BEFORE correcting any science extraction.

The calibration sequence is as follows:
```
cal_badpix [every night]
cal_loc [DARK_FLAT; every night]
cal_loc [FLAT_DARK; every night]
cal_shape [every night]
cal_ff [every night]
cal_thermal [DARK_DARK_INT; every night]
cal_thermal [DARK_DARK_TEL; every night]
cal_wave_night [every night]
```

The telluric star sequence is as follows:
```
cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
cal_leak [OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
```

Note one must run all tellurics before running science. Not having
sufficient tellurics processed will lead to poor telluric correction for the
science.


The science star sequence is as follows:
```
cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
cal_leak [OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night; SCIENCE_TARGETS]
```
