==========================================
Radial velocity via CCF
==========================================

The CCF method is very often used for PRV work, particularly in the optical domain. In the early APERO effort, it was
the main tool to derive precise RV values. When implementing a near-infrared version of the CCF, a number of
challenges appeared. The near-infrared domain is plagued with telluric absorption, and even after telluric correction,
some wavelength domains are expected to have significant excess noise levels. Deep or saturated telluric lines cannot
be corrected and are better left as gaps (represented as \NAN) in the spectrum that are fixed for the entire time
series considered. When computing a CCF, how does one account for gaps in the data? The star's yearly line of sight
variations will cause this gap to shift against the stellar spectrum by up to :math:`\pm 32 kms^{-1}` depending
on ecliptic latitude. In the optical, one can simply reject the entire domain affected by the gap (64 :math:`kms^{-1}`
plus the gap width); however, at optical wavelengths, deep absorption lines are sufficiently sparse that the overall
loss in wavelength domain due to telluric absorption is small, which is not the case in the near-infrared.

To further obfuscate the issue, telluric absorption varies between nights, so if one went down this path of masking,
it would end with the masking of a large window affected by any line that gets deeper than a given threshold, even if
only once in a time-series that may include hundreds of visits. The combination of varying conditions and yearly BERV
excursions leads to a loss of domain that is simply unacceptable, especially considering that the parts of the
near-infrared that are richest in sharp spectroscopic features (See Figure 4 in Artigau et al. 2022) are at the blue
and red edges of the H band, which are affected by telluric water absorption.

We opted for a CCF that correlates weighted delta functions against the spectrum but set the weight to zero when
reaching a point below 0.5 telluric transmission (where unity is no telluric absorption). This is done on a
spectrum-to-spectrum basis, to minimize the effective throughput losses. This CCF measurement is performed per
spectrum using one of the 3 standard masks available in \APERO depending on the star's temperature (GL846, Gl699,
Gl905 respectively for Teff >3500 K, 3000-3500 K, <3000 K. We derive per-order as well as global CCFs. These data
products are useful to confirm the systemic velocity of the star, avoiding eventual target misidentifying, as well
as for flagging spectroscopic binaries. For time-series analysis, it can be significantly improved upon by using
all observations to perform a spectral cleaning to obtain a much cleaner CCF or through completely different methods,
such as the line-by-line algorithm.
