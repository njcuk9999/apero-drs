# 08 - Parallelise the per-order loop in `extract_orders`

**File:** `apero-core/aperocore/science/extract/extract_model_core.py`
**Function:** `extract_orders` (lines 500 - 604)
**Benchmark test:** _covered indirectly by_ `test_perf_extraction_ribbon`

## Rough impact

The function iterates over ~49 orders and for each one calls
`weighted_fit_batch` up to `nclip` times. Each call is a few hundred
milliseconds on a full ribbon (see `04-extraction-vectorised.md`).
For a typical setup:

- ~49 orders x ~200 ms per order (best case) = **~10 s wall time**
- **Parallel across 8 cores (thread pool)**: **~1.5 s wall time**
- **Speed-up**: **~5 - 7x** on typical build nodes

The orders are numerically independent - each one writes disjoint
`(y1:y2, :)` slabs of the output images and its own column of the
flux arrays - so no locking is needed.

## Why it is not parallel today

The loop is a plain Python `for order_num in range(norders):` and
writes into shared arrays `flux1`, `flux2`, `zero_points`, `model1`,
`model2`, `residual`, `nsig`, `error`, `zero_image`. Because those
slabs are strictly disjoint, thread-safe writes are automatic.

The reason no explicit parallelism has been added is probably that
each iteration also allocates ribbon-sized scratch arrays inside
`weighted_fit_batch`, so pure Python cost would fight the GIL. The
work inside `weighted_fit_batch` is numpy under the hood (releases
the GIL for large enough reductions), so a thread pool of moderate
size scales well in practice.

## What to change

Wrap the loop with `joblib.Parallel`. Sketch:

```python
from joblib import Parallel, delayed

def _one_order(order_num, y1, y2, image, profile1, profile2,
               noise, nclip, nsig_clip, robust, nu, n_iter, trim_keep,
               trace_nan_frac):
    """Fit one ribbon; returns everything needed to write outputs."""
    if y1 < 0 or y2 > image.shape[0]:
        return order_num, None
    rib_sci = np.array(image[y1:y2], dtype=float)
    rib1 = np.array(profile1[y1:y2], dtype=float)
    rib2 = np.array(profile2[y1:y2], dtype=float)
    if robust:
        for _ in range(nclip):
            xout = weighted_fit_batch(rib1, rib2, rib_sci, noise,
                                      nu=nu, n_iter=n_iter,
                                      trim_keep=trim_keep,
                                      trace_nan_frac=trace_nan_frac)
            amp1, amp2, zero_point = xout[:3]
            model = (amp1 * np.nan_to_num(rib1)
                     + amp2 * np.nan_to_num(rib2) + zero_point)
            err = np.sqrt(np.abs(model) + noise ** 2)
            with np.errstate(invalid='ignore'):
                rib_sci[(rib_sci - model) / err > nsig_clip] = np.nan
    else:
        xout = weighted_fit_batch(rib1, rib2, rib_sci, noise,
                                  nu=nu, n_iter=n_iter,
                                  trim_keep=trim_keep,
                                  trace_nan_frac=trace_nan_frac)
        amp1, amp2, zero_point = xout[:3]
        model = (amp1 * np.nan_to_num(rib1)
                 + amp2 * np.nan_to_num(rib2) + zero_point)
    return order_num, (amp1, amp2, zero_point, model, rib1, rib2)

results = Parallel(n_jobs=n_jobs, prefer='threads')(
    delayed(_one_order)(k, int(row1[k]), int(row2[k]),
                        image, profile1, profile2, noise, nclip,
                        nsig_clip, robust, nu, n_iter, trim_keep,
                        trace_nan_frac)
    for k in range(norders))

for order_num, res in results:
    if res is None:
        continue
    amp1, amp2, zero_point, model, rib1, rib2 = res
    ...  # existing post-fit assembly (zero-point MAD, model1/model2, etc.)
```

Keep the post-fit "zero-point outlier" and `products/extras`
assembly on the main thread so the code that writes into `model1`,
`model2`, `residual`, `nsig`, `error`, `zero_image` stays where it is.

`n_jobs` should be plumbed through from the caller. The APERO
convention is a `CORES` param on the `ParamDict`; the APERO wrapper
next to this science function should pass it as an argument.

## Risk / correctness

- Threads (not processes) are the right choice: no pickling of large
  ribbons, and the heavy work is in numpy which releases the GIL.
- Output arrays are pre-allocated and each thread writes disjoint
  slabs, so no race.
- Fall back to a serial loop when `n_jobs=1` for debugging.

## Where the caller should choose `n_jobs`

The APERO wrapper in `apero-drs/apero/science/extract/*.py` should
read `params['CORES']` (already used elsewhere) and pass it as
`n_jobs` to `extract_orders`. Do not hard-code `-1` inside the
science function.

## Test coverage

- Add a correctness test asserting that
  `extract_orders(..., n_jobs=1)` and `extract_orders(..., n_jobs=4)`
  produce equal outputs on a small synthetic ribbon set.
- The per-order timing already lives in
  `test_perf_extraction_ribbon`; the whole-pipeline win is best
  measured with an APERO integration run rather than a unit
  benchmark.
