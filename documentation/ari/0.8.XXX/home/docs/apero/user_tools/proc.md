---
card_label: apero_processing
card_icon: fa-solid fa-screwdriver-wrench
---

# apero_processing

**Short name:** PROC  **Type:** tool  **Kind:** processing  **Instrument:** default

The processing script is the recommended way to run the reduction.
It takes a :term:`run-ini-file` which contains parameters specific to the users
needs for that processing session. Based on these run-ini-file parameters and the
raw data (stored in the :term:`DRS_DATA_RAW` directory) a set of recipes or a
:term:`recipe-sequences` will determine which recipes are run for which raw files.

The run-ini-files are an important part of the processing script and have
many options to control the processing run.

!!! note

    Some of the following arguments can also be added to the command-line or python function call
    (see section 4)

Options are:

- RUN_NAME: the name of the run
- SEND_EMAIL: whether to send an email on start/finish
- EMAIL_ADDRESS: the email address to send an email to
- RUN_OBS_DIR: Whether to limit processing to a single :term:`observation-directory`
- EXCLUDE_OBS_DIRS: Whether to ignore certain observation-directories
- INCLUDE_OBS_DIRS: Whether to limit processing to a set of observation-directories
- PI_NAMES: Whether to limit processing to a single or list of PI_NAMES (must match the header key :term:`KW_PI_NAME`)
- MASTER_OBS_DIR: The :term:`observation-directory` to use as the master

!!! note

    this should not be changed in general but does require calibrations from this night to be
    present in the raw directory.

    .. warning:: Currently we do not support multiple master_obs_dir and a full reduction should never mix
    different master observation-directories

- CORES: The number of cores to use
!!! warning

    This should always be at least N-1 less than the total number of cores available

- STOP_AT_EXCEPTION: The processing code will not continue past an error and will stop
- TEST_RUN: Runs the processing script without running any recipes
!!! note

    This is highly recommended, please check that you are reducing the expected data before running
    without TEST_RUN = False

- USE_ENGINEERING: If True engineering observation-directories (those without science observation).
!!! note

    In general we do not recommend to reduce these nights as they may
    reduce the quality of reduced data

- TRIGGER_RUN: For use in online reductions only

- USE_REJECTLIST: If True checks that odometer code aren't already flagged as bad files

- RECAL_TEMPLATES: If True recalculates the templates that are already present.
!!! warning

    This should only be done when re-reducing all data for a single object.
    Recalculating the template for only new observations will greatly affect RV precision
    and we do not recommend doing any time series analysis with a varying template.
    .. note:: A template hash key is available in the header of files that have used a template. If
    unsure check that the template hash matches for all observations.

- UPDATE_OBJ_DATABASE: If True the locally stored object database is updated from online.
!!! warning

    Do not do this unless you are re-reducing all the data. If the object database
    has updated parameters this could affect RV precision (as the BERV calculation may
    change).

- RUN_XXX: For each recipe (or recipe in a sequence) there is a :term:`shortname` associated with it. A user can
           turn on and off recipes within a sequence without having to create a new sequence.
           i.e. setting `RUN_PP = False` will turn of the `PP` recipe (apero_preprocessing) all recipe-runs in an
           apero_processing run will be skipped.

- SKIP_XXX: Similar to RUN_XXX there is a :term:`shortname` that can be skipped, if and only if the recipe-run can be
            found in the logging database (i.e. all required arguments are identical) and it has successfully completed
            in a previous apero_processing run, or when run individually

- TELLURIC_TARGETS: A filter for certain recipes that use hot star observations to only use certain hot star object names
                     (and thus only use certain observations). The default value is "All" which uses all telluric objects
                     in a pre-configured list of telluric object.

- SCIENCE_TARGETS: A filter for certain recipes that use science observations. Using this a user can only reduced data
                   for a single object name or a list of object names (separated by a comma).
                   For example if one sets `SCIENCE_TARGETS=Gl699` and had `RUN_EXTOBJ=True` only extractions of Gl699
                   would be reduced

The very last piece of information required is the sequences (or individual recipe runs) that are required.
The should be numbered id00000, id00001, id00002 etc and should only contain an individual recipe run (with all correct
arguments) or a sequence name. For sequence names see the sequences page for an instrument
(e.g. for spirou click here).

## Usage

```bash
apero_processing.py {runfile}[STRING] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{runfile}[STRING]` | [STRING] The run file to use in reprocessing |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--obs_dir[STRING]` | PROCESS_OBS_DIR_HELP |
| `--filename[STRING]` | [STRING] The 'filename' to reprocess (default is None for all files) |
| `--exclude_obs_dirs[STRING]` | PROCESS_EXCLUDE_OBS_DIRS_HELP |
| `--include_obs_dirs[STRING]` | PROCESS_INCLUDE_OBS_DIRS_HELP |
| `--cores[STRING]` | [INTEGER] Number of cores to use in processing |
| `--test[True,False,1,0,None]` | [BOOLEAN] If True does not process any files just prints an output of what recipes would be run |
| `--trigger` | [BOOLEAN] If True activates trigger mode (i.e. will stop processing at the first point we do not find required files). Note one must define --night in trigger mode |
| `--science_targets[STRING]` | [STRING] A list of object names to process as science targets (if unsets default to the run.in file) must be separated by a comma and surrounded with speech-marks i.e. 'target1,target2,target3' |
| `--telluric_targets[STRING]` | [STRING] A list of object names to process as telluric targets (if unsets default to the run.in file) must be separated by a commas and surrounded with speech-marks i.e. 'target1,target2,target3' |
| `--update_objdb` | Update the object database - only recommended if doing a full reprocess with all data. |
| `--to_file[STRING]` | [STRING] Output recipes to run to text file (sets --test=True) |
| `--verify` | [SWITCH] Verify input run file (but do not run) |
| `--queue_mode[True,False,1,0,None]` | Whether to run in queue mode (jobs are added to the queue instead of being processed directly). Overrides QUEUE_MODE from the run file and the QUEUE.MODE constant. |

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
