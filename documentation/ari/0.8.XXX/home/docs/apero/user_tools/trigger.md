---
card_label: apero_trigger
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_trigger

**Short name:** TRIGGER  **Type:** nolog-tool  **Kind:** processing  **Instrument:** default

The apero trigger runs continuiously and tries to accurately reduces night data.

It requires a master night to be processed BEFORE starting.


#### How it works

It works as follows:

    - copies files from a "live directory" into a sym-linked directory
      (the live directory is defined be --indir, the sym-lined directory
      is the raw directory defined in installation -- i.e. DRS_DATA_RAW)

    - tries to figure out what has been done previously
        - this is done in two steps

        - first step: calibrations
            - it uses the log database and the `trigger_night_calibrun.ini`
              file to work out (per obs_dir) whether at least one of  each
              recipe has been run (it counts QC failures as done)
            - if all steps are not complete it runs `apero processing` with the
              `trigger_night_calibrun.ini` run.ini file with the standard
              skips in `apero_processing`
            - apero_processing will stop if a recipe finds no runs (this is
              only true in `TRIGGER_RUN=True` mode

        - second step: science
            - this step is only done once all calibrations are deemed to be
              completed
            - it uses the log database, index database and the
              `trigger_night_scirun.ini` file to work out whether all recipes
              with science DPRTYPES have been run (per obs_dir)
            - if there aren't the same number of raw science files as recipe
              runs (in the log database) it will attempt to re-run
              `apero processing` with the `trigger_night_scirun.ini` run.ini
              file with the standard skips in `apero_processing`
            - apero_processing will stop if a recipe finds no runs (this is
              only true in `TRIGGER_RUN=True` mode


#### Caveats

- results may not be optimal - we recommended running all nights together in
  an offline manner (after having all nights) for optimal results, for example:
      - calibrations may be sub-optimal (missing/using wrong night etc)
      - telluric correction may not be using all hot stars
      - templates may be sub-optimal
      - polar recipes cannot be produced online
- A master night must be run before running `apero_trigger.py`
- Adding files for older nights after newer nights could result in unwanted behaviour
  (especially when it comes to calibrations)
- Removing files may result in new calibrations being generated with less calibrations
  than before (apero_processing skip only works with the same number of files)
  and apero will use the most recently reduced calibration
- Once calibrations are finished for a night remove/adding calibration files will not
  re-trigger the calibration sequence (unless --reset is used)
- All obs_dir and files in the --indir will be processed, use --ignore to remove
  certain obs_dirs from the obs_dirs list

## Usage

```bash
apero_trigger.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--indir[STRING]` | [STRING] The input directory to scan for new data. (This is not the apero defined raw directory) |
| `--reset` | Reset the trigger (default is False and thus we use cached files to speed up trigger). This means after nights are marked done (calib/sci) they will not be reprocessed. Thus --reset to avoid this. |
| `--ignore[STRING]` | [STRING] Ignore certain obs_dir (observation directories) by default all directories in --indir are reduced. Using ignore will ignore certain directories and not add them to the the sym-linked (DRS_DATA_RAW) directory. |
| `--wait[1>INT>3600]` | [INTEGER] Number of second to wait between processing runs. Should not be too low (below 10s its too fast) unless testing, or too high (above 3600s) |
| `--calib[STRING]` | [STRING] The run.ini file to use for calibration trigger run |
| `--sci[STRING]` | [STRING] The run.ini file to use for science trigger run |
| `--trigger_test` | Active test mode (does not run recipes) |

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
