---
card_label: apero_thermal_spirou
card_icon: fa-solid fa-flask
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/sequences/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# apero_thermal_spirou

**Short name:** THERM  **Type:** recipe  **Kind:** calib-night  **Instrument:** SPIROU

## Thermal calibration

The nightly thermal recipe takes preprocessed `DARK_DARK_INT` files or `DARK_DARK_TEL` files (as many as given by
the user or as many as occur on each of the nights being used via `apero_processing`). It combines the `DARK_DARK_INT`
or `DARK_DARK_TEL` files into a single `DARK_DARK_INT` or `DARK_DARK_TEL` respectively (via a median combination of
the images). These combined `DARK_DARK_INT` or `DARK_DARK_TEL` files are then extracted.

The thermal background seen by SPIRou in a science exposure is the sum of the black body contribution of the sky, the
Cassegrain unit (at the temperature of the telescope), the calibration unit (for the reference channel), and the
thermal emission of the hermetic feedthroughs that connect the fibers into the cryostat. A small contribution also
arises from the Earth's atmosphere itself. This emissivity is proportional to one minus the telluric transmission at
the corresponding wavelength and if left unaccounted for in the thermal model would lead to emission-like features in
the thermal-corrected spectrum in the strongest absorption lines. From a series of sky-dark frames, we measured that
the median additional emissivity from the saturated absorption line is at the 4% level of the black body envelope.
We account for the additional contribution by using a median sky absorption spectrum and adding a small contribution
proportional to the excess emissivity due to the Earth's atmosphere in strong absorption lines. Note this contribution
is only added for the `DARK_DARK_TEL` files (as the `DARK_DARK_INT` images do not see the sky). For this reason, we
split generating the thermal calibration files into two steps: we generate the `DARK_DARK_INT` thermal calibration
files, then after a wavelength solution has been generated we generate the `DARK_DARK_TEL` thermal calibration files
(which require a nightly wavelength solution to add the contribution due to the emission-like features).

Considering that the telescope and front-end temperature change through the night, one needs to apply a thermal
correction that is adjusted per frame (this is done as part of the extraction recipe). While the slope of the black
body contribution changes very little over the $2.1-2.5 \mu m$ domain, within which the thermal background is
significant, the amplitude of the contribution varies by a factor of >2 between nights (typically a factor 2 for
every $8^\circ$
C) and needs to be adjusted for individual observations. While we have no external measurement of
the thermal background, there are a number of completely saturated telluric water absorption features
$2.4-2.5 \mu m$ that provide a measure of the total thermal emission seen by SPIRou. These regions are used to
scale the thermal background model such that they have a median flux of zero.

The thermal calibration files (`THERMALI` and `THERMALT`) are then saved to the calibration database for use
throughout APERO. The `THERMALI` calibrations are used for correcting internal lamp spectra (i.e., other calibrations)
and `THERMALT` calibrations are used to correct all science spectra.

## Usage

```bash
apero_thermal_spirou.py {obs_dir}[STRING] [FILE:DARK_DARK_INT,DARK_DARK_TEL] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:DARK_DARK_INT,DARK_DARK_TEL]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Current accepts all preprocessed filetypes. All files used will be combined into a single frame. |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--badpixfile[FILE:BADPIX]` | [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks 'directory' |
| `--badcorr[True/False]` | [BOOLEAN] Whether to correct for the bad pixel file |
| `--backsub[True/False]` | [BOOLEAN] Whether to do background subtraction |
| `--combine[True/False]` | [BOOLEAN] Whether to combine fits files in file list or to process them separately |
| `--darkfile[FILE:DARKREF]` | [STRING] The Dark file to use (CALIBDB=DARKM) |
| `--darkcorr[True/False]` | [BOOLEAN] Whether to correct for the dark file |
| `--fiber[ALL,AB,A,B,C]` | [STRING] Define which fibers to extract |
| `--flipimage[True/False]` | [BOOLEAN] Whether to flip fits image |
| `--fluxunits[ADU/s,e-]` | [STRING] Output units for flux |
| `--locofile[FILE:LOC_LOCO]` | [STRING] Sets the LOCO file used to get the coefficients (CALIBDB=LOC_{fiber}) |
| `--orderpfile[FILE:LOC_LOCO]` | [STRING] Sets the Order Profile file used to get the coefficients (CALIBDB=ORDER_PROFILE_{fiber} |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--resize[True/False]` | [BOOLEAN] Whether to resize image |
| `--shapex[FILE:SHAPE_X]` | [STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX) |
| `--shapey[FILE:SHAPE_Y]` | [STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY) |
| `--shapel[FILE:SHAPEL]` | [STRING] Sets the SHAPE local file used to get the local transforms (CALIBDB = SHAPEL) |
| `--wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT]` | [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks 'directory' |
| `--no_in_qc` | Disable checking the quality control of input files |
| `--forceext[True/False]` | [BOOLEAN] Sets whether to extract input files if files found on disk (defaults to THERMAL_ALWAYS_EXTRACT) |

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

See the instrument [file definitions](/docs/apero/instruments/spirou/file_definitions) for the full file catalogue.

| name | description | HDR[DRSOUTID] | file type | suffix | fibers | dbname | dbkey | input file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EXT_E2DS_FF | Extracted + flat-fielded 2D spectrum | EXT_E2DS_FF | .fits | _e2dsff | AB, A, B, C | -- | -- | DRS_PP |
| THERMALI_E2DS | Extracted sci=DARK calib=DARK thermal calibration file, where dark is an internal dark | THERMALI_E2DS | .fits | _thermal_e2ds_int | AB, A, B, C | calibration | THERMALI | DARK_DARK_INT |
| THERMALT_E2DS | Extracted sci=DARK calib=DARK thermal calibration file, where dark is a telescope dark | THERMALT_E2DS | .fits | _thermal_e2ds_tel | AB, A, B, C | calibration | THERMALT | DARK_DARK_TEL |
