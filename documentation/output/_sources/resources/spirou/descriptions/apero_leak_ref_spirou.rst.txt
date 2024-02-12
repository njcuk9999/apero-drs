==================================
Leak reference calibration
==================================

For PRV observations, the observational setup is most often one with a science object in the A and B fibers and an
FP illumination in the C fiber (i.e., `OBJ_FP` or `POLAR_FP`). Considering that the SPIRou slicer has sharp edges
in its pupil, there is a diffraction pattern that leads to a spike in the cross-fiber direction and a modest
cross-fiber component in the leakage. The leakage of the FP spectrum onto the science spectrum is constant through
time as it is solely due to pupil geometry, and can therefore be calibrated and subtracted. The reference leak
recipe finds all `DARK_FP` files in the raw directory (from the reference night). Each `DARK_FP` file is then
extracted. Once all `DARK_FP` files are extracted they are combined for each fiber: AB, A, B, and C (via a median
across all extracted \ETDS files) creating one image (:math:`49\times4088`) per fiber. Conceptually, the leak
correction is straightforward: take the combined `DARK_FP`, normalize each C fiber FP to unity (using the 5th
percentile of FP flux within the order) and measure the recovered spectrum in the A and B fibers. For any given
`OBJ_FP` or `POLAR_FP` observation, one simply measures the C fiber FP flux and scales the leakage in A and B
accordingly.

The method has been tested over the lifetime of SPIRou and subtracts the high-frequency component of the leakage at a
level better than 1 in 100 in the most contaminated orders. The reference leak calibration file (`REFLEAK`) is then
saved to the calibration database for use throughout APERO.