---
card_label: apero_database
card_icon: fa-solid fa-code
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_database

**Short name:** DBMGR  **Type:** nolog-tool  **Kind:** admin  **Instrument:** default

The apero_database recipe gives some ways to manage the local SQL/MySQL databases and tables.


The options are:

- kill all database operations (--kill): Rarely the database completely
  freezes the --kill option should free this up if this is not possible use
  the apero_database_kill recipe.

- update object database (--objdb): Use the online google sheet to update the
  local object database

!!! note

    This requires an internet connection

- update (--update) the calibration, telluric, log and index database using the files on
  disk in all the current apero profile data directories (raw/tmp/red/calib/tellu)

- import (--importdb) a csv file into either the calibration, telluric, index, log or object database

!!! note

    Columns must conform with current database definitions
    .. note:: You must also give the --csv argument with the absolute path to the csv file

    .. note:: The language database can also be imported but this is not recommended

    .. note:: use the --join option to decide how to add the database (replace removes current database,
    append adds the csv contents to the end)

- export (--exportdb) a csv file for the calibration, telluric, index, log or object database.

!!! note

    You must also give the --csv argument with the absolute path to the csv file
    .. note:: The language database can also be imported but this is not recommended

- manage all apero tables i.e. delete (--delete) a database using a GUI to select
  which tables (across all APERO profiles)

!!! warning

    Only remove databases you are sure are not being used. This is not
    backed up

## Usage

```bash
apero_database.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--push` | Push pending database entries to the database |
| `--pushname[STRING]` | Shortname of the pending database entries to push |
| `--kill` | Use this when database is stuck and you have no other opens (mysql only) |
| `--dbkind[all,calib,tellu,findex,log,astrom,reject,lang]` | Database kind to update or reset. Must use inconjuction with --update or --reset |
| `--update` | Use this to update the database based on files on disk in the correct directories (Currently updates calib/tellu/log and index databases) |
| `--reset` | Reset current databases |
| `--csv[STRING]` | Path to csv file. For --importdb this is the csv file you wish to add. For --exportdb this is the csv file that will be saved. |
| `--exportdb[calib,tellu,findex,log]` | Export a database to a csv file |
| `--importdb[calib,tellu,findex,log]` | Import a csv file into a database |
| `--join[replace,append]` | How to add the csv file to database: append adds all lines to the end of current database, replace removes all previous lines from database. Default is ‘replace’. |
| `--delete` | Load up the delete table GUI (MySQL only) |
| `--cores[INT]` | Number of cores to use for parallel database updates (default is 0, which uses value from yaml file). Use with --update to enable parallel processing for calib, tellu, log, and index databases. |
| `--block_kind[STRING]` | Block kind filter (not always used) |
| `--keys[STRING]` | Keyname of entries to remove (used in combination with --telludb or --calibdb) |
| `--since[STRING]` | Date to remove entries since (used in combination with --telludb or --calibdb) format is YYYY-MM-DD or YYYY-MM-DD hh:mm:ss |
| `--before[STRING]` | Date to remove entries before (used in combination with --telludb or --calibdb) format is YYYY-MM-DD or YYYY-MM-DD hh:mm:ss |
| `--deletefiles` | Whether to delete files from disk when removing entries (using in combination with --telludb or --calibdb and --since / --keys) |
| `--test` | Run the removal of entries in test mode |

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
