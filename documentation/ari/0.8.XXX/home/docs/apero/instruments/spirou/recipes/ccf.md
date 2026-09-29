---
card_label: apero_ccf_spirou
card_icon: fa-solid fa-flask
---

# apero_ccf_spirou

**Short name:** CCF  **Type:** recipe  **Kind:** rv  **Instrument:** SPIROU

## Radial velocity via CCF

The CCF method is very often used for PRV work, particularly in the optical domain. In the early APERO effort, it was
the main tool to derive precise RV values. When implementing a near-infrared version of the CCF, a number of
challenges appeared. The near-infrared domain is plagued with telluric absorption, and even after telluric correction,
some wavelength domains are expected to have significant excess noise levels. Deep or saturated telluric lines cannot
be corrected and are better left as gaps (represented as \NAN) in the spectrum that are fixed for the entire time
series considered. When computing a CCF, how does one account for gaps in the data? The star's yearly line of sight
variations will cause this gap to shift against the stellar spectrum by up to $\pm 32 kms^{-1}$ depending
on ecliptic latitude. In the optical, one can simply reject the entire domain affected by the gap (64 $kms^{-1}$
plus the gap width); however, at optical wavelengths, deep absorption lines are sufficiently sparse that the overall
loss in wavelength domain due to telluric absorption is small, which is not the case in the near-infrared.

To further obfuscate the issue, telluric absorption varies between nights, so if one went down this path of masking,
it would end with the masking of a large window affected by any line that gets deeper than a given threshold, even if
only once in a time-series that may include hundreds of visits. The combination of varying conditions and yearly BERV
excursions leads to a loss of domain that is simply unacceptable, especially considering that the parts of the
near-infrared that are richest in sharp spectroscopic features (See Figure 4 in Artigau et al. 2022) are at the blue
and red edges of the H band, which are affected by telluric water absorption.

We opted for a CCF that correlates weighted delta functions against the spectrum but set the weight to zero when
reaching a point below 0.5 telluric transmission (where unity is no telluric absorption). This is done on a
spectrum-to-spectrum basis, to minimize the effective throughput losses. This CCF measurement is performed per
spectrum using one of the 3 standard masks available in APERO depending on the star's temperature (GL846, Gl699,
Gl905 respectively for Teff >3500 K, 3000-3500 K, <3000 K. We derive per-order as well as global CCFs. These data
products are useful to confirm the systemic velocity of the star, avoiding eventual target misidentifying, as well
as for flagging spectroscopic binaries. For time-series analysis, it can be significantly improved upon by using
all observations to perform a spectral cleaning to obtain a much cleaner CCF or through completely different methods,
such as the [line-by-line algorithm](https://lbl.exoplanets.ca).

## Usage

```bash
apero_ccf_spirou.py {obs_dir}[STRING] [FILE:EXT_E2DS_FF,TELLU_OBJ] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:EXT_E2DS_FF,TELLU_OBJ]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Currently allowed types: E2DS, E2DSFF, TELLU_OBJ (For dprtype = OBJ_FP, OBJ_DARK) |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--mask[FILE:CCF_MASK]` | [STRING] Define the filename to the CCF mask to use. Can be full path or a file in the ./data/spirou/ccf/ folder |
| `--rv[FLOAT]` | [FLOAT] The target RV to use as a center for the CCF fit (in km/s) |
| `--width[FLOAT]` | [FLOAT] The CCF width to use for the CCF fit (in km/s) |
| `--step[FLOAT]` | [FLOAT] The CCF step to use for the CCF fit (in km/s) |
| `--masknormmode[None,all,order]` | [STRING] Define the type of normalization to apply to ccf masks, 'all' normalized across all orders, 'order' normalizes independently for each order, 'None' applies no mask normalization |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--blazefile[FILE:FF_BLAZE]` | [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' (CALIBDB=BADPIX) |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
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

| name | description | HDR[DRSOUTID] | file type | suffix | fibers | input file |
| --- | --- | --- | --- | --- | --- | --- |
| CCF_RV | Cross-correlation RV results file | CCF_RV | .fits | _ccf | AB, A, B, C | EXT_E2DS_FF, TELLU_OBJ |

## Plots

**Debug plots:** 
`CCF_RV_FIT`, `CCF_RV_FIT_LOOP`, `CCF_SWAVE_REF`, `CCF_PHOTON_UNCERT`

**Summary plots:** 
`SUM_CCF_PHOTON_UNCERT`, `SUM_CCF_RV_FIT`
