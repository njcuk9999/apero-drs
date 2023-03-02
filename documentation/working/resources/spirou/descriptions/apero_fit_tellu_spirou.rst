================================================
Correcting telluric absorption (ftellu)
================================================

All hot stars and science targets are corrected for telluric absorption. The first step, as with mktellu, is the
pre-cleaning correction. Then, we correct the residuals of the pre-cleaning at any given wavelength by fitting a
linear combination of water and dry components. We assume that any given absorption line in the TAPAS absorption
spectrum has a strength that is over or underestimated relative to reality, the residuals after correction will
scale, as a first order, with the absorption of the chemical species. The same is true with line profiles; if the
wings of a line are over or underestimated, the residuals will scale with absorption We correct the telluric absorption
on the combined AB extracted spectrum and subsequently use the same reconstructed absorption (for fiber AB) to correct
the extracted spectra for fibers A and B individually.

