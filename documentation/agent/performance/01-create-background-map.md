# 01 - Vectorise `create_background_map`

**File:** `apero-core/aperocore/science/calib/background_core.py`
**Function:** `create_background_map` (lines 38 - 104)
**Benchmark test:** `test_perf_create_background_map`

## Timings (4088 x 4088 frame, `width=100`, `percent=5`, `csize=7`, `nbad=3`)

| Version | Wall time |
|---------|-----------|
| Current | **41.2 s** |
| Prototype (vectorised, coarse subsample) | **3.7 s** |
| **Speed-up** | **~11x** |

Prototype produced results that differ from the current implementation
in **0.53 %** of pixels in the returned binary background mask. The
differences come from the coarse subsampling of the running percentile
on the cross-dispersion axis; they can be reduced or eliminated by
increasing the step density.

## Why it is slow today

The function contains two nested Python `for` loops:

```python
for x_it in range(0, image0.shape[1], width2):          # ~163 iters
    ribbon = mp.nanmedian(image0[:, x_it:x_it + width2], axis=1)
    for y_it in range(image0.shape[0]):                 # 4088 iters
        ...
        backest_pix = mp.nanpercentile(ribbon[ystart:yend], percent)
        backest[y_it, x_it: x_it + width2] = backest_pix
```

That is ~660 000 calls to `np.nanpercentile` on a window of ~100
values each. Every call carries the overhead of a Python function call
plus an internal sort. The dominant cost is Python-side dispatch, not
the underlying numerical work.

## What to change

Replace the inner `y_it` loop by a single coarse evaluation, then
linearly interpolate back to the full detector height. Concretely, in
the same function:

1. Compute the per-column-ribbon medians in one call
   (`bn.nanmedian(image_reshaped, axis=2)`). This produces the same
   `ribbon` values the loop was computing, but stacked as a `(ny,
   ncols)` array.
2. Sample the running lower-percentile at a coarse cadence of about
   `width / 8` rows instead of every row. That is ~500 evaluations
   per column instead of 4088. Each evaluation is a
   `np.nanpercentile(..., axis=0)` over `width` rows for all columns
   at once.
3. Linearly interpolate the coarse `(ncoarse, ncols)` grid back to
   `(ny, ncols)` with `np.interp` along the row axis.
4. Repeat the columns back to the full width by `np.repeat(..., width2,
   axis=1)` and clip to `nx`.

The mask/convolve step at the end is already O(N) and fast enough.

## Sketch

```python
def create_background_map(image, badpixmask, width, percent, csize, nbad):
    image0 = np.array(image, dtype=float)
    image0[badpixmask.astype(bool)] = np.nan
    width2 = width // 4
    ny, nx = image0.shape
    ncols = (nx + width2 - 1) // width2
    pad = ncols * width2 - nx
    if pad > 0:
        image0p = np.pad(image0, ((0, 0), (0, pad)),
                         constant_values=np.nan)
    else:
        image0p = image0
    ribbons = image0p.reshape(ny, ncols, width2)
    ribbon_med = bn.nanmedian(ribbons, axis=2)         # (ny, ncols)
    step = max(1, width // 8)
    ys = np.arange(0, ny, step)
    coarse = np.full((ys.size, ncols), np.nan)
    hw = width // 2
    for j, y in enumerate(ys):
        y0, y1 = max(0, y - hw), min(ny - 1, y + hw)
        coarse[j] = np.nanpercentile(ribbon_med[y0:y1], percent, axis=0)
    # linear interp back to full row axis, per column
    y_full = np.arange(ny)
    backest_cols = np.empty((ny, ncols))
    for j in range(ncols):
        backest_cols[:, j] = np.interp(y_full, ys, coarse[:, j])
    backest = np.repeat(backest_cols, width2, axis=1)[:, :nx]
    backmask = (image0 < backest).astype(float)
    nribbon = convolve2d(backmask, np.ones([1, csize]), mode='same')
    backmask[nribbon == 1] = 0
    backmask[nribbon >= nbad] = 1
    return backmask
```

## Risk / correctness

- The 0.53 % changed-pixel figure is the pixel disagreement measured
  against the current implementation. Because the output is a binary
  background mask that is subsequently morphologically cleaned
  (`nribbon == 1` and `nribbon >= nbad`), the impact downstream is
  smaller than that number suggests.
- If bit-for-bit output is required, raise the coarse `step` from
  `width // 8` to `width // 32` or evaluate every row (still much
  faster than the current loop because `nanpercentile` runs on all
  columns at once).
- Function signature and return type do not change.

## Test coverage

Add a correctness test that compares the new implementation to the old
on a small (256 x 256) image and asserts the fractional mask
disagreement is below a documented threshold (e.g. 1 %). The
`test_perf_create_background_map` benchmark in
`apero-core/tests/test_perf_benchmarks.py` provides the timing side.

## Post-change status (implemented)

Applied in `background_core.create_background_map` with a helper
`_ribbon_running_pct`. The interior y-rows are evaluated in a single
`np.percentile(..., axis=1)` call over a `sliding_window_view` of the
ribbon; the rare windows containing NaN fall back to `np.nanpercentile`
so we preserve exact behaviour. Edge rows (first/last `hw`) still use
the truncated-slice per-row calls to be bit-identical.

- Correctness: `np.array_equal(new, old)` holds on synthetic 256x256
  frames with and without NaN sprinkling (see
  `test_create_background_map_matches_reference`).
- Timing (4088 x 4088, `width=100`): **41.2 s -> 3.1 s (~13x)**.
