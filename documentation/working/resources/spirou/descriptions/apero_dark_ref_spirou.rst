==================================
Dark reference calibration
==================================

As \spirou has no moving internal parts for increased stability, one cannot move the fiber out of view and
independently measure the detector's dark current. Thus dark frames are non-trivial to construct, as there are
two independent contributions to the `dark' image, one arising from the dark current of the science arrays and
the other from thermal emission. This problem is mainly seen in the $K$ band and is shared with any PRV spectrograph
for which the fiber thermal emission is commensurate with the per-pixel dark current.

The thermal background manifests itself as a very low-level contribution (typically 0.015 e-/s/pixel), well below
the typical target flux, but has a high flux tail of much brighter pixels. As the SPIRou science array has an
extremely stable temperature (sub-milli Kelvin), one expects the pixel dark current to be very stable. From all
preprocessed `DARK_DARK` files, across all nights, we select a subset of 100 `DARK_DARK` files, uniformly
distributed in time as much as possible using a sorting function. If there are less than 100 `DARK_DARK` files across
all available nights we use all files; this becomes our reference dark.

One could use this as the single step for dark correction, but a significant challenge arises. The fiber train is
always connected and the science array always sees the thermal emission from the fibers and the hermetic feedthrough
connecting the fibers to the cryostat. This thermal emission changes with the temperature of the fiber train and
moves, at the pixel level, on timescales of months to years following thermal cycles and maintenance of the instrument.
Applying a simple scaling of the dark current, including the thermal background from the fiber, would lead to
erroneous subtraction in science data, with sometimes an over subtraction of :math:`\sim2.4\,\mu m` flux, leading to
negative flux. We opt for a decoupling of the two contributions in the data calibration.
We construct a high-frequency median dark current, which contains pixel-to-pixel detector contributions and
low-frequency components from the thermal background of the fiber train. The high-frequency component can be
scaled with integration time while the low-frequency one needs to be adjusted.
This high-pass reference dark image is then saved to the calibration database for use throughout APERO.