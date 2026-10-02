---
card_label: apero_extract_spirou
card_icon: fa-solid fa-flask
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/sequences/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# apero_extract_spirou

**Short name:** EXT  **Type:** recipe  **Kind:** extract  **Instrument:** SPIROU

## Extraction

The extraction recipe takes any preprocessed file (as many as given by the user but in general just one single file).
The files are combined (if requested) and are calibrated using our standard image calibration technique. Once
calibrated, the correct (closest in time) order profile (`ORDERP`), positions of the orders (`LOCO`), `SHAPELOCAL`,
shape reference (x and y maps), and wavelength solution are loaded for each fiber (AB, A, B, and C). The order profiles
and input image are transformed to the reference FP grid using the affine transformation, and using the shape x and y
maps the image is corrected for the slicer geometry, the tilt and the bending due to the echelle orders.

The extraction recipe then extracts the flux (using optimal extraction), calculates the barycentric correction,
corrects contamination from the reference fiber (if an FP is present in the reference fiber), corrects for the flat,
corrects for the thermal contribution and generates the 1D spectrum.


### Optimal extraction

Once the image and the order profile (from localization) have been corrected for the slicer geometry and curvature of
the echelle orders we extract out the combined flux in the science channels (fibers A and B) to create a fiber AB,
as well as extracting out the flux in A and B (for polarization work) and C separately (for the reference fiber
calibrations). As the orders are already straightened we use just the localization coefficient value at the center of
the image to extract vertically along each order. We then divide the image by the order profile to provide a weighting
across the order (i.e., an optimal extraction, Horne et al. 1986}). The final step of the optimal extraction is to sum
vertically across the columns accounting for cosmic rays by using a sigma clip $|flux|>10\sigma$ away from the
median value for that column. This creates our `E2DS` (extracted 2D spectrum) and for SPIRou, this leads to images
with 49 orders and 4088 pixels along the orders.


### BERV correction

Ideally, any stellar spectrum observed would be measured from a point stationary with respect to the barycenter of the
Solar System (Wright et al. 2014). However, ground-based observations are subject to: the orbit of the Earth, the
rotation of the Earth, precession and other Earth motions, and to a lesser extent gravitation time dilation,
leap-second offsets, and factors affecting the star itself (i.e., parallax, proper motions, etc). We use the term BERV
(Barycentric Earth Radial Velocity) hereinafter to collect all these terms into a single measurement which can be used
to correct a specific spectrum at a specific point in time. We calculate the BERV using the barycorrpy package, which
uses the astrometric parameters fed in at the preprocessing level. The calculation from barycorrpy includes the
estimate for the BERV itself and the corrected or barycentric Julian Date (BJD) at the mid-exposure time. barycorrpy
has a precision better than the $cm s^{-1}$ level. We also estimate the maximum BERV value for this object
across the year. If for any reason the BERV calculation fails with barycorrpy we calculate an estimate of the BERV
(precise to $\sim 10 m s^{-1}$, modified from PyAstronomy.pyasl.baryvel; a python implementation of helcorr)
and flag that an estimated BERV correction was calculated. This estimated BERV is not precise enough for PRV work but
is sufficient to allow for acceptable telluric correction.


### Leak Correction

For scientific observations, the reference fiber either has a DARK or an FP illuminating the pixels in this fiber.
For PRV an FP allows a simultaneous RV measurement of an FP alongside the measurement of the stellar RV; this allows
precise tracking of the instrumental drift when the simultaneous FP is compared to the `FP_FP` from the nightly
wavelength solution calibration. However, light from the FP has been shown to slightly contaminate the science fibers
and thus we provide a correction for such calibration.

During the reference sequence  many `DARK_FP` are combined (and extracted) to form a model of the light seen in the
science fibers when no light (other than the contribution from the DARK) was present as well as an extracted reference
fiber measurement of the FP flux that caused said contamination in the science fibers. Using these models, the
contamination measured in the science channels of the reference leak recipe is then scaled to the flux of the
simultaneous FP of the observation (using the extracted flux from this scientific observation we are trying to correct).
Then, this model is subtracted from the original science observation for each of the science fibers (AB or A or B),
order-by-order:

$$
    ratio_{i} = \frac{\Sigma(L[C]_{i}S[C]_{i})}{\Sigma(S[C]_{i}^2)}
$$

$$
    scale_{i} = \frac{L[AB,A,B]_{i}}{ratio_{i}}
$$

$$
    S[AB,A,B]_{i,corr} = S[AB,A,B]_{i} - scale_{i}
$$

where L[C] is the model of the FP from the leak reference recipe, S[C] is the 2D extracted spectrum in the reference
fiber (fiber C), L[AB,A,B] is the model of the contamination from the FP from the leak reference recipe in the science
fibers (either AB or A or B), S[AB,A,B] is the 2D extracted flux in the science fibers (either AB or A or B),
S[AB,A,B]_{corr} denotes the leak-corrected 2D extracted spectrum in the science fibers (either AB or A or B) and
i denotes that this is done order-by-order.


### Thermal correction

The reference dark, applied during the standard image calibration phase, removes the high-frequency components of the
dark; however, the thermal contribution still remains (and varies on a night-by-night basis). For this reason, we use
nightly extracted `DARK_DARK` files to model the thermal contribution present in an observation during the night.
The thermal correction model comes in two flavors, one for science observations where we assume there is some sort of
continuum to the spectrum and telluric contamination as well as a small contribution arising from the Earth's
atmosphere itself, and one for HC or FP extractions where these assumptions are not true.

In the case where we have a scientific observation, a `DARK_DARK_TEL` (where the calibration fiber sees the cold source
and the science fibers see the mirror covers) is used. The extracted `DARK_DARK_TEL`  is then median filtered with a
width of 101 pixels (on a per-order basis). This width was chosen to be big enough to capture large-scale structures
in the dark and not be significantly affected by readout noise. A fit is then made to the red most orders
($>2450 nm$) using only flux lower than 0.01 from a transmission spectrum from the Transmissions of the
AtmosPhere for AStromomical data tool (TAPAS) -- i.e., a domain where transmission is basically zero. We assume that
we can safely use any flux with a transmission of order zero to scale the thermal background to this zero transmission
value.

$$
    mask = \left\{ \begin{array}{cl}
    1: & TAPAS < 0.01  \\
    0: & \text{otherwise} \\
    \end{array} \right. \\
$$

$$
    ratio = median\left( \frac{TT[AB,A,B,C]\times mask}{S[AB,A,B,C] \times mask} \right)
$$

$$
    S[AB,A,B,C]_{corr} = S[AB,A,B,C] - \frac{TT[AB,A,B,C]}{ratio}
$$

where TAPAS is the TAPAS spectrum, TT[AB,A,B,C] is a nightly extracted `DARK_DARK_TEL` spectrum, S[AB,A,B,C] denotes
the 2D extracted spectrum prior to correction and $S[AB,A,B]_{corr}$ denotes the thermally corrected 2D extracted
spectrum.

In the case where we have an HC or an FP observation, a `DARK_DARK_INT` (where all three fibers see only the cold source,
not the sky nor the mirror covers) is used. The extracted `DARK_DARK_INT` is then median filtered (again with a width
of 101 pixels on a per-order basis) and a fit is made using an envelope to measure the thermal background in the
reddest orders ($>2450\, nm$). The envelope is constructed by using the flux below the 10th percentile (i.e.,
not in the HC or FP peaks). This is then converted into a ratio and scaled to the observation we are correcting.


$$
    ratio = median\left( \frac{TI[AB,A,B,C]}{P_{10}(TI[AB,A,B,C])} \right)
$$

$$
    S[AB,A,B,C]_{corr} = S[AB,A,B,C] - \frac{TI[AB,A,B,C]}{ratio}
$$

where $P_{10}$ is the 10th percentile value, TI[AB,A,B,C] is a nightly extracted `DARK_DARK_INT` spectrum
(median filtered with a width of 101 pixels), S[AB,A,B,C] denotes the 2D extracted spectrum prior to correction and
$S[AB,A,B]_{corr}$ denotes the thermally corrected 2D extracted spectrum.


### S1D generation

The `E2DS` and `E2DSFF` formats are not necessarily the most convenient for science analysis, having duplicated
wavelength coverage at order overlap and slightly varying velocity sampling with each order and between orders.
We therefore transform the `E2DSFF` file into the `S1D` format. The `S1D` is sampled on a constant grid for all
objects. We have two differing `S1D` formats, one with a uniform step in wavelength (0.05 nm/pixel) and one with a
constant step in velocity (1 $km s^{-1}$/pixel), both being sampled between 965 nm and 2500 nm. Numerically,
to construct the `S1D`, we use as an input the `E2DSFF` file prior to blaze correction and the blaze file as inputs.
We create two `S1D` vectors, one corresponding to the total flux and one corresponding to the total blaze on the
destination wavelength grid. We use a 5th order polynomial spline to project the flux of a given order onto the flux
grid and perform the same operation with the blaze onto the weight vector. We do not consider the blaze below 20% of
the peak blaze value and values on the destination wavelength grids that are out of the order's range are set to zero.
We loop through orders and sum the contribution of each order onto the respective destination grids for the `E2DSFF`
science flux and blaze. Note that the `S1D` generation only depends on the blaze calibration. As such any spectrum
(regardless of emission lines, low flux, or strong bands) can be converted to `S1D` format and we generate `S1D` for
`HC_HC` and `FP_FP` as well as science targets.

## Usage

```bash
apero_extract_spirou.py {obs_dir}[STRING] [FILE:DRS_PP] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:DRS_PP]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Current accepts all preprocessed filetypes. All files used will be combined into a single frame. |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--quicklook[True/False]` | [BOOLEAN] Sets whether extraction done in quick look mode |
| `--badpixfile[FILE:BADPIX]` | [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks 'directory' |
| `--badcorr[True/False]` | [BOOLEAN] Whether to correct for the bad pixel file |
| `--backsub[True/False]` | [BOOLEAN] Whether to do background subtraction |
| `--blazefile[FILE:FF_BLAZE]` | [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' (CALIBDB=BADPIX) |
| `--combine[True/False]` | [BOOLEAN] Whether to combine fits files in file list or to process them separately |
| `--combine_method[STRING]` | Method to combine files (if --combine=True) |
| `--objname[STRING]` | Sets the object name to extract (filters input files) |
| `--dprtype[STRING]` | [STRING] Sets the DPRTYPE to extract (filters input files) |
| `--darkfile[FILE:DARKREF]` | [STRING] The Dark file to use (CALIBDB=DARKM) |
| `--darkcorr[True/False]` | [BOOLEAN] Whether to correct for the dark file |
| `--fiber[ALL,AB,A,B,C]` | [STRING] Define which fibers to extract |
| `--flipimage[True/False]` | [BOOLEAN] Whether to flip fits image |
| `--fluxunits[ADU/s,e-]` | [STRING] Output units for flux |
| `--flatfile[FILE:FF_FLAT]` | [STRING] Define a custom file to use for flat correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' |
| `--locofile[FILE:LOC_LOCO]` | [STRING] Sets the LOCO file used to get the coefficients (CALIBDB=LOC_{fiber}) |
| `--orderpfile[FILE:LOC_LOCO]` | [STRING] Sets the Order Profile file used to get the coefficients (CALIBDB=ORDER_PROFILE_{fiber} |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--resize[True/False]` | [BOOLEAN] Whether to resize image |
| `--shapex[FILE:SHAPE_X]` | [STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX) |
| `--shapey[FILE:SHAPE_Y]` | [STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY) |
| `--shapel[FILE:SHAPEL]` | [STRING] Sets the SHAPE local file used to get the local transforms (CALIBDB = SHAPEL) |
| `--leakcorr[True/False]` | [BOOLEAN] Sets whether to do the leak correction (else defaults to CORRECT_LEAKAGE value in constants) |
| `--thermal[True/False]` | [BOOLEAN] Sets whether to do the thermal correction (else defaults to THERMAL_CORRECT value in constants) |
| `--thermalfile[FILE:THERMALI_E2DS,THERMALT_E2DS]` | [STRING] Sets the Thermal correction file to use (CAILBDB = THERMAL_{fiber}) |
| `--wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT]` | [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks 'directory' |
| `--force_ref_wave` | Force using the reference wave solution |
| `--no_in_qc` | Disable checking the quality control of input files |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |

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
| EXT_S1D_W | 1D stitched spectrum (constant wavelength binning) | EXT_S1D_W | .fits | _s1d_w | AB, A, B, C | -- | -- | DRS_PP |
| EXT_S1D_V | 1D stitched spectrum (constant velocity binning) | EXT_S1D_V | .fits | _s1d_v | AB, A, B, C | -- | -- | DRS_PP |
| ORDERP_STRAIGHT | Straightened order profile for an individual image | ORDERP_STRAIGHT | .fits | _orderps | AB, A, B, C | -- | -- | SHAPEL |
| DEBUG_BACK | Individual file background map | DEBUG_BACK | .fits | _background.fits | -- | -- | -- | DRS_PP |
| EXT_FPLIST | FP lines identified from extracted FP fiber | EXT_FPLIST | .fits | _ext_fplines | AB, A, B, C | -- | -- | EXT_E2DS_FF, EXT_E2DS_FF |
| QL_E2DS_FF | Extracted + flat-fielded 2D spectrum (quick output) | QL_E2DS_FF | .fits | _q2dsff | AB, A, B, C | -- | -- | DRS_PP |
| FLAT_RESPONSE | Per-order flat-field response profile from the convolve_irregular resampling algorithm | FLAT_RESPONSE | .fits | _flat_response | AB, A, B, C | calibration | FLAT_RES | EXT_E2DS_FF, EXT_E2DS_FF, QL_E2DS_FF, QL_E2DS_FF |

## Plots

**Debug plots:**
`FLAT_ORDER_FIT_EDGES1`, `FLAT_ORDER_FIT_EDGES2`, `FLAT_BLAZE_ORDER1`, `FLAT_BLAZE_ORDER2`, `THERMAL_BACKGROUND`, `EXTRACT_SPECTRAL_ORDER1`, `EXTRACT_SPECTRAL_ORDER2`, `EXTRACT_S1D`, `EXTRACT_S1D_WEIGHT`, `WAVEREF_EXPECTED`, `EXTRACT_MODEL_BACKGROUND`, `FLAT_RESPONSE_ORDER1`, `FLAT_RESPONSE_ORDER2`

**Summary plots:**
`SUM_FLAT_ORDER_FIT_EDGES`, `SUM_EXTRACT_SP_ORDER`, `SUM_EXTRACT_S1D`, `SUM_EXTRACT_MODEL_BACKGROUND`, `SUM_FLAT_RESPONSE_ORDER`
