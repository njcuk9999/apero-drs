---
card_label: apero_shape_spirou
card_icon: fa-solid fa-flask
---

# apero_shape_spirou

**Short name:** SHAPE  **Type:** recipe  **Kind:** calib-night  **Instrument:** SPIROU

## Nightly shape calibration

Before extracting the spectrum, we need to transform the image into a format that is amenable to a simple
1-dimensional collapse. Given our reference FP grid and the x and y displacements maps, on a given night, we only
need to find the affine transform that registers FP peaks onto the reference FP image and updates the x and y
transform maps within the affine contribution. This assumes that the order curvature is constant through the life
of the instrument and that the slicer shape is stable. We note that as the order profiles are determined in each
nightly calibration, a slight (sub-pixel) modification of the position of orders would have no impact on the
extracted spectra which are extracted with the profile measured for the corresponding night.

The nightly shape recipe takes preprocessed `FP_FP` files (as many as given by the user or as many as occur on each
of the nights being used via `apero_processing`). It combines the `FP_FP` files into a single `FP_FP` per night
(via a median combination of the images). After combining, the `FP_FP` images are calibrated using our standard
image calibration technique. We take the `REFFP`, `SHAPEX` and `SHAPEY` calibrations from the calibration database.
If multiple exist we use the closest in time (using the header key `MIDEXPOSURE` from the header).
To find the linear transform parameters (dx, dy, A, B, C, and D) between the reference `FP_FP` and this night's
`FP_FP` we find all the FP peaks in the reference `FP_FP` image and in the nightly `FP_FP` image. Once we have the
linear transform parameters we shift and transform the combined and calibrated nightly `FP_FP` via our shape
transform algorithm and save the transformed image and un-transformed image to disk (for manual comparison to the
input `FP_FP` image).

As part of quality control, we check that the RMS of the residuals in both directions (across order and along the
order) are less than 0.1 pixel, which has been found to be optimal to flag pathological cases. The transformation
parameters (dx, dy, A, B, C, and D, henceforth `SHAPELOCAL`) are then saved to the calibration database (if both
quality control criteria are met) for use throughout APERO.

## Usage

```bash
apero_shape_spirou.py {obs_dir}[STRING] [FILE:FP_FP] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:FP_FP]` | Current allowed types: FP_FP |

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
| `--flipimage[True/False]` | [BOOLEAN] Whether to flip fits image |
| `--fluxunits[ADU/s,e-]` | [STRING] Output units for flux |
| `--fpref[FILE:REF_FP]` | [STRING] Sets the FP reference file to use (CALIBDB = FPREF) |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--resize[True/False]` | [BOOLEAN] Whether to resize image |
| `--shapex[FILE:SHAPE_X]` | [STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX) |
| `--shapey[FILE:SHAPE_Y]` | [STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY) |
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

| name | description | HDR[DRSOUTID] | file type | suffix | dbname | dbkey | input file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SHAPEL | Nightly shape calibration files | SHAPEL | .fits | _shapel | calibration | SHAPEL | FP_FP |
| SHAPEL_IN_FP | Input FP file for nightly shape comparison | SHAPEL_IN_FP | .fits | _shapel_in_fp.fits | -- | -- | FP_FP |
| SHAPEL_OUT_FP | Output FP file for nightly shape comparison | SHAPEL_OUT_FP | .fits | _shapel_out_fp.fits | -- | -- | FP_FP |
| DEBUG_BACK | Individual file background map | DEBUG_BACK | .fits | _background.fits | -- | -- | DRS_PP |

## Plots

**Debug plots:** 
`SHAPEL_ZOOM_SHIFT`, `SHAPE_LINEAR_TPARAMS`

**Summary plots:** 
`SUM_SHAPEL_ZOOM_SHIFT`
