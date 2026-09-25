# 07 - Vectorise `lowpassfilter` sampling loop

**File:** `apero-core/aperocore/math/gen_math.py`
**Function:** `lowpassfilter` (lines 994 - 1094)
**Benchmark test:** `test_perf_lowpassfilter`

## Timings (`n=8176`, `width=101`)

| Version | Wall time |
|---------|-----------|
| Current | **6.2 ms** |
| Prototype target | **1 - 2 ms** |
| **Speed-up** | **~3 - 5x** |

Per-call the win is small, but this function is called **once per
order per iteration** inside `iterative_box_background` (163 * niter =
~500 calls per frame) and again inside multiple wavelength/telluric
paths, so the aggregate is measurable.

## Why it is slow today

```python
for it in np.arange(-width // 2, len(input_vect) + width // 2, width // 4):
    ...
    xmed.append(fast.nanmean(pixval))
    ymed.append(fast.nanmedian(input_vect[pixval]))
```

- Python-level append into growing lists (`xmed`, `ymed`).
- One `fast.nanmean` + one `fast.nanmedian` per iteration on ~25
  elements each. Function-call overhead dominates over the actual
  reduction.
- The subsequent "if there are duplicate xmed" branch is O(len(xmed)^2)
  because it loops with `np.mean(ymed[xmed == xmed2[i]])`.

## What to change

Replace the sampling loop with a single strided-window computation.
Because `width // 4` is the step and the window is `width` samples,
this is exactly what `bn.move_median` and `bn.move_mean` compute at
every position; picking every `width // 4`-th output gives the same
`ymed` and `xmed`.

```python
def lowpassfilter(input_vect, width=101, k=1, frac_valid_min=0,
                  trim_valid=False):
    n = len(input_vect)
    step = max(width // 4, 1)
    idx = np.arange(n)
    # position of each sliding window's right edge
    med = bn.move_median(input_vect, window=width, min_count=1)
    # index positions where we still keep samples
    keep_positions = np.arange(width - 1, n, step)
    ymed = med[keep_positions]
    # xmed = mean position of finite values inside each window is
    # approximately the window centre; the exact per-window
    # nan-mean-position can be reproduced with bn.move_mean(idx *
    # finite_mask) / bn.move_mean(finite_mask):
    finite = np.isfinite(input_vect).astype(float)
    num = bn.move_mean(idx * finite, window=width, min_count=1)
    den = bn.move_mean(finite, window=width, min_count=1)
    with np.errstate(invalid='ignore', divide='ignore'):
        xmed_full = num / den
    xmed = xmed_full[keep_positions]
    good = np.isfinite(ymed) & np.isfinite(xmed) & (den[keep_positions] > frac_valid_min)
    xmed = xmed[good]
    ymed = ymed[good]
    if len(xmed) < 3:
        return np.full(n, np.nan)
    # collapse duplicate xmed once with pandas / np.unique + reduceat
    uniq, idxu = np.unique(xmed.astype(int), return_inverse=True)
    if uniq.size != xmed.size:
        summed = np.zeros(uniq.size)
        counts = np.zeros(uniq.size)
        np.add.at(summed, idxu, ymed)
        np.add.at(counts, idxu, 1)
        xmed = uniq.astype(float)
        ymed = summed / counts
    spline = InterpolatedUnivariateSpline(xmed, ymed, k=k, ext=3)
    lowpass = spline(np.arange(n))
    if trim_valid:
        valid_pos = np.where(np.isfinite(input_vect))[0]
        lowpass[:valid_pos.min()] = np.nan
        lowpass[valid_pos.max():] = np.nan
    return lowpass
```

The `bn.move_median` / `bn.move_mean` calls each cost ~0.5 ms on 8176
elements, so the total is well below 2 ms.

## Risk / correctness

- The current implementation samples with an integer step that goes
  from `-width // 2` to `n + width // 2`. The proposed replacement
  covers positions `[width - 1, n - 1]`, i.e. it does not extrapolate
  before the first full window. Because the current implementation
  clips `low_bound < 0` to 0 anyway, the effective window at the
  edges was already truncated; add two extra sample points at
  `idx = 0` and `idx = n - 1` to keep the spline anchored at the ends.
- `frac_valid_min` is preserved by comparing `den[keep_positions]`
  (fraction of finite pixels per window).

## Test coverage

- `test_perf_lowpassfilter` for timing.
- Add a correctness test that generates a smooth curve with sprinkled
  NaNs, runs both the old and new implementations, and asserts
  `np.allclose(new, old, rtol=1e-6, equal_nan=True)` away from the
  first and last `width` pixels.
