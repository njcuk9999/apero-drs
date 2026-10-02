---
card_label: apero_flat_spirou
card_icon: fa-solid fa-flask
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/sequences/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# apero_flat_spirou

**Short name:** FF  **Type:** recipe  **Kind:** calib-night  **Instrument:** SPIROU

## Flat and Blaze calibration

An essential part of the extraction process is calibrating the flat field response (removing the effect of the
pixel-to-pixel sensitivity variations) and calculating the blaze function. The blaze can be seen visually in the raw
and preprocessed images as a darkening of the orders, especially at the blue end, towards the sides of the detector
(in the along-order direction).

The nightly flat recipe takes preprocessed `FLAT_FLAT` files (as many as given by the user or as many as occur on
each night being used via `apero_processing`). It combines the `FLAT_FLAT` files into a single `FLAT_FLAT` per night
(via a median combination of the images). After combining, the `FLAT_FLAT` images are calibrated using our standard
image calibration technique. The combined, calibrated `FLAT_FLAT` file is then extracted (using the same extraction
algorithms presented in Section \ref{sec:extraction}). The rest of the flat and blaze recipe is handled per order.
Once extracted, the `E2DS` ($49\times4088$) is median filtered (with a width of 25 pixels) and all pixels with
flux less than 0.05 the 95th percentile flux value or greater than 2 times the 95th percentile flux value are
removed. Each `FLAT_FLAT` `E2DS` order is then fit with a sinc function:

$$
    \text{B}_i = AS(sin(\theta)/\theta)^2
$$

$$
    S = 1 + s(x_i - L)
$$

$$
    \theta = \pi \bar{x_i} / P
$$

$$
    \bar{x_i} = (x_i - L) + Q(x_i - L)^2 + C(x_i - L)^3
$$

where $\text{B}_i$ is the blaze model for the ith `E2DS` order, A is the amplitude of the sinc function, P is
the period of the sinc function, s is the slope of the sinc function, $x_i$ is the flux vector of the `E2DS`
order, L is the linear center of the sinc function, Q is a quadratic scale term, and C is a cubic scale term.
The terms fit in the sinc function are A, P, L, Q, C and s as a function of $x_i$.

Once we have a set of parameters the blaze function for this order is $\text{B}_i$ for all values of the flux
for this order. The original `E2DS` order is then divided by the blaze function and this is used as the flat profile.
A standard deviation of the flat is also calculated for quality control purposes. This process is repeated for each
order producing a full blaze and flat profile ($49\times4088$) for the input `FLAT_FLAT` files. To avoid
erroneous contributions to the flat any outlier pixels (outside 10$\sigma$ or within $\pm$0.2 of unity)
are set to NaN. Note that the multiplication of the blaze and the flat is equivalent to the full response function of
the detector. For some orders (#34 and #74), there is a large residual at one edge of the blaze falloff.
This is due to the mismatch between the analytical function used and the actual profile; the flat-field correction
accounts for this mismatch.

For quality control, we check that the standard deviation of the flat for each order is less than 0.05. The flat
(`FLAT`) and blaze (`BLAZE`) profiles are then saved to the calibration database (if the quality control criteria are
met) for use throughout APERO.

## Usage

```bash
apero_flat_spirou.py {obs_dir}[STRING] [FILE:FLAT_FLAT,DARK_FLAT,FLAT_DARK] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:FLAT_FLAT,DARK_FLAT,FLAT_DARK]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Current allowed types: FLAT_FLAT or DARK_FLAT or FLAT_DARK but not a mixture (exclusive) |

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
| `--no_in_qc` | Disable checking the quality control of input files |
| `--forceext[True/False]` | If True, always re-extract the flat even if the output already exists (overrides CAL.FLAT.ALWAYS_EXTRACT) |

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
| FF_FLAT | Flat calibration file | FF_FLAT | .fits | _flat | AB, A, B, C | calibration | FLAT | FLAT_FLAT |
| FF_BLAZE | Blaze calibration file | FF_BLAZE | .fits | _blaze | AB, A, B, C | calibration | BLAZE | FLAT_FLAT |
| ORDERP_STRAIGHT | Straightened order profile for an individual image | ORDERP_STRAIGHT | .fits | _orderps | AB, A, B, C | -- | -- | SHAPEL |
| DEBUG_BACK | Individual file background map | DEBUG_BACK | .fits | _background.fits | -- | -- | -- | DRS_PP |
| FLAT_RESPONSE | Per-order flat-field response profile from the convolve_irregular resampling algorithm | FLAT_RESPONSE | .fits | _flat_response | AB, A, B, C | calibration | FLAT_RES | EXT_E2DS_FF, EXT_E2DS_FF, QL_E2DS_FF, QL_E2DS_FF |
| EXT_E2DS_FF | Extracted + flat-fielded 2D spectrum | EXT_E2DS_FF | .fits | _e2dsff | AB, A, B, C | -- | -- | DRS_PP |

## Plots

**Debug plots:**
`FLAT_ORDER_FIT_EDGES1`, `FLAT_ORDER_FIT_EDGES2`, `FLAT_BLAZE_ORDER1`, `FLAT_BLAZE_ORDER2`, `FLAT_EDGE_ORDERS`

**Summary plots:**
`SUM_FLAT_ORDER_FIT_EDGES`, `SUM_FLAT_BLAZE_ORDER`, `SUM_FLAT_EDGE_ORDERS`
