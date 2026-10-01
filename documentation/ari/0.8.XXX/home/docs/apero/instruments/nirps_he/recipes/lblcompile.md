---
card_label: apero_lbl_compile_nirps_he
card_icon: fa-solid fa-flask
---

# apero_lbl_compile_nirps_he

**Short name:** LBLCOMPILE  **Type:** recipe  **Kind:** lbl  **Instrument:** NIRPS_HE

Run LBL compute

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Usage

```bash
apero_lbl_compile_nirps_he.py {objname}[STRING] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{objname}[STRING]` | [STRING] The object name to process |

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

**Output directory:** `PATH.LBL // Default: "lbl" directory`

| name | description | file type | basename |
| --- | --- | --- | --- |
| LBL_RDB | LBL rdb file (RVs) in ascii-rdb format | .rdb | lbl_{obj}_{temp} |
| LBL_RDB_FITS | LBL rdb file (RVs) in fits format | .fits | lbl_{obj}_{temp} |
| LBL_RDB2 | LBL binned per night rdb file (RVs) | .rdb | lbl2_{obj}_{temp} |
| LBL_RDB_DRIFT | LBL Drift corrected rdb file | .rdb | lbl_{obj}_{temp}_drift |
| LBL_RDB2_DRIFT | LBL Drift corrected binned rdb file | .rdb | lbl2_{obj}_{temp}_drift |
| LBL_DRIFT | LBL drift file (calculated from FPs) | .rdb | drift |
