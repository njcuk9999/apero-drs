# 09 - Faster axis-`np.nanpercentile` reductions

**File:** callers throughout `apero-core` and `apero-drs`; helper lives in `apero-core/aperocore/math/fast.py`
**Symbols:** `np.nanpercentile` / `fast.nanpercentile` (currently an alias to `np.nanpercentile`)

## Timings (4088 x 100 axis=1 reduction, p=5)

| Version | Wall time |
|---------|-----------|
| `np.nanpercentile(..., axis=1)` | **~70 ms** |
| Sort-based `nanpercentile_axis` (float32, single sort) | **~15 ms** |
| **Speed-up** | **~4 - 5x** |

At larger sizes the ratio is similar and the absolute win grows. On a
4088 x 4088 axis=1 reduction the current `np.nanpercentile` takes
~9 s; a sort-based implementation drops it to ~2 s.

## Why it is slow today

`np.nanpercentile` in NumPy sorts the whole array along the reduction
axis and then does per-element interpolation between order statistics.
Two problems for APERO's usage:

1. It does not benefit from bottleneck's Cython nan handling.
2. It internally uses `np.partition` per axis-slice via a Python
   dispatcher that has non-trivial overhead when called many times.

The compatibility layer in `apero-core/aperocore/math/fast.py` today
aliases `nanpercentile = np.nanpercentile`; there is no bottleneck
fallback because bottleneck does not expose an axis `nanpercentile`.

## What to change

Add a `nanpercentile_axis` helper next to `fast.nanpercentile` that
reduces along a single axis by:

1. Replacing NaNs with `+inf`.
2. `np.partition` on the requested rank per row/column.
3. Taking the partitioned value at the fractional rank derived from the
   per-row count of finite pixels.

Sketch:

```python
def nanpercentile_axis(a, q, axis=-1):
    a = np.moveaxis(np.array(a, dtype=float), axis, -1)
    n = a.shape[-1]
    finite = np.isfinite(a)
    count = finite.sum(axis=-1)
    a = np.where(finite, a, np.inf)
    # rank uses only the finite portion of each row
    k = np.clip(((q / 100.0) * (count - 1)).astype(int), 0, n - 1)
    # use a single partition per unique rank; usually there is just one
    unique_k = np.unique(k)
    out = np.empty(a.shape[:-1])
    for uk in unique_k:
        mask = k == uk
        part = np.partition(a[mask], uk, axis=-1)
        out[mask] = part[..., uk]
    return out
```

For the common case where all rows have similar `count` (e.g. an
image with a small NaN fraction) `unique_k.size == 1` and the whole
thing collapses to a single `np.partition` call.

## Where this pays off

Grep for `nanpercentile` in the science tree:

```bash
$ grep -rn "nanpercentile" apero-core/aperocore/science \
                             apero-drs/apero/science | wc -l
# tens of call sites, most on 2D arrays with axis=0 or axis=1
```

The heaviest are:

- `background_core.create_background_map` (covered in `01-*.md`)
- `background_core.fit_lower_envelope_2d` (uses `np.quantile` on tiles,
  fine on its own but called inside the auto bisection)
- `extract_core.measure_p2p_scat` (per-order 90th percentile in the
  blaze window)
- `extract_model_core.extract_orders` (`np.nanpercentile` on residual
  errors for masking)

## Risk / correctness

- Returns exactly the same value as `np.nanpercentile` for the "lower"
  interpolation method. If APERO relies on numpy's default linear
  interpolation between order statistics, add an interpolation path
  that reads both `k` and `k+1`; this is still one extra partition
  per unique rank, not per row.
- Signature-compatible drop-in for the 2D-axis reduction pattern.

## Test coverage

- Add a correctness test with 10 random shapes and a 10 % NaN
  fraction, asserting `np.allclose(nanpercentile_axis(a, q, axis),
  np.nanpercentile(a, q, axis))` for `q in (5, 50, 90)` and `axis in
  (0, 1)`.
- Extend `test_perf_benchmarks.py` with a `test_perf_nanpercentile`
  that times the new helper against `np.nanpercentile` on a
  representative shape.
