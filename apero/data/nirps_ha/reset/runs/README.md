# The Run file README

Note: Please do not change the example run files (these will be overwritten on reset)


## Using `processing.py`

`processing.py` can be used in a few different ways but always requires the following

1) The instrument (`SPIROU`)

2) The run file to execute

i.e.
```
apero/tools/bin/processing.py SPIROU limited_run.ini
```

## The processing run files ( `{RUN_FILE}`)

These are located in the `{DRS_DATA_RUNS}` (default=`/data/runs/`) directory. They can be used in two ways

### 1) Process automatically

By default it processes every night and every file that can be found in the `{DRS_DATA_RAW}` (default=`/data/raw/`)  directory.
One can turn on specific nights to process in several ways 
(a) setting the `NIGHT_NAME` in the selected `{RUN_FILE}`
(b) adding a night to the `BNIGHTNAMES` (blacklist = reject) or `WNIGHTNAMES` (whitelist = keep)
(c) adding an extra argument to `processing.py` (`--nightname`, `--bnightnames`, `--wnightnames`) 

One can also just process a single file by adding an extra argument to `processing.py` (`--filename`)

One can also tell the recipe to only process specific targets 
(when the recipes can accept targets -- i.e. extraction, telluric fitting, CCF) 
by changing the `TELLURIC_TARGETS` key for tellurics or the `SCIENCE_TARGETS` key for science objects in the `{RUN_FILE}`

For processing automatically `id00000` should be set to one of the sequence names (see below) 
-- note that the id number should always be unique.

Note one can turn on/off recipes in a sequence by setting `RUN_{RECIPE}` to False, or skip files that already exist by 
setting `SKIP_{RECIPE}` to False - these will only be affected if `{RECIPE}` is in the sequence.

Note that all found filenames will be processed in parallel if `CORES` set to a number greater than 1.


### 2) Process a set of specific instructions

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

## The available sequences

Sequences are defined in the `apero/core/instruments/{INSTRUMENT}/recipe_definitions.py` script.
These enable the user to quickly process sets of data in specific orders based on their needs.

Note these can be combined in any order the user wants but some assume others have been completed first (in terms of files needed).
i.e. 

```
id00001 = master_run
id00002 = calib_run
id00003 = tellu_run
id00004 = science_run
```

Currently defined sequences are:

### 1. `full_run`

```
cal_preprocessing
cal_dark_master
cal_badpix [master night]
cal_loc [DARK_FLAT; master night]
cal_loc [FLAT_DARK; master night]
cal_shape_master
cal_badpix [every night]
cal_loc [DARK_FLAT; every night]
cal_loc [FLAT_DARK; every night]
cal_shape [every night]
cal_ff [every night]
cal_thermal [every night]
cal_wave [HCONE_HCONE + FP_FP; every night]
cal_extract [OBJ_DARK + OBJ_FP; every night; ALL OBJECTS]
obj_mk_tellu_db
obj_fit_tellu_db
cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night]
```

### 2. `limited_run`

Similar to `full_run` but uses the `{TELLURIC_TARGETS}` and `{SCIENCE_TARGETS}` 
to filter the objects processed

```
cal_preprocessing
cal_dark_master
cal_badpix [master night]
cal_loc [DARK_FLAT; master night]
cal_loc [FLAT_DARK; master night]
cal_shape_master
cal_badpix [every night]
cal_loc [DARK_FLAT; every night]
cal_loc [FLAT_DARK; every night]
cal_shape [every night]
cal_ff [every night]
cal_thermal [every night]
cal_wave [HCONE_HCONE; every night]
cal_wave [HCONE_HCONE + FP_FP; every night]
cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night; SCIENCE_TARGETS]
```

### 3. `master_run`

Only run the master recipes

```
cal_preprocessing
cal_dark_master
cal_badpix [master night]
cal_loc [DARK_FLAT; master night]
cal_loc [FLAT_DARK; master night]
cal_shape_master
```

### 4. `calib_run`

Only run the nightly calibration sequences and make a complete calibration database.
(assumes that the master run is done i.e. `master_run`)

```
cal_badpix [every night]
cal_loc [DARK_FLAT; every night]
cal_loc [FLAT_DARK; every night]
cal_shape [every night]
cal_ff [every night]
cal_thermal [every night]
cal_wave [HCONE_HCONE; every night]
cal_wave [HCONE_HCONE + FP_FP; every night]
```

### 5. `tellu_run`

Only run the steps required to process `{TELLURIC_TARGETS}` and make the telluric database.
(assumes that calibrations have been done i.e. `calib_run`)

```
cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
```

### 6. `science_run`

Only run the steps required to process `{SCIENCE_TARGETS}` 
(assumes that calibrations and tellurics have been done i.e. `calib_run` and `tellu_run`)

```
cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night; SCIENCE_TARGETS]
```
