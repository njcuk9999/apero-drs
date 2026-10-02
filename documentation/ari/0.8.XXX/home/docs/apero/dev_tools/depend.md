---
card_label: apero_dependencies
card_icon: fa-solid fa-code
related:
  - apero/tools/
  - developer/
  - reference/
  - glossary
---

# apero_dependencies

**Short name:** DEPEND  **Type:** nolog-tool  **Kind:** admin  **Instrument:** default

The apero_dependencies recipe takes no arguments.

It scans through all valid python scripts within the apero module and prints
stats on:

- the number of lines
- the number of empty lines (no text)
- the number of comments
- the number of code lines (not comments)

We aim to have at least as many comments as lines of code, the text will
display in yellow for any script that this is not true for.

At the end the total number of these stats is printed.

i.e. for 2022-01-24

```
00:48:19.152-  |DEPEND| 	total lines: 156638
00:48:19.171-  |DEPEND| 	total empty lines: 11270
00:48:19.192-  |DEPEND| 	total lines of comments: 67476
00:48:19.220-  |DEPEND| 	total lines of code: 77892
```

Below this the modules that are used (and the current system versions) is
printed - standard modules have no version but this can be used as a
quick check of which modules should be in the requirements files.

i.e. for 2022-01-24

```
traceback       (No version info)
IPython         (8.0.1)
ipdb            (No version info)
pdb             (No version info)
ctypes          (1.1.0)
mpl_toolkits    (No version info)
tqdm            (4.62.3)
barycorrpy      (0.4.4)
matplotlib      (3.5.1)
struct          (No version info)
astropy         (5.0)
sqlalchemy      (1.4.28)
yagmail         (0.14.260)
multiprocessing (No version info)
numba           (0.54.1)
tkinter         (No version info)
Tkinter         (NOT INSTALLED)
bottleneck      (1.3.2)
mysql           (No version info)
string          (No version info)
tkFileDialog    (NOT INSTALLED)
tkFileFialog    (NOT INSTALLED)
tkFont          (NOT INSTALLED)
ttk             (NOT INSTALLED)
PIL             (9.0.0)
astroquery      (0.4.4)
collections     (No version info)
contextlib      (No version info)
copy            (No version info)
datetime        (No version info)
hashlib         (No version info)
pandasql        (No version info)
pandastable     (0.12.2)
pathlib         (No version info)
scipy           (1.7.3)
setuptools      (58.0.4)
signal          (No version info)
skimage         (0.19.1)
time            (No version info)
ttkthemes       (No version info)
typing          (No version info)
argparse        (1.1)
getpass         (No version info)
glob            (No version info)
gspread_pandas  (3.0.4)
importlib       (No version info)
itertools       (No version info)
numpy           (1.20.3)
os              (No version info)
pandas          (1.3.5)
pkg_resources   (No version info)
random          (No version info)
re              (2.2.1)
requests        (2.27.1)
shutil          (No version info)
socket          (No version info)
sqlite3         (No version info)
sys             (No version info)
textwrap        (No version info)
threading       (No version info)
warnings        (No version info)
yaml            (6.0)
```

## Usage

```bash
apero_dependencies.py {options}
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
