# 04 - Vectorise the per-column loop in `extract_core.extraction`

**File:** `apero-core/aperocore/science/extract/extract_core.py`
**Function:** `extraction` (lines 39 - 136)
**Benchmark test:** `test_perf_extraction_ribbon`

## Timings (71 x 8176 ribbon, `r1=r2=15`, `cosmic_sigcut=5`)

| Version | Wall time per order | 49 orders x 2 fibers |
|---------|--------------------:|---------------------:|
| Current | **178 ms** | ~17 s |
| Prototype (fully vectorised) | **14 ms** | ~1.4 s |
| **Speed-up** | **~13x** | **~12 s saved per exposure** |

The prototype output matched the current implementation to **0.0
relative error** on the spectrum (`spe`) and to identical cosmic-ray
counts (`cpt`) on synthetic data, so this optimisation is a straight
rewrite that preserves numerical behaviour.

## Why it is slow today

`extraction` performs the same operations on every column of the
ribbon inside a Python loop:

```python
for ic in ics:               # dim2 = 8176 iterations
    sx = simage[j1s[ic]:j2s[ic] + 1, ic]      # slice
    fx = orderp[j1s[ic]:j2s[ic] + 1, ic]      # slice
    sumfx = mp.nansum(fx)
    ...
    amp = mp.nanmedian(sx / fx)
    ...
    nsig = ares / mp.nanmedian(ares)
    ...
    spe[ic] = mp.nansum(wsxfx) / sum_wfxfx
```

Each iteration is ~10 numpy calls on tiny (~30 element) vectors. The
per-call overhead of numpy/bottleneck (attribute lookup, dtype
promotion, memory allocation) dominates the actual FLOPs. On a
71 x 8176 order this is ~80 000 numpy calls.

Because `j1s[ic]` and `j2s[ic]` are constant along the order (the
first line of the function evaluates the Chebyshev at the single
central column and broadcasts with `np.full`), the loop can be
replaced by a single set of 2D reductions on the entire ribbon.

## What to change

Rewrite the loop as axis-0 reductions on the ribbon:

```python
def extraction(simage, orderp, pos, r1, r2, cosmic_sigcut):
    dim1, dim2 = simage.shape
    jc = mp.val_cheby(pos, dim2 // 2, domain=[0, dim2])
    j1 = int(round(jc - r1))
    j2 = int(round(jc + r2))
    if j1 <= 0 or j2 >= dim1:
        # keep the original loop as a slow fallback for the edge case
        ...
    sx = simage[j1:j2 + 1]                       # (h, dim2)
    fx = orderp[j1:j2 + 1].astype(float, copy=True)
    sumfx = bn.nansum(fx, axis=0)                # (dim2,)
    ok = sumfx > 0
    fx[:, ok] = fx[:, ok] / sumfx[ok]
    fx[:, ~ok] = 1.0
    amp = bn.nanmedian(sx / fx, axis=0)          # (dim2,)
    res = sx - fx * amp
    ares = np.abs(res)
    nsig = ares / bn.nanmedian(ares, axis=0)     # (dim2,)
    if (r1 + r2) > 10:
        weights = nsig < cosmic_sigcut
    else:
        weights = np.isfinite(nsig)
    weights_f = weights.astype(float)
    wsxfx = weights_f * sx * fx
    wfxfx = weights_f * fx * fx
    sum_wfxfx = bn.nansum(wfxfx, axis=0)
    spe = bn.nansum(wsxfx, axis=0) / sum_wfxfx
    spelong = wsxfx / sum_wfxfx
    spelong[~weights] = np.nan
    cpt = int((~weights).sum())
    return spe, spelong, cpt, weights_f
```

The `if (r1 + r2) > 10` check is preserved so the "narrow NIRPS fiber"
branch is handled identically.

## Risk / correctness

- The current implementation already treats `jcs` as constant along
  the order (`np.full(dim2, ...)`) so vectorising is safe. If the
  Chebyshev is later evaluated per column, replace the scalar `jc`
  above with the array version and use `np.take_along_axis` to
  extract the ribbon.
- All reductions used already exist in `aperocore.math.fast` /
  `bottleneck`, so no new dependency.

## Extra opportunity: parallelise the outer loop

`extract_core.extraction` is called once per order from
`extract_orders_from_e2ds` / `apero.science.extract.other`. The orders
are independent, so wrapping the outer loop in
`joblib.Parallel(n_jobs=params['CORES'])(delayed(extraction)(...))`
reduces the wall-time roughly linearly with core count. This is
covered in more detail in `08-extract-orders-parallel.md`.

## Test coverage

- `test_perf_extraction_ribbon` provides the timing target.
- Add a correctness test that generates a small ribbon and asserts the
  vectorised output matches the current output to within
  `np.finfo(float).eps * n` on `spe` and exactly on `cpt`.
