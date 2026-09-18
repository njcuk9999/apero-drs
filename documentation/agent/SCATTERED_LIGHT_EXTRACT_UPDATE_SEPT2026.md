# Scattered-Light Extraction Update, September 2026

## Purpose

This document records the extraction migration from the legacy APERO
per-fiber path toward the model/background method developed in
`apero-updates-extraction/background_removal2.py`.

The migration is deliberately staged. The science extraction path now emits
one flat-corrected E2DSFF product per fiber while the new numerical path is
validated.

## Previous APERO Extraction

The original `apero_extract_{instrument}.py` recipes performed these steps
inside a fiber loop:

1. Load shape, localisation, wavelength, flat, and blaze products.
2. Straighten the calibrated image.
3. Extract one fiber at a time with `extract.extract2d()`.
4. Apply leak correction using a previously extracted reference fiber.
5. Apply flat/blaze correction to create E2DSFF.
6. Apply thermal correction.
7. Build S1D products, pixel-to-pixel statistics, QC, plots, and files.

This path is tightly coupled to E2DS/E2DSFF property dictionaries and file
writers. It also cannot fit overlapping fiber profiles simultaneously.

## Upstream Calibration Products

The new path reuses products already created by APERO calibration recipes:

- `extract.order_profiles()` loads the straightened `ORDERP_{fiber}`
  extensions from the combined `LOC_LOCO` product.
- `apero_loc` writes `ORDER_POS_MAP`, `ORDER_RANGE_TABLE`, `ORDER_TOP`,
  `ORDER_BOTTOM`, and `ORDER_MID` into `LOC_LOCO`. The range table remains
  the trace-label contract. The ribbon products are computed once with
  `extract_model_core.ribbon_geometry()` from merged localization fits and
  are consumed by extraction; SPIROU has 49 paired ribbon positions.
- `apero_shape` writes `DXMAP_NO_SHAPE` into the `SHAPEL` product.
- `shape.get_shape_calibs()` loads `DXMAP_NO_SHAPE` into `sprops`.

`extract.order_profiles()` now returns an `oprops` dictionary containing:

- `ORDERP`
- `ORDERPFILE`
- `ORDERPTIME`
- `LOCOFILE`
- `ORDER_MAP`
- `ORDER_RANGES`

This keeps all localisation-derived extraction inputs together.

## New APERO Path

The new APERO orchestration is in
`apero-drs/apero/science/extract/model_background.py`.

`run_all_fiber_model()` currently performs:

1. Use the existing straightened order profiles.
2. Build paired order ribbons with `ribbon_geometry()`.
3. Fit both fiber profiles and a zero point simultaneously with
   `extract_orders()`.
4. Build fitted amplitudes and model products.
5. Reverse-transform the loaded order profiles into the science frame.
6. Rebuild the fitted model in science coordinates with `model_in_science()`.
7. Estimate the smooth scattered-light background from the model-subtracted
   straightened image.
8. Sample the background into the science frame.
9. Estimate readout noise and apply hysteresis masking.
10. Extract spectra from the background-corrected science frame with
    `extract_spectra()` and irregular local polynomial fits.
11. Extract the profile-throughput (blaze) grid on the same spectrum grid for
  S1D stitching.

The result exposes both transitional and new products:

- `MODEL_SPECTRA`: fitted amplitude spectra for the two fibers and
  `COMBINED`.
- `SCIENCE_MODEL`, `SCIENCE_FIBER_MODEL`, and `SCIENCE_ZERO_MODEL`.
- `SCIENCE_XMAP`.
- `SPECTRA` and `SPECTRUM_GRID` from science-frame irregular-grid extraction.
- `BLAZE`, the profile-throughput grid for each extraction grouping.
- Background, error, residual, sigma, and mask products.

The three instrument extraction recipes invoke this orchestration before the
existing APERO output/cleanup loop.

The new path also registers `EXTRACT_MODEL_BACKGROUND` through the standard
APERO plotting system. It displays the science-frame model,
background-subtracted science, residual, and hysteresis mask without writing
ad hoc recipe-side plotting files.

The same plot is now registered as `SUM_EXTRACT_MODEL_BACKGROUND` for all
three extraction recipe definitions.

The transitional `spectra_to_eprops()` adapter consumes `SPECTRA` and its
uncertainties, rather than using the fitted straight-frame amplitudes as the
primary spectrum. This means the existing APERO S1D/QC/writer path is already
fed by the new science-frame extraction. Replacing this adapter still requires
a new shared output metadata contract for QC, headers, and order tables.

Instrument-specific fiber grouping is now supplied by instrument class APIs
(`FIBER_SPECTRAL_GROUPS()` and `FIBER_RIBBON_INTERLEAVED()`). The pure core
receives grouping data and booleans only; it does not branch on instrument
names.

S1D creation now also receives `SPECTRA` and its uncertainties directly from
the recipe. The existing `e2ds_to_s1d()` implementation is reused as the grid
and stitching engine, but it no longer reads the adapter's E2DS array as its
science input.

Leak correction now receives the reference spectrum directly from the
simultaneous model products rather than waiting for a reference E2DS file to
be produced earlier in the compatibility loop.

The recipes now call the spectra-level leak interface directly. The existing
low-level calibration/reference algorithm is reused, while the old
`manage_leak_correction()` property-bag entry point is no longer used by the
extraction recipes.

The SPIROU extraction recipe now also calls `correct_spectrum_thermal()` on
the model-extracted spectrum. This reuses `tcorrect1()`/`tcorrect2()` while
moving thermal correction off the old property-bag entry point.

The extraction recipes no longer call the legacy flat/blaze correction on the
new spectra. The fitted profiles already normalize the extracted spectra, and
the core now computes the profile-throughput grid described by
`background_removal2.py::extract_blaze()`. S1D stitching uses that grid;
legacy flat/blaze values remain available for transitional metadata.

The APERO wrapper converts the fitted straight-frame model from electrons back
to ADU before estimating scattered light. This matches the reference script
and is required for non-unit-gain instruments such as NIRPS.

The user-facing numerical controls from `background_removal2.py` now live in
the `CAL.EXT` APERO constants and are overridden for SPIROU, NIRPS-HA, and
NIRPS-HE: `RON_START`, `FIT_RON`, `RON_STRIDE`, `RON_LAG`, `BKG_BOX`,
`BKG_STRIDE_FRAC`, `MASK_NSIG1`, `MASK_NSIG2`, `FIT_ROBUST`, `FIT_NCLIP`,
`FIT_NSIG_CLIP`, `FIT_ZP_MAD_CUT`, `SAVGOL_WINDOW`, `SAVGOL_POLYORDER`,
`SAVGOL_STEP`, `SAVGOL_CUT`, `SAVGOL_MINPTS`, `SAVGOL_WEIGHT`, and
`MAKE_BLAZE`. The wrapper reads these directly from `ParamDict`; missing
constants are no longer silently replaced by script literals.

Reference-script settings for hard-coded input paths, output directories,
debug PDFs, diagnostic pauses, and the optional flat-built profile experiment
remain script-only because APERO already owns those through recipe inputs,
plot configuration, calibration products, and standard output handling.

The three extraction recipe definitions now resolve their `E2DS_FILE` and
quicklook `Q2DS_FILE` keys to the E2DSFF file definitions. This makes the
flat-corrected product the actual extraction output while compatibility key
names are being retired. Normal and quicklook writers now write and register
only the E2DSFF-backed product.

The instrument file definitions now register only the E2DSFF-suffixed normal
and quicklook products. Legacy variable names remain aliases temporarily so
downstream definitions can be migrated without creating a second file.

Shared extraction configuration, leak-reference creation, FPLINES, wavelength
output creation, visualisation, and UberV now consume the E2DSFF product
directly. The extraction recipe no longer registers separate `E2DS_FILE` or
`Q2DS_FILE` outputs. Calibration recipe logical names such as
`LEAK_E2DS_FILE` remain for their independent calibration contracts, but they
also point to the E2DSFF file definition.

## Pure Core Algorithms

Profile-independent numerical functions live under
`apero-core/aperocore/science/extract/extract_model_core.py`.

Generic array algorithms live under
`apero-core/aperocore/math/interpolate.py`, including:

- nearest-finite NaN filling,
- bilinear expansion and sampling,
- normalized kernel totals,
- irregular local polynomial fitting,
- finite-sample cubic spline construction.

The science extraction core includes:

- readout-noise fitting,
- between-order readout-noise estimation,
- hysteresis masking,
- coarse background modelling,
- trace and spectral grouping,
- ribbon geometry,
- robust profile fitting,
- science-frame model reconstruction,
- irregular-grid spectrum extraction.

The core accepts plain arrays, scalars, and dictionaries. APERO parameters,
recipes, calibration files, and logging remain in the APERO wrapper layer.

## Comparison With `background_removal2.py`

The new path follows the important numerical structure of
`background_removal2.py` without copying its standalone-script I/O model.

Implemented or integrated:

- `ribbon_geometry`
- `weighted_fit_batch`-style simultaneous profile fitting
- robust trimmed fit starts
- `extract_orders`
- `model_in_science`
- coarse `background_model`
- bilinear background sampling
- `fit_ron`
- `ron_between_orders`
- hysteresis masking
- irregular local polynomial extraction
- profile-based model and background separation

Intentionally different:

- Calibration products are loaded through APERO's existing database and file
  definitions.
- Order profiles come from `extract.order_profiles()`.
- Shape and localisation products come from `apero_shape` and `apero_loc`.
- APERO recipe logging, parameter provenance, QC, plotting, and output
  handling remain in APERO wrappers.
- The standalone script's filesystem cache and hard-coded instrument paths are
  not copied into the recipe.

## Transitional Work Remaining

The new extraction path is active. The recipe-local legacy spatial extraction
call has been removed; the remaining compatibility loop exists to preserve
the current leak, thermal, S1D, QC, and file-writer contracts.

Remaining work:

1. Replace the temporary `spectra_to_eprops()` adapter with a new extraction
  metadata/output contract for QC, headers, and order tables.
2. Complete the comment and function-placement review requested in
  `AGENTS.md`.

The flat/blaze calibration recipes still use the established `extract2d()`
calibration algorithm. Those calls operate on flat calibration frames and do
not create the science E2DS product.

## Validation

The migration currently has focused pure-core and APERO wrapper tests, plus
full APERO DRS coverage. The most recent validation reported:

- 14 focused `apero-core` extraction tests passed.
- 9 focused APERO extraction integration tests passed.
- 184 full `apero-drs/tests` tests passed.

Small synthetic tests still emit interpolation warnings when their coarse grid
has only one interval. These warnings are confined to the synthetic fixture;
real detector-sized grids have the expected multiple interpolation intervals.
