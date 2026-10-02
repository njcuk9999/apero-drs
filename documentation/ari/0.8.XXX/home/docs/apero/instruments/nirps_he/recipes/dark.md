---
card_label: apero_dark_nirps_he
card_icon: fa-solid fa-flask
related:
  - apero/instruments/nirps_he
  - apero/instruments/nirps_he/sequences/
  - apero/instruments/nirps_he/file_definitions/
  - glossary
---

# apero_dark_nirps_he

**Short name:** DARK  **Type:** recipe  **Kind:** calib-night  **Instrument:** NIRPS_HE

Dark finding recipe for NIRPS HE

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Usage

```bash
apero_dark_nirps_he.py {obs_dir}[STRING] [FILE:DARK_DARK,NIGHT_SKY_SKY] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{obs_dir}[STRING]` | [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory |
| `[FILE:DARK_DARK,NIGHT_SKY_SKY]` | [STRING/STRINGS] A list of fits files to use separated by spaces. Current allowed types: DARK_DARK_INT, DARK_DARK_TEL, DARK_DARK_SKY |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--combine[True/False]` | [BOOLEAN] Whether to combine fits files in file list or to process them separately |
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

See the instrument [file definitions](/docs/apero/instruments/nirps_he/file_definitions) for the full file catalogue.

| name | description | HDR[DRSOUTID] | file type | suffix | dbname | dbkey | input file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DARKI | Internal dark calibration file | DARKI | .fits | _darki | calibration | DARKI | DARK_DARK |
| DARKI | Internal dark calibration file | DARKI | .fits | _darki | calibration | DARKI | DARK_DARK |
| DARKNS | Night Sky dark calibration file | DARKNS | .fits | _dark_ns | calibration | DARK_NS | NIGHT_SKY_SKY |

## Plots

**Debug plots:**
`DARK_IMAGE_REGIONS`, `DARK_HISTOGRAM`

**Summary plots:**
`SUM_DARK_IMAGE_REGIONS`, `SUM_DARK_HISTOGRAM`
