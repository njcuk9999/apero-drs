==================================
Nightly shape calibration
==================================

Before extracting the spectrum, we need to transform the image into a format that is amenable to a simple
1-dimensional collapse. Given our reference FP grid and the x and y displacements maps, on a given night, we only
need to find the affine transform that registers FP peaks onto the reference FP image and updates the x and y
transform maps within the affine contribution. This assumes that the order curvature is constant through the life
of the instrument and that the slicer shape is stable. We note that as the order profiles are determined in each
nightly calibration, a slight (sub-pixel) modification of the position of orders would have no impact on the
extracted spectra which are extracted with the profile measured for the corresponding night.

The nightly shape recipe takes preprocessed `FP_FP` files (as many as given by the user or as many as occur on each
of the nights being used via `apero_processing`). It combines the `FP_FP` files into a single `FP_FP` per night
(via a median combination of the images). After combining, the `FP_FP` images are calibrated using our standard
image calibration technique. We take the `REFFP`, `SHAPEX` and `SHAPEY` calibrations from the calibration database.
If multiple exist we use the closest in time (using the header key `MIDEXPOSURE` from the header).
To find the linear transform parameters (dx, dy, A, B, C, and D) between the reference `FP_FP` and this night's
`FP_FP` we find all the FP peaks in the reference `FP_FP` image and in the nightly `FP_FP` image. Once we have the
linear transform parameters we shift and transform the combined and calibrated nightly `FP_FP` via our shape
transform algorithm and save the transformed image and un-transformed image to disk (for manual comparison to the
input `FP_FP` image).

As part of quality control, we check that the RMS of the residuals in both directions (across order and along the
order) are less than 0.1 pixel, which has been found to be optimal to flag pathological cases. The transformation
parameters (dx, dy, A, B, C, and D, henceforth `SHAPELOCAL`) are then saved to the calibration database (if both
quality control criteria are met) for use throughout APERO.