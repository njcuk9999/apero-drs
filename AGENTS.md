# AGENTS.md — APERO DRS Codebase Guide

## Project Overview
APERO (A PipelinE to Reduce Observations) is a multi-instrument astronomical spectroscopy pipeline. Active instruments: **SPIROU**, **NIRPS_HA**, **NIRPS_HE**, **SPIP**. Version: `0.7.x` (stable); `0.8.x` (in development).

---

## Architecture & Layer Rules

The codebase is strictly layered with enforced import rules (documented at the top of each module):

```
apero/base/      ← Foundation: NO apero imports allowed (base.py, drs_base.py, drs_db.py)
apero/core/      ← Infrastructure: constants, file types, databases, recipe framework
apero/science/   ← Science algorithms: calib/, extract/, polar/, telluric/, velocity/
apero/recipes/   ← Entry-point scripts, one per instrument (spirou/, nirps_ha/, etc.)
apero/tools/     ← Admin tools: apero_processing, apero_database, apero_reset, etc.
apero/lang/      ← Language/text database (ENG/FR), keyed string lookup via textentry()
apero/io/        ← I/O utilities: drs_fits, drs_image, drs_path, drs_table, drs_lock
```

Violating import rules (e.g., importing `core` from `base`) will cause circular import failures.

---

## Instrument-Specific Code Pattern

Each instrument has a subdirectory in `apero/core/instruments/{instrument}/` containing:
- `default_config.py` — user-configurable parameters
- `default_constants.py` — pipeline constants (numeric, string, bool)
- `default_keywords.py` — FITS header keyword mappings
- `file_definitions.py` — `DrsFitsFile`/`DrsInputFile` file-type definitions with header key matchers
- `pseudo_const.py` — computed constants as methods of `PseudoConstants(DefaultPseudoConstants)`
- `recipe_definitions.py` — CLI argument/option definitions reused across recipes

**To override a default constant for a specific instrument, always use `.copy(__NAME__)`:**
```python
# In apero/core/instruments/spirou/default_constants.py
EFFGAIN = EFFGAIN.copy(__NAME__)
EFFGAIN.value = 0.999
```
Never mutate originals — each instrument gets its own `Const` instance.

---

## Recipe Structure

Every recipe in `apero/recipes/{instrument}/` follows this mandatory pattern:

```python
__NAME__ = 'apero_extract_spirou.py'
__INSTRUMENT__ = 'SPIROU'
WLOG = drs_log.wlog

def main(obs_dir=None, files=None, **kwargs):
    fkwargs = dict(obs_dir=obs_dir, files=files, **kwargs)
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    llmain, success = drs_startup.run(__main__, recipe, params)
    return drs_startup.end_main(params, llmain, recipe, success)

def __main__(recipe, params):
    # All actual logic lives here; receives DrsRecipe + ParamDict
    ...
    return locals()
```

`bin/apero_*_spip.py` are thin wrappers that call each recipe's `main()`.

---

## Central Parameter Dictionary (`ParamDict`)

`params` is the universal context object passed through all functions. Key namespaces:
- `params['INPUTS']` — CLI/function keyword arguments (e.g., `params['INPUTS']['FILES']`)
- `params['DATA_DICT']` — data passed between internal calls
- All instrument constants from `default_config` / `default_constants` are merged in at startup

Access constants via `params['CONSTANT_NAME']`; instrument-computed values via `pconst = constants.pload()`.

---

## Database System

7 databases managed through `apero/core/core/drs_database.py`:

| Name    | Class                    | Purpose                          |
|---------|--------------------------|----------------------------------|
| calib   | `CalibrationDatabase`    | Calibration file registry        |
| tellu   | `TelluricDatabase`       | Telluric star file registry      |
| findex  | `FileIndexDatabase`      | All processed file index         |
| log     | `LogDatabase`            | Recipe execution logs            |
| astrom  | `AstrometricDatabase`    | Object astrometry                |
| lang    | —                        | Text/language key lookup         |
| reject  | `RejectDatabase`         | Rejected file registry           |

Backend: SQLite (default) or MySQL. Low-level SQL lives in `apero/base/drs_db.py`.

---

## Logging Convention

All log calls use `WLOG` with text keys (language-independent):
```python
WLOG(params, 'warning', textentry('10-016-00012', args=wargs), sublevel=2)
WLOG(params, 'error', textentry('00-001-00001'))  # raises DrsCodedException
WLOG(params, 'info', 'Plain string also accepted')
```
Log levels: `'info'`, `'warning'`, `'error'`, `'debug'`, `''` (blank/print only).

---

## Configuration & Environment

- **`$DRS_UCONFIG`** — required env var pointing to the user profile directory containing `install.yaml`
- Per-instrument user overrides: `$DRS_UCONFIG/{INSTRUMENT}/user_config.ini`, `user_constants.ini`, `user_keywords.ini`
- Data directories (configurable in `user_config.ini`): `raw/`, `tmp/` (preprocessed), `reduced/`, `calibDB/`, `telluDB/`, `msg/`, `plot/`, `runs/`

---

## Installation (Developer)

```bash
conda create --name apero-env-07 && conda activate apero-env-07
pip install -r requirements_current.txt          # pinned deps (Python 3.9)
pip install -U -e ./apero-ri                     # optional web UI
# then run setup/install.py to create instrument profile
```

`lbl` (line-by-line RV) is a required git dependency: `lbl @ git+https://github.com/njcuk9999/lbl.git@apero_v7`

---

## Key Files for New Features

| Task | Files to read/edit |
|------|--------------------|
| Add a new recipe | `apero/core/instruments/{inst}/recipe_definitions.py`, then create `apero/recipes/{inst}/apero_new_{inst}.py` |
| Add a new file type | `apero/core/instruments/{inst}/file_definitions.py` |
| Add/change a constant | `apero/core/instruments/{inst}/default_constants.py` (use `.copy()`) |
| Add a new science function | `apero/science/{domain}/` module |
| Add a tool/utility | `apero/tools/recipes/bin/` |

## Companion Repository

`apero-utils/` (separate repo) provides post-processing utilities, organized under `spirou/`, `nirps/`, and `general/`. These are standalone scripts, not imported by the main pipeline.

