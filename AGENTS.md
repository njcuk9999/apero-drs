# APERO Agent Guidelines

## Package layout

- `apero-core/aperocore` contains reusable, DRS-independent functionality.
  Do not add imports from `apero` or APERO recipe/configuration code here.
- `apero-drs/apero` is the data-reduction pipeline. Keep dependencies layered:
  `apero.base` has no APERO imports; `apero.lang` may depend only on `base`;
  core modules must depend only on lower-level core, language, and base modules.
  Higher-level `io`, `plotting`, `recipes`, `science`, and `tools` modules may
  depend on the layers below them.
- `apero-ri/apero_ri` is the Flask reduction interface. It may use `aperocore`
  and `apero`, but interface-specific code belongs in the RI package.

## Git commit messages

Every commit (whether authored by Claude, GitHub Copilot, or a human) must
start with a bracketed tag naming the package(s) and project(s) touched,
followed by a short imperative summary:

```
[PACKAGE.PROJECT] Short imperative summary of the change
```

- `PACKAGE` is `APERO` (apero-drs), `APEROCORE` (apero-core), or
  `APERO+APEROCORE` when a single commit spans both packages. Use `ARI` for
  `apero-ri` changes.
- `PROJECT` is one of the project tags below, upper-case. Combine multiple
  projects touched by the same commit with `+`, e.g.
  `[APERO.LOC+SHAPE]` or `[APERO.PP+CAL+EXT+POL]`.
- Do not invent ad-hoc spellings of an existing tag (e.g. `EXTRACTION` vs
  `EXTRACT`, `LOCALISATION` vs `LOC`) - past commits were inconsistent here;
  use the exact tag from the list below so tags stay greppable.
- If a change genuinely doesn't fit an existing project, add the new tag to
  the list below in the same commit rather than leaving it undocumented.

Current project tags (not exhaustive - extend this list as needed):

- `CORE` - shared/base functionality in `aperocore` not tied to one project
- `SETUP` - installation, environment, packaging, `pip`/`setup.py`
- `DEV` - `apero.dev` / developer-only tooling and test scaffolding
- `PREPROCESS` - `apero_preprocess`
- `LOC` - localisation (`apero_loc`)
- `SHAPE` - shape calibration (`apero_shape`)
- `EXTRACT` - extraction (`apero_extract`, `apero_flat`, `apero_thermal`)
- `WAVE` - wavelength solution (`apero_wave_ref`, `apero_wave_night`)
- `TELLURIC` - telluric correction (`apero_mk_tellu`, `apero_fit_tellu`)
- `TEMPLATE` - template creation (`apero_mk_template`)
- `CCF` - cross-correlation function (`apero_ccf`)
- `LBL` - line-by-line integration
- `POL` - polarimetry
- `TOOLS` - `apero.tools` scripts and utilities
- `ASTROMETRICS` - astrometric database / gaia crossmatch
- `RESET` - `apero_reset` and profile reset logic
- `DATABASE` - calibration/telluric/index database code
- `PROCESSING` - `apero_processing` / recipe sequencing
- `STARTUP` - `drs_startup`, recipe/module initialization and import speed
- `CHECKS` - `apero_checks` / data-quality checks
- `REJECT` - manual/auto rejection of files
- `QUEUE` - job queue management
- `VISU` - visualisation tools (`apero.tools.module.visulisation`)
- `KEYWORDS` - FITS header keyword definitions
- `PSEUDO_CONST` - instrument pseudo-constants
- `VERSION` - version bump / release metadata
- `RI` - `apero-ri` specific changes (usually paired with the `ARI` package
  tag instead, but use this project tag if `PACKAGE` is `APERO+APEROCORE`)

Examples:

```
[APERO.EXTRACT] Vectorize background-map percentile filtering
[APEROCORE.CORE] Route nan-aware stats through math wrapper
[APERO.LOC+SHAPE] Move order-profile straightening into apero_shape
[APERO+APEROCORE.EXTRACT] Add flat-response calibDB round trip
```

## Changing a function's inputs or outputs

- When you change a function's parameters (added/removed/reordered/retyped)
  or its return type/shape (e.g. a tuple becomes a `ParamDict`, or the keys
  of a returned dict change), grep the whole monorepo (`apero-core`,
  `apero-drs`, `apero-ri`, and `tools/`) for every call site and update each
  one in the same change. Do not update only the call sites you happen to be
  working on. A `bout['KEY']` style access on what used to be a tuple return
  will not raise at import time - it silently reassigns whatever the caller
  unpacks it into, so an unrefactored caller is a correctness bug, not a
  crash you can catch with a quick smoke test.
- After changing a signature, search for the old call pattern (not just the
  function name) to catch callers that unpack a return value positionally,
  since those are the ones most likely to break silently.

## `aperocore.science` functions

- Functions in `apero-core/aperocore/science/*_core.py` (e.g. `wave_core.py`,
  `background_core.py`, `localisation_core.py`, `shape_core.py`) must not import or receive
  an APERO `ParamDict`, `DrsRecipe`, `DrsFitsFile`, or any other apero-drs
  object. They must only take plain, well-documented arguments (numpy
  arrays, floats, ints, strings, tuples/lists of those). This keeps them
  usable by external packages that depend on `apero-core` without an APERO
  profile/`apero-drs` installed.
- Put the thin apero wrapper that reads params/config, unpacks a
  `ParamDict`/`DrsFitsFile`/calibration file, and calls the corresponding
  `aperocore.science` function next to the higher-level apero function it
  supports (e.g. `apero-drs/apero/science/calib/localisation.py` wraps
  `aperocore.science.calib.localisation_core`).


## Python code

@.github/instructions/python-apero.instructions.md

- Prefer `np.array(x)` over `np.asarray(x)`. `np.asarray` avoids a copy when
  `x` is already an array, which can cause hard-to-trace mutations of the
  caller's data. Use `np.array(x)` (which always copies) unless you have
  explicitly profiled the allocation and determined that a view is safe.
- Import `aperocore.math` as `from aperocore import math as mp` and use its
  wrapped functions instead of the numpy equivalent whenever one exists,
  e.g. `mp.nanmedian`, `mp.nanpercentile`, `mp.nanmean`, `mp.nanstd`,
  `mp.nansum`, `mp.nanmax`, `mp.nanmin`, `mp.nanargmax`, `mp.nanargmin`,
  `mp.median` in place of `np.nanmedian`, `np.nanpercentile`, `np.nanmean`,
  `np.nanstd`, `np.nansum`, `np.nanmax`, `np.nanmin`, `np.nanargmax`,
  `np.nanargmin`, `np.median`. These route through `bottleneck` when
  available for speed, with numpy as the fallback. Exception: if the call
  needs a tuple `axis` (e.g. `axis=(1, 3)`), keep the raw `np.*` call —
  `bottleneck`'s implementations only accept an int or `None` axis, so
  `mp.*` would break at runtime with `bottleneck` installed. This rule does
  not apply inside `apero-core/aperocore/math/*` itself, where the raw
  `np.*` calls are the actual implementation/fallback.

## APERO recipe structure: top-level principles

- APERO recipe `__main__` functions should be top-level, easy to follow, and
  minimal in code — the less code in the recipe the better.
- Structure each recipe with clear `# ----` section headers that name each
  phase (e.g. ``# Main extraction``, ``# Flat response``, ``# Fiber loop``).
  Each section should contain a brief description of what is happening and
  ideally a single call to a science function.  Occasional ``if`` statements
  are fine to show that a section is skipped in a particular case.
- Avoid multi-line argument lists directly in the recipe body; collect
  arguments into named lists/dicts using the ``xargs`` / ``xkwargs`` pattern
  (where ``x`` is a short context prefix, e.g. ``lkargs`` for leak) and call
  with splat expansion:
  ```python
  lkargs = [params, recipe, spectrum, ref_e2ds, infile, fiber]
  lkkwargs = dict(database=calibdbm)
  lkout = leak.correct_spectra_leak(*lkargs, **lkkwargs)
  corrected_spectrum, leakcorr, leak_props = lkout
  ```
- All instruments that process the same data type must use an identical recipe
  structure — if the steps are the same, the code should be the same.
  Instrument-specific differences belong in constants or science modules,
  not in duplicated recipe blocks.
- The main per-file setup (shape calibration, image calibration, order
  profiles, shape transform, geometry, and model extraction) should be
  delegated to a single ``extract.main_extract()`` call that returns all
  products needed by the fiber loop.

## APERO recipe structure: code guidelines

- Most lines of Python code should have a concise comment when their purpose,
  data-flow role, or non-obvious assumption is not immediately clear. Use
  comments to make the surrounding algorithm easy to follow, while avoiding
  empty narration that merely repeats the code.
- New or modified Python functions should type all parameters and return
  values, and their docstrings should document every parameter and the return
  value. Keep annotations and documentation aligned with the actual API.
- TODO: review all extraction migration code added during this work,
  especially the `apero-core` extraction/math modules, APERO extraction
  wrappers, fiber descriptors, and recipe hooks. Add concise comments to
  nearly every line where that improves understanding, but leave genuinely
  self-explanatory lines uncommented.
- Main APERO recipe scripts should generally define only `main` and
  `__main__`. Put reusable helpers in an appropriate module under
  `apero.tools.module`, `apero.core`, `apero.io`, or another shared package
  location.
- APERO plots should go through the standard `recipe.plot(...)` system, not
  ad hoc matplotlib/PDF output in recipes. Register the plot name in
  `apero-drs/apero/plotting/definitions.yaml`, implement the plotting function
  in `apero-drs/apero/plotting/plot_functions.py`, enable it on the owning
  recipe with `set_debug_plots(...)` or `set_summary_plots(...)` in the
  relevant instrument `recipe_definitions.py`, and call it from recipe/science
  code as `recipe.plot('PLOT_NAME', ...)` with arrays/properties passed as
  keyword arguments.
- Do not write fallback/dual-path code to support an old file, database, or
  calibration layout alongside the new one (e.g. `if is_combined: ... else:
  <old behaviour>`). APERO profiles are reset/rebuilt from a clean state
  between versions, so the pipeline never needs to read data produced by a
  previous code version. Change the code and its callers to the new
  behaviour outright; do not keep the old path "just in case".

## APERO tests

- Use `apero.dev` for every unit test and response test. It provides the
  default parameters and loads `DRS_UCONFIG` without accessing an APERO
  profile.
- Keep unit tests deterministic and focused on one behavior. Do not require
  network access, databases, or large data assets; place such coverage in
  separate integration tests.
- Run the narrow package suite from the repository root:

  ```bash
  PYTHONPATH="apero-core" python -m pytest -q apero-core/tests
  PYTHONPATH="apero-core:apero-drs" python -m pytest -q apero-drs/tests
  PYTHONPATH="apero-ri" python -m pytest -q apero-ri/tests
  ```

## APERO constants

- Every constant is declared once, in a `CDict.add(...)` call in
  `apero-drs/apero/instruments/default/constants.py`, inside the `cgroup`
  section it belongs to (e.g. `cgroup = 'CAL.BCORR'`). Give it `value=None`
  there (no instrument default belongs in this file), the correct `dtype`
  (`int`, `float`, `bool`, `str`, `list` with `dtypei=...` for a list of a
  simple type, or `'path'`), `source=__NAME__`, `group=cgroup`, and a clear
  `description` explaining what the constant controls and, if relevant,
  which function/recipe reads it.
- Each instrument then overrides the value in its own
  `apero-drs/apero/instruments/<instrument>/constants.py` (currently
  `spirou`, `nirps_ha`, `nirps_he`) using `CDict.set('NAME', value=...,
  source=__NAME__, group=cgroup)` under the matching `cgroup` section. Do
  not repeat `dtype`/`description` here - `set` reuses the definition from
  `default/constants.py`. Add the override to all instruments, even if the
  value is identical across them, so the constant is never left undefined
  for one instrument.
- Keep the explanatory comment from the corresponding `CDict.add(...)`
  definition immediately above every instrument-level `CDict.set(...)`
  override. The instrument files should explain what each overridden value
  controls even though the type and description are defined centrally.
- Access a constant in code as `params['GROUP.NAME']` or, in functions that
  accept overrides, via `param_functions.PCheck` (aliased `pcheck` in most
  modules): `pcheck(params, 'GROUP.NAME', 'localvar', func=func_name,
  override=override_kwarg)`. Follow the pattern used by `no_sub` in
  `apero/science/calib/background.py::correction` for how to expose a
  constant as an optional keyword argument that defaults to the params
  value.
- For a constant that is a tuple/list of numbers (e.g. polynomial orders,
  bin counts), use `dtype=list, dtypei=float` (or `dtypei=int`) in
  `default/constants.py` and a plain Python list (e.g. `value=[16, 16]`) in
  each instrument override; `CDict` does not support raw tuples.

## APERO keywords

- Every new header keyword is declared once in
  `apero-drs/apero/instruments/default/keywords.py` with `KDict.add(...)`.
  Give it `key='NULL'`, the correct `dtype`, `source=__NAME__`, and a clear
  `description` explaining what the keyword records.
- Each instrument then overrides the FITS card name in its own
  `apero-drs/apero/instruments/<instrument>/keywords.py` using
  `KDict.set('KW_NAME', key='CARDNAME', comment='...')`. Add the override to
  all instruments (`spirou`, `nirps_ha`, `nirps_he`) so the keyword is never
  left undefined for one instrument.
- Keep the explanatory comment from the corresponding `KDict.add(...)`
  definition immediately above every instrument-level `KDict.set(...)`
  override, matching the constants convention.

## APERO RI

- Apply the instructions in `apero-ri/.github/instructions/` for every RI
  change. Read `ari-new-page.instructions.md` and
  `ari-tables.instructions.md` before adding a page or table.
- Keep permissions in `apero_ri/resources/pages.yaml` and `groups.yaml`.
  Enforce access in the Python route or view helper, never only in a template.
- Put instrument-specific settings in
  `apero_ri/resources/aprofile_instruments/*.yaml`, not hard-coded Python.
  Keep the v7/v8 SPIROU and NIRPS configuration key sets aligned.
- Use `apero_ri/ari_api/` helpers for internal ARI API calls rather than raw
  `requests` calls. Register async tasks in `apero_ri/tasks/__init__.py`.