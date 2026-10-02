---
card_label: apero_changelog
card_icon: fa-solid fa-code
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_changelog

**Short name:** CLOG  **Type:** nolog-tool  **Kind:** admin  **Instrument:** default

apero_changelog is used to prouce a nicly formatted change log from the
git commits (requires git commits to have messages).

The developer is asked whether a new version is required.
Versions must be in the form X.X.XXX where X is a number.

The recipe then updates the change log as well as update several files
throughout APERO and the documentation to update the version and date.

A git tag is also created to mark a new version.

!!! warning

    This change is hard to undo. Please use carefully and check
    the current version well before making a new version

!!! note

    This will add all untagged commits to this tag and version. For
    multiple commits see section 1.1.

#### 1.1 Adding a few versions at one time

If there are many commits and a few versions are required one can
add tags using `git tag {version} {commit number}` at the points
where a new version is required. Using `git log --since {date} > log.txt`
will produce a log of commit numbers since a date (set this date to the
previous verseion date). Do all but the most recent "version" this way and
then do the last one using apero_changelog and it will have the desired affect.

i.e.

```
git log --since 2020-09-03 > log.txt

git tag 0.1.234 3f95c84d1f54ae70c067aa2d253de31972abe93b
git tag 0.1.235 3f95c84d1f54ae70c067aa2d253de31972abe93b
git tag 0.1.236 4fea06752d89151896c5258caecfd3fe12e0c64d

apero_changelog.py    # for version 0.1.237
```

## Usage

```bash
apero_changelog.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--preview` | [BOOLEAN] If True previews the changelog before making any changes if False makes changes without preview |

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
