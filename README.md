# APERO - A PipelinE to Reduce Observations

##  Latest version

- master (long term stable) V0.5.000
- developer (tested) V0.6.001
- working (untested) V0.6.001

---
---

## Pre-Installation

#### 1. clone this repository

```bash
git clone https://github.com/njcuk9999/apero-drs
```

This may take some time (in future most of the data required will be a separate download),
and we still have many (now redundant) files from the spirou_py3 repository

Note if you have a git from the spirou_py3 you need to redirect it:
```bash
cd ./apero-drs
git remote set-url origin https://github.com/njcuk9999/apero-drs
```

---

#### 2. change to the repository directory
```bash
cd ./apero-drs
```

---

#### 3. checkout the correct branch

- For Master version: 
```
git checkout master
```
- For Developer version:
```
git checkout developer
```
- For Working version:
```
git checkout working
```

---
---

## Installation (Currently only for `developer` and `working` versions)

Make sure pre-installation is done first!

---

#### 1. run the installation script
```bash
python setup/install.py
```

---

#### 2. Follow the step-by-step guide:

A. `User config path`: This is the path where your configuration will be saved.
If it doesn't exist you will be prompted to create it. 
(This will be referred to as `DRS_UCONFIG` from now on (default is `/home/user/apero/`)

B. `Settings for {INSTRUMENT}`: Install {INSTRUMENT}. If yes it will install the 
instrument if not then it will not install the instrument. Currently only 
SPIRou is supported.

C. `Set up paths individually`. If [Y]es it will allow you to set each path separately
(i.e. for raw, tmp, reduced, calibDB etc). If no you will just set one path and
all folders (raw, tmp, reduced, calibDB etc)) will be created under this directory.

D. `Setting the directories` (either one directory or each of the sub-directories
required - i.e. raw, tmp, reduced, calibDB etc)

E. `Clean install?` __WARNING__: If you type [Y]es you will be prompted (later) to reset
the directories this means any previous data in these directories will be removed.
Note you can always say later to individual cases.


F. This process will then repeat for all instruments. __NOTE: Currently only SPIRou is supported__

G. In the `Copying files` step if you asked for a clean install if directories 
are not empty you will be prompted to reset them one-by-one 
(__NOTE: THIS WILL REMOVE ALL DATA FROM THIS SPECIFIC DIRECTORY)__

---

#### 3. Installation is then complete

---

#### 4. Running apero

To run apero you need to do __one__ of the following

__NOTE__: these three are equivalent only do __one__


##### i) alias to apero to your startup script (RECOMMENDED)
For example 

`alias apero "source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup"`  (tcsh/csh)
`alias apero=""source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup"`  (bash)

to `~/.bashrc` or `~/.bash_profile` or  `~/.tcshrc` or `~/.profile`

and type `apero` every time you open a new terminal 


##### ii) source environmental variables directly

 `source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup`
 and type this command every time you open a new terminal

where: 
 - `{DRS_UCONFIG}` is the config path set up in step __2A__
 - `{SYSTEM}` is either `bash` or `sh` depending on your shell


##### iii) add the contents of `{DRS_UCONFIG}/config/apero.{SYSTEM}.setup` to your startup script

i.e. one of the following `~/.bashrc`, `~/.bash_profile`, `~/.tcshrc`, `~/.profile`
(apero will be ready to use in every new terminal).

For example adding to `~/.bashrc`:
```bash
# setup paths
export PATH="/scratch/apero_dev/apero/tools/bin":$PATH
export PATH="/scratch/apero_dev/bin":$PATH
export PATH="/scratch/apero_dev/":$PATH

# setup up python path
export PYTHONPATH="/scratch/apero_dev/apero/tools/bin":$PYTHONPATH
export PYTHONPATH="/scratch/apero_dev/bin":$PYTHONPATH
export PYTHONPATH="/scratch/apero_dev/":$PYTHONPATH

# setup drs config path
export DRS_UCONFIG="/home/user/apero/config/"

# force numpy  to only use 1 core max
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

# run the validation script for SPIROU
python /scratch/apero_dev/apero/tools/bin/validate.py SPIROU
```


---


## TODO

- finish `obj_spec_spirou` and `obj_pol_spirou` [Do not use them now]
- output files like CFHT (e.fits, p.fits, v.fits etc)
- data separate download from DRS
- setup instrument
- move `object_query_list.fits` to `calibDB`
- write documentation and paper
- go through all summary plots and decide which plots, write figure captions,
improve plots, write quality control description, decide which header keys to print
- add `plot== 3` (all debug plots shown) and `plot==4` (all debug plots saved) modes
- display func for all functions
- add raw (via run) to file explorer
- Windows compatibility
- add doc strings to all functions, descriptions to all constants, review all 
constant min/max/dtypes
- add more debug printouts
- deal with all python warnings
- add EA mask generation from templates
- add EA template matching 

---

## Currently known issues

- wave solution sometimes using HC wave solution sometimes FP wave solution - WHY?
- telluric correction is slightly worse than before (due to wavelength solution?)
- CCF still showing problems with noise (maybe same problem as telluric correction?)
- BERV file gets locked (Ctrl+C to unlock) - WHY?
- index.fits not found - during parallel writes to index.fits - locking system is flawed - is this fixed?
- file explorer is broken (needs updating)
- 

---
---

## Using APERO

You can use apero to individually run recipes or process a set of files

---

### Using apero individually

Recipes (the scripts to run) are stored in the `./apero/recipes/{instrument}` path
once installed these recipes are copied to the `./bin/` directory and can be used 
from the command line or in python or in ipython (recommended).

i.e. from the shell
```bash
cal_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. using python
```bash
python cal_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. in ipython
```
run apero/recipes/spirou/cal_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. in a python script
```python
import cal_badpix_spirou

ll = cal_badpix_spirou.main('night_name', flatfiles='file1.fits', darkfiles='file2.fits')
```

__NOTE__: there is a --help option available for every recipe

---

### Using `processing.py`

`processing.py` can be used in a few different ways but always requires the following

1) The instrument (`SPIROU`)

2) The run file to execute

i.e.
```
apero/tools/bin/processing.py SPIROU limited_run.ini
```

#### The processing run files ( `{RUN_FILE}`)

These are located in the `{DRS_DATA_RUNS}` (default=`/data/runs/`) directory. They can be used in two ways

##### 1) Process automatically

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
id00001 = master_run
id00002 = calib_run
id00003 = tellu_run
id00004 = science_run
```

Currently defined sequences are:

##### 1. `full_run`

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

##### 2. `limited_run`

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

##### 3. `master_run`

Only run the master recipes

```
cal_preprocessing
cal_dark_master
cal_badpix [master night]
cal_loc [DARK_FLAT; master night]
cal_loc [FLAT_DARK; master night]
cal_shape_master
```

##### 4. `calib_run`

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

##### 5. `tellu_run`

Only run the steps required to process `{TELLURIC_TARGETS}` and make the telluric database.
(assumes that calibrations have been done i.e. `calib_run`)

```
cal_extract [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
obj_mk_tellu [OBJ_DARK + OBJ_FP; every night; TELLURIC_TARGETS]
```

##### 6. `science_run`

Only run the steps required to process `{SCIENCE_TARGETS}` 
(assumes that calibrations and tellurics have been done i.e. `calib_run` and `tellu_run`)

```
cal_extract [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_mk_template [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
obj_fit_tellu [OBJ_DARK + OBJ_FP; every night; SCIENCE_TARGETS]
cal_ccf [OBJ_DARK + OBJ_FP; fiber=AB; every night; SCIENCE_TARGETS]
```

