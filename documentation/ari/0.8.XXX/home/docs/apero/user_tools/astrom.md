---
card_label: apero_astrometrics
card_icon: fa-solid fa-screwdriver-wrench
---

# apero_astrometrics

**Short name:** ASTROM  **Type:** tool  **Kind:** user  **Instrument:** default

Run this recipe to check, find and/or add targets to the online astrometric database

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Usage

```bash
apero_astrometrics.py {objects}[STRING] {options}
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `{objects}[STRING]` | [STRING] A list of object names to check, find and/or add to the online database. Should be comma separated without white spaces |

## Optional arguments

| Argument | Description |
| --- | --- |
| `--overwrite` | Do not check if object is currently in database. Overwrite old value. |
| `--getteff` | Attempt to get Teff from header value. Requires a raw file of this object and the index database to be up-to-date |
| `--nopmrequired` | Do not require proper motion (not recommended) |
| `--test` | Run in test mode (do not add to database) |
| `--check` | Check object database for basic errors |
| `--fileoption[STRING]` | Use a absolute filepath to identy an object (i.e. from RA/Dec). Note this overrides "OBJECTS", however OBJECT must be set to something to run astrometrics. |
| `--aliases[STRING]` | Aliases to add to the database for this object. Note this should only be used with a single object name. |

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
