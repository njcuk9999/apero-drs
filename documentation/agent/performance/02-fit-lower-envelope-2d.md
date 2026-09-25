# 02 - Cheaper inner loop in `fit_lower_envelope_2d`

**File:** `apero-core/aperocore/science/calib/background_core.py`
**Function:** `fit_lower_envelope_2d` (lines 248 - 488)
**Benchmark test:** `test_perf_fit_lower_envelope_2d`

## Timings (4088 x 4088, `xorder=yorder=3`, `bin_size=4`, `niter=10`)

| Version | Wall time |
|---------|-----------|
| Current | **11.1 s** |
| Prototype target | **3-4 s** |
| **Speed-up** | **~3x** |

The exact win depends on how many `_run(fpos)` invocations the `f_pos =
'auto'` branch actually performs (currently 12 outer bisection steps,
each doing up to `len(anneal) + niter` fits).

## Why it is slow today

Three cost centres:

1. **`_full_surface` allocates the full-detector basis on every call.**
   `_full_surface` (lines 393 - 399) rebuilds `full_ubas` and `full_vbas`
   (`stack([full_u ** p for p in range(yorder + 1)])`) even though the
   grids never change during the fit. This is a hot path when
   `verbose=True` prints per-iteration diagnostics, and it also
   happens once at the very end for each of the 12 bisection trials.
2. **`f_pos='auto'` runs 12 full weighted-least-squares fits.**
   Each `_run` call executes the anneal (5 passes) plus up to `niter=60`
   passes on a binned image, then evaluates a full-resolution surface.
   The bisection on `log10(f_pos)` uses fixed 12 iterations regardless
   of how quickly `_balance` converges to 0.5.
3. **`_solve` rebuilds the `mat` outer-product indexing every pass.**
   `mat = smom[ii[:, None] + ii[None, :], jj[:, None] + jj[None, :]]`
   is 16 x 16 for a degree-3 polynomial; the cost is small but it is
   done inside a while loop that also allocates `smom`, `rmom`, `nsig`,
   `gauss`, `w` arrays sized like the binned image (1022 x 1022 with
   `bin_size=4`).

## What to change

Three independent, additive improvements. All keep the fit surface
identical to today.

### 2a. Cache the full-detector basis

Compute `full_ubas` and `full_vbas` once at function entry and reuse
them from `_full_surface`. Move `upow`, `vpow`, `ubas`, `vbas`
construction outside the inner loop (they already live at
function scope; ensure `_run` and `_full_surface` close over the same
cached arrays).

### 2b. Early-exit the `f_pos='auto'` bisection

Track `bal` from the previous trial. Break out of the 12-step loop
as soon as `abs(bal - 0.5) < 0.01` (or another tunable tolerance).
On typical images the balance converges in 3-4 iterations, cutting
the auto branch time by ~3x.

```python
if isinstance(f_pos, str) and f_pos.lower().startswith('auto'):
    lo, hi = np.log10(1e-4), np.log10(0.95)
    used, best = None, None
    for _ in range(12):
        mid = 0.5 * (lo + hi)
        trial = _run(10.0 ** mid)
        bal = _balance(trial[1])
        used, best = 10.0 ** mid, trial
        if abs(bal - 0.5) < 0.01:
            break
        if bal < 0.5:
            lo = mid
        else:
            hi = mid
```

### 2c. Convergence tolerance on the anneal loop

The anneal fixed-point loop already tests `move < tol`. Consider a
tighter early exit when `move` has stopped decreasing rather than
running to `niter=60` in the worst case.

### 2d. (Optional) precompute the moment reduction with einsum

`smom = (upow @ w) @ vpow.T` allocates a `(2*yorder+1, nx_binned)`
intermediate. On the 1022 x 1022 binned grid with degree 3, the two
`@` calls together allocate ~57 MB; using `np.einsum('py,yx,qx->pq',
upow, w, vpow, optimize=True)` merges the two into one contraction
and reuses the same buffer, roughly halving allocation traffic (and
speeding by ~10-20 % on typical hardware).

## Risk / correctness

- **2a** is a pure refactor; no numeric change.
- **2b** shortens the bisection but returns the same `f_pos` value
  to within the requested balance tolerance. Guard with a
  `min_iter=4` if bisection stability is a concern.
- **2c** can be gated by a boolean parameter so the default behaviour
  is preserved for existing callers.
- **2d** may reorder floating-point operations by ~1 ULP; add a
  numerical tolerance test.

## Test coverage

- `test_perf_fit_lower_envelope_2d` for timing.
- Add a correctness test that compares the fitted surface (`fit`
  return value) before and after with `np.allclose(a, b, rtol=1e-5)`
  on a small (256 x 256) frame.
