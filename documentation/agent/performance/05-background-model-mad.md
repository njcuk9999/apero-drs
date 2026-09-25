# 05 - Smaller working set in `background_model` and `_mad_from_sorted`

**File:** `apero-core/aperocore/science/extract/extract_model_core.py`
**Functions:** `background_model` (lines 181 - 236) and `_mad_from_sorted` (lines 135 - 178)
**Benchmark test:** `test_perf_background_model`

## Timings (4088 x 4088 image, `size=(31, 7)`)

| Version | Wall time |
|---------|-----------|
| Current | **2.5 s** |
| Prototype target | **~1 s** |
| **Speed-up** | **~2 - 3x** |

## Why it is slow today

`background_model` uses `sliding_window_view` on the padded image to
build a coarse `(nyc, nxc, ky*kx)` view. It then processes `chunk=128`
coarse rows at a time. Each chunk block:

```python
block = window[row0:row1].reshape(row1 - row0, nxc,
                                  ky * kx).astype(np.float32)
sorted_box = np.sort(block, axis=2)
count = np.sum(np.isfinite(block), axis=2)
```

- `.astype(np.float32)` copies the view (which is otherwise a stride
  trick) into a fresh contiguous buffer of roughly
  `128 x 260 x 217 x 4` bytes = **28 MB** per chunk.
- `np.sort(..., axis=2)` allocates another 28 MB and does an
  introsort per box (28k boxes per chunk).
- `_mad_from_sorted` then runs `np.take_along_axis` ~`log2(217) + 1`
  = 9 times inside the bisection, each producing another 28 MB
  temporary.

The dominant costs are memory allocation and cache-unfriendly indexed
gathers, not arithmetic.

## What to change

Three additive improvements.

### 5a. Use `np.partition` for the median instead of full sort

The current code sorts each box just to get the median at
`index = count // 2` and the count of finite values. `np.partition`
partitions in linear time and is roughly 2x faster than `np.sort`
for the same shape.

```python
part = np.partition(block, ky * kx // 2, axis=2)
box_med = part[..., ky * kx // 2]
```

For MAD, keep a sorted view of only the region around the median
(`np.partition(block, [q_lo, q_median, q_hi], axis=2)`). The current
"exact median of finite values only" behaviour can be preserved by
first replacing NaNs with `+inf`, partitioning, then walking back with
the finite `count`.

### 5b. Skip the `.astype(np.float32)` copy

`sliding_window_view` returns a strided view of the padded float64
array. Sorting on a strided view is slower than on a contiguous
buffer, but the buffer does not need to be `float32`: keep it in the
image's native dtype. If float32 was chosen for RAM, the peak working
set is already dominated by `sorted_box` (28 MB), and a float64 copy
(56 MB) is still cheap next to the sort itself. Choose one or the
other and remove the redundant copy that today allocates twice.

### 5c. Coarser default `stride_frac`

The default `stride_frac=0.5` yields a coarse grid of
`(ny/(ky//2), nx/(kx//2))` = `(260, 1168)` for a 4088 x 4088 image.
On the flat calibration path the background varies smoothly, so
`stride_frac=0.75` would cut the number of boxes by ~2 with no
observable change in the final expanded image (`expand_bilinear` is
already bilinear).

`stride_frac` is a keyword argument, so the change is a caller-side
tuning knob rather than a hard-coded change; add a sentence in the
docstring recommending 0.75 for detector-scale backgrounds.

## Risk / correctness

- **5a** produces the same median for every box; MAD needs the guard
  above but the returned values are analytically equal (both are order
  statistics of the same finite set).
- **5b** is a pure allocation/dtype cleanup.
- **5c** is a documented tuning knob; correctness is unchanged for
  callers that keep the current default.

## Test coverage

- `test_perf_background_model` for timing.
- Add a correctness test that compares the current output to the new
  output on a 512 x 512 image with `stride_frac=0.5` and asserts
  `np.allclose(new_med, old_med)` and `np.allclose(new_err, old_err,
  rtol=1e-6, equal_nan=True)`.
