---
card_label: apero_pol_spirou
card_icon: fa-solid fa-flask
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/sequences/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# apero_pol_spirou

**Short name:** POLAR  **Type:** recipe  **Kind:** polar  **Instrument:** SPIROU

## Polarimetry

The polarimetry module for APERO was adapted from the [spirou-polarimetry](https://github.com/edermartioli/spirou-polarimetry).
SPIRou as a polarimeter can measure either circular (Stokes V) or linear (Stokes Q or U) polarization in the line
profiles. Each polarimetric measurement is performed by 4 exposures obtained with the Fresnel rhombs set at different
orientations (see Section 3.1 of Donati et al. 2020).

.. list-table:: Index positions of the Fresnel rhombs (RHB1 and RHB2) for exposures taken in each observing mode of SPIRou.
    :widths: 20, 10, 10, 10, 10, 10, 10, 10, 10
    :header-rows: 2

    * - Observing
      - Exp1
      - Exp1
      - Exp2
      - Exp2
      - Exp3
      - Exp3
      - Exp4
      - Exp4
    * - mode
      - RHB1
      - RHB2
      - RHB1
      - RHB2
      - RHB1
      - RHB2
      - RHB1
      - RHB2
    * - Stokes IU
      - P16
      - P2
      - P16
      - P14
      - P4
      - P2
      - P4
      - P14
    * - Stokes IQ
      - P2
      - P14
      - P2
      - P2
      - P14
      - P14
      - P14
      - P2
    * - Stokes IV
      - P14
      - P16
      - P2
      - P16
      - P2
      - P4
      - P14
      - P4

In the Table above we provide the index position of each Fresnel rhomb, as they appear in the FITS header, for each
exposure in the corresponding polarimetric mode.

These indices are used by APERO to recognize exposures within a polarimetric sequence, and then correctly apply the
method introduced by Donati et al. 1997 to calculate polarimetric spectra.

The polarization spectra of SPIrou are calculated using the technique introduced by Donati et al. 1997, which is
summarized as follows.  Let $f_{i\parallel}$ and $f_{i\perp}$ be the extracted flux in a given spectral
element of fiber A and B channels, where $i=\{1,2,3,4\}$ gives the exposure number in the polarimetric sequence.
Note that the extracted flux can be either the extracted spectrum or the extracted telluric corrected spectrum; by
default in APERO, we use the telluric corrected spectrum. The total flux of unpolarized light (Stokes I) is calculated
by the sum of fluxes in the two channels and in all exposures, i.e.,

$$
F_{I} = \sum_{i=1}^{4}{(f_{i\parallel} + f_{i\perp})}
$$

Let us define the ratio of polarized fluxes as

$$
r_{i} = \frac{f_{i\parallel}}{f_{i\perp}}
$$

which gives a relative measurement of the flux between the two orthogonal polarization states. In an ideal system,
:math`r=1` means completely unpolarized light, and other values provide the amount (or the degree) of polarization that
can be calculated as in Equation 1 of Donati et al. 1997, i.e.,

$$
P = \frac{f_{\parallel} - f_{\perp}}{f_{\parallel} + f_{\perp}} = \frac{r - 1}{r + 1}
$$

Therefore, in principle, one could obtain the amount of polarization with a single exposure. However, this measurement
is not optimal, since it only records the two states of polarization at the same time but not at the same pixel.
To obtain a measurement that records the same state of polarization at the same pixel, it suffices to take a second
exposure with one of the quarter-wave analyzers rotated by $90^{\circ}$ with respect to the first exposure,
consisting  of the 2-exposure mode. One can also use the 4-exposure (2 pairs) mode, where the polarization state in
the two channels is swapped between pairs, which better corrects for slight deviations of retarders from nominal
characteristics (retardance and orientation) and also corrects for the differences in transmission between the two
channels caused, for example, by different throughput of the two fibers, or by a small optical misalignment.
For this reason, SPIRou only operates in the 4-exposure mode, which is accomplished by rotating the analyzers
accordingly in each exposure, as detailed in the table above. The equation to calculate the degree of
polarization for the 4-exposure mode can be obtained in two different ways, by using the Difference method or by the
Ratio method, as defined in sections 3.3 and 3.4 of Bagnulo et al. 2009 and also in Equation 3 of Donati et al. 1997.
The degree of polarization for a given Stokes parameter $X=\{U, Q, V\}$ in the Difference method is calculated by

$$
P_{X} =  \frac{1}{4}\sum_{k=1}^{2}{\left(\frac{r_{2k-1}-1}{r_{2k-1}+1} - \frac{r_{2k}-1}{r_{2k}+1}\right)}
$$

and for the Ratio method the degree of polarization is given by

$$
P_{X} =  \frac{(\prod_{k=1}^{2}{r_{2k-1}/r_{2k}})^{1/4} - 1}{(\prod_{k=1}^{2}{r_{2k-1}/r_{2k}})^{1/4} + 1}
$$

Another advantage of using two pairs of exposures is that one can calculate the null polarization (NULL1 and NULL2) as
in equations 20 and 26 of Bagnulo et al. 2009, which provides a way to quantify the amount of spurious polarization.
The null polarization for the Difference method is given by

$$
NULL_{X} =  \frac{1}{4}\sum_{k=1}^{2}{\left[(-1)^{k-1}\left(\frac{r_{2k-1}-1}{r_{2k-1}+1} - \frac{r_{2k}-1}{r_{2k}+1}\right)\right]}
$$

and for the Ratio method the null polarization is given by

$$
NULL_{X} = \frac{\left(\prod_{k=1}^{2}{r_{2k-1}/r_{2k}}\right)^{\frac{(-1)^{k-1}}{4}} - 1}{\left(\prod_{k=1}^{2}{r_{2k-1}/r_{2k}}\right)^{\frac{(-1)^{k-1}}{4}} + 1}
$$

Finally, the uncertainties of polarimetric measurements can be calculated from the extracted fluxes and their
uncertainties (denoted here by $\sigma$) by equations A3 and A10 of Bagnulo et al. 2009. In the Difference
method, the variance for each spectral element is given by

$$
\sigma_{X}^{2} = \frac{1}{16} \sum_{i=1}^{4}{ \left\{ \left[ \frac{2 f_{i\parallel} f_{i\perp}}{(f_{i\parallel} + f_{i\perp})^{2}} \right]^{2}   \left[ \frac{\sigma_{i\parallel}^{2}}{f_{i\parallel}^{2}} + \frac{\sigma_{i\perp}^{2}}{f_{i\perp}^{2}} \right] \right\} }
$$

and in the Ratio method the variance is given in terms of the flux ratio $r_{i}$, i.e.,

$$
\sigma_{X}^{2} = \frac{\left( \frac{r_{1}}{r_{2}} \frac{r_{4}}{r_{3}} \right)^{1/2}} { 4 \left[ \left( \frac{r_{1}}{r_{2}} \frac{r_{4}}{r_{3}} \right)^{1/4} + 1\right]^{4}} \sum_{i=1}^{4}{\left[ \frac{\sigma_{i\parallel}^{2}}{f_{i\parallel}^{2}} + \frac{\sigma_{i\perp}^{2}}{f_{i\perp}^{2}} \right]}
$$

Applying this formalism to SPIRou spectra, we obtain values that vary continuously throughout the spectrum and are
systematically above or below zero for each spectrum, which we refer to here as the `continuum polarization'.
For general scientific applications with SPIRou, this continuum polarization is actually spurious as it reflects
small differences in the injection between  beams, and must therefore be fitted and removed. This step is mandatory
before performing measurements in spectral lines. APERO applies an iterative sigma-clip algorithm to fit either a
polynomial or a spline to model the continuum polarization.

### Least-Squares Deconvolution

The least-squares deconvolution method (LSD) is an efficient technique that combines the signal from thousands of
spectral lines retaining the same line profile information to obtain a mean velocity profile for the intensity,
polarization, and null spectra.  A common application of this technique concerns the measurement of the Zeeman split
into Stokes V (circularly polarized) profiles. The Zeeman split is a physical process where electronic transitions
occurring in the presence of a magnetic field have their main energy transition level split into two additional levels,
forming a double line in the intensity spectrum. An interesting feature of these lines is that they are circularly
polarized and their polarizations have opposite signs. Therefore, by observing the circularly polarized spectrum one
can obtain a characteristic Stokes V profile that provides a way to detect and characterize the magnetism in stellar
photospheres with great sensitivity.

APERO implements the LSD calculations using the formalism introduced by Donati et al. 1997, summarized as follows.
Let us first consider the weight of a given spectral line i, $w_{i} = g_{i} \lambda_{i} d_{i}$, where g is the
Landé factor (magnetic sensitivity), $\lambda$ is the central wavelength, and d is the line depth.
Then one can construct the line pattern function

$$
M(v)= \sum_{i=1}^{N_{l}}{w\delta(v - v_{i})}
$$

where $N_{l}$ is the number of spectral lines considered in the analysis, $\delta$ is the Dirac function,
and v is the velocity. The transformation from wavelength ($\lambda$) to velocity space is performed by the
relation $dv/d\lambda = c / \lambda$, where c is the speed of light.

The LSD profile is calculated by the following matrix equation:

$$
\rm{\bf Z} = \left( \rm{\bf M}^{t}.\rm{\bf S}^{2}.\rm{\bf M} \right)^{-1} \rm{\bf M}^{t} . \rm{\bf S}^{2} . \rm{\bf P}
$$

where $\rm{\bf P}$ is the polarimetric spectrum, and $\rm{\bf S}$ is the covariance matrix, a diagonal
matrix where each element in the diagonal is given by $S_{jj}=1/\sigma_{j}$, with $\sigma_{j}$ being the
uncertainty in the polarimetric spectrum.

Note that one can also calculate the null polarization LSD profile by substituting the polarimetric spectrum
$\rm{\bf P}$ by the null spectrum $\rm{\bf N}$.  The intensity LSD is also possible, by using the flux
spectrum $\rm{\bf F}$, but in this case the line weight is simply given by the line depth,
i.e, $w_{i} = d_{i}$.

In practice, LSD requires a few important steps to be executed by APERO. First, each individual spectrum is cleaned
using a sigma-clip rejection algorithm to minimize the impact of outliers in the LSD profile. Then we set a grid of
velocities to calculate the LSD profile, where the grid is defined by the following parameters: an initial velocity,
$v_{0}$, a final velocity, $v_{f}$, and the total number of points in the grid, $N_{v}$.

Next, a fast and accurate method is necessary to project the spectral values onto the velocity grid. Finally, an
appropriate catalog of spectral lines (line mask) needs to be adopted for the LSD calculations. APERO selects the
line mask from a repository of masks, where the selection is based on the proximity to the effective temperature of
the star observed.  The \APERO masks are computed using the VALD catalog (Piskunov et al. 1995) and a MARCS model
atmosphere (Gustafsson et al. 2008) with an effective temperature ranging from 2500 to 5000 K in steps of 500 K, and
the same surface gravity of $\log g=5.0$ dex. The lines that are effectively used in the LSD analysis are
selected with line depths above a given threshold, which is set to 3% by default and with a Lande factor of
$g_{\rm eff}>0$, resulting in a total of approximately 2500 atomic lines that cover the full spectral range of
SPIRou.

The LSD analysis is not computed in a standard automated run of APERO but the module is supplied and can be activated
with the use of a single keyword in the APERO profiles or run after processing.

## Usage

```bash
apero_pol_spirou.py {obs_dir}[STRING] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--exposures[FILE:EXT_E2DS_FF,TELLU_OBJ]` | List of exposures to add (order determined by recipe) |
| `--exp1[FILE:EXT_E2DS_FF,TELLU_OBJ]` | Override input exposure 1 |
| `--exp2[FILE:EXT_E2DS_FF,TELLU_OBJ]` | Override input exposure 2 |
| `--exp3[FILE:EXT_E2DS_FF,TELLU_OBJ]` | Override input exposure 3 |
| `--exp4[FILE:EXT_E2DS_FF,TELLU_OBJ]` | Override input exposure 4 |
| `--objrv[FLOAT]` | Object radial velocity [km/s] |
| `--lsdmask[STRING]` | LSD mask |
| `--output[STRING]` | Output file |
| `--output_lsd[STRING]` | Output LSD file |
| `--lsd` | Run LSD analysis |
| `--noqccheck` | Do not check quality control of inputs |
| `--blazefile[FILE:FF_BLAZE]` | [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' (CALIBDB=BADPIX) |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT]` | [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks 'directory' |
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

See the instrument [file definitions](/docs/apero/instruments/spirou/file_definitions) for the full file catalogue.

| name | description | HDR[DRSOUTID] | file type | suffix | input file |
| --- | --- | --- | --- | --- | --- |
| POL_DEG | Polarimetry 2D degree of polarisation file | POL_DEG | .fits | _pol | EXT_E2DS_FF, TELLU_OBJ |
| NULL_POL1 | 2D Null polarisation 1 file | NULL_POL1 | .fits | _null1_pol | EXT_E2DS_FF, TELLU_OBJ |
| NULL_POL2 | 2D Null polarisation 2 file | NULL_POL2 | .fits | _null2_pol | EXT_E2DS_FF, TELLU_OBJ |
| STOKESI_POL | Polarimetry 2D stokes I polarisation file | STOKESI_POL | .fits | _StokesI | EXT_E2DS_FF, TELLU_OBJ |
| LSD_POL | Least squares deconvolution file | LSD_POL | .fits | _lsd_pol | EXT_E2DS_FF, TELLU_OBJ |
| POL_CALIB | Polarimetry 2D shifted wavelength solution and blaze calibration file | POL_CALIB | .fits | _pol_calib | EXT_E2DS_FF, TELLU_OBJ |
| S1DW_POL | Polarimetry 2D degree of polarisation file (constant wavelength binning) | S1DW_POL | .fits | _s1d_w_pol | EXT_E2DS_FF, TELLU_OBJ |
| S1DV_POL | Polarimetry 2D degree of polarisation file (constant velocity binning) | S1DV_POL | .fits | _s1d_v_pol | EXT_E2DS_FF, TELLU_OBJ |
| S1DW_NULL1 | 1D Null polarisation 1 file (constant wavelength binning) | S1DW_NULL1 | .fits | _s1d_w_null1 | EXT_E2DS_FF, TELLU_OBJ |
| S1DV_NULL1 | 1D Null polarisation 1 file (constant velocity binning) | S1DV_NULL1 | .fits | _s1d_v_null1 | EXT_E2DS_FF, TELLU_OBJ |
| S1DW_NULL2 | 1D Null polarisation 2 file (constant wavelength binning) | S1DW_NULL1 | .fits | _s1d_w_null2 | EXT_E2DS_FF, TELLU_OBJ |
| S1DV_NULL2 | 1D Null polarisation 2 file (constant velocity binning) | S1DV_NULL2 | .fits | _s1d_v_null2 | EXT_E2DS_FF, TELLU_OBJ |
| S1DW_STOKESI | Polarimetry 1D stokes I polarisation file (constant wavelength binning) | S1DW_STOKESI | .fits | _s1d_w_stokesi | EXT_E2DS_FF, TELLU_OBJ |
| S1DV_STOKESI | Polarimetry 1D stokes I polarisation file (constant velocity binning) | S1DV_STOKESI | .fits | _s1d_v_stokesi | EXT_E2DS_FF, TELLU_OBJ |

## Plots

**Debug plots:**
`POLAR_FIT_CONT`, `POLAR_CONTINUUM`, `POLAR_RESULTS`, `POLAR_STOKES_I`, `POLAR_LSD`, `EXTRACT_S1D_WEIGHT`, `EXTRACT_S1D`

**Summary plots:**
`SUM_EXTRACT_S1D`
