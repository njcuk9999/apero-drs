import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline


# spectrum --> flux in the reference frame of the file wave1
# wave1 --> initial wavelength grid
# wave2 --> destination wavelength grid
# retruns spectrum resampled to wave2

def wave2wave(spectrum, wave1, wave2):
    # size of array, assumes wave1, wave2 and spectrum have same shape
    sz = np.shape(spectrum)

    output_spectrum = np.zeros(sz) + np.nan

    # looping through the orders to shift them from one grid to the other
    for iord in range(sz[0]):
        # only interpolate valid pixels
        g = np.isfinite(spectrum[iord, :])
        print(np.mean(g))
        # if no valid pixel, thn skip order
        if np.sum(g) != 0:
            # spline the spectrum
            spline = IUVSpline(wave1[iord, g], spectrum[iord, g], k=5, ext=1)

            # keep track of pixels affected by NaNs
            splinemask = IUVSpline(wave1[iord, :], g, k=5, ext=1)

            # spline the input onto the output
            output_spectrum[iord, :] = spline(wave2[iord, :])

            # find which pixels are not NaNs
            mask = splinemask(wave2[iord, :])

            # set to NaN pixels outside of domain
            bad = (output_spectrum[iord, :] == 0)
            output_spectrum[iord, bad] = np.nan

            # affected by a NaN value
            # normally we would use only pixels ==1, but we get values
            # that are not exactly one due to the interpolation scheme.
            # We just set that >99.9% of the
            # flux comes from valid pixels
            bad = (mask <= 0.999)
            # mask pixels affected by nan
            output_spectrum[iord, bad] = np.nan

    return output_spectrum
