---
card_label: apero_langdb
card_icon: fa-solid fa-code
---

# apero_langdb

**Short name:** LANG  **Type:** nolog-tool  **Kind:** admin  **Instrument:** default

apero_langdb is used to view, update or reload the language database.

The view option (--find) loads a GUI that provides a search of all
message codes in APERO.

Message codes have the form XX-XXX-XXXXX  where each X is a digit.

One can search a code and find all python files which have that message code
and locate some other information about that message code.

The update option (--update or --upgrade) takes the current database.xsl file
and writes various csv files and update the local language database.

Similarly the reload optoin (--reload) just updates the local language database
(with the current csv files) this option is useful if updating APEROs version.

## Usage

```bash
apero_langdb.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--find` | Displays the message locator GUI |
| `--update` | Updates local language database and local text files with any changes |
| `--reload` | Reloads the local language database (with text file changes) |

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
