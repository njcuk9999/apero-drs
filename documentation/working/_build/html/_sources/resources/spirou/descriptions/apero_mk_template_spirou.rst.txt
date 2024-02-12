================================================
Template generation (mktemp)
================================================

Templates for each astrophysical object are created simply by shifting all observations (in BERV) from their nightly
wavelength solution to the reference wavelength solution. This effectively creates a cube (In practice some
astrophysical objects have thousands of observations so a median is done in parts, splitting into bins in time,
combining the median cubes together to produce one final cube, to reduce computational requirements) of observations
for specific astrophysical objects which are then normalized (per observation) by the median for each order.

We pass a low-pass filter over this cube and then the cube is reduced to a single 2D (extracted and
telluric-corrected) spectrum by taking a median in the time dimension (across observations). The same process is done
for the 1D spectrum. The 2D templates are copied to the telluric database for use in the rest of the telluric
cleaning process (the second iterations of mktellu and ftellu), except if the BERV change throughout all
epochs is below 8 :math:`km s^{-1}`. The 1D spectrum is saved as a useful output of APERO.