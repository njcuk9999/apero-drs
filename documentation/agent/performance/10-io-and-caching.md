# 10 - Recipe-level I/O and calibration lookups

**Files:** `apero-drs/apero/io/*`, `apero-drs/apero/science/**/*` callers, `apero-drs/apero/recipes/spirou/*`
**Scope:** pipeline-wide, not a single hot function

Unlike the other suggestions in this directory this one is not backed
by a single microbenchmark, but by a checklist of patterns that were
observed while auditing the recipe/science layers. Each pattern has a
concrete recommendation and an estimate of the practical impact based
on how often it appears in an end-to-end run.

## 10a. Cache calibration-DB lookups per recipe invocation

`apero.core` calibration-DB helpers are called from many science
modules (`flat_blaze`, `shape`, `wave`, `leak`, `thermal`, `extract`).
Each call goes through the ParamDict-driven CalibDB lookup and, in
many cases, re-reads and re-parses the calibration FITS header.

**Recommendation.** Add a per-recipe-run `dict` cache keyed by
`(calib_key, obstime, fiber)` that memoises the resolved calibration
file path and its loaded HDU. On a recipe like `apero_extract_spirou`
which reads shape, order profile, and background calibrations for
each of 3 fibers, this typically saves several disk reads per file.

**Estimated impact.** ~1 - 3 s per exposure on cold caches. Larger
on NFS-mounted `DRS_CALIB_DB` (which is common on shared clusters).

## 10b. Prefer `astropy.io.fits.getdata(..., memmap=True)` for large reads

The extraction path currently reads full 4088 x 4088 float32/float64
arrays with `astropy.io.fits.getdata`. When only the header (or a
small slab) is needed - e.g. reading a HEADER keyword to decide
whether to skip a step - loading the whole HDU is wasted I/O.

**Recommendation.** Audit `apero-drs/apero/io/drs_fits.py` for
`getdata`/`getheader` call pairs and merge them into a single
`with fits.open(path, memmap=True) as hdul: ...` block so
metadata-only paths never materialise the pixel array. `memmap=True`
should be the default for the pixel-heavy reads too, as long as the
consumer converts to a real array (`np.array(hdu.data)`) before the
file handle closes.

**Estimated impact.** 0.5 - 2 s per exposure depending on the number
of intermediate calibrations that only need the header.

## 10c. Avoid re-writing intermediate FITS products the pipeline does
     not consume

Several extraction / calibration paths write PDFs, PNGs and
intermediate FITS files (via `recipe.plot(...)` and the summary
system). Some are large (E2DS/S1D/PP intermediates). If a downstream
recipe never reads them and they are only there for QC, gate them
behind a `params['PLOT_LEVEL'] > 0` check that is disabled during
batch reductions.

**Recommendation.** Do not remove the plots; move the file-writing
side behind an existing pipeline flag. The plotting registry in
`apero-drs/apero/plotting/definitions.yaml` is the right place to
tag heavy plots as `batch_skip: true`.

**Estimated impact.** Non-trivial on large N-exposure runs; less
about CPU and more about SSD write bandwidth and downstream `find`
cost on the reduction tree.

## 10d. Use `concurrent.futures.ThreadPoolExecutor` for the
     per-file preprocess loop

`apero_preprocess` (and its analogues) processes files one at a time
in a Python `for` loop. Preprocessing is IO-bound (raw read + calibration
lookup + rotation + save), so a thread pool of 4-8 workers scales
almost linearly.

**Recommendation.** In `apero-drs/apero/recipes/spirou/apero_preprocess_spirou.py`,
wrap the outer file loop with `concurrent.futures.ThreadPoolExecutor`
sized from `params['CORES']`. Keep the logger writes serialised via
`apero.core.core.drs_log`'s existing thread-safe path.

**Estimated impact.** For a night with ~200 preprocess targets,
walk-clock drops from ~15 minutes to ~3 - 4 minutes on an 8-core
workstation.

## 10e. Batch database writes on the reduction-manifest side

`apero.core.core.drs_database` calls execute one INSERT per output
file. On a full night this fires thousands of small transactions.
Wrapping the ingest loop in a single transaction (or using
`executemany` where the DB backend supports it) shrinks the manifest
write phase from minutes to seconds.

**Recommendation.** Audit the sqlite/MySQL commit points in
`apero-drs/apero/core/core/drs_database.py` and expose a
`with db.batch(): ...` context that opens a single transaction for
the calling scope. `apero_processing` should hold that context open
for the whole night's ingest.

**Estimated impact.** Reduces the "ingest" phase at the end of a
processing job by 5 - 15x.

## What is intentionally not on this list

- **Rewriting recipes in C/Cython.** APERO is a numpy pipeline; the
  wins in this document come from either avoiding Python for-loops on
  pixel arrays or coalescing I/O.
- **Adding a GPU backend.** The extraction routines are already
  memory-bound on modern CPUs; GPU work would need a much larger
  rewrite for uncertain wins.
- **Changing the recipe structure** away from `main_extract()` /
  ribbon-per-order. That structure is what makes `08-*.md` (per-order
  parallelism) trivial to land.

## Test coverage

No microbenchmarks fit in `apero-core/tests/test_perf_benchmarks.py`
for these - they need a real APERO profile, calibration tree, and
representative night of data. The right harness is an end-to-end
wall-time measurement of `apero_processing` for one night, before
and after each of 10a - 10e. Log those numbers back into this file.
