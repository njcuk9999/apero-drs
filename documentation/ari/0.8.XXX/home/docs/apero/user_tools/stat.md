---
card_label: apero_stats
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_stats

**Short name:** STAT  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

The apero stats file is usually run during or after a apero_processing run.

There are three modes:

- timing mode: (using --mode=timing)
- quality control mode: (using --mode=qc)
- error mode: (using --mode=error)

If the `--plog` argument is used (with the absolute path to a apero log file group)
then only the stats for that apero_processing run are used


#### 1.1 Timing mode

This mode takes all the :term:`recipe-runs` in the logger database (at this point in time) and measures
various timing stats for each recipe.

!!! warning

    timing mode has to read and sort all log entries. This can take
    quite some time to get the stats of a full run of data

!!! note

    The --plog argument is not used for timing mode

The stats are printed per recipe (named by the :term:`shortname`) and are as
follows:

- Mean time: the mean time for recipes of this shortname +/- the standard deviation
- Median time: the median time for recipes of this shortname +/- the standard deviation
- The range in times (minimum and maximum) for recipes of this shortname
- The number of runs (`Nruns`) of this recipe attempted
- The total time recipes of this shortname were running (end of last recipe run minus start of first recipe run)
!!! note

    The total time is only correct if all recipes of this shortname were run without interruption with no
    other recipe runs between - this is the standard apero_processing approach but may not be true if
    analysing multiple log entries

- The total cpu time the recipe of this shortname were running (the duration) note if all recipes of this shortname
  ran in a single block this should be the time taken if done on a single core
- efficiency `(total cpu time)/(total time)`, perfect efficiency would give a value equal to the number of cores used
  (however a perfect efficiency is impossible)

!!! note

    If `Nruns` is less than the number of cores the total cpu time and total time should be the same and the
    efficiency should tend towards (or be exactly 1).

As well as the stats, after all stats have printed a histogram of each recipe with over 10 recipe-runs is plotted.
This shows this distribution of timings for each shortname.


1.2 Quality control mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^6

This mode takes all the :term:`recipe-runs` in the logger database and prints statistics on the quality control
recorded in each recipe (if present).

!!! warning

    quality control mode has to read and sort all log entries. This can take
    quite some time to get the stats of a full run of data

!!! note

    The --plog argument is not used for timing mode

The stats are printed per recipe (named by the :term:`shortname`) and are as
follows:

- The number passed compared to the number that finished in total
- The number failed compared to the number that finished in total
- The Mean/Median/Max/Min and criteria of failure for each quality control
- The number that were still "running" when this report was made (should be zero if not apero_processing is running)
- The number that ended successfully (i.e. did not encouter an error or exception - handled or otherwise)

As well as this for each shortname that has quality control a plot is produced. This plot should show N+1 panels,
where N is the number of quality control criteria. The top panel shows the global pass/fail/ended statistics
(taking into account all quality control criteria). The other panels show (if numeric) a value of the quality control
criteria measured for each recipe run with that shortname as a function of observation date
(from header key :term:`KW_MID_OBS_TIME`). These values should be in blue and in red (as a dashed line) compared to
a logic threshold (i.e. points above or below, depending on the criteria fail or pass).

This process is repeated for each shortname and graphs and or stats are shown if quality control criteria are available
and numeric.


#### 1.3 Error mode

The error mode takes all errors caught during apero_processing runs.
Using the --plog argument one can select just a single apero_processing run.

!!! note

    the only log files that should be used as an argument to --plog are in
    the :term:`DRS_DATA_MSG` directory, specifically `./tool/other/APEROL-PID-{PID}-apero_processing.log` files
    (there should be one of these log files for each time apero_processing was run) where :term:`PID` is the unique
    PID for that apero_processing run.

The error mode groups all found errors into files based on the apero error codes given (i.e. EXX-XXX-XXXXX) and also
groups any errors that do not have an apero error code (unexpected exceptions) by the last line of text of that
exception (generally these are the same for the same exception).

Statistic of these are printed to the screen and a directory is added to the
`DRS_DATA_MSG/report/APEROL-PID-{PID}_apero_processing/` directory.

Files are saved as the error code: E_XX_XXX_XXXXX.log or if they were unexpected exceptions with a E_UNHANDLE_YYYYY.log
where YYYYY increases from 0 up to the maximum number of unique unexpected execptions.

Each of these error log files contains all errors that match

```
#================================================
# {i} / {total}
# RUNSTRING = program.py {arguments} {options}
#=================================================

ERROR MSG LINE 1
ERROR MSG LINE 2
...
ERROR MSG LINE N
```

Where i is the nth error of this type, total is the total number of errors of this type

## Usage

```bash
apero_stats.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--mode[STRING]` | [STRING] Stats mode. Any combination of the following (separated by a comma, no white spaces). For all use “all”. For timing statistics use "timing". For quality control statistics use "qc". For error statistics use "error". For memory statistics use "memory". For file index use “findex”.  I.e. --mode=qc,memory  runs the qc and memory stats. |
| `--plog[STRING]` | [STRING] Specify a certain log file (full path) |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--sql[STRING]` | [STRING] Specify a SQL WHERE clause to narrow the stats |
| `--limit[INT]` | Limit the number of entries in memory plot (any recipe with more than this limit is left out of stats) |

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

## Plots

**Debug plots:**
`STATS_TIMING_PLOT`, `STAT_QC_RECIPE_PLOT`, `STAT_RAM_PLOT`
