# 03 - Parallelise `iterative_box_background` column loop

**File:** `apero-core/aperocore/science/calib/background_core.py`
**Function:** `iterative_box_background` (lines 189 - 246)
**Benchmark test:** `test_perf_iterative_box_background`

## Timings (4088 x 4088, `width=100`, `niter=3`)

| Version | Wall time |
|---------|-----------|
| Current | **9.3 s** |
| Prototype target | **2 - 3 s** |
| **Speed-up** | **~3 - 4x** |

## Why it is slow today

Inside a `niter` loop the function iterates all box centres `yc`:

```python
for _ in range(niter):
    ...
    for ii, icol in enumerate(yc):                     # ~163 iters
        i0 = np.max([icol - width // 2, 0])
        i1 = np.min([icol + width // 2, image2.shape[1]])
        with warnings.catch_warnings(record=True) as _:
            medcol = np.nanmedian(image2b[:, i0:i1], axis=1)   # slow
        background_image_offset[:, ii] = mp.lowpassfilter(medcol, width)
    background_image_full += mapc(background_image_offset, coords,
                                  order=2, cval=np.nan, output=float,
                                  mode='constant')
```

Two independent costs:

1. `np.nanmedian(image2b[:, i0:i1], axis=1)` on a 4088 x 100 slice
   costs ~50 ms and is called 163 times per iteration -> ~8 s per
   `niter`. Bottleneck's `bn.nanmedian` is ~2x faster than the numpy
   version APERO is calling here.
2. `mp.lowpassfilter(medcol, width)` on a 4088-long vector allocates
   several intermediate arrays and is not parallel.

## What to change

Three additive improvements.

### 3a. Use `bn.nanmedian` instead of `np.nanmedian`

The wrapper `mp.nanmedian` (which does dispatch to bottleneck) is used
elsewhere in the file. Replace the raw `np.nanmedian` call:

```python
medcol = mp.nanmedian(image2b[:, i0:i1], axis=1)
```

Expect roughly 2x on this line, i.e. ~4 s -> ~2 s per `niter`.

### 3b. Parallelise the box-centre loop

Each iteration of the `for ii, icol in enumerate(yc)` loop is
independent (they write disjoint columns of
`background_image_offset`). Wrap it with `joblib.Parallel` so the
outer 163 columns fan out across cores:

```python
from joblib import Parallel, delayed

def _one_col(icol, image2b, width):
    i0 = max(icol - width // 2, 0)
    i1 = min(icol + width // 2, image2b.shape[1])
    medcol = mp.nanmedian(image2b[:, i0:i1], axis=1)
    return mp.lowpassfilter(medcol, width)

cols = Parallel(n_jobs=-1, prefer='threads')(
    delayed(_one_col)(icol, image2b, width) for icol in yc)
background_image_offset[:, :] = np.stack(cols, axis=1)
```

On an 8-core machine this brings the per-iteration cost down further.
Because the work is a mix of pure numpy (nanmedian) and pure Python
(lowpassfilter, which allocates), threads are the right backend for
speed on Linux without a fork overhead.

### 3c. Precompute box indices once

`yc` and the associated `(i0, i1)` pairs never change across `niter`
iterations. Compute them once outside the loop and reuse them.

## Risk / correctness

- 3a is bit-identical when bottleneck is present (already the assumed
  environment; `bottleneck==1.6.0` is pinned in `apero-core/pyproject.toml`).
- 3b reproduces the current results because the columns are disjoint;
  the only nondeterminism is thread scheduling order, which does not
  affect numerical values.
- 3c is a trivial refactor.

## Test coverage

- `test_perf_iterative_box_background` for timing.
- Add a correctness test asserting `np.allclose(new_full, old_full)`
  on a 256 x 256 synthetic frame with `niter=2`.
