==========================================
Wavelength solution reference calibration
==========================================

The wavelength solution generation follows the general idea of (Hobson et al 2021) however since publication there has
been an overall reshuffling of the logic. As such we present an overview of the process here but refer the reader to
(Hobson et al 2021) for further specific details.

The reference wavelength solution recipe takes preprocessed `FP_FP` and `HC_HC` files (as many as given by the user or
as many as occur on the nights being used via `apero_processing`) from the reference night. It combines the `FP_FP` and
`HC_HC` files into a single `FP_FP` and a single `HC_HC file (via a median combination of the images). These combined
`FP_FP` and `HC_HC` files are then extracted.

We first consider the combined flux in fibers A and B (the AB fiber). We locate the `HC_HC` lines, starting with a
line list generated as in (Hobson et al 2021), fitting each peak with a Gaussian and measuring the position of the
peak, and inferring peak wavelength from an initial guess at the wavelength solution from physical models. The first
time this HC finding is performed we allow for a global offset between the current `HC_HC` file and the initial guess
at the wavelength solution (this is important when our reference night is far in time from when our initial
wavelength solution data was taken).

For the `FP_FP` AB fiber, a similar process is followed. However, instead of a single Gaussian, an Airy function is
used (to account for the previous and following FP peak in the fitting process):

.. math::

    F_{airy} = A\left( 0.5 \left(1 + \frac{2\pi(x-x_0)}{w} \right) \right)^{\beta} + DC

where F is the modeled flux of the FP, A is the amplitude of the FP peak, :math:`x_0` is the central position of the
FP peak, w is the period of the FP in pixel space, :math:`\beta` is the shape factor of the FP peak and DC is a
constant offset. Once we have found all HC and FP lines in the AB fiber we calculate the wavelength solution.

The accurate wavelength solution for reference night is then found through the following steps:

    - From FP peak spacing within each order, derive an effective cavity length per order.
    - Fit the chromatic dependency of the cavity with a 5th order polynomial and keep that cavity in a reference file;
      through the life of the instrument, we will assume that cavity changes are achromatic relative to this polynomial.
    - From the chromatic cavity solution, we find the FP order value of each peak, typically numbering from ~600 to
      ~24500 respectively at long and short wavelength ends of the SPIRou domain.
    - From the peak numbering, which is known to be an integer, we can refine the wavelength solution within each
      order. This solution is kept as a reference wavelength solution.

The finding of the fiber AB HC and FP lines and the calculation of the wavelength solution is repeated multiple times
(in an iterative process). We essentially forget the locations of the HC and FP lines and re-find them as if we
hadn't found them before, only this time instead of the initial guess wavelength solution we use the previous
iteration's calculated solution and the previous iterations calculated cavity width fit as a starting point.

Finally, after three iterations, which is sufficient to converge to floating point accuracy, we re-find the HC and FP
lines for the AB fiber one last time using the final reference wavelength solution and final cavity width fit. We also
make an estimate of the resolution, splitting the detector into a grid of 3$\times$3 and using all HC lines in each
sector to estimate the line profile and thus the resolution of each sector. We then process each fiber (A, B, and C)
in a similar manner to the AB fiber (finding HC and FP lines from the extracted images and calculating the wavelength
solution) the only difference being we do not fit the cavity width nor do we fit the chromatic term; we force the
coefficients to be the ones found with the AB fiber.

For quality control purposes we calculate an FP binary mask using the cavity width fit and use this to perform a
cross-correlation function between the mask and the extracted FP for all fibers (AB, A, B, and C). We use the
cross-correlation function to measure the shift of the wavelength solutions measured in fiber AB compared to
fibers A, B, and C and confirm that this is less than 2 :math:`ms^{-1}`. As a second quality control, we match FP
lines (found previously) between the fibers and directly calculate the difference in velocity between these lines as
a second metric on the radial velocity shift between the fibers' wavelength solutions. Note that typically for the
reference night the value of these quality control metrics is around 10-20 :math:`cms^{-1}` between fibers
(i.e. :math:`AB-A`, :math:`AB-B`, :math:`AB-C`).

The reference wavelength solution file (`REFWAVE`) for each fiber, a cavity fit file, and a table of all HC and FP
lines found are then saved to the calibration database for use throughout APERO. A resolution map is also saved.
The `HC_HC` and `FP_FP` extracted files have their headers updated with the reference wavelength solution.
