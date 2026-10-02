---
card_label: apero_precheck
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_precheck

**Short name:** PRECHECK  **Type:** tool  **Kind:** processing  **Instrument:** default

The precheck recipe allows the user to check the current raw data stored in the
:term:`DRS_DATA_RAW` directory. These checks are split into two parts a
file check and a object check. The checks are based on a supplied :term:`run-ini-file`
which controls which recipes are and are not being used for a specific apero_processing
run.

The file checks are as follows:

1. The number of calibrations in each :term:`observation-directory` and whether
   this meets the minimum number of calibrations required for the sequence
   defined in the :term:`run-ini-file`. A list of observation-directories that
   will cause problems due to missing calibrations is printed during the
   precheck recipe run.

!!! note

    Note if the observation-directory is sorted by observation night
    this will correctly flag if there are nights without calibrations
    within +/- the required time frame (controlled by :term:`MAX_CALIB_DTIME`)
    but will not be able to assess whether calibrations pass quality
    control during processing.

2. The number of science and telluric files found (note if the run-in-file has
   `USE_ENGINEERING = False` any observation-directory without science files will
   be ignored by the apero_processing recipe. The list of engineering observation-directories
   is also printed during the precheck recipe run.

The object check is done as follows:

1. The object database is checked for all valid entries (and any ignore entries)
2. All unique object names in raw files are checked against the object database
   object names (and associated aliases of each object name)
3. Any object name not in the current database and not in the current ignore list
   are printed for the user to decide whether object must be added to the
   database or left to use the header values

!!! note

    Objects are only required in the database for accurate BERV calculations,
    as such only objects required precision radial velocity must be in the
    database, however we recommend all objects be added.

## Usage

```bash
apero_precheck.py {runfile}[STRING] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{runfile}[STRING]` | [STRING] The run file to use in reprocessing |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--obs_dir[STRING]` | PROCESS_OBS_DIR_HELP |
| `--exclude_obs_dirs[STRING]` | PROCESS_EXCLUDE_OBS_DIRS_HELP |
| `--include_obs_dirs[STRING]` | PROCESS_INCLUDE_OBS_DIRS_HELP |
| `--no_file_check` | Don’t check the number of files on disk and don’t flag these errors |
| `--no_obj_check` | Don’t check object database with current set of raw files and don’t flag these errors |

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
