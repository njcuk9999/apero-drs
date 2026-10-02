---
card_label: apero_go
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_go

**Short name:** GO  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

apero_go is used to to find current paths set by current profile.

The paths are set via the user_config.py files (in the :term:`DRS_UCONFIG` directory).

Available paths (reffered to :term:`block_kind`) are:
raw, tmp, red, calib, tellu, out, assets, plot, run and log.

## Usage

```bash
apero_go.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--data` | Find the current data directory |
| `--all` | Display all relevant paths |
| `--setup` | Display DRS_UCONFIG path |
| `--mysql` | Display MySQL parameters |
| `--rawdir` | Find the current raw data directory |
| `--tmpdir` | Find the current tmp data directory |
| `--reddir` | Find the current red data directory |
| `--calibdir` | Find the current calib data directory |
| `--telludir` | Find the current tellu data directory |
| `--outdir` | Find the current out data directory |
| `--assetsdir` | Find the current asset data directory |
| `--plotdir` | Find the current plot data directory |
| `--rundir` | Find the current run data directory |
| `--logdir` | Find the current msg data directory |
| `--otherdir` | Find the current other data directory |
| `--lbldir` | Find the current lbl data directory |

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

This recipe produces no registered output files.
