---
card_label: apero_listing
card_icon: fa-solid fa-screwdriver-wrench
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_listing

**Short name:** LIST  **Type:** nolog-tool  **Kind:** user  **Instrument:** default

The apero_listing recipe re-builds the index database.
It has various ways of doing this:

 - :term:`observation-directory` (using the --obs_dir argument) to select one observation-directory
 - :term:`block_kind` (using the --block_kind argument) to select either "raw", "tmp" or "red" data directory
 - excluding observation directories: these directories will be ignored
   (multiple observation-directories should be comma separated)
 - including observation directories: these directories will be included and everything else ignored
   (multiple observation-directories should be comma separated)

## Usage

```bash
apero_listing.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--obs_dir[STRING]` | LISTING_HELP_OBS_DIR |
| `--block_kind[raw,tmp,red,out]` | [STRING] The kind of indexs to rebuild (i.e. raw, tmp or reduced) |
| `--exclude_obs_dirs[STRING]` | PROCESS_EXCLUDE_OBS_DIRS_HELP |
| `--include_obs_dirs[STRING]` | PROCESS_INCLUDE_OBS_DIRS_HELP |

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
