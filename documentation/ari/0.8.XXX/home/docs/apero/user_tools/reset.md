---
card_label: apero_reset
card_icon: fa-solid fa-screwdriver-wrench
---

# apero_reset

**Short name:** RESET  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

The apero_reset recipe resets all (or some) of the data directories defined by the user

!!! warning

    Be very careful using this recipe, you can delete a lot of data very quickly
    There is no backup generated once apero_reset has been run.

For a normal run no arguments are required.

The reset recipe will guide you through all the data directories that can be reset and ask
whether you want to reset the directores. You must type "yes" to reset a directory.

If an directory is already empty it will be skipped.

The data directories that can be reset are as follows:

1. Assets directory

    This resets the :term:`DRS_DATA_ASSETS` directory (removes all files, and all databases)

2. Tmp directory

    This resets the :term:`DRS_DATA_WORKING` directory (removes all files) and the index database
    with :term:`block_kind` = "tmp"

3. Reduced directory

    This resets the :term:`DRS_DATA_REDUC` directory (removes all files) and the index database
    with :term:`block_kind` = "red"

4. Calibration directory

    This resets the :term:`DRS_CALIB_DB` directory (removes all files and copies in default ones) and
    resets the calibration database to its default state

5. Telluric directory

    This resets the :term:`DRS_TELLU_DB` directory (removes all files and copies in default ones) and
    resets the telluric database to its default state

6. Log directory

    This reset the :term:`DRS_DATA_MSG` directory (removes all files) and resets the log database.

!!! note

    After this is done, SKIP_XXX in the :term:`run-ini-files` does not skip files even if
    they are still on disk

7. Run directory

    This resets the :term:`DRS_DATA_RUN` directory (removes all files and copies in all default ones)

8. Out directory

    This resets the :term:`DRS_DATA_OUT` directory (removes all files) and the index database
    with :term:`block_kind` = "out"


!!! note

    You can use the `--warn=False` argument to avoid having to type "yes". `--warn=False` will reset everything
    without any warning (not recommended)

## Usage

```bash
apero_reset.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--nolog` | [BOOLEAN] If True logs the reset else is quite |
| `--nowarn` | [BOOLEAN] If True asks for user to type 'YES' before each reset |
| `--database_timeout[INT]` | [INTEGER] Set the database timeout number of tries |
| `--only_assets` | Reset only the assets directory |
| `--only_tmp` | Reset only the tmp directory |
| `--only_red` | Reset only the reduced directory |
| `--only_calib` | Reset only the calibration directory |
| `--only_tellu` | Reset only the telluric directory |
| `--only_log` | Reset only the log directory |
| `--only_plot` | Reset only the plot directory |
| `--only_run` | Reset only the run directory |
| `--only_lbl` | Reset only the lbl directory |
| `--only_out` | Reset only the out directory |
| `--only_other` | Reset only the other directory |

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
