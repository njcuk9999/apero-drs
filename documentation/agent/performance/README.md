# APERO performance suggestions

Written 2026-09-24. Each file in this directory is a self-contained
proposal for a single performance improvement in `apero-core` or
`apero-drs`. No code has been changed by these notes: every proposal
describes what to change, roughly where, and includes a before/after
timing estimate that was reproduced with a prototype during the audit.

## How the numbers were measured

Timings were produced on the same machine that hosts this repo, using
`np.random.default_rng(0)` synthetic data at the array sizes that
appear in production:

- `4088 x 4088` detector frames (SPIRou/NIRPS style)
- `71 x 8176` straightened order ribbons

The benchmarks live in `apero-core/tests/test_perf_benchmarks.py`
(marker `perf`). Run them with:

```bash
PYTHONPATH="apero-core" python -m pytest -q -s \
    -m perf apero-core/tests/test_perf_benchmarks.py
```

They are excluded from the default suite.

## Suggestions (ordered by wall-clock impact)

| # | Doc | Function | Rough win | Where |
|---|-----|----------|-----------|-------|
| 1 | [01-create-background-map.md](01-create-background-map.md) | `background_core.create_background_map` | ~11x (41s -> 4s) | `apero-core/aperocore/science/calib/background_core.py` |
| 2 | [02-fit-lower-envelope-2d.md](02-fit-lower-envelope-2d.md) | `background_core.fit_lower_envelope_2d` | ~2-3x (11s -> 4s) | same file |
| 3 | [03-iterative-box-background.md](03-iterative-box-background.md) | `background_core.iterative_box_background` | ~3-4x (9s -> 2s) | same file |
| 4 | [04-extraction-vectorised.md](04-extraction-vectorised.md) | `extract_core.extraction` | ~13x (178ms/order -> 14ms) | `apero-core/aperocore/science/extract/extract_core.py` |
| 5 | [05-background-model-mad.md](05-background-model-mad.md) | `extract_model_core.background_model` + `_mad_from_sorted` | ~2-3x (2.5s -> 1s) | `apero-core/aperocore/science/extract/extract_model_core.py` |
| 6 | [06-measure-box-min-max.md](06-measure-box-min-max.md) | `gen_math.measure_box_min_max` | ~55x (4.3ms -> 0.08ms) | `apero-core/aperocore/math/gen_math.py` |
| 7 | [07-lowpassfilter.md](07-lowpassfilter.md) | `gen_math.lowpassfilter` | ~3-5x (6ms -> 1-2ms) | same file |
| 8 | [08-extract-orders-parallel.md](08-extract-orders-parallel.md) | `extract_model_core.extract_orders` | linear in cores (~4-8x) | `apero-core/aperocore/science/extract/extract_model_core.py` |
| 9 | [09-nanpercentile-fast.md](09-nanpercentile-fast.md) | project-wide `np.nanpercentile` axis reductions | ~5-10x on hot spots | callers throughout |
| 10 | [10-io-and-caching.md](10-io-and-caching.md) | recipe-level FITS reads / DB lookups | pipeline wall-clock | `apero-drs/apero/recipes/*` and `apero-drs/apero/io/*` |

## Guiding principles used

- **Move Python loops that touch every pixel into numpy/bottleneck reductions.**
  APERO already uses `bottleneck` via `aperocore.math.fast`, so the fix
  is usually just "call the axis-reduction version instead of looping".
- **Avoid re-copies of large arrays.** `np.array(x, dtype=float)` on
  something already `float` and used only for reading is an allocation
  APERO can pay once at the boundary. (The CLAUDE.md rule to prefer
  `np.array` over `np.asarray` still applies; the win is at the caller.)
- **Prefer moving-window primitives** (`bn.move_min`, `bn.move_max`,
  `bn.move_median`) to hand-written Python sliding windows.
- **Coarse-then-expand** where a full-resolution median/percentile is
  not needed (the pipeline already does this in
  `extract_model_core.background_model` and `correct_local_background`;
  the same trick applies elsewhere).
- **Parallelise the outer per-order loop** in `extract_orders` and
  friends; each order is independent, and modern nodes are 8+ cores.

## What was intentionally left alone

- Numerical results must not change. Proposals either keep results
  bitwise identical (`extract_core.extraction`, `measure_box_min_max`)
  or introduce a coarser grid whose difference is bounded and
  documented (`create_background_map`).
- No new dependency is required. `bottleneck`, `scipy`, `numexpr`,
  and `numba` are already pinned in `apero-core/pyproject.toml`.
- Nothing in `apero-drs` recipe control flow is touched. Speedups are
  drop-in inside science functions or in narrowly scoped helper code.

## Suggested rollout order

1. Land the benchmark test file first (already committed with this doc
   set) so any change can be measured against the same baseline.
2. Do `#4` and `#6` — both are exact-match rewrites, low risk.
3. Do `#1`, `#3`, `#5` — these change the number of samples used but
   the differences are small and each doc quantifies them.
4. Do `#8` — needs an env knob for `n_jobs` but is otherwise safe.
5. Do `#2` last — the largest structural change.

## Implementation status (2026-09-25)

Suggestions #4, #6, #5, #1, #3, #2 are now landed. Parallelism-based
suggestions (`#8`; sub-item 3b of `#3`) were intentionally skipped —
APERO handles parallelism at a higher level. `#7`, `#9`, `#10` remain
open. Measured post-change wall times on this repo:

| # | Function | Before | After | Speedup |
|---|----------|--------|-------|---------|
| 4 | `extract_core.extraction` (71 x 8176) | ~178 ms | ~14 ms | ~13x |
| 6 | `gen_math.measure_box_min_max` (4096, 32) | 4.30 ms | 0.075 ms | ~55x |
| 1 | `create_background_map` (4088 x 4088) | 41.2 s | 3.1 s | ~13x |
| 3 | `iterative_box_background` (4088 x 4088, niter=3) | 9.3 s | 7.24 s | ~1.3x |
| 5 | `extract_model_core.background_model` (4088 x 4088) | 2.53 s | 2.58 s | negligible |
| 2 | `fit_lower_envelope_2d` (4088 x 4088, bin=4, niter=10) | 11.1 s | 8.42 s | ~1.3x |

`#5` shipped as an `expand_bilinear` batching cleanup (see doc); the
dominant cost is still `np.sort` inside `_mad_from_sorted` and would
need a larger rewrite to shift meaningfully.
