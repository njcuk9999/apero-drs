import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline


def wave2wave(e2ds_data, wave1, wave2):
    # transform e2ds data from one wavelength grid to another.

    for iord in range(49):
        keep = np.isfinite(e2ds_data[iord])
        spl = InterpolatedUnivariateSpline(wave1[iord][keep],e2ds_data[iord][keep],k=3, ext=1)
        e2ds_data[iord][keep] = spl(wave2[iord][keep])

    return e2ds_data
