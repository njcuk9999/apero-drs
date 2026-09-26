# 11 - Recipe / tool cold-start time

**Files:** `apero-core/aperocore/math/*.py`,
`apero-core/aperocore/science/calib/wave_core.py`,
`apero-drs/apero/science/extract/__init__.py`,
`apero-drs/apero/science/extract/berv.py`,
`apero-drs/apero/utils/drs_startup.py`,
`apero-core/aperocore/core/drs_misc.py`,
`apero-core/aperocore/constants/param_functions.py`,
`apero-drs/apero/plotting/plotter.py`,
`apero-drs/apero/plotting/plot_functions.py`
**Scope:** every recipe / tool invocation (fixed per-run overhead)

Unlike suggestions 1 - 9 this one is not about a hot pixel loop. It
is about the fixed wall-time that every recipe pays before its first
line of science runs. On this machine, running a SPIROU recipe with
no arguments (i.e. up to the point where `drs_startup.setup()`
returns) currently costs about **6 - 8 seconds** on a warm cache,
and closer to **12 - 15 seconds** the first time in a shell session
(cold FS cache, cold pip metadata). None of that time does any
science; it is all import graph + boot-up bookkeeping.

The `apero_processing` and per-file recipes fan out to dozens of
recipe invocations per night, so shaving a few seconds off each
compound quickly. The findings below are grouped into two buckets:

- **11a - 11d:** trim the import graph (measured with
  `python -X importtime` on `apero.recipes.spirou.apero_extract_spirou`).
- **11e - 11h:** trim the runtime of `drs_startup.setup()` itself
  (measured with wall-time probes inserted around each block).

## How the numbers were measured

Import-graph numbers:

```bash
export PYTHONPATH="apero-core:apero-drs:apero-ri"
python -X importtime -c \
    "from apero.recipes.spirou import apero_extract_spirou" \
    2>&1 | awk -F'|' 'NF==3 { gsub(/ /,"",$2); \
    if ($2+0 > 100000) print $0}'
```

That prints every cumulative import that costs > 100 ms. The lines
quoted below come from that command.

`drs_startup.setup()` numbers come from `time.perf_counter()` probes
around `python_git_stats`, `load_config`, `recipe_setup`,
`option_manager`, and each `params.copy()`.

## Baseline (2026-09-25 on this host)

```
import time:       540  643760              statsmodels.api
import time:      1136  852114          aperocore.math.fast
import time:       219  1500630          aperocore.math
import time:     11878  768398        astropy.coordinates
import time:      6101  309722         astropy.table
import time:      8990  2527683    apero.science.extract.berv
import time:      3866  256505      aperocore.base.base
import time:       425  1505489      aperocore.constants.param_functions
import time:       227  1532241  apero.recipes.spirou.apero_extract_spirou
```

Micro-timing on the setup phase:

| Phase | Cost |
|-------|------|
| `python_git_stats` (`pip freeze` iteration + git repo scan) | 4.2 s |
| Import graph up to `apero_extract_spirou` module | 2.5 s |
| `load_pconfig` first call + `constants.py` execution (815 `CDict.add`) | ~0.3 s |
| `recipe_setup` (argparse construction, ~40 add_argument calls) | ~0.1 s |
| 3 - 4 `params.copy()` calls near the end of `__setup__` | ~0.15 s |

Total cold-start dominated by import graph and `python_git_stats`.

## 11a. Lazy-import `statsmodels.api`, `scipy.signal`, and other
     unused-at-module-load heavyweights

Three top-level imports account for roughly **1.5 s of import time**
that every recipe pays, even when the imported module is never used
in the recipe's code path:

- `apero-core/aperocore/math/gen_math.py:21`
  `import statsmodels.api as statsmodels` - used only inside
  `linear_minimization_wls` (one function, one call site).
  `import statsmodels.api` alone is ~450 ms and it drags in
  `pandas` (~200 ms).
- `apero-core/aperocore/science/calib/wave_core.py:23`
  `import statsmodels.api as statsmodels` - imported but never
  referenced in that file. Pure dead-cost.
- `apero-core/aperocore/math/fast.py:15`
  `from scipy import signal` - the only use is
  `signal.medfilt(a, kernel_size=window)` on line 379 as a
  bottleneck fallback. `scipy.signal` costs ~680 ms and pulls
  `scipy.stats` (via `_support_alternative_backends`) which is
  another ~250 ms.

**Recommendation.** Move each of these to a function-local import
inside the single caller (or wrap in a module-level helper that
imports on first use and caches). Delete the unused
`wave_core.py` import outright. Concretely:

```python
# aperocore/math/gen_math.py
def linear_minimization_wls(...):
    import statsmodels.api as sm   # lazy
    res_wls = sm.WLS(y, x, weights=...)
    ...
```

Same pattern for `scipy.signal.medfilt` inside `fast.medfilt`.

**Estimated impact.** ~1.3 - 1.5 s off every recipe cold-start.
No behavioural change - the function still imports the same module
the first time it is called.

## 11b. Break the `apero.science.extract.__init__` re-export chain
     for `berv`

`apero-drs/apero/science/extract/__init__.py` unconditionally does
`from apero.science.extract import berv`. `berv.py` in turn does
`from astropy.coordinates import SkyCoord, Distance`, which pulls
in `astropy.coordinates` (~770 ms) plus `astropy.table` (~310 ms).

Every recipe that imports anything from `apero.science.extract`
(most of them) pays this cost, even recipes like `apero_flat` /
`apero_dark_ref` / `apero_shape` that never call BERV code.

**Recommendation.** Two options, in decreasing order of intrusion:

1. Drop `berv`, `extraction`, `gen_ext`, `model_background` from
   the eager `__init__.py` re-exports. Callers that need
   `extract.get_berv` should `from apero.science.extract import berv`
   themselves. That is a one-line change per caller and matches
   the pattern already used elsewhere (`apero.science.calib` does
   not re-export at all).
2. If the re-export API must stay, wrap the module attribute in a
   `__getattr__` (PEP 562) so `apero.science.extract.get_berv` only
   imports `berv` on first attribute access:

   ```python
   def __getattr__(name):
       if name in _LAZY:
           mod = importlib.import_module(_LAZY[name][0])
           return getattr(mod, _LAZY[name][1])
       raise AttributeError(name)
   ```

   with `_LAZY = {'get_berv': ('apero.science.extract.berv', 'get_berv'), ...}`.

**Estimated impact.** ~1.0 s off recipes that never touch BERV
(most calibration recipes). Extraction recipes still pay it, but
only when they actually need it.

## 11c. Defer `apero.plotting.plotter` import out of `drs_startup`

`drs_startup.py:47` imports `apero.plotting.plotter` at module load,
which drags in `matplotlib.pyplot` (~430 ms) and, transitively via
`plot_functions` and `mp`, `aperocore.math` (which is another
~1.1 s if 11a is not yet done).

In non-interactive runs plotting is a no-op (the recipe sets
`enable_plotter=False` or the plot level is 0). Even in interactive
runs, plotter setup does not need to happen before `setup()`
returns - the first `recipe.plot(...)` call would trigger it.

**Recommendation.** Move `from apero.plotting import plotter`
inside the function(s) in `drs_startup.py` that actually use the
`plotter` symbol (search shows it is used only by
`_enable_plotter` / a small number of helpers). Every other entry
point of `drs_startup` never touches it.

**Estimated impact.** ~0.4 s off every recipe that runs with
`enable_plotter=False` or `--plot 0`. Stacks with 11a - saving is
larger before 11a lands because plotter re-imports the whole
`aperocore.math` chain.

## 11d. Trim the `aperocore.base.base` top-level import chain

`aperocore.base.base` is ~256 ms cumulative, of which ~170 ms is
`astropy.time` and ~90 ms is the ruamel.yaml suite (six separate
`ruamel.yaml.*` imports). The `Time` / `TimeDelta` symbols are
used in ~a dozen functions across the codebase; the ruamel-yaml
classes are used only inside `load_yaml` / `dump_yaml`.

**Recommendation.** Split `aperocore.base.base` into two modules
or apply a module-level `__getattr__` so that
`Time`, `TimeDelta`, `CommentedMap`, `ScalarFloat`, etc. are
imported lazily on first access. `base.IPARAMS`,
`base.load_yaml()` and other startup-critical symbols must stay
eager - only the astropy/ruamel bindings need to be deferred.

**Estimated impact.** ~0.2 s cold-start, and it removes
`astropy.time` from the required-at-import set (helps any tool
that imports `aperocore.base.base` but never touches Time).

## 11e. Rewrite `python_git_stats` to skip `pip freeze` by default

`aperocore/core/drs_misc.py:337 python_git_stats(params)` runs on
every single recipe invocation via
`drs_startup.__setup__:287`. It currently:

1. Iterates `pip._internal.operations.freeze.freeze()` and inserts
   one `PYTHONMOD_<pkg>` (or `PYTHONOTHER_<pkg>`) parameter into
   `params` per installed package.
2. Opens a `git.Repo(...)` on the drs root and reads
   `active_branch.name` and `head.object.hexsha`.

`pip freeze` on this host is **4.2 s** for 234 packages. Every
recipe run pays it. The output is only used to write into log/YAML
headers ("what was installed when this reduction ran"). It does not
influence any decision the pipeline makes.

**Recommendation.**

- Gate `pip freeze` behind a run-time flag (`params['LOG_ENVIRONMENT']`
  or the existing debug level, e.g. only run when `GLOBAL.DEBUG >= 1`
  or when `recipe.recipe_kind == 'reference'`). Most calibration
  and science runs do not need the manifest.
- When it does run, capture the manifest **once per apero-processing
  batch** into a file (e.g. `PATH.LOG_FULL/env_manifest.yaml`) and
  have subsequent recipe invocations just record the path. The
  manifest does not change during a night of reductions.
- Keep the git branch/hash - both are cheap (~5 - 20 ms) and
  useful for reproducibility. But use `subprocess.run(['git',
  'rev-parse', 'HEAD'], ...)` instead of importing `GitPython`,
  which is heavier than the CLI and only used here.
- The 234 individual `params[f'PYTHONMOD_{key}'] = ...` inserts
  each trigger `ParamDict.__setitem__` (see 11f). Coalesce them
  into a single `params['PYTHONMOD']` dict so ParamDict only pays
  one `__setitem__` cost.

**Estimated impact.** ~4 s off every recipe cold-start (dominant
single-line win on this list).

## 11f. Cut `display_func` cost from `ParamDict.__setitem__`

`ParamDict.__setitem__` (`param_functions.py:153`) calls
`display_func('__setitem__', __NAME__, self.class_name)` on every
insert. `display_func` builds a formatted string
(`'aperocore.constants.param_functions.ParamDict.__setitem__()'`)
that is then **discarded** - `func_name` is not used anywhere in
`__setitem__` after the assignment. `ParamDict.set()`
(`param_functions.py:251`) has the same call.

At startup a recipe inserts ~1500 keys (constants + keywords +
`PYTHONMOD_*` from 11e + `PATH.*` + `INPUTS.*`). That is ~1500
throw-away string builds. It is a small individual cost but
compounds with `.copy()` (see 11g) which re-triggers every
`__setitem__`.

**Recommendation.** Delete the `display_func` call in
`__setitem__` and `set()` (and anywhere else the result is
unused). If the intent was to feed into a debug breakpoint hook,
gate it behind `if DEBUG_TRACE:` at module level so the hot path
pays nothing.

**Estimated impact.** ~50 - 150 ms off startup depending on how
many `.copy()` calls are made. Small in absolute terms but a
correctness-safe cleanup.

## 11g. Deduplicate `params.copy()` calls in `drs_startup.__setup__`

`drs_startup.py:342-397` currently does:

```python
WLOG.pin = recipe.params.copy()
params = recipe.params.copy()
...
params.lock()
recipe.params = params.copy()
WLOG.pin = params.copy()
```

That is **4 deep copies** of a ~1500-key ParamDict, each of which
deep-copies every value and re-inserts them via the source-tracking
`__setitem__`. Measured overhead: ~150 ms.

**Recommendation.**

- After `params.lock()`, the params object is immutable by
  contract. `recipe.params = params` (no copy) and
  `WLOG.pin = params` are safe. Locking exists precisely so
  downstream code cannot mutate.
- The first `WLOG.pin = recipe.params.copy()` (line 342) is done
  before the lock and can be replaced by a lightweight snapshot -
  `WLOG.pin` is only read in log formatters; a shallow view of
  the .data dict is sufficient.
- Consolidate into one authoritative copy before the lock, then
  share the reference.

**Estimated impact.** ~100 - 130 ms per recipe cold-start.

## 11h. Cache `find_recipe` / `pconst.RECIPEMOD()` per Python process

`drs_startup.__setup__:194-203` calls `load_pconfig` and then
`pconst.RECIPEMOD()` on every invocation. `load_pconfig` is
already cached (`PCONFIG_CACHE`), but `RECIPEMOD()` returns a
freshly-imported `recipe_definitions` module wrapper each call,
and `find_recipe` linearly scans the resulting list to match by
recipe name.

For long-running processes (`apero_processing`, ARI request
handlers) that call `setup()` repeatedly, this repeats the
`file_definitions.py` execution (154 `DrsFitsFile(...)`
constructions) and the `recipe_definitions.py` execution (29
`DrsRecipe(...)` constructions) unnecessarily.

**Recommendation.** Add a `functools.lru_cache(maxsize=None)`
wrapper around `pconst.RECIPEMOD()` and `pconst.FILEMOD()` keyed
on `(instrument,)`; and cache `find_recipe(name, instrument)` in
a small dict keyed on `(name, instrument)`. Both are pure lookups
- their outputs are the same for the lifetime of the process.

**Estimated impact.** Negligible on a one-shot recipe (~10 ms).
Large on `apero_processing` runs that spawn many in-process
recipe invocations: turns O(N * 154 FITS-file constructions)
into O(154).

## What is intentionally not on this list

- **Native compilation / Cython the setup path.** The wins above
  are all pure-Python / import-graph and do not require touching
  the C extension surface.
- **Trimming the ~200 ms `astropy.units` import.** It is used
  pervasively (`plot_functions`, `berv`, `file_definitions`) and
  the payback of lazy-loading it is small compared to 11a - 11e.
- **Removing `matplotlib` entirely from the boot path.** 11c
  defers it; deleting it altogether would break the interactive
  plotter and is out of scope.
- **Compiling `.pyc` files eagerly.** Python already caches them
  and the `.pyc` write cost is not on the critical path here.

## Suggested rollout order

1. **11e first.** `python_git_stats` is the single largest win
   (~4 s) and the change is contained to one function.
2. **11a next.** Lazy-import the three heavy modules
   (`statsmodels.api` x2, `scipy.signal`). Each caller is a
   handful of lines.
3. **11c and 11b.** Defer `plotter` and break the
   `extract.__init__` re-export chain. These stack cleanly with
   11a because they were pulling in `aperocore.math` transitively.
4. **11d.** Split `aperocore.base.base`. This is the largest
   structural change but the safest to do last, since 11a - 11c
   already remove most of the pressure on `aperocore.math`.
5. **11f and 11g.** ParamDict micro-optimisations. Do together;
   both touch `param_functions.py`.
6. **11h.** Only meaningful for long-running batch processes;
   land after end-to-end profiling confirms it matters.

## Test coverage

Add a startup-time benchmark alongside
`apero-core/tests/test_perf_benchmarks.py`:

```python
@pytest.mark.perf
def test_recipe_import_time():
    import time, importlib, sys
    for mod in list(sys.modules):
        if mod.startswith(('apero', 'aperocore')):
            del sys.modules[mod]
    t0 = time.perf_counter()
    importlib.import_module(
        'apero.recipes.spirou.apero_extract_spirou')
    dt = time.perf_counter() - t0
    assert dt < 1.0, f'recipe import regressed: {dt:.2f}s'
```

Pair it with a `setup()` wall-time regression check that uses
`apero.dev` (per AGENTS.md) so it does not need a full profile.
Baseline the numbers here after each of 11a - 11h lands and log
them into this file, mirroring the table in `README.md`.
