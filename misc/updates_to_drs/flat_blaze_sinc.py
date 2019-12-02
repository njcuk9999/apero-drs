from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def sinc(x, amp, period, lin_center, quad_scale, slope, peak_cut=0.0):
    # function to be ajdusted to the blaze.
    # y = A * (  sin(x)/x  )^2 * (1+C*x)
    #
    # where X is a position along the x pixel axis. This assumes
    # that the blaze follows an airy pattern and that there may be a slope
    # to the spectral energy distribution.
    #

    # Transform the x expressed in pixels into a streched version
    # expressed in phase. The quadratic terms allows for a variation of
    # dispersion along the other
    xp = 2 * np.pi * (((x - lin_center) + quad_scale * (
                x - lin_center) ** 2) / period)

    # this avoids a division by zero
    if np.min(np.abs(xp) / period) < 1e-9:
        small_x = (np.abs(xp) / period) < 1e-9
        xp[small_x] = 1e-9

    yy = amp * (np.sin(xp) / xp) ** 2

    # if we set a peak_cut threshold then values below that fraction of the
    # peak sinc value are set to NaN.
    if peak_cut != 0:
        yy[yy < (peak_cut * amp)] = np.nan

    # multiplicative slope in the SED
    yy *= (1 + slope * (x - lin_center))

    return yy


# 2279063f_pp_e2ds_AB.fits
# 2295066f_pp_e2ds_AB.fits
# 2334232f_pp_e2ds_AB.fits
sp = fits.getdata('2334232f_pp_e2ds_AB.fits')

# threshold, expressed in peak below which the blaze is set to NaN
peak_cut = 0.3

# rejection threshold for the blaze sinc fit
Nsigfit = 4.0

doplot = True

flat = np.array(sp)

# x pixel value of the spectrum
xpix = np.arange(sp.shape[1])

for iord in range(sp.shape[0]):

    y = sp[iord, :]

    # region over which we will fit
    keep = np.isfinite(y)

    # guess of peak value, we do not take the max as there may be a hot/bad pix
    # in the order
    p95 = np.nanpercentile(y, 95)

    # how many points above 50% of peak value?
    # The period should be a factor of about 2.0 more than the domain
    # that is above the 5th percentile
    n50 = np.sum(y[np.isfinite(y)] > p95 / 2.0)

    # median position of points above 95th percentile
    pospeak = np.median(xpix[y > p95])

    # starting point for the fit to the blaze sinc model
    # we start with :
    #
    # peak value is == 95th percentile
    # period of sinc is == 2x the width of pixels above 50% of the peak
    # the peak position is == the median x value of pixels above 95th percent.
    # no quadratic term
    # no SED slope
    p0 = [p95, n50 * 2.0, pospeak, 0, 0]

    # we set reasonable bounds
    bounds = ((p95 * .5, n50 * .1, pospeak - 200, -1e-4, -1e-2),
              (p95 * 1.5, n50 * 10, pospeak + 200, 1e-4, 1e-2))

    # we optimize over pixels that are not NaN
    popt, pcov = curve_fit(sinc, xpix[keep], y[keep], p0=p0, bounds=bounds)

    for ite in range(2):
        # we construct a model with the peak cut-off
        model = sinc(xpix, popt[0], popt[1], popt[2], popt[3], popt[4],
                     peak_cut=peak_cut)

        # we find residuals to the fit and normalize them
        residual = (y - model)
        residual /= np.nanmedian(np.abs(residual))

        # we keep only non-NaN model points (i.e. above peak_cut) and
        # within +- Nsigfit dispersion elements
        keep = (np.abs(residual) < Nsigfit) & np.isfinite(model)
        popt, pcov = curve_fit(sinc, xpix[keep], y[keep], p0=p0, bounds=bounds)

    print(popt)
    if doplot == True:
        model = sinc(xpix, popt[0], popt[1], popt[2], popt[3], popt[4],
                     peak_cut=peak_cut)

        fig, ax = plt.subplots(nrows=2, ncols=1)
        ax[0].plot(xpix, y, '.', color='orange')
        ax[0].plot(xpix[keep], y[keep], 'g.')
        ax[0].plot(xpix, model, 'r-')
        ax[0].set(title=str(iord), xlim=[0, 4088])
        ax[1].plot(xpix, y / model, '.', color='orange')
        ax[1].plot(xpix[keep], y[keep] / model[keep], 'g.')
        ax[1].set(ylim=[.9, 1.1], xlim=[0, 4088])

        plt.show()
    flat[iord, :] /= model

    print(iord, np.nanstd(flat[iord, keep]))

fits.writeto('test.fits', flat, overwrite=True)
