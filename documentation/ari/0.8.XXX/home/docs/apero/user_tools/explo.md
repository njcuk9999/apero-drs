---
card_label: apero_explorer
card_icon: fa-solid fa-screwdriver-wrench
---

# apero_explorer

**Short name:** EXPLO  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

The apero_explorer recipe is designed as a graphical user interface (GUI) between the user and the
various databases that APERO uses. The script downloads a static copy of the SQL database,
changes are not updated or saved in real time (but can be updated/saved by selecting the
correct menu options).

Tables within the database currently accessible with the explorer are:

- calib: The calibration database
- tellu: The telluric database
- index: The file index database
- log: The logger database
- object: The object astrometric database
- lang: The text and language database

The GUI allows the user to:

- Do File operations:
    - Open a pickle file to replace the current database
    - Import a csv file to replace the current database
    - Save a pickle file of the current database
    - Export a csv file of the current database

- Edit the current database
    - Find and replace a string with another value
    - Filter rows by a certain criteria
    - Add rows and columns

- Table operations
    - refresh the current database (with updates since launching the GUI)
    - Save changes for the current database to the main database
    - Clean strings
    - Remove formatting
    - Get some information of the table formatting

!!! note

    No changes will be saved unless you use the "Table>Save to Database" option

!!! note

    We do not recommend changing any of the database entries without good reason
    and without talking to the developers

In addition to the GUI explorer, apero_explorer can be run in "flag mode".

This recipes both the --recipe and --flagnum arguments to be used.

```
apero_explorer.py --recipe=PP --flagnum=21
```

Gives the binary flags for "preprocessing" (shortname: PP) when the decimal
representation of the flags is set to a value of (21)

The output for apero_explorer is then as follows:

```
 Flag mode: PP[21]
 recipe = apero_preprocess_spirou.py
   IN_PARALLEL         : True
   RUNNING             : False
   ENDED               : True
   OBJ                 : False
   QCPASSED            : True
```

Showing that the flag number 21 (binary 10101) corresponds to these flags being
true or false.

Note the flags are specific to a specific recipe and thus the --recipe argument
must be used.

## Usage

```bash
apero_explorer.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--hash` | Display all hash columns (hidden by default) |
| `--recipe[STRING]` | [STRING] Recipe or shortname for recipe (must be used in combination with –flagnum) |
| `--flagnum[INT]` | [INTEGER] Instead of running explorer converts a binary flagg to a set of binary flags for a recipe (must be used in combination with –recipe) |

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
