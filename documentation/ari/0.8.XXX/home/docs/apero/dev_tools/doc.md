---
card_label: apero_documentation
card_icon: fa-solid fa-code
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_documentation

**Short name:** DOC  **Type:** nolog-tool  **Kind:** admin  **Instrument:** default

The apero_documentation recipe allows updatings, compiling and uploading of
this documenation (via Sphinx).

One can do this for all instruments (--instruments=ALL) or for an individual
instrument (however the compile and upload will re-compile/re-upload all
local files).

If the file_definitions.py has been updated one can use the
--filedef argument to update the documentation file definitions.

If the recipes within recipe_definitions.py has been updated one can use the
--recipedef argument to update the documentation and if the sequences within
recipe_definitions.py has been updated one can use the --recipeseq argument
to update the docuementation.

The safest option is to use --filedef --recipedef --recipeseq to update all
automatically created definitions.

One can compile the html and/or latex documents by using --compile and change
between compiling html/latex/both with the --mode option.

Finally one can --upload the changes to the webserver (password will be
required for the rsync)

!!! warning

    you must make sure --compile has been done before this otherwise
    you could sync a empty directory and remove all files from the
    webserver

In general one probably runs this command with all arguments.
i.e.

```
apero_documentation.py --filedef --recipedef --recipeseq --compile --upload --mode=html
```

## Usage

```bash
apero_documentation.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--instruments[STRING]` | [STRING] Which instrument(s) to run this for (default is current instrument) can also write ALL to get all instruments or list instruments separated by a comma |
| `--compile` | Compile all rst pages |
| `--upload` | [Bool] If True upload documentation to defined server (for web access) |
| `--all` | --filedef --recipedef and --recipeseq |
| `--filedef` | Compile the docs for file definitions |
| `--recipedef` | Compile the docs for recipe definitions |
| `--recipeseq` | Compile the docs for recipe sequences |
| `--mode[both,html,latex]` | [STRING] Which mode to output in "html", "latex" or "both". Default is "both". |
| `--ari` | Generate the apero-ri markdown documentation tree (documentation/ari/{docversion}/home/docs/apero) from the recipe and file definitions |
| `--docversion[STRING]` | [STRING] Documentation version directory to write to with --ari (e.g. 0.8.XXX). Defaults to the major version of the running APERO. |
| `--migrate_desc` | One-off migration of the legacy rst descriptions in documentation/working/resources to documentation/descriptions (markdown). Existing markdown fragments are never overwritten. |

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
