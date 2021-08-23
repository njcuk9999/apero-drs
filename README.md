# APERO - A PipelinE to Reduce Observations

Last updated: 2020-07-04

## Contents

1) [Latest version](#1-latest-version)
2) [Pre-Installation](#2-pre-installation)
3) [Installation](#3-installation)
4) [To Do and Known Issues](#4-todo-and-currently-known-issues)
5) [Using APERO](#5-using-apero)
    - [Using apero individually](#51-using-apero-individually)
    - [Using APERO processing recipe](#52-using-apero-processing-recipe)
6) [APERO run order](#6-apero-run-order)
7) [APERO outputs](#7-apero-outputs)
8) [APERO recipes](#8-APERO-Recipes)
    - [preprocessing](#81-preprocessing-recipe)
    - [dark master](#82-dark-master-recipe)
    - [bad pixel](#83-bad-pixel-correction-recipe)
    - [localisation](#84-localisation-recipe)
    - [shape master](#85-shape-master-recipe)
    - [shape (local)](#86-shape-per-night-recipe)
    - [flat/blaze](#87-flatblaze-correction-recipe)
    - [thermal](#88-thermal-correction-recipe)
    - [leak master](#89-master-leak-correction-recipe)
    - [wavelength master](#810-master-wavelength-solution-recipe)
    - [wavelength (local)](#811-nightly-wavelength-solution-recipe)
    - [extraction](#812-extraction-recipe)
    - [leak correction](#813-leak-correction-recipe)
    - [make telluric](#814-make-telluric-recipe)
    - [fit telluric](#815-fit-telluric-recipe)
    - [make template](#816-make-template-recipe)
    - [ccf](#817-ccf-recipe)
    - [polarimetry](#818-polarimetry-recipe)


## APERO module code diagram

Using the Github Action [Repo Visualizer](https://github.com/githubocto/repo-visualizer)

![Visualization of the codebase](./documentation/working/_static/diagram.svg)

##  1 Latest version
[Back to top](#apero---a-pipeline-to-reduce-observations)

- master (long term stable) V0.6.131 (2020-09-10)
    ```
    This is the version currently recommended for all general use. It may not
    contain the most up-to-date features until long term support and stability can
    be verified.
    ```
- developer (tested) V0.6.131 (2020-09-10)
    ```
    Note the developer version should have been tested and semi-stable but not
    ready for full sets of processing and defintely not for release for
    non-developers or for data put on archives. Some changes may not be
    in this version that are in the working version.
    ```
- working (untested) V0.6.131 (2020-09-10)
    ```
    Note the working version will be the most up-to-date version but has not been
    tested for stability - use at own risk.
    ```
---
---

## 2 Pre-Installation
[Back to top](#apero---a-pipeline-to-reduce-observations)

#### 2.1 clone this repository

```bash
git clone https://github.com/njcuk9999/apero-drs
```

This may take some time (in future most of the data required will be a separate download),
and we still have many (now redundant) files from the spirou_py3 repository


##### Upgrading from the spirou_py3

This is not recommended. A clean install is recommended.

Note if you must do this you need to redirect github:
```bash
cd ./spirou-drs
git remote set-url origin https://github.com/njcuk9999/apero-drs
mv ../spirou-drs ../apero-drs
```

---

#### 2.2 change to the repository directory
```bash
cd ./apero-drs
```

---

#### 2.3 checkout the correct branch

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

## 3 Installation
[Back to top](#apero---a-pipeline-to-reduce-observations)

(Currently only for `developer` and `working` versions)

Make sure pre-installation is done first!

---

#### 3.1 run the installation script
```bash
python setup/install.py --name={PROFILE}
```

You should choose a memorable profile name - this will be used in several places
note that it should not contain spaces or punctuation characters (other than
the underscore `_`)

---

#### 3.2 Follow the step-by-step guide:

A. `User config path`: This is the path where your configuration will be saved.
If it doesn't exist you will be prompted to create it.
(This will be referred to as `DRS_UCONFIG` from now on (default is `/home/user/apero/`)

B. `Choose an instrument`: Install {INSTRUMENT}. If yes it will install the
instrument if not then it will not install the instrument. Use must select a number.
Currently only SPIRou is supported. Note to use multiple instruments install multiple times.

C. `Choose a database`: Either (1) use sqlite (recommended for single machine use) -
no setup required OR (2) use mysql (required for multiple machine use) - setup required
note it is probably worth reading the "multiple machine" section of this read me
before continuing!

Choosing MySQL will prompt you for:
- the hostname (i.e. localhost)
- a username (the mysql username)
- a password (the mysql password), note this will be stored in plain text format
  so don't use personal or sensitive passwords here,
- a database name (i.e. the MySQL database you wish tables to be created in)
- a profile to use (in general this can be left blank) but if you want to share
  tables between setups this is the place to add another {PROFILE} name. Note these
  profile names are used to keep the mysql database tables separate.

D. `Set up paths individually`. If [Y]es it will allow you to set each path separately
(i.e. for raw, tmp, reduced, calibDB etc). If no you will just set one path and
all folders (raw, tmp, reduced, calibDB etc)) will be created under this directory.

`Setting the directories` (either one directory or each of the sub-directories
required - i.e. raw, tmp, reduced, calibDB etc)

E. `Plot mode required`: this is the plotting mode - you can change this later
in the user config files

F. `Clean install?` Do you want a clean install. If this is your first installing
to these data directories your answer will be [Y]es.

__WARNING__: If you type [Y]es you will be prompted (later) to reset
the directories this means any previous data in these directories will be removed.
Note you can always say later to individual cases.

Note if you have given empty directories you MUST run a clean install to copy
the required files to the given directories.

In the `Copying files` step if you asked for a clean install if directories
are not empty you will be prompted to reset them one-by-one
(__NOTE: THIS WILL REMOVE ALL DATA FROM THIS SPECIFIC DIRECTORY)__

---

#### 3.3 Installation is then complete

---

#### 3.4 Running apero

To run apero you need to do __one__ of the following

__NOTE__: these three are equivalent only do __one__


##### i) alias to apero to your startup script (RECOMMENDED)
For example

`alias apero "source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup"`  (tcsh/csh)
`alias apero="source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup"`  (bash/zsh)

to `~/.bashrc` or `~/.bash_profile` or  `~/.tcshrc` or `~/.profile`, `~/.zshrc` or `~/.zprofile`

and type `apero` every time you open a new terminal


##### ii) source environmental variables directly

 `source {DRS_UCONFIG}/config/apero.{SYSTEM}.setup`
 and type this command every time you open a new terminal

where:
 - `{DRS_UCONFIG}` is the config path set up in step __2A__
 - `{SYSTEM}` is either `bash` or `sh` depending on your shell


##### iii) add the contents of `{DRS_UCONFIG}/config/apero.{SYSTEM}.setup` to your startup script

i.e. one of the following `~/.bashrc`, `~/.bash_profile`, `~/.tcshrc`, `~/.profile`, `~/.zshrc`, `~/.zprofile`
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


## 4 TODO and Currently known issues
[Back to top](#apero---a-pipeline-to-reduce-observations)

Most recent update notes, the current todo list and known issues are listed [here](https://www.github.com/njcuk9999/apero-drs/UPDATE_NOTES.txt).

---
---

## 5 Using APERO
[Back to top](#apero---a-pipeline-to-reduce-observations)

You can use apero to individually run recipes or process a set of files

---

### 5.1 Using apero individually

Recipes (the scripts to run) are stored in the `./apero/recipes/{instrument}` path
once installed these recipes are linked to the `./bin/` directory and can be used
from the command line or in python or in ipython (recommended).

i.e. from the shell
```bash
apero_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. using python
```bash
python apero_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. in ipython
```
run apero/recipes/spirou/apero_badpix_spirou.py --flatfiles file1.fits --darkfiles file2.fits
```

i.e. in a python script
```
import apero_badpix_spirou

ll = apero_badpix_spirou.main('night_name', flatfiles='file1.fits', darkfiles='file2.fits')
```

__NOTE__: there is a --help option available for every recipe

---

### 5.2 Using APERO processing recipe

`apero_processing.py` can be used in a few different ways but always requires the following

1) The instrument (`SPIROU`)

2) The `run.ini` file to execute

i.e.
```
tools/bin/apero_processing.py SPIROU mini_run.ini
```

#### 5.2.1 The processing run file (`{RUN_FILE}`)

These are located in the `{DRS_DATA_RUNS}` (default=`/data/runs/`) directory. They can be used in two ways

##### 1) Process automatically

By default it processes every night and every file that can be found in the `{DRS_DATA_RAW}` (default=`/data/raw/`)  directory.
One can turn on specific nights to process in several ways

<ol type='a'>
   <li> setting the `NIGHT_NAME` in the selected `{RUN_FILE}` </li>
   <li> adding a night to the `EXCLUDE_OBS_DIRS` (blacklist = reject) or `INCLUDE_OBS_DIRS` (whitelist = keep) </li>
   <li> adding an extra argument to `apero_processing.py` (`--obs_dir`, `--exclude_obs_dirs`, `--include_obs_dirs`) </li>
</ol>

One can also just process a single file by adding an extra argument to `apero_processing.py` (`--filename`)

One can also tell the recipe to only process specific targets (targets here are defined as `OBJ_FP` or `OBJ_DARK`)
when (and only when) the recipes can accept targets -- i.e. extraction, telluric fitting, CCF etc
by changing the `TELLURIC_TARGETS` key for tellurics or the `SCIENCE_TARGETS` key for science objects in the `{RUN_FILE}`.
Note that setting either of these to `All` or `None` will remove this as a filter and in most cases should result in
all targets being reduced. For `TELLURIC_TARGETS = "All"` this will use the provided list of all telluric hot stars.
For `SCIENCE_TARGETS = "All"` this should find all targets defined by the header key `OBJECT` that are not
telluric hot stars - this depends heavily on what is in the `OBJECT` header key for all files.

For processing automatically `id00000` should be set to one of the sequence names (see [below](#522-The-available-sequences)
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

#### 5.2.2 The available sequences

Sequences are defined in the `apero/core/instruments/{INSTRUMENT}/recipe_definitions.py` script.
These enable the user to quickly process sets of data in specific orders based on their needs.

Note these can be combined in any order the user wants, but some assume others have been completed first (in terms of files needed).
i.e.

```
id00001 = master_seq
id00002 = calib_seq
id00003 = tellu_seq
id00004 = science_seq
```

Currently defined sequences are found here:

- [SPIROU](apero/data/spirou/reset/runs/README.md)
- [NIRPS](apero/data/nirps_ha/reset/runs/README.md)


---

# 6 APERO run order
[Back to top](#apero---a-pipeline-to-reduce-observations)

As mentioned above this depends on what sequence you wish to use but as
an overview the steps are as follows

<ol>

<li> Choose a master night

(i.e. 2018-09-25)

If using the processing script one must set this in that file else
when choosing arguments one must use them from the master night choosen.

Note one has to run `apero_badpix` and `apero_loc` calibrations for the master night
in order to run the shape master recipe.
</li>

<li> Run all the preprocessing

Note one must preprocess ALL nights for the master to work) - it will only
combine darks(for the master dark) and fps (for the master shape) from
preprocessed data (i.e. use sequence `pp_seq`)
</li>


<li> Run the master sequence (i.e. use sequence `master_seq`)
i.e.
```
apero_dark_master
apero_badpix [master night]
apero_loc [DARK_FLAT; master night]
apero_loc [FLAT_DARK; master night]
apero_shape_master
apero_shape [master night]
apero_flat [master night]
apero_leak_master
apero_thermal [DARK_DARK_INT; master night]
apero_thermal [DARK_DARK_TEL; master night]
apero_wave_master
```

Note if any step in the master sequence fails you cannot continue with the
night runs.
</li>

<li> Run the night sequences

These must be in this order but could be night-by-night or
all of one then all of the other). If all badpix are run first
then the loc will have the best chance at having bad pixel correction from a
night close to it. If one runs night by night then the next step will only
have access to calibrations from nights already processed.

Note again one should extract all telluric stars and run the telluric sequence
(to create a telluric database) BEFORE correcting any science extraction.

The calibration sequence is as follows:
```
apero_badpix [every night]
apero_loc [DARK_FLAT; every night]
apero_loc [FLAT_DARK; every night]
apero_shape [every night]
apero_flat [every night]
apero_thermal [DARK_DARK_INT; every night]
apero_thermal [DARK_DARK_TEL; every night]
apero_wave_night [every night]
```

The telluric star sequence is as follows:
```
apero_extract [spec + pol; every night; TELLURIC_TARGETS]
apero_leak [OBJ_FP; every night; TELLURIC_TARGETS]
apero_mk_tellu [spec + pol; every night; TELLURIC_TARGETS]
apero_fit_tellu [spec + pol; every night; TELLURIC_TARGETS]
apero_mk_template [spec + pol; every night; TELLURIC_TARGETS]
apero_mk_tellu [spec + pol; every night; TELLURIC_TARGETS]
```

Note one must run all tellurics before running science. Not having
sufficient tellurics processed will lead to poor telluric correction for the
science.


The science star sequence is as follows:
```
apero_extract [spec + pol; every night; SCIENCE_TARGETS]
apero_leak [OBJ_FP; every night; SCIENCE_TARGETS]
apero_fit_tellu [spec + pol; every night; SCIENCE_TARGETS]
apero_mk_template [spec + pol; every night; SCIENCE_TARGETS]
apero_fit_tellu [spec + pol; every night; SCIENCE_TARGETS]
apero_ccf [spec + pol; fiber=AB; every night; SCIENCE_TARGETS]
```
</li>
</ol>

---
---

# 7 APERO Inputs
[Back to top](#apero---a-pipeline-to-reduce-observations)

---

## 7.1 Input Files

Also known as raw files

- `4096 x 4096`
- PP files use `DPRTYPE` to identify files

| DPRTYPE       | SBCCAS_P	| SBCREF_P	| SBCALI_P | OBSTYPE    |	TRG_TYPE	| EXT.    |
| --------------|-----------|-----------|----------|------------|---------------|---------|
| DARK_DARK_INT	| pos_pk	| pos_pk	| P4	   | DARK	    | CALIBRATION	| d.fits  |
| DARK_DARK_TEL	| pos_pk	| pos_pk	| P5	   | DARK	    | CALIBRATION	| d.fits  |
| OBJ_DARK	    | pos_pk	| pos_pk	| ?	       | OBJECT	    | TARGET		| o.fits  |
| DARK_DARK_SKY	| pos_pk	| pos_pk	| ?	       | OBJECT	    | SKY			| o.fits  |
| DARK_FP_SKY   | pos_pk    | pos_fp    | ?        | OBJECT     | SKY           | o.fits  |
| OBJ_FP	    | pos_pk	| pos_fp	| ?	       | OBJECT	    | TARGET		| o.fits  |
| FP_FP	        | pos_fp	| pos_fp	| ?	       | ALIGN	    | CALIBRATION	| a.fits  |
| LFC_LFC       | pos_rs    | pos_rs    | ?        | ALIGN      | CALIBRATION   | a.fits  |
| FLAT_DARK	    | pos_wl	| pos_pk	| ?	       | FLAT	    | CALIBRATION	| f.fits  |
| DARK_FLAT	    | pos_pk	| pos_wl	| ?	       | FLAT	    | CALIBRATION	| f.fits  |
| FLAT_FLAT	    | pos_wl	| pos_wl	| ?	       | FLAT	    | CALIBRATION	| f.fits  |
| HCONE_DARK	| pos_hc1	| pos_pk	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |
| HCTWO_DARK	| pos_hc2	| pos_pk	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |
| FP_HCONE      | pos_fp	| pos_hc1   | ?	       | COMPARISON | CALIBRATION	| c.fits  |
| FP_HCTWO      | pos_fp	| pos_hc2   | ?	       | COMPARISON | CALIBRATION	| c.fits  |
| HCONE_FP      | pos_hc1   | pos_fp    | ?        | COMPARISON | CALIBRATION   | c.fits  |
| HCTWO_FP      | pos_hc2   | pos_fp    | ?        | COMPARISON | CALIBRATION   | c.fits  |
| DARK_HCONE    | pos_pk	| pos_hc1	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |
| DARK_HCTWO    | pos_pk	| pos_hc2	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |
| HCONE_HCONE	| pos_hc1	| pos_hc1	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |
| HCTWO_HCTWO	| pos_hc2	| pos_hc2	| ?	       | COMPARISON	| CALIBRATION	| c.fits  |

---
---

# 8 APERO Recipes
[Back to top](#apero---a-pipeline-to-reduce-observations)

---


Note These are not in the required run order.
Please do not run them in this order.
See [APERO run order](#APERO-run-order) for the correct order.


### 8.1 Preprocessing Recipe

Cleans file of detector effects.

##### *Run*:
```
apero_preprocess_spirou.py [DIRECTORY] [RAW_FILES]
```
##### *Optional Arguments*:
```
    --skip, --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_WORKING   \\ default: "tmp" directory
```
##### *Output files*:
```
{ODOMETER_CODE}_pp.fits  \\ preprocessed files (4096x4096)
```

##### *Plots*:

None




---

### 8.2 Dark Master Recipe

Collects all dark files and creates a master dark image to use for correction.

##### *Run*:
```
apero_master_spirou.py
```
##### *Optional Arguments*:
```
    --filetype, --database, --plot,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
DARKM {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_dark_master.fits  \\ dark master file (4096x4096) + FITS-TABLE
```

##### *Plots*:

None

##### *Notes*:

Does not require a master night choice - finds darks from all preprocessed nights.





---

### 8.3 Bad Pixel Correction Recipe

Creates a bad pixel mask for identifying and deal with bad pixels.

##### *Run*:
```
apero_badpix_spirou.py [DIRECTORY] -flatfiles [FLAT_FLAT] -darkfiles [DARK_DARK_TEL]
apero_badpix_spirou.py [DIRECTORY] -flatfiles [FLAT_FLAT] -darkfiles [DARK_DARK_INT]
```
##### *Optional Arguments*:
```
    --database, --combine, --flipimage, --fluxunits, --plot, --resize,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
BADPIX {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
BKGRDMAP {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_badpixel.fits  \\ bad pixel map file (3100x4088)
{ODOMETER_CODE}_pp_bmap.fits      \\ background mask file (3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)
```

##### *Plots*:

```
BADPIX_MAP
```






---

### 8.4 Localisation Recipe

Finds the orders on the image.

##### *Run*:
```
apero_loc_spirou.py [DIRECTORY] [FLAT_DARK]
apero_loc_spirou.py [DIRECTORY] [DARK_FLAT]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --plot, --resize,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
ORDER_PROFILE_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
LOC_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_order_profile_C.fits  \\ order profile file (3100x4088)
{ODOMETER_CODE}_pp_loco_C.fits           \\ localisation centers map file (49x4088)
{ODOMETER_CODE}_pp_fwhm-order_C.fits     \\ localisation widths map file (49x4088)
{ODOMETER_CODE}_pp_with-order_C.fits     \\ localisation superposition file (3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)
```

##### *Plots*:

```
LOC_MINMAX_CENTS, LOC_MIN_CENTS_THRES, LOC_FINDING_ORDERS, LOC_IM_SAT_THRES,
LOC_ORD_VS_RMS, LOC_CHECK_COEFFS, LOC_FIT_RESIDUALS
```





---

### 8.5 Shape Master Recipe

Creates a master FP image from all FPs processed. Uses this to work out the
required shifts due to the FP master image, slicer pupil geometry and the
bending of the orders (found in localisation).

##### *Run*:
```
apero_shape_master_spirou.py [DIRECTORY] -hcfiles [HCONE_HCONE] -fpfiles [FP_FP]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --locofile,
    --plot, --resize,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
SHAPEX {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
SHAPEY {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
FPMASTER {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_shapex.fits            \\ dx shape map (3100x4088)
{ODOMETER_CODE}_pp_shapey.fits            \\ dy shape map (3100x4088)
{ODOMETER_CODE}_pp_fpmaster.fits          \\ fp master file (3100x4088) + FITS-TABLE
DEBUG_{ODOMETER_CODE}_shape_out_bdx.fits  \\ dx map before dy map (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_in_fp.fits    \\ input fp before shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_out_fp.fits   \\ input fp after shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_in_hc.fits    \\ input hc before shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_out_hc.fits   \\ input hc after shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)
```

##### *Plots*:

```
SHAPE_DX, SHAPE_ANGLE_OFFSET_ALL, SHAPE_ANGLE_OFFSET, SHAPE_LINEAR_TPARAMS
```





---

### 8.6 Shape (per night) Recipe

Takes the shape master outputs (shapex, shapey and fpmaster) and applies
these transformations to shift the image to the master fp frame, unbend images
and shift to correct for slicer pupil geometry.

##### *Run*:
```
apero_shape_spirou.py [DIRECTORY] [FP_FP]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --fpmaster,
    --plot, --resize, --shapex, --shapey,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
SHAPEL {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_shapel.fits            \\ local shape map (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_in_fp.fits    \\ input fp before shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_shape_out_fp.fits   \\ input fp after shape corr (3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)
```

##### *Plots*:

```
SHAPE_DX, SHAPE_ANGLE_OFFSET_ALL, SHAPE_ANGLE_OFFSET, SHAPE_LINEAR_TPARAMS
```





---

### 8.7 Flat/Blaze Correction Recipe

Extracts out flat images in order to measure the blaze and produced blaze
correction and flat correction images.

##### *Run*:
```
apero_flat_spirou.py [DIRECTORY] [FLAT_FLAT]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --fiber, --flipimage, --fluxunits,
    --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
FLAT_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
BLAZE_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_blaze_{FIBER}.fits          \\ blaze correction file (49x4088)
{ODOMETER_CODE}_pp_flat_{FIBER}.fits           \\ blaze correction file (49x4088)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits   \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits       \\ debug background file (7x3100x4088)
```

##### *Plots*:

```
FLAT_ORDER_FIT_EDGES1, FLAT_ORDER_FIT_EDGES2, FLAT_BLAZE_ORDER1,
FLAT_BLAZE_ORDER2
```






---

### 8.8 Thermal Correction Recipe

Extracts dark frames in order to provide correction for the thermal background
after extraction of science / calibration frames.

##### *Run*:
```
apero_thermal_spirou.py [DIRECTORY] [DARK_DARK_INT]
apero_thermal_spirou.py [DIRECTORY] [DARK_DARK_TEL]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --fiber, --flipimage, --fluxunits,
    --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --wavefile,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
THERMALT_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
THERMALI_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits       \\ debug background file (7x3100x4088)
{ODOMETER_CODE}_pp_thermal_e2ds_int_{FIBER}.fits  \\ extracted thermal for dark_dark_int (49x4088)
{ODOMETER_CODE}_pp_thermal_e2ds_tel_{FIBER}.fits  \\ extracted thermal for dark_dark_tel (49x4088)
```

##### *Plots*:

None





---

### 8.9 Master leak correction recipe

Extracts all DARK_FP files and creates a model for later leak correction.

##### *Run*:
```
apero_leak_master.py [DIRECTORY]
```
##### *Optional Arguments*:
```
    --filetype, --database, --plot
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
LEAKM_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_leak_master_{FIBER}.fits        \\ leak correction maste rfile (49x4088)
```

##### *Plots*:

None

### 8.10 Master wavelength solution Recipe

Creates a wavelength solution and measures drifts (via CCF) of the FP relative
to the FP master

##### *Run*:
```
apero_wave_master_spirou.py [DIRECTORY] -hcfiles [HCONE_HCONE] -fpfiles [FP_FP]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --blazefile,
    --combine, --darkfile, --darkcorr,  --fiber, --flipimage,
    --fluxunits,  --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --wavefile, -hcmode, -fpmode,
    --forceext,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
WAVEM_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
WAVEHCL_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
WAVEFPL_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits          \\ debug background file (7x3100x4088)

{ODOMETER_CODE}_pp_e2dsff_linelist_{FIBER}.dat      \\ wave stats hc line list
{ODOMETER_CODE}_pp_e2dsff_wavemres_{FIBER}.fits     \\ wave res table (multi extension fits)
{ODOMETER_CODE}_pp_e2dsff_wavem_hc_{FIBER}.fits     \\ wave solution from hc only (49x4088)
{ODOMETER_CODE}_pp_e2dsff_wavem_fp_{FIBER}.fits     \\ wave solution from hc + fp (49x4088)
apero_wave_results.tbl                                \\ wave res table (ASCII-table)
{ODOMETER_CODE}_pp_e2dsff_mhc_lines_{FIBER}.tbl     \\ wave hc lines (ASCII-table)
{ODOMETER_CODE}_pp_wavem_hclines_{FIBER}.fits       \\ wave hc ref/measured lines table (FITS-TABLE)
{ODOMETER_CODE}_pp_wavem_fplines_{FIBER}.fits      \\ wave fp ref/measured lines table (FITS-TABLE)
{ODOMETER_CODE}_pp_e2dsff_ccf_{FIBER}.fits          \\ ccf code [FITS-TABLE]
```

##### *Plots*:

```
WAVE_HC_GUESS, WAVE_HC_BRIGHTEST_LINES, WAVE_HC_TFIT_GRID, WAVE_HC_RESMAP, WAVE_LITTROW_CHECK1,
WAVE_LITTROW_EXTRAP1, WAVE_LITTROW_CHECK2, WAVE_LITTROW_EXTRAP2, WAVE_FP_FINAL_ORDER,
WAVE_FP_LWID_OFFSET, WAVE_FP_WAVE_RES, WAVE_FP_M_X_RES, WAVE_FP_IPT_CWID_1MHC, WAVE_FP_IPT_CWID_LLHC,
WAVE_FP_LL_DIFF, WAVE_FP_MULTI_ORDER, WAVE_FP_SINGLE_ORDER, CCF_RV_FIT, CCF_RV_FIT_LOOP, WAVEREF_EXPECTED,
EXTRACT_S1D, EXTRACT_S1D_WEIGHT, WAVE_FIBER_COMPARISON, WAVE_FIBER_COMP, WAVENIGHT_ITERPLOT, WAVENIGHT_HISTPLOT
```




---

### 8.11 Nightly wavelength solution Recipe

Calculates corrections to the master wavelength solution as a nightly wavelength
solution and measures drifts (via CCF) of the FP relative to the FP master

##### *Run*:
```
apero_wave_night_spirou.py [DIRECTORY] -hcfiles [HCONE_HCONE] -fpfiles [FP_FP]
```
##### *Optional Arguments*:
```
    --database, --badpixfile, --badcorr, --backsub, --blazefile,
    --combine, --darkfile, --darkcorr,  --fiber, --flipimage,
    --fluxunits,  --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --wavefile, -hcmode, -fpmode,
    --forceext
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Calibration database entry*:
```
WAVE_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits          \\ debug background file (7x3100x4088)

{ODOMETER_CODE}_pp_e2dsff__wave_night_{FIBER}.fits     \\ wave night solution (49x4088)
{ODOMETER_CODE}_pp_wavem_hclines_{FIBER}.fits       \\ wave hc ref/measured lines table (FITS-TABLE)
{ODOMETER_CODE}_pp_wavem_fplines_{FIBER}.fits      \\ wave fp ref/measured lines table (FITS-TABLE)
{ODOMETER_CODE}_pp_e2dsff_ccf_{FIBER}.fits          \\ ccf code [FITS-TABLE]
```

##### *Plots*:

```
WAVENIGHT_ITERPLOT WAVENIGHT_HISTPLOT WAVEREF_EXPECTED
CCF_RV_FIT CCF_RV_FIT_LOOP EXTRACT_S1D EXTRACT_S1D_WEIGHT
```




---

### 8.12 Extraction Recipe

Extracts any preprocessed image using all the calibrations required.

##### *Run*:
```
apero_extract_spirou.py [DIRECTORY] [PP_FILE]

```
##### *Optional Arguments*:
```
    --badpixfile, --badcorr, --backsub, --blazefile,
    --combine, --objname, --dprtype, --darkfile, --darkcorr,
    --fiber, --flipimage, --fluxunits, --flatfile,
    --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --thermal, --thermalfile, --wavefile,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```

##### *Output files*:
```
{ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits          \\ debug background file (7x3100x4088)
{ODOMETER_CODE}_pp_ext_fplines_{FIBER} .fits      \\ the FP ref/measured lines (FOR OBJ_FP only)
```

##### *Plots*:

```
FLAT_ORDER_FIT_EDGES1, FLAT_ORDER_FIT_EDGES2, FLAT_BLAZE_ORDER1,
FLAT_BLAZE_ORDER2, THERMAL_BACKGROUND, EXTRACT_SPECTRAL_ORDER1,
EXTRACT_SPECTRAL_ORDER2, EXTRACT_S1D, EXTRACT_S1D_WEIGHT
```




---

### 8.13 Leak correction Recipe

Corrects extracted files for leakage coming from a FP (for OBJ_FP files only)

##### *Run*:
```
apero_leak_spirou.py [DIRECTORY] [PP_FILE]

```
##### *Optional Arguments*:
```
    --database, --plot, --leakfile
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```

##### *Output files*:
```
{ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
DEBUG_{ODOMETER_CODE}_pp_background.fits          \\ debug background file (7x3100x4088)
```

##### *Plots*:

None




---

### 8.14 Make Telluric Recipe

Takes a hot star and calculates telluric transmission

##### *Run*:
```
apero_mk_tellu_spirou.py [DIRECTORY] [E2DS & OBJ_DARK]
apero_mk_tellu_spirou.py [DIRECTORY] [E2DSFF & OBJ_DARK]
apero_mk_tellu_spirou.py [DIRECTORY] [E2DS & OBJ_FP]
apero_mk_tellu_spirou.py [DIRECTORY] [E2DSFF & OBJ_FP]
```
##### *Optional Arguments*:
```
    --database, --blazefile, --plot, --wavefile
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
##### *Telluric database entry*:
```
TELLU_CONV_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
TELLU_TRANS_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
##### *Output files*:
```
{ODOMETER_CODE}_pp_tellu_trans_{FIBER}.fits    \\ telluric transmission file (49x4088)
{WAVEFILE}_tellu_conv_{FIBER}.npy              \\ tapas convolved with wave file (49x4088)
```

##### *Plots*:

```
MKTELLU_WAVE_FLUX1, MKTELLU_WAVE_FLUX2
```






---

### 8.15 Fit Telluric Recipe

Using the telluric tramission calculates principle components (PCA) to
correct input images of atmospheric absorption.

#### *Run*:
```
apero_fit_tellu_spirou.py [DIRECTORY] [E2DS & OBJ_DARK]
apero_fit_tellu_spirou.py [DIRECTORY] [E2DSFF & OBJ_DARK]
apero_fit_tellu_spirou.py [DIRECTORY] [E2DS & OBJ_FP]
apero_fit_tellu_spirou.py [DIRECTORY] [E2DSFF & OBJ_FP]
```
#### *Optional Arguments*:
```
    --database, --blazefile, --plot, --wavefile
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
#### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
#### *Telluric database entry*:
```
TELLU_CONV_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
TELLU_TRANS_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
#### *Output files*:
```
{ODOMETER_CODE}_pp_e2dsff_tcorr_{FIBER}.fits    \\ telluric corrected e2dsff file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_tcorr_{FIBER}.fits     \\ telluric corrected s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_tcorr_{FIBER}.fits     \\ telluric corrected s1d constant in velocity space (FITS-TABLE)
{ODOMETER_CODE}_pp_e2dsff_recon_{FIBER}.fits    \\ reconstructed transmission e2dsff file (49x4088)
{ODOMETER_CODE}_pp_s1d_w_recon_{FIBER}.fits     \\ reconstructed transmission s1d constant in pixel space (FITS-TABLE)
{ODOMETER_CODE}_pp_s1d_v_recon_{FIBER}.fits     \\ reconstructed transmission s1d constant in velocity space (FITS-TABLE)
```

#### *Plots*:

```
EXTRACT_S1D, EXTRACT_S1D_WEIGHT, FTELLU_PCA_COMP1, FTELLU_PCA_COMP2,
FTELLU_RECON_SPLINE1, FTELLU_RECON_SPLINE2, FTELLU_WAVE_SHIFT1,
FTELLU_WAVE_SHIFT2, FTELLU_RECON_ABSO1, FTELLU_RECON_ABSO2
```





---

### 8.16 Make Template Recipe

Uses all telluric corrected images of a certain object name to create
and BERV and wavelength corrected template in order to server as a better
model SED for telluric correction.

`apero_mk_tellu_spirou.py` and `apero_fit_tellu_spirou.py` need to be rerun after
template generation.

#### *Run*:
```
apero_mk_template_spirou.py [OBJNAME]
```
#### *Optional Arguments*:
```
    --filetype, -fiber,
    --database, --blazefile, --plot, --wavefile
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
#### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```
#### *Telluric database entry*:
```
TELLU_CONV_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
TELLU_TRANS_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
```
#### *Output files*:
```
Template_{OBJNAME}_{filetype}_{FIBER}.fits  \\ Template for object (3100x4088) + FITS TABLE
Template_s1d_{OBJNAME}_sc1d_w_{FIBER}.fits  \\ Template s1d constant in pixel space for object FITS TABLE + FITS TABLE
Template_s1d_{OBJNAME}_sc1d_v_{FIBER}.fits  \\ Template s1d constant in velocity space for object FITS TABLE + FITS TABLE
BigCube0_{OBJNAME}_{filetype}_{FIBER}.fits  \\ Cube of obs making template earth reference (49 x N x 4088)
BigCube_{OBJNAME}_{filetype}_{FIBER}.fits   \\ Cube of obs making template star reference (49 x N x 4088)
```

#### *Plots*:

```
EXTRACT_S1D
```





---

### 8.17 CCF Recipe

Cross correlates the input image against a mask and measures a radial velocity
per order, and combines to give an over all radial velocity measurement.
Also (where possible) takes into account the FP drift measured by a CCF in the
wave solution (when wave solution used a FP)

##### *Run*:
```
apero_ccf_spirou.py [DIRECTORY] [E2DS & OBJ_FP]
apero_ccf_spirou.py [DIRECTORY] [E2DSFF & OBJ_FP]
apero_ccf_spirou.py [DIRECTORY] [E2DS_CORR & OBJ_FP]
apero_ccf_spirou.py [DIRECTORY] [E2DSFF_CORR & OBJ_FP]
apero_ccf_spirou.py [DIRECTORY] [E2DS & OBJ_DARK]
apero_ccf_spirou.py [DIRECTORY] [E2DSFF & OBJ_DARK]
apero_ccf_spirou.py [DIRECTORY] [E2DS_CORR & OBJ_DARK]
apero_ccf_spirou.py [DIRECTORY] [E2DSFF_CORR & OBJ_DARK]
```
##### *Optional Arguments*:
```
    --mask, --rv, --width, --step
    --database, --blazefile, --plot
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```

##### *Output files*:
```
{ODOMETER_CODE}_pp_{INTYPE}_{FIBER}_ccf_{mask}_{FIBER}.fits  \\ CCF for science channel file (FITS-TABLE)
{ODOMETER_CODE}_pp_{INTYPE}_{FIBER}_ccf_fp_{FIBER}.fits      \\ CCF for reference channel file (FITS-TABLE)

```

##### *Plots*:

```
CCF_RV_FIT, CCF_RV_FIT_LOOP, CCF_SWAVE_REF, CCF_PHOTON_UNCERT
```




---

### 8.18 Polarimetry Recipe

Produces all polarimetry outputs.

##### *Run*:
```
pol_spirou.py [DIRECTORY] [E2DSFF]
pol_spirou.py [DIRECTORY] [E2DSFF_CORR]
```
##### *Optional Arguments*:
```
    --blazefile, --plot, --wavefile,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --quiet, --help
```
##### *Output Dir*:
```
DRS_DATA_REDUC   \\ default: "reduced" directory
```

##### *Output files*:
```
{ODOMETER_CODE}_pp_{INTYPE}_pol.fits               // polar file
{ODOMETER_CODE}_pp_{INTYPE}_StokesI.fits           // stokes file
{ODOMETER_CODE}_pp_{INTYPE}_null1_pol.fits         // null 1 file
{ODOMETER_CODE}_pp_{INTYPE}_null2_pol.fits         // null 2 file
{ODOMETER_CODE}_pp_{INTYPE}_lsd_pol.fits           // lsd file
{ODOMETER_CODE}_pp_{INTYPE}_s1d_w_pol.fits         // s1d polar file constant in pixel space for object
{ODOMETER_CODE}_pp_{INTYPE}_s1d_v_pol.fits         // s1d polar file constant in velocity space
{ODOMETER_CODE}_pp_{INTYPE}_s1d_w_null1.fits       // s1d null 1 file constant in pixel space for object
{ODOMETER_CODE}_pp_{INTYPE}_s1d_v_null1.fits       // s1d null 1 file constant in velocity space
{ODOMETER_CODE}_pp_{INTYPE}_s1d_w_null2.fits       // s1d null 2 file constant in pixel space for object
{ODOMETER_CODE}_pp_{INTYPE}_s1d_v_null2.fits       // s1d null 2 file constant in velocity space
{ODOMETER_CODE}_pp_{INTYPE}_s1d_w_stokesi.fits     // s1d stokes file constant in pixel space for object
{ODOMETER_CODE}_pp_{INTYPE}_s1d_v_stokesi.fits     // s1d stokes file constant in velocity space
```

##### *Plots*:

```
POLAR_CONTINUUM, POLAR_RESULTS, POLAR_STOKES_I, POLAR_LSD,
EXTRACT_S1D, EXTRACT_S1D_WEIGHT
```



[Back to top](#apero---a-pipeline-to-reduce-observations)

---

# 9 Processing on multiple cores / nodes / computers


One of the most important things if running on multiple nodes or computers
is to make sure the database mode is set to MySQL. Sqlite mode is not supported
for complicated setups.

Currently you can run on multiple cores on one machine using apero_processing
directly

## Notes on number of cores

Note that you should allow between 3-5 Gb per core to run the apero_processing
script

Note you should make sure MySQL has at least a maximum number of connections
equal to the number of cores + 1.





[Back to top](#apero---a-pipeline-to-reduce-observations)



