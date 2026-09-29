---
card_label: apero_dark_ref_spirou
card_icon: fa-solid fa-flask
---

# apero_dark_ref_spirou

**Short name:** DARKREF  **Type:** recipe  **Kind:** calib-reference  **Instrument:** SPIROU

## Dark reference calibration

As \spirou has no moving internal parts for increased stability, one cannot move the fiber out of view and
independently measure the detector's dark current. Thus dark frames are non-trivial to construct, as there are
two independent contributions to the `dark' image, one arising from the dark current of the science arrays and
the other from thermal emission. This problem is mainly seen in the K band and is shared with any PRV spectrograph
for which the fiber thermal emission is commensurate with the per-pixel dark current.

The thermal background manifests itself as a very low-level contribution (typically 0.015 e-/s/pixel), well below
the typical target flux, but has a high flux tail of much brighter pixels. As the SPIRou science array has an
extremely stable temperature (sub-milli Kelvin), one expects the pixel dark current to be very stable. From all
preprocessed `DARK_DARK` files, across all nights, we select a subset of 100 `DARK_DARK` files, uniformly
distributed in time as much as possible using a sorting function. If there are less than 100 `DARK_DARK` files across
all available nights we use all files; this becomes our reference dark.

One could use this as the single step for dark correction, but a significant challenge arises. The fiber train is
always connected and the science array always sees the thermal emission from the fibers and the hermetic feedthrough
connecting the fibers to the cryostat. This thermal emission changes with the temperature of the fiber train and
moves, at the pixel level, on timescales of months to years following thermal cycles and maintenance of the instrument.
Applying a simple scaling of the dark current, including the thermal background from the fiber, would lead to
erroneous subtraction in science data, with sometimes an over subtraction of $\sim2.4\,\mu m$ flux, leading to
negative flux. We opt for a decoupling of the two contributions in the data calibration.
We construct a high-frequency median dark current, which contains pixel-to-pixel detector contributions and
low-frequency components from the thermal background of the fiber train. The high-frequency component can be
scaled with integration time while the low-frequency one needs to be adjusted.
This high-pass reference dark image is then saved to the calibration database for use throughout APERO.

## Usage

```bash
apero_dark_ref_spirou.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--filetype[STRING]` | Current allowed types: DARK_DARK |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
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

| name | description | HDR[DRSOUTID] | file type | suffix | dbname | dbkey | input file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DARKREF | Reference dark calibration file | DARKREF | .fits | _dark_ref | calibration | DARKREF | DARK_DARK_TEL, DARK_DARK_INT |
