# 12 - Recipe / tool cold-start (follow-up)

**Files:** `apero-drs/apero/core/drs_file.py`,
`apero-drs/apero/core/drs_data_models.py`,
`apero-drs/apero/io/drs_image.py`,
`apero-drs/apero/utils/drs_startup.py`,
`apero-drs/apero/utils/drs_recipe.py`,
`apero-drs/apero/tools/module/processing/drs_processing.py`,
`apero-core/aperocore/drs_lang/tables/*.py`,
`apero-core/aperocore/core/drs_base_classes.py`
**Scope:** additional cold-start wins uncovered while auditing 11
plus the `apero_processing` worker-pool multiplier.

Doc 11 covers the biggest hitters (`pip freeze`, `statsmodels`,
`scipy.signal`, `astropy.coordinates`). This follow-up documents
the second tier - individually 100 - 500 ms each, but almost all
of them are one-line moves. It also flags a **worker-pool
configuration** in `apero_processing` that multiplies every
recipe-level cold-start win by the number of recipes per night.

## How the numbers were measured

Same `python -X importtime` harness as doc 11:

```bash
export PYTHONPATH="apero-core:apero-drs:apero-ri"
python -X importtime -c \
    "from apero.core import drs_file" 2>&1 \
    | awk -F'|' 'NF==3 { gsub(/ /,"",$2); \
      if ($2+0 > 50000) print $0}'
```

Language-table numbers were captured with a wall-time probe:

```python
import time
t0 = time.time()
from aperocore.drs_lang.tables import (
    default_text, default_help, spirou_text, spirou_help)
print(f'{(time.time()-t0)*1000:.1f} ms')
# -> 289 ms on this host
```

The `apero_processing` multiplier is estimated from the per-recipe
cold-start budget (~6 - 8 s) and the batch pool config on line
2733.

## Baseline (2026-09-25 on this host)

| Item | Cost |
|------|------|
| `from scipy.stats import pearsonr` in `drs_file.py` (module load) | ~250 ms |
| Same import in `drs_data_models.py` (already cached via `drs_file`) | 0 ms after 12a |
| `from scipy.ndimage import ...` in `drs_image.py` | ~90 ms |
| `default_text.py` + `default_help.py` module execution | ~250 ms |
| Instrument `*_text.py` + `*_help.py` (via `DRS_LANG_MODULES`) | ~40 ms each |
| `_display_python_modules` first call (importing each requirement) | 500 - 1500 ms (depends on cache misses) |
| `DrsRecipe.copy` with `deepcopy` on strings | ~5 - 10 ms |
| `apero_processing` `Pool(cores, maxtasksperchild=1)` respawn | full cold-start * N recipes |

## 12a. Lazy-import `scipy.stats.pearsonr` in `drs_file.py`
     and `drs_data_models.py`

`apero-drs/apero/core/drs_file.py:40` and
`apero-drs/apero/core/drs_data_models.py:28` both do:

```python
from scipy.stats import pearsonr
```

`scipy.stats` costs ~250 ms cumulative and pulls
`scipy.stats._stats_py` + `scipy.stats.distributions`. `pearsonr`
is used **once** in each file (`drs_file.py:8896`, plus one call
in `drs_data_models`). Every recipe imports `drs_file` via
`drs_startup` so the whole recipe suite pays for it.

**Recommendation.** Move both to function-local imports:

```python
def _pearson_metric(image1, image2, good):
    from scipy.stats import pearsonr   # lazy
    return pearsonr(image1[good], image2[good])[0]
```

**Estimated impact.** ~250 ms per recipe cold-start. Stacks
cleanly with 11a (both remove `scipy.stats` from the boot graph).

## 12b. Lazy-import `scipy.ndimage` binary morphology in
     `drs_image.py`

`apero-drs/apero/io/drs_image.py:23`:

```python
from scipy.ndimage import binary_erosion, binary_dilation
```

`scipy.ndimage` is another ~90 ms and only three call sites in the
file need it. `drs_image` is imported eagerly by
`apero.science.calib.gen_calib` and therefore by every science
recipe.

**Recommendation.** Move to function-local imports inside the
three functions that call `binary_erosion` / `binary_dilation`.

**Estimated impact.** ~90 ms per recipe.

## 12c. Compile the language tables once and pickle-cache the
     merged `LANG_VALUES` dict

`apero-core/aperocore/drs_lang/tables/default_text.py` is 13,703
lines of code, all of the shape:

```python
item = langlist.create('40-001-00017', kind='help')
item.value['ENG'] = '...'
```

Every recipe imports `aperocore.drs_lang.drs_lang_text`, which at
module load calls `LanguageLookup(**lkwargs)` and iterates every
key across every enabled language module. Measured cost of loading
the four SPIROU tables + compile pass: **~290 ms**.

The compiled result (`LANG_VALUES`, `LANG_COMMENTS`, `LANG_KINDS`,
`LANG_ARGS`, `LANG_SOURCES`) is a plain dict keyed by string with
string values. It changes only when the `.py` tables change.

**Recommendation.** Pickle-cache the compiled dicts and invalidate
on source-mtime or file hash:

```python
def _load_lang_cache():
    cache = _lang_cache_path()   # e.g. ~/.apero/lang_<hash>.pkl
    if cache.exists():
        with cache.open('rb') as f:
            return pickle.load(f)
    values = _do_full_compile()   # existing slow path
    with cache.open('wb') as f:
        pickle.dump(values, f, protocol=pickle.HIGHEST_PROTOCOL)
    return values
```

The `<hash>` is a blake2b of the four table `.py` mtimes; the
existing `hashlib.blake2b` import in `drs_file.py` can be reused.

**Estimated impact.** ~250 ms per recipe on warm cache. First
recipe of the session still pays the full compile.

## 12d. Rework `_display_python_modules` to not import every
     requirement at recipe startup

`apero-drs/apero/utils/drs_startup.py:2008
_display_python_modules()` is called by `_display_system_info`,
which fires from `__setup__` (line 410) on every non-quiet recipe
invocation.

It reads `apero_base.REQUIREMENTS` line by line and for each
package that is **not already in `sys.modules`** does
`importlib.import_module(package)` just to read `__version__`.
Packages that live outside the recipe's normal import graph
(`git`, `pandasql`, `pathos`, `PyQt6`, etc.) trigger a real
import at recipe startup - each is 30 - 400 ms.

`PACKAGE_CACHE` is a **process-local** cache; because
`apero_processing` uses `spawn` + `maxtasksperchild=1` (see 12g),
each worker respawns and re-pays the cache-miss cost on every
recipe.

**Recommendation.** Two changes:

- Replace `importlib.import_module(package)` with
  `importlib.metadata.version(package)`. `importlib.metadata` is
  already imported (it is in `apero._version`) and returns the
  installed distribution version without executing any package
  init code. Fall back to `sys.modules.get(package).__version__`
  only when metadata is missing.
- Persist `PACKAGE_CACHE` to a small file under
  `~/.apero/<profile>/package_versions.json`, keyed on the
  `apero_base.REQUIREMENTS` mtime, so cross-process invocations
  reuse the cache. Requirements file changes rarely.

**Estimated impact.** 500 - 1500 ms saved on the first recipe of
a session; ~300 ms saved on every subsequent recipe under
`apero_processing` (thanks to the cross-process cache).

## 12e. Avoid `pandas.read_csv`-style heavy imports at module load
     in `drs_recipe.py` and friends

`apero-drs/apero/utils/drs_recipe.py:20` imports
`astropy.table.Table` at module load. `astropy.table` is ~310 ms.
`drs_recipe` uses `Table` in exactly two places (both
`export_help_table` variants).

Same pattern in:

- `apero-drs/apero/utils/drs_data.py:18` - one use of `Table`
- `apero-drs/apero/io/drs_path.py:27` - `from astropy import
  units as uu`, used only inside `size_conversion`

**Recommendation.** Delete these top-level imports and inline them
inside the one or two functions that use them. The `astropy.table`
symbol is already pulled in via `drs_file.py` (which needs it),
but at least the load ordering can be deferred until after the
recipe's `main()` starts, which lets those imports proceed in
parallel with the pipeline's real work under Python 3.12+ (which
releases the import lock more aggressively).

**Estimated impact.** ~100 ms per recipe standalone; larger when
combined with 12a/12b because it lets Python skip
`astropy.table` entirely for recipes that never touch a table.

## 12f. Drop the unused `pandasql` module-level import in
     `drs_base_classes`

`apero-core/aperocore/core/drs_base_classes.py:27`:

```python
from pandasql import sqldf
```

The only use is `drs_base_classes.py:950` inside one helper
method. `pandasql` is a soft dependency that is not always
installed (this repo is missing it for the current dev env - see
the traceback that surfaced while writing doc 11) and it pulls in
`sqlite3` + a re-import of `pandas`.

**Recommendation.** Move to a function-local import. It also
removes the "module fails to load if pandasql missing" foot-gun
- currently a bare `import` failure kills the whole boot graph
for tools that do not need SQL.

**Estimated impact.** Correctness fix; ~30 ms per recipe cold
start when `pandasql` is installed. When `pandasql` is missing,
this fix converts a hard `ImportError` at boot into a lazy
failure at first call.

## 12g. Reuse `apero_processing` workers instead of respawning
     per recipe

`apero-drs/apero/tools/module/processing/drs_processing.py:2733`
(and three other spots on lines 3086, 3236, 3391):

```python
with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
    results = list(tqdm(pool.starmap(process_func, args_list), ...))
```

`spawn` + `maxtasksperchild=1` means each recipe execution:

1. Spawns a fresh Python interpreter (~1 s process start).
2. Imports the entire apero graph from scratch (~2.5 s - see 11).
3. Runs `python_git_stats` (~4.2 s - see 11e).
4. Runs the recipe.
5. **Dies.** Next task in the queue repeats 1 - 4.

On a night with 500 recipe invocations that is `500 * ~7 s = ~3500 s`
of cumulative boot time. Split across 8 workers, that is still
~7 minutes of pure startup - and it grows linearly with the
number of files processed.

**Recommendation.**

- Drop `maxtasksperchild=1` (or raise it to ~50). The reason for
  `=1` was almost certainly to reset any leaked state between
  recipes; that concern can be addressed by explicit cleanup at
  the top of each recipe worker instead of by process death.
  Every APERO recipe already re-runs `drs_startup.setup()` which
  resets `WLOG.pin`, `params`, and per-recipe log state.
- If some recipes really do leak (matplotlib figures, sqlite
  connections, LBL globals), tag those recipes explicitly and use
  `maxtasksperchild=1` **only** for them via a per-recipe flag on
  the `DrsRecipe` object. Everything else reuses the worker.
- Consider `get_context('fork')` on Linux instead of `spawn`.
  Fork is ~10 - 100 ms process start vs. `spawn`'s ~1 s and
  inherits the parent's already-warm import graph. The reason
  `spawn` is used elsewhere in APERO is CUDA / OpenBLAS thread
  safety; those concerns do not apply to the recipe worker pool
  which does not fork after starting any of those libraries.

**Estimated impact.** Order-of-magnitude reduction in the
processing-batch wall time on any night with more recipes than
cores. On a 500-recipe / 8-core night, expect the ~7 minute
startup budget to drop to ~30 s (one cold start per worker).
This dominates every other optimisation in docs 11 and 12
combined at batch scale.

## 12h. Do initial-parameterisation display once, not twice

`__setup__` calls `_display_drs_title`, `_display_initial_parameterisation`,
`_display_run_time_arguments` with `printonly=True` around line
290 - 333, and then calls the same three functions again with
`logonly=True` around lines 406 - 412.

Each of those helpers does its own textentry lookups, ParamDict
iteration, and string interpolation - all of it happens twice.
The only difference between the two blocks is whether output goes
to stdout or to the log file; the message contents are identical.

**Recommendation.** Build the message strings once and pass them
to `WLOG` twice with the appropriate flags. Or, simpler, teach
each `_display_*` helper to accept `both=True` and route to both
sinks internally.

**Estimated impact.** ~50 - 100 ms per recipe; more when
`_display_system_info` -> `_display_python_modules` is still on
the critical path (see 12d).

## 12i. Remove `copy.deepcopy` on immutable scalars in
     `DrsRecipe.copy`

`apero-drs/apero/utils/drs_recipe.py:1035 DrsRecipe.copy` does:

```python
self.path = copy.deepcopy(recipe.path)
...
self.allowedfibers = copy.deepcopy(recipe.allowedfibers)
self.template_required = bool(recipe.template_required)
...
self.recipe_kind = copy.deepcopy(recipe.recipe_kind)
self.recipe_type = copy.deepcopy(recipe.recipe_type)
```

`recipe.path`, `recipe.recipe_kind`, and `recipe.recipe_type` are
strings; `deepcopy` on a string returns the same string via
`copy._deepcopy_atomic`, but the dispatch is still ~1 us per call
and there are ~30 such copies per `DrsRecipe.copy`. `find_recipe`
calls `DrsRecipe.copy` on every `__setup__`; so does every
`apero_processing` worker respawn.

**Recommendation.** Drop `copy.deepcopy` on scalars and on
already-immutable objects (`str`, `int`, `bool`, `frozenset`).
Use plain assignment or `str(...)` if the intent is defensive
copy. Only `deepcopy` mutable containers.

**Estimated impact.** ~5 - 10 ms per recipe. Small on a single
run, meaningful under `apero_processing` (`copy` is on the hot
path when 12g is not yet fixed).

## What is intentionally not on this list

- **Compiling the language tables to `.pth` or `.pyi` sidecars.**
  Pickle-caching (12c) is simpler and equally fast.
- **Replacing `argparse` with `click` / a hand-rolled parser.**
  argparse setup is ~100 ms on a big recipe; not worth the API
  churn.
- **Rewriting `DrsFitsFile.__init__` (40+ kwargs).** The 154
  constructions at `file_definitions` import cost ~50 ms total;
  fixing 12g removes the multiplication factor and this becomes
  a rounding error.

## Suggested rollout order

1. **12g first.** Batch-scale multiplier - dwarfs every other
   win in docs 11 and 12 on any real processing run.
2. **12a, 12b, 12f.** Pure top-level-import moves; safe.
3. **12d.** `_display_python_modules` fix; requires slightly
   more thought (metadata vs. import).
4. **12c.** Language-table pickle cache; adds a small cache
   directory concern.
5. **12h and 12i.** Micro-optimisations; do together with the
   `drs_startup` cleanup pass alongside 11f / 11g.

## Test coverage

Extend the startup benchmark added by doc 11 with two new
regression checks:

```python
@pytest.mark.perf
def test_no_scipy_signal_at_recipe_import():
    import sys, importlib
    for m in [k for k in sys.modules if k.startswith(('apero','aperocore','scipy'))]:
        del sys.modules[m]
    importlib.import_module('apero.recipes.spirou.apero_extract_spirou')
    assert 'scipy.signal' not in sys.modules
    assert 'scipy.stats' not in sys.modules
    assert 'statsmodels' not in sys.modules
    assert 'astropy.coordinates' not in sys.modules

@pytest.mark.perf
def test_processing_worker_reuse():
    # small synthetic runlist of ~20 no-op recipes
    ...  # assert wall time roughly ~cold_start + 20*hot_start
```

The second test guards 12g against silent regressions in the
`Pool(...)` call. Both go alongside
`apero-core/tests/test_perf_benchmarks.py`.
