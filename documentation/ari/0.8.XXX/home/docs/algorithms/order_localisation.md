---
card_label: Order localisation
card_icon: fa-solid fa-wave-square
---

# Order localisation and profile fitting

## Scope

This page describes the current v0.8 localisation stage implemented by
`apero.science.calib.localisation.calc_localisation`. The function consumes a
2-D order-profile image for one fiber and returns Chebyshev coefficients for
the order centers and widths. Instrument constants control the filter sizes,
area limits, fit degrees, allowed detector range, and fiber-specific behavior.

This is the order-detection/fitting stage. The surrounding recipe combines
and calibrates input images, selects fibers, applies quality checks, and writes
calibration products; those wrapper operations are not repeated here.

## 1. Build a spatial threshold

Let $I(y,x)$ be the order-profile image, where $x$ is the dispersion direction
and $y$ is the cross-dispersion direction. The detector columns are processed
in bins of width $b$. For each bin beginning at $x_j$, form the cross-dispersion
profile

$$
P_j(y) = \operatorname{median}_{x_j \leq x < x_j+b} I(y,x).
$$

Apply the configured lower and upper percentile filters, with spatial window
size $s$:

$$
L_j(y) = \operatorname{PercentileFilter}(P_j, p_{\mathrm{low}}, s),
\qquad
H_j(y) = \operatorname{PercentileFilter}(P_j, p_{\mathrm{high}}, s).
$$

The threshold assigned to every column in the bin combines the two local
percentiles as follows:

$$
T_j(y) = L_j(y) + \frac{H_j(y)}{2}.
$$

The binary candidate mask is $M(y,x) = [I(y,x) > T_j(y)]$. The first and last
$b$ columns are masked to avoid incomplete edge bins. Non-finite image values
are replaced by zero before thresholding.

## 2. Identify candidate order regions

Label 8-connected components in $M$. Components must exceed the configured
minimum area $A_{\min}$. Within each candidate component $R$, pixels below
five percent of its 95th-percentile flux are removed:

$$
I(y,x) < 0.05\,Q_{0.95}\bigl(I|_R\bigr).
$$

Each mask row is median-filtered with width 11, then binary dilation is
applied. Ordinary fibers receive one dilation; fibers configured for a
combined localization solution receive the configured number of dilation
iterations. The mask is relabelled after cleanup, again retaining only
components larger than $A_{\min}$.

## 3. Fit candidate centerlines

A candidate is considered only if its labelled pixels cross the detector
midpoint in $x$. For each candidate, fit a Chebyshev polynomial to its
cross-dispersion coordinates as a function of dispersion coordinate:

$$
y_r(x) = \sum_{k=0}^{d_c} c_{r,k}\,T_k(\tilde{x}),
\qquad \tilde{x}\in[-1,1],
$$

where $d_c$ is the configured center-fit degree and the implementation maps
$x$ into the detector domain `[0, n_x]`. Evaluate the fitted center at the
detector midpoint. Keep candidates whose midpoint center falls within the
configured `$y_{\min}$` and `$y_{\max}$` limits, then sort them by center.

For fibers with order doublets, a fifth-degree polynomial models the center
index trend. Residual sign and the configured fiber parity select one member
of each doublet. A robust polynomial fit to consecutive center gaps rejects
outliers; the accepted gap trend is used to infer missing order indices.

For each Chebyshev coefficient $c_k$, robustly fit that coefficient against
the inferred order index and evaluate the fit across a padded order-index
range. This imposes smooth coefficient trends across neighboring orders. The
predicted centers are clipped to the configured detector range and their
constant coefficients are adjusted to remain anchored to nearby measured
centers, within one quarter of the median order spacing.

## 4. Fit order widths

At a set of configured dispersion samples, count candidate pixels in a
cross-dispersion strip around each sample. Normalize by the strip width and
add the implementation's two-pixel margin to obtain a width estimate. For the
final width fit, count labelled pixels per dispersion column, select the
illuminated span using half its 90th-percentile count, trim 15 pixels from each
end, smooth with a 15-pixel box, and robustly fit a Chebyshev polynomial of the
configured degree.

Finally, robustly fit each width coefficient against the corresponding
order's cross-dispersion position. Evaluate these coefficient trends at the
final order centers. The returned center and width coefficient arrays are
consumed by later localisation code to construct order maps and bounds.

## Quality controls and diagnostics

This function plots the initial/cleaned masks, fiber-doublet residuals, order
gaps, width coefficients, and fitted curves over the image through the
standard recipe plotting system. Recipe-level checks validate the resulting
order count and geometry before calibration products are accepted.

## Implementation

- Implementation: `apero-drs/apero/science/calib/localisation.py`, function
  `calc_localisation`.
- Relevant constants: `CAL.LOC.BINSIZE`, `BOX_PTILE_LOW`, `BOX_PTILE_HIGH`,
  `PTILE_FILTER_SIZE`, `MIN_ORDER_AREA`, `CENT_POLYDEG`, `WID_POLYDEG`,
  `RANGE_WID_SUM`, `YDET_MIN`, `YDET_MAX`, and `NUM_WID_SAMPLES`.

## References

- Cook et al. (2022), [The SPIRou Legacy Survey: radial velocity precision
  and data reduction](https://arxiv.org/abs/2211.01358). This paper describes
  a previous APERO pipeline state; use it for context, not as a specification
  of every v0.8 implementation detail.
- [Chebyshev polynomials](https://en.wikipedia.org/wiki/Chebyshev_polynomials)
