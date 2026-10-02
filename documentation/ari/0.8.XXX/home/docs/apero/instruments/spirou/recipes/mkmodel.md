---
card_label: apero_mk_model_spirou
card_icon: fa-solid fa-flask
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/sequences/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# apero_mk_model_spirou

**Short name:** MKMODEL  **Type:** recipe  **Kind:** tellu-hotstar  **Instrument:** SPIROU

## Water and dry component models (mkmodel)

During the pre-cleaning process (Artigau in prep.) for the hot stars (done as part of Amktellu) we calculate the
water and dry exponents of absorption. Once we have observed a sufficiently large library of telluric hot stars,
typically a few tens under varying airmass and water column conditions, we take all of the residual transmission
maps that passed quality control and calculate a linear minimization of the parameters. The linear minimization is
done per pixel per order, across all transmission maps (removing outliers with a sigma clipping approach) against a
three-vector sample (the bias level of the residual, the water absorption exponent, and the dry absorption exponent).
The output is three vectors each the same size as the input 2D spectrum ($49\times4088$), one for each of the
three vector samples. These are used in every ftellu recipe run to correct the telluric
residuals after telluric cleaning. The three vectors are saved and added to the telluric database.

## Usage

```bash
apero_mk_model_spirou.py {options}
```

## Optional arguments

| Argument | Description |
| --- | --- |
| `--database[True/False]` | [BOOLEAN] Whether to add outputs to calibration/telluric databases |
| `--plot[0>INT>4]` | [INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode |
| `--no_in_qc` | Disable checking the quality control of input files |

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

See the instrument [file definitions](/docs/apero/instruments/spirou/file_definitions) for the full file catalogue.

| name | description | HDR[DRSOUTID] | file type | basename | fibers | dbname | dbkey |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TRANS_MODEL | Telluric transmission model file | TRANS_MODEL | .fits | trans_model_{0} | AB, A, B | telluric | TELLU_MODEL |

## Plots

**Debug plots:**
`MKTELLU_MODEL`

**Summary plots:**
`SUM_MKTELLU_MODEL`
