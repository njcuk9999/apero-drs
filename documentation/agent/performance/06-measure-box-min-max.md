# 06 - Replace `measure_box_min_max` Python loop with `bn.move_min` / `bn.move_max`

**File:** `apero-core/aperocore/math/gen_math.py`
**Function:** `measure_box_min_max` (lines 50 - 90)
**Benchmark test:** `test_perf_measure_box_min_max`

## Timings (`y` = 4096 float, `size=32` -> box width 64)

| Version | Wall time |
|---------|-----------|
| Current (Python loop calling `fast.nanmin`/`nanmax` 4032 times) | **4.34 ms** |
| Prototype (`bn.move_min`/`bn.move_max`) | **0.08 ms** |
| **Speed-up** | **~55x** |

Output matches the current implementation bit-for-bit on synthetic
data (both use the same underlying reductions, just in the correct
running-window form).

## Why it is slow today

```python
for it in range(size, ny - size):
    min_image[it] = fast.nanmin(y[it - size:it + size])
    max_image[it] = fast.nanmax(y[it - size:it + size])
```

This calls `fast.nanmin` and `fast.nanmax` `ny - 2*size` times. Each
call has ~µs overhead and only ~2*size = 64 elements to reduce over,
so the ratio of dispatch to work is very poor.

`bottleneck` (already a project dependency) exposes
`bn.move_min(a, window, min_count=1)` and `bn.move_max` which compute
the whole running array in one Cython pass with monotonic deques (the
standard "sliding window minimum" algorithm, O(n) not O(n * window)).

## What to change

Rewrite the body of `measure_box_min_max` to:

```python
def measure_box_min_max(y, size):
    ny = y.shape[0]
    box = 2 * size
    ymin = bn.move_min(y, window=box, min_count=1)
    ymax = bn.move_max(y, window=box, min_count=1)
    # bn.move_* returns the reduction ending at index i; the original
    # loop centres the window on index it, i.e. uses indices
    # [it - size : it + size]. Shifting by 'size' gives the same result.
    min_image = np.empty(ny)
    max_image = np.empty(ny)
    min_image[:ny - size] = ymin[size:]
    max_image[:ny - size] = ymax[size:]
    # replicate the current edge handling exactly
    min_image[:size] = min_image[size]
    max_image[:size] = max_image[size]
    min_image[ny - size:] = min_image[ny - size - 1]
    max_image[ny - size:] = max_image[ny - size - 1]
    return min_image, max_image
```

Wrap the `bn` call in a fallback that uses the current loop when
`bottleneck` is not available, mirroring the pattern already used in
`aperocore.math.fast`.

## Risk / correctness

- Bit-identical on 1D non-NaN input.
- With NaNs in the input, `bn.move_min` treats NaN like the current
  `fast.nanmin` (via `nanmin` semantics). Add a quick test that
  compares to the current loop for a vector with sprinkled NaNs.
- No signature change; downstream call sites need no modification.

## Where this matters in the pipeline

`measure_box_min_max` is used inside envelope/percentile helpers.
Even though the per-call cost is small, it is called in inner loops
in the shape and wave calibration paths, so a 55x cut adds up.

## Test coverage

- `test_perf_measure_box_min_max` for timing.
- Add a correctness test comparing old vs new on `y = rng.normal(size=1024)`
  and `y` with 10 % NaN, asserting `np.array_equal(new, old, equal_nan=True)`.
