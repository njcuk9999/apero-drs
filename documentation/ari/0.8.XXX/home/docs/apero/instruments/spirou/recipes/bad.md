---
card_label: apero_badpix_spirou
card_icon: fa-solid fa-flask
---

# apero_badpix_spirou

**Short name:** BAD  **Type:** recipe  **Kind:** calib-night  **Instrument:** SPIROU

## Bad pixel calibration


The bad pixel recipe takes preprocessed `DARK_DARK` and `FLAT_FLAT` files (as many as given by the user or as many as
occur on the nights being used via pre-processing). It combines all `DARK_DARK` files and all `FLAT_FLAT` files into a
single `DARK_DARK` and a single `FLAT_FLAT` (via a median combination of the images). Bad pixels are then identified
in the `FLAT_FLAT` by using Equation:

$$
M_{\text{flat } i,j} = \left\{ \begin{array}{cl}
  1 : & FLAT_{i,j} \text{ is not finite} \\
  1 : & \mid (FLAT_{i,j} / FLAT_{\text{med } i,j}) - 1 \mid > \text{cut\_ratio} \\
  1 : & FLAT_{\text{med } i,j} < \text{illum\_cut} \\
  0 : & \text{otherwise} \\
\end{array} \right.
$$

where $FLAT_{i,j}$ is the flux in ith row jth column of the `FLAT_FLAT` image;
$FLAT_{\text{med }}$ is the median filtered flat image (using a filtering width of 7 pixels)
and $M_{\text{flat } i,j}$ is 1 to flag a bad pixel or 0 otherwise, cut_ratio is 0.5 (flagging pixels
with a response less than 50 percent of their neighbors or unphysically brighter than neighbors) and
illum\_cut is 0.05 (flagging pixels at the edge of the blaze response). `FLAT` and $FLAT_{\text{med }}$
have first been normalized by the $90^{\rm th}$ percentile of flux in the median filtered flat image.
Thus $M_{\text{flat}}$ is a Boolean flag map of bad pixels on the flat image.
For the `DARK_DARK` image, bad pixels are identified using Equation:

$$
M_{\text{dark } i,j} = \left\{ \begin{array}{cl}
  1 : & DARK_{i,j} \text{ is not finite} \\
  1 : & DARK_{i,j} > 5.0 \text{ADU/s}  \\
  0 : & \text{otherwise} \\
\end{array} \right.
$$

where $DARK_{i,j}$ is the flux in the ith row jth column of the dark image.
Thus $M_{\text{dark}}$ is a Boolean flag map of bad pixels on the dark image.
We choose a value of 5.0 ADU/s as it is representative of the pixel flux of a typical science target.
Including pixels with a brighter level of dark current than this leads to a loss in SNR rather than a gain.
We note that this threshold could be target-dependent but for simplicity we use a single value.

In addition to this bad pixels in a full detector engineering flat (FULLFLAT taken during commissioning)
are also identified using Equation:

$$
M_{\text{full-flat } i,j} = \left\{ \begin{array}{cl}
  1 : & \mid FULLFLAT_{i,j} - 1 \mid > 0.3  \\
  0 : & \text{otherwise} \\
\end{array} \right.
$$

where $FULLFLAT_{i,j}$ is the flux in ith row jth column of the full detector engineering flat.
Thus $M_{\text{full-flat}}$ is a Boolean flag map of bad pixels on the full detector engineering flat image.
We chose 0.3 as this flagged the defective regions identified manually on the detector.
The $1 \sigma$ dispersion of the full detector engineering flat image is 2 percent.

These three bad pixel maps are then combined into a single bad pixel map.

## Usage

```bash
apero_badpix_spirou.py {obs_dir}[STRING] --flatfiles[FILE:FLAT_FLAT] --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `--flatfiles[FILE:FLAT_FLAT]` | Current allowed types: FLAT_FLAT |
| `--darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT]` | Current allowed types: DARK_DARK |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--combine[True/False]` | [BOOLEAN] Whether to combine fits files in file list or to process them separately |
| `--flipimage[True/False]` | [BOOLEAN] Whether to flip fits image |
| `--fluxunits[ADU/s,e-]` | [STRING] Output units for flux |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--resize[True/False]` | [BOOLEAN] Whether to resize image |
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
| BADPIX | Bad pixel map | BADPIX | .fits | _badpixel | calibration | BADPIX | FLAT_FLAT |
| BKGRD_MAP | Bad pixel background map | BKGRD_MAP | .fits | _bmap.fits | calibration | BKGRDMAP | FLAT_FLAT |

## Plots

**Debug plots:**
`BADPIX_MAP`

**Summary plots:**
`SUM_BADPIX_MAP`
