---
card_label: apero_mk_tellu_spirou
card_icon: fa-solid fa-flask
---

# apero_mk_tellu_spirou

**Short name:** MKTELL  **Type:** recipe  **Kind:** tellu-hotstar  **Instrument:** SPIROU

## Residual transmission of hot stars (mktellu)

The residual transmission recipe takes a single hot star observation (an extracted, flat-fielded 2D spectrum).
The first step is a pre-cleaning correction which essentially removes the bulk of the telluric absorption, producing
a corrected 2D spectrum as well as an absorption spectrum, sky model, and an estimate of the water and dry components
of the absorption (Artigau in prep). The pre-cleaning uses a stellar template, if available, to better measure the
water and dry components. The corrected 2D spectrum is then normalized by the 95$^{th}$ percentile of the blaze per
order and the residual transmission map is created by using a low-pass filter (per order) on the hot star (and
dividing by a template if present).

We make sure the pre-cleaning was successful (i.e., the water component exponent is between 0.1 and 15 and the dry
component exponent is between 0.8 and 3.0) and check that the SNR for each order is above a $100$; subsequently, the
hot star residual transmission maps are added to the telluric database.

## Usage

```bash
apero_mk_tellu_spirou.py {obs_dir}[STRING] [FILE:EXT_E2DS_FF] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:EXT_E2DS_FF]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Currently  allowed types: E2DS, E2DSFF |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--blazefile[FILE:FF_BLAZE]` | [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' (CALIBDB=BADPIX) |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT]` | [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks 'directory' |
| `--use_template[True/False]` | Whether to use the template provided from the telluric database |
| `--template[FILE:TELLU_TEMP]` | Filename of the custom template to use (instead of from telluric database) |
| `--finiteres[True/False]` | Whether to do the finite resolution correction (Always false if no template) |
| `--no_in_qc` | Disable checking the quality control of input files |

## Special arguments

<details>
<summary>Arguments common to all APERO recipes</summary>

| Argument | Description |
| --- | --- |
| `--xhelp[STRING]` | Extended help menu (with all advanced arguments) |
| `--debug[STRING]` | Activates debug mode (Advanced mode [INTEGER] value must be an integer greater than 0, setting the debug level) |
| `--list_night[STRING]` | Lists the night name directories in the input directory if used without a 'directory' argument or lists the files in the given 'directory' (if defined). Only lists up to 15 files/directories |
| `--list_all[STRING]` | Lists ALL the night name directories in the input directory if used without a 'directory' argument or lists the files in the given 'directory' (if defined) |
| `--version[STRING]` | Displays the current version of this recipe. |
| `--info[STRING]` | Displays the short version of the help menu |
| `--program[STRING]` | [STRING] The name of the program to display and use (mostly for logging purpose) log becomes date \| {THIS STRING} \| Message |
| `--recipe_kind[STRING]` | [STRING] The recipe kind for this recipe run (normally only used in apero_processing.py) |
| `--parallel[STRING]` | [BOOL] If True this is a run in parellel - disable some features (normally only used in apero_processing.py) |
| `--shortname[STRING]` | [STRING] Set a shortname for a recipe to distinguish it from other runs - this is mainly for use with apero processing but will appear in the log database |
| `--idebug[STRING]` | [BOOLEAN] If True always returns to ipython (or python) at end (via ipdb or pdb) |
| `--ref[STRING]` | If set then recipe is a reference recipe (e.g. reference recipes write to calibration database as reference calibrations) |
| `--crunfile[STRING]` | Set a run file to override default arguments |
| `--quiet[STRING]` | Run recipe without start up text |
| `--nosave` | Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once. |
| `--force_indir[STRING]` | [STRING] Force the default input directory (Normally set by recipe) |
| `--force_outdir[STRING]` | [STRING] Force the default output directory (Normally set by recipe) |

</details>

## Outputs

**Output directory:** `PATH.RED // Default: "red" directory`

| name | description | HDR[DRSOUTID] | file type | suffix | fibers | dbname | dbkey | input file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TELLU_CONV | Telluric convolution file | -- | .npy | _tellu_conv | AB, A, B | telluric | TELLU_CONV | WAVESOL_REF, WAVE_NIGHT, WAVESOL_DEFAULT |
| TELLU_TRANS | Telluric transmission file | TELLU_TRANS | .fits | _tellu_trans | AB, A, B | telluric | TELLU_TRANS | EXT_E2DS_FF |
| TELLU_SCLEAN | Sky-cleaning file | TELLU_SCLEAN | .fits | _tellu_sclean.fits | -- | -- | -- | EXT_E2DS_FF |
| TELLU_PCLEAN | Telluric pre-cleaning file | TELLU_PCLEAN | .fits | _tellu_pclean | AB, A, B | telluric | TELLU_PCLEAN | EXT_E2DS_FF |

## Plots

**Debug plots:** 
`TELLU_SKY_CORR_PLOT`, `MKTELLU_WAVE_FLUX1`, `MKTELLU_WAVE_FLUX2`, `TELLUP_MEAN_RES`, `TELLUP_ABSO_SPEC`, `TELLUP_CLEAN_OH`, `FTELLU_RECON_SPLINE2`, `TELLU_FINITE_RES_CORR`

**Summary plots:** 
`SUM_MKTELLU_WAVE_FLUX`, `SUM_TELLUP_MEAN_RES`, `SUM_TELLUP_ABSO_SPEC`
