---
card_label: apero_validate
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_validate

**Short name:** VALID  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

The validation recipe confirms that the configuration settings entered during the
installation process (or updated manually in the files afterwards) are correct to at least
setup APERO.

As part of the validation recipe constants are print to the screen, similarly
to when any recipe-run is started.

.. _startup_splash:

#### startup splash


The configuration values printed are as follows:

- The Instrument, :term:`PID` and current version of APERO
- :term:`DRS_DATA_RAW`: the raw directory
- :term:`DRS_DATA_REDUC`: the reduced data directory
- :term:`DRS_DATA_WORKING`: the preprocessed data directory
- :term:`DRS_CALIB_DB`:
- :term:`DRS_TELLU_DB`:
- :term:`DRS_DATA_ASSETS`:
- :term:`DRS_DATA_MSG`:
- :term:`DRS_DATA_RUN`:
- :term:`DRS_DATA_PLOT`:
- DRS_CONFIG: a list of places parameters and constants are taken from (ordered
  in decending priority
- DATABASE: The database type (MYSQL or SQLITE3)
- DATABASE-CALIB: the address of the calibration database table
- DATABASE-TELLU: the address of the telluric database table
- DATABASE-INDEX: the address of the index database table
- DATABASE-LOG: the address of the log database table
- DATABASE-OBJECT: the address of the object database table
- DATABASE-LANG: the address of the language database table
- :term:`DRS_PRINT_LEVEL`: the standard output (console) level of logging
- :term:`DRS_LOG_LEVEL`: the log file level of logging
- :term:`DRS_PLOT`: the plotting mode (0, 1 or 2)

The splash screen should look similar to this:


.. image:: ../../../_static/images/apero_splash.png

## Usage

```bash
apero_validate.py {options}
```

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
