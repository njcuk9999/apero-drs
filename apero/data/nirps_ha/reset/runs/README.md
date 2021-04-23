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

By default it processes every obs dir and every file that can be found in the `{DRS_DATA_RAW}` (default=`/data/raw/`)  directory.
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
id00001 = apero_ccf_spirou.py 2018-08-05 2295651o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00002 = apero_ccf_spirou.py 2018-08-05 2295652o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00004 = apero_ccf_spirou.py 2018-08-05 2295653o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
id00005 = apero_ccf_spirou.py 2018-08-05 2295654o_pp_e2dsff_tcorr_AB.fits --mask masque_Oct19_Vrp9_Berv33.mas --rv 11.9 --width 20 --step 0.05
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

where spec = OBJ_DARK + OBJ_FP

| recipe                                                          | SHORT_NAME |
| --------------------------------------------------------------- | ---------- | 
| apero_pp_master [master obs dir]                                | PPM        |
| apero_preprocess [every obs dir]                                | PP         |
| apero_dark_master                                               | DARKM      |
| apero_badpix [master obs dir]                                   | BADM       |
| apero_loc [DARK_FLAT; master obs dir]                           | LOCM       |
| apero_loc [FLAT_DARK; master obs dir]                           | LOCM       |
| apero_shape_master                                              | SHAPEM     |
| apero_shape [master obs dir]                                    | SHAPELM    |
| apero_flat [master obs dir]                                     | FLATM      |
| apero_leak_master [master_night]                                | LEAKM      |
| apero_thermal [DARK_DARK_INT; master obs dir]                   | THIM       |
| apero_thermal [DARK_DARK_TEL; master obs dir]                   | THTM       |
| apero_wave_master [master obs dir]                              | WAVEM      |
|                                                                 |            |
| apero_badpix [every obs dir]                                    | BAD        |
| apero_loc [DARK_FLAT; every obs dir]                            | LOC        |
| apero_loc [FLAT_DARK; every obs dir]                            | LOC        |
| apero_shape [every obs dir]                                     | SHAPE      |
| apero_flat [every obs dir]                                      | FF         |
| apero_thermal [DARK_DARK_INT; every obs dir]                    | THERMAL    |
| apero_thermal [DARK_DARK_TEL; every obs dir]                    | THERMAL    |
| apero_wave_night [every obs dir]                                | WAVE       |
| apero_extract [spec; every obs dir; ALL OBJECTS]                | EXTALL     |
| apero_leak [OBJ_FP; every obs dir; ALL OBJECTS]                 | LEAKALL    |
| apero_mk_tellu [spec; every obs dir; hot stars]                 | MKTELLU1   |
| apero_fit_tellu [spec; every obs dir; hot stars]                | MKTELLU2   |
| apero_mk_template [spec; every obs dir; hot stars]              | MKTELLU3   |
| apero_mk_tellu [spec; every obs dir; hot stars]                 | MKTELLU4   | 
| apero_fit_tellu [spec; every obs dir; non hot stars]            | FTELLU1    |
| apero_mk_template [spec; every obs dir; non hot stars]          | FTELLU2    |
| apero_fit_tellu [spec; every obs dir; non hot stars]            | FTELLU3    |
| apero_ccf [spec; fiber=AB; every obs dir]                       | CCF        |
| apero_postprocess [spec; fiber=AB; every obs dir]               | POSTALL    |

##### 2. `limited_seq`

Similar to `full_seq` but uses the `{TELLURIC_TARGETS}` and `{SCIENCE_TARGETS}` 
to filter the objects processed

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

where spec = OBJ_DARK + OBJ_FP

| recipe                                                                | SHORT_NAME |
| --------------------------------------------------------------------- | ---------- | 
| apero_pp_master [master obs dir]                                      | PPM        |
| apero_preprocess [every obs dir]                                      | PP         |
| apero_dark_master                                                     | DARKM      |
| apero_badpix [master obs dir]                                         | BADM       |
| apero_loc [DARK_FLAT; master obs dir]                                 | LOCMC      |
| apero_loc [FLAT_DARK; master obs dir]                                 | LOCMAB     |
| apero_shape_master                                                    | SHAPEM     |
| apero_shape [master obs dir]                                          | SHAPELM    |
| apero_flat [master obs dir]                                           | FLATM      |
| apero_leak_master [master_night]                                      | LEAKM      |
| apero_thermal [DARK_DARK_INT; master obs dir]                         | THIM       |
| apero_thermal [DARK_DARK_TEL; master obs dir]                         | THTM       |
| apero_wave_master [master obs dir]                                    | WAVEM      |
|                                                                       |            |
| apero_badpix [every obs dir]                                          | BAD        |
| apero_loc [DARK_FLAT; every obs dir]                                  | LOCC       |
| apero_loc [FLAT_DARK; every obs dir]                                  | LOCAB      |
| apero_shape [every obs dir]                                           | SHAPE      |
| apero_flat [every obs dir]                                            | FF         |
| apero_thermal [DARK_DARK_INT; every obs dir]                          | THERMAL    |
| apero_thermal [DARK_DARK_TEL; every obs dir]                          | THERMAL    |
| apero_wave_night [every obs dir]                                      | WAVE       |
| apero_extract [spec + pol; every obs dir; TELLURIC_TARGETS]           | EXTTELL    |
| apero_extract [spec + pol; every obs dir; SCIENCE_TARGETS]            | EXTOBJ     |
| apero_leak [OBJ_FP + POLAR_FP; every obs dir; TELLURIC_TARGETS]       | LEAKTELL   |
| apero_leak [OBJ_FP + POLAR_FP; every obs dir; SCIENCE_TARGETS]        | LEAKOBJ    |
| apero_mk_tellu [spec + pol; every obs dir; TELLURIC_TARGETS]          | MKTELLU1   |
| apero_fit_tellu [spec + pol; every obs dir; TELLURIC_TARGETS]         | MKTELLU2   |
| apero_mk_template [spec + pol; every obs dir; TELLURIC_TARGETS]       | MKTELLU3   |
| apero_mk_tellu [spec + pol; every obs dir; TELLURIC_TARGETS]          | MKTELLU4   | 
| apero_fit_tellu [spec + pol; every obs dir; SCIENCE_TARGETS]          | FTELLU1    |
| apero_mk_template [spec + pol; every obs dir; SCIENCE_TARGETS]        | FTELLU2    |
| apero_fit_tellu [spec + pol; every obs dir; SCIENCE_TARGETS]          | FTELLU3    |
| apero_ccf [spec + pol; fiber=AB; every obs dir]                       | CCF        |
| apero_postprocess [spec + pol; fiber=AB; every obs dir; TELLURIC_TARGETS] | TELLPOST   |
| apero_postprocess [spec + pol; fiber=AB; every obs dir; SCIENCE_TARGETS] | SCIPOST    |

##### 3. preprocessing runs

Only run the preprocessing recipe


###### 3a: `pp_seq`

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| apero_pp_master [master obs dir]                                    | PPM        |
| apero_preprocess [every obs dir]                                    | PP         |


###### 3b: `pp_seq_opt`

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                                   | SHORT_NAME |
| ------------------------------------------------------------------------ | ---------- | 
| apero_preprocess [every obs dir; OBJECT="Calibration"]                   | PP_CAL     |
| apero_preprocess [every obs dir; SCIENCE_TARGETS]                        | PP_SCI     |
| apero_preprocess [every obs dir; TELLURIC_TARGETS]                       | PP_TEL     |
| apero_preprocess [every obs dir; HC1_HC1]                                | PP_HC1HC1  |
| apero_preprocess [every obs dir; DARK_FP]                                | PP_DFP     |
| apero_preprocess [every obs dir; FP_DARK]                                | PP_FPD     |
| apero_preprocess [every obs dir; LFC_LFC]                                | PP_LFC     |
| apero_preprocess [every obs dir; LFC_FP]                                 | PP_LFCFP   |
| apero_preprocess [every obs dir; FP_LFC]                                 | PP_FPLFC   |



##### 4. `master_seq`

Only run the master recipes

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| apero_dark_master                                                   | DARKM      |
| apero_badpix [master obs dir]                                       | BADM       |
| apero_loc [DARK_FLAT; master obs dir]                               | LOCMB      |
| apero_loc [FLAT_DARK; master obs dir]                               | LOCMA      |
| apero_shape_master                                                  | SHAPEM     |
| apero_shape [master obs dir]                                        | SHAPELM    |
| apero_flat [master obs dir]                                         | FLATM      |
| apero_leak_master [master_night]                                    | LEAKM      |
| apero_thermal [DARK_DARK_INT; master obs dir]                       | THIM       |
| apero_thermal [DARK_DARK_TEL; master obs dir]                       | THTM       |
| apero_wave_master [master obs dir]                                  | WAVEM      |



##### 5. `calib_seq`

Only run the nightly calibration sequences and make a complete calibration database.
(assumes that the master run is done i.e. `master_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                              | SHORT_NAME |
| ------------------------------------------------------------------- | ---------- | 
| apero_badpix [every obs dir]                                        | BAD        |
| apero_loc [DARK_FLAT; every obs dir]                                | LOCB       |
| apero_loc [FLAT_DARK; every obs dir]                                | LOCA       |
| apero_shape [every obs dir]                                         | SHAPE      |
| apero_flat [every obs dir]                                          | FF         |
| apero_wave_night [every obs dir]                                    | WAVE       |



##### 5. `tellu_seq`

Only run the steps required to process `{TELLURIC_TARGETS}` and make the telluric database.
(assumes that calibrations have been done i.e. `calib_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                                 | SHORT_NAME |
| ---------------------------------------------------------------------- | ---------- | 
| apero_extract [spec; every obs dir; TELLURIC_TARGETS]                  | EXTTELL    |
| apero_leak [OBJ_FP; every obs dir; TELLURIC_TARGETS]                   | LEAKTELL   |
| apero_mk_tellu [spec; every obs dir; TELLURIC_TARGETS]                 | MKTELLU1   |
| apero_fit_tellu [spec; every obs dir; TELLURIC_TARGETS]                | MKTELLU2   |
| apero_mk_template [spec; every obs dir; TELLURIC_TARGETS]              | MKTELLU3   |
| apero_mk_tellu [spec; every obs dir; TELLURIC_TARGETS]                 | MKTELLU4   | 
| apero_postprocess [spec; fiber=AB; every obs dir; TELLURIC_TARGETS]    | TELLPOST   |


##### 6. `science_seq`

Only run the steps required to process `{SCIENCE_TARGETS}` 
(assumes that calibrations and tellurics have been done i.e. `calib_seq` and `tellu_seq`)

where `recipe` is the recipe run and `short_name` is the name used in the `RUN_INI_FILES`
i.e. for RUN_XXXX and SKIP_XXXX.

| recipe                                                                      | SHORT_NAME |
| --------------------------------------------------------------------------- | ---------- | 
| apero_extract [spec; every obs dir; SCIENCE_TARGETS]                        | EXTOBJ     |
| apero_leak [OBJ_FP; every obs dir; SCIENCE_TARGETS]                         | LEAKOBJ    |
| apero_fit_tellu [spec; every obs dir; SCIENCE_TARGETS]                      | FTELLU1    |
| apero_mk_template [spec; every obs dir; SCIENCE_TARGETS]                    | FTELLU2    |
| apero_fit_tellu [spec; every obs dir; SCIENCE_TARGETS]                      | FTELLU3    |
| apero_ccf [spec; fiber=AB; every obs dir]                                   | CCF        |
| apero_postprocess [spec; fiber=AB; every obs dir; SCIENCE_TARGETS]          | SCIPOST    |

##### 7. `quick_seq`

This is the quick look sequence (only runs extraction to get snr) does not
run berv, thermal correction, s1d creation, ccf etc - do not use these outputs
for science or the rest of the steps. This is done by adding the `--quicklook=True`
to the apero_extract recipe input.

| recipe                                                                  | SHORT_NAME |
| ----------------------------------------------------------------------- | ---------- | 
| apero_extract [spec; every obs dir; SCIENCE_TARGETS; --quicklook=True]  | EXTOBJ     |


##### 8. `eng_seq`

This is full of engineering sequences that probably will only be used with most options turned off.

| recipe                                                                | SHORT_NAME |
| --------------------------------------------------------------------- | ---------- | 
| apero_extract [HCONE_HCONE; every obs dir]                            | EXT_HC1HC1 |
| apero_extract [FP_FP; every obs dir]                                  | EXT_FPFP   |
| apero_extract [DARK_FP; every obs dir]                                | EXT_DFP    |
| apero_extract [FP_DARK; every obs dir]                                | EXT_FPD    |
| apero_extract [DARK_DARK_SKY; every obs dir]                          | EXT_SKY    |
| apero_extract [LFC_LFC; every obs dir]                                | EXT_LFC    |
| apero_extract [LFC_FP; every obs dir]                                 | EXT_LFCFP  |
| apero_extract [FP_LFC; every obs dir]                                 | EXT_FPLFC  |

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

Note one has to run `apero_badpix` and `apero_loc` calibrations for the master 
observation directory in order to run the shape master recipe.

2) Run all the preprocessing

Note one must preprocess ALL nights for the master to work) - it will only 
combine darks(for the master dark) and fps (for the master shape) from 
preprocessed data (i.e. use sequence `pp_seq`)



3) Run the master sequence (i.e. use sequence `master_seq`)
i.e. 
```
apero_dark_master
apero_badpix [master observation directory]
apero_loc [DARK_FLAT; master observation directory]
apero_loc [FLAT_DARK; master observation directory]
apero_shape_master
apero_shape [master observation directory
apero_flat [master observation directory]
apero_leak_master
apero_thermal [DARK_DARK_INT; master observation directory]
apero_thermal [DARK_DARK_TEL; master observation directory]
apero_wave_master
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
apero_badpix [every obs dir]
apero_loc [DARK_FLAT; every obs dir]
apero_loc [FLAT_DARK; every obs dir]
apero_shape [every obs dir]
apero_flat [every obs dir]
apero_thermal [DARK_DARK_INT; every obs dir]
apero_thermal [DARK_DARK_TEL; every obs dir]
apero_wave_night [every obs dir]
```

The telluric star sequence is as follows:
```
apero_extract [spec; every obs dir; TELLURIC_TARGETS]
apero_leak [OBJ_FP; every obs dir; TELLURIC_TARGETS]
apero_mk_tellu [spec; every obs dir; TELLURIC_TARGETS]
apero_fit_tellu [spec; every obs dir; TELLURIC_TARGETS]
apero_mk_template [spec; every obs dir; TELLURIC_TARGETS]
apero_mk_tellu [spec; every obs dir; TELLURIC_TARGETS]
```

Note one must run all tellurics before running science. Not having
sufficient tellurics processed will lead to poor telluric correction for the
science.


The science star sequence is as follows:
```
apero_extract [spec; every obs dir; SCIENCE_TARGETS]
apero_leak [OBJ_FP; every obs dir; SCIENCE_TARGETS]
apero_fit_tellu [spec; every obs dir; SCIENCE_TARGETS]
apero_mk_template [spec; every obs dir; SCIENCE_TARGETS]
apero_fit_tellu [spec; every obs dir; SCIENCE_TARGETS]
apero_ccf [spec; fiber=AB; every obs dir; SCIENCE_TARGETS]
```
