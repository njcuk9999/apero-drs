================================================
Post processing
================================================

The final data products that go to PIs are composite files of many of the outputs of APERO. For SPIRou, these are
sent to the Canadian Data Astronomy Center (CADC, accessible from https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) but
are only produced for science targets and hot stars (i.e., `OBJ_FP`, `OBJ_DARK`, `POLAR_FP`, and `POLAR_DARK`) and not
for calibrations by default. There are currently five post-processing files each linked to a single odometer code.
These are the 2D extracted output (e.fits), the 2D telluric corrected output (t.fits), the 1D output (s.fits), the
velocity output (v.fits), and the polarimetric outputs (p.fits). A summary of the CADC output files is available in
table below.

.. list-table:: Science ready outputs sent to the Canadian Data Astronomy Center, CADC).
    :widths: 10, 90
    :header-rows: 1

    * - File
      - Description
    * - (odometer)e.fits
      - 2D extracted spectrum for fibers AB, A, B, C, wavelength solution, and blaze
    * - (odometer)s.fits
      -  1D extracted spectrum for fibers AB, A, B, C, and telluric corrected spectrum if available
    * - (odometer)t.fits
      - 2D telluric corrected spectrum for fiber AB, A, B, wavelength solution, blaze, and reconstructed atmospheric transmission
    * - (odometer)v.fits
      - combined and per order CCFs for fitting the radial velocity of the star
    * - (odometer)p.fits
      - polarimetric products (Polarimetric flux, Stokes I, Null vectors, wavelength solution, and blaze)


2D extraction product (e.fits)
---------------------------------

These are the combined extracted products. All extensions are two-dimensional spectra of size :math:`4088\times49`.
The e.fits file contains the extracted spectrum for each order for each fiber and the matching wavelength and blaze
solution for each order and each fiber. The files are identified with a single odometer generated at the time of
observation followed by an e.fits suffix.


2D telluric corrected product (t.fits)
----------------------------------------

These are the combined telluric-corrected products. All extensions are two-dimensional spectra of size
:math:`4088\times49`. The t.fits file contains the telluric corrected spectrum for each order and each fiber and the
matching wavelength and blaze solution for each order and each fiber. The files are identified with a single odometer
code at the time of observation followed by a t.fits suffix.

1D extraction and 1D telluric corrected product (s.fits)
----------------------------------------------------------

These are the combined 1D spectrum products and consist of two tables. The two tables consist of the 1D spectrum in 1.
velocity units and 2. wavelength units. They each consist of the following columns: the wavelength solution, the
extracted flux in AB, A, B, and C, the telluric corrected flux in fibers AB, A, and B (if available), and the
associated uncertainties for each flux column.  The files are identified with a single odometer code at the time of
observation followed by an s.fits suffix.

Velocity product (v.fits)
-----------------------------

The velocity products are packaged into the v.fits file. Currently, only the CCF values are added as an extension as
the LBL products are computed separately. The CCF file consists of the CCF generated for each radial velocity element
(by default this is between :math:`\pm 300 ms^{-1}` in steps of 0.5 :math:`m s^{-1}`) for each order and a combined
CCF for the same radial velocity elements. The files are identified with a single odometer code at the time of
observation followed by a v.fits suffix. Once the LBL module is able to be used with APERO it will add an extension
to the v.fits (the rdb extension described in the `LBL documentation <https://lbl.exoplanets.ca>`_.).

Polarimetric product (p.fits)
--------------------------------

These are the combined polarimetric products. The p.fits file consists of eight image extensions and three table
extensions. The first two tables are the 1D representations of the 2D polarimetric products (listed in the extensions
above) in 1. velocity units and 2. wavelength units. They each consist of the following columns: the wavelength
solution, the polarimetric flux, the Stokes I flux, the Null 1 and 2 fluxes, and the associated uncertainties on each
flux column. The third table lists the configuration parameters used to run APERO. Although polarimetric products
are the combination of at least 4 odometer codes, files are associated with a single odometer code (the first in the
sequence at the time of observation) followed by a p.fits suffix.

