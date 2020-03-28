from astropy.io import fits
from astropy.table import Table
from astropy import units as uu
import numpy as np
import warnings
import sys
import os
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import curve_fit
from scipy.stats import chisquare
import matplotlib.pyplot as plt


# =============================================================================
# Define variables
# =============================================================================
# if all files copied to same directory set these to ''
# WORKSPACE1 = ''
# WORKSPACE2 = ''
# these files are on cook@nb19
WORKSPACE1 = '/scratch3/rali/spirou/mini_data/reduced/2019-04-20/'
WORKSPACE2 = '/scratch3/rali/drs/apero-drs/apero/data/spirou/ccf/'
# build file paths
IN_FILE = os.path.join(WORKSPACE1, '2400515o_pp_e2dsff_tcorr_AB.fits')
BLAZE_FILE = os.path.join(WORKSPACE1, '2019-04-20_2400404f_pp_blaze_AB.fits')
MASK_FILE = os.path.join(WORKSPACE2, 'masque_sept18_andres_trans50.mas')
WAVE_FILE = os.path.join(WORKSPACE1,
                         '2019-04-19_2400388c_pp_e2dsff_AB_wave_night_AB.fits')
# variables (from constants)
MASK_WIDTH = 1.7
MASK_MIN_WEIGHT = 0.0
MASK_COLS = ['ll_mask_s', 'll_mask_e', 'w_mask']
CCF_STEP = 0.5
CCF_WIDTH = 300
CCF_RV_NULL = -9999.99
CCF_N_ORD_MAX = 48
BLAZE_NORM_PERCENTILE = 90
BLAZE_THRESHOLD = 0.3
FIT_TYPE = 1
IMAGE_PIXEL_SIZE = 2.28
# constants
SPEED_OF_LIGHT = 299792.458


# =============================================================================
# Define functions
# =============================================================================
def read_mask():
    table = Table.read(MASK_FILE, format='ascii')
    # get column names
    oldcols = list(table.colnames)
    # rename columns
    for c_it, col in enumerate(MASK_COLS):
        table[oldcols[c_it]].name = col
    # return table
    return table


def get_mask(table, mask_width, mask_min, mask_units='nm'):
    ll_mask_e = np.array(table['ll_mask_e']).astype(float)
    ll_mask_s = np.array(table['ll_mask_s']).astype(float)
    ll_mask_d = ll_mask_e - ll_mask_s
    ll_mask_ctr = ll_mask_s + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c
    if mask_width > 0:
        ll_mask_d = mask_width * ll_mask_s / SPEED_OF_LIGHT
    # make w_mask an array
    w_mask = np.array(table['w_mask']).astype(float)
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    if mask_min < 1.0:
        mask = w_mask > mask_min
        ll_mask_d = ll_mask_d[mask]
        ll_mask_ctr = ll_mask_ctr[mask]
        w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    else:
        w_mask = np.ones(len(ll_mask_d))
    # ----------------------------------------------------------------------
    # deal with the units of ll_mask_d and ll_mask_ctr
    # must be returned in nanometers
    # ----------------------------------------------------------------------
    # get unit object from mask units string
    unit = getattr(uu, mask_units)
    # add units
    ll_mask_d = ll_mask_d * unit
    ll_mask_ctr = ll_mask_ctr * unit
    # convert to nanometers
    ll_mask_d = ll_mask_d.to(uu.nm).value
    ll_mask_ctr = ll_mask_ctr.to(uu.nm).value
    # ----------------------------------------------------------------------
    # return the size of each pixel, the central point of each pixel
    #    and the weight mask
    return ll_mask_d, ll_mask_ctr, w_mask


def relativistic_waveshift(dv, units='km/s'):
    """
    Relativistic offset in wavelength

    default is dv in km/s

    :param dv: float or numpy array, the dv values
    :param units: string or astropy units, the units of dv
    :return:
    """
    # get c in correct units
    # noinspection PyUnresolvedReferences
    if units == 'km/s' or units == uu.km/uu.s:
        c = SPEED_OF_LIGHT
    # noinspection PyUnresolvedReferences
    elif units == 'm/s' or units == uu.m/uu.s:
        c = SPEED_OF_LIGHT * 1000
    else:
        raise ValueError("Wrong units for dv ({0})".format(units))
    # work out correction
    corrv = np.sqrt((1 + dv / c) / (1 - dv / c))
    # return correction
    return corrv


def iuv_spline(x, y, **kwargs):
    # check whether weights are set
    w = kwargs.get('w', None)
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)

    if np.sum(~nanmask) < 2:
        y = np.zeros_like(x)
    elif np.sum(nanmask) == 0:
        pass
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


def fit_ccf(rv, ccf, fit_type):
    """
    Fit the CCF to a guassian function

    :param rv: numpy array (1D), the radial velocities for the line
    :param ccf: numpy array (1D), the CCF values for the line
    :param fit_type: int, if "0" then we have an absorption line
                          if "1" then we have an emission line

    :return result: numpy array (1D), the fit parameters in the
                    following order:

                [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :return ccf_fit: numpy array (1D), the fit values, i.e. the gaussian values
                     for the fit parameters in "result"
    """
    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        print('\tERROR: RV AND CCF SHAPE DO NOT MATCH')
        sys.exit()

    # deal with all nans
    if np.sum(np.isnan(ccf)) == len(ccf):
        # log warning about all NaN ccf
        print('\tWARNING: NANS in CCF')
        # return NaNs
        result = np.zeros(4) * np.nan
        ccf_fit = np.zeros_like(ccf) * np.nan
        return result, ccf_fit

    # get constants
    max_ccf, min_ccf = np.nanmax(ccf), np.nanmin(ccf)
    argmin, argmax = np.nanargmin(ccf), np.nanargmax(ccf)
    diff = max_ccf - min_ccf
    rvdiff = rv[1] - rv[0]
    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        if np.nanmax(ccf) != 0:
            a = np.array([-diff / max_ccf, rv[argmin], 4 * rvdiff, 0])
        else:
            a = np.zeros(4)
    # else (fit_type == 1) then we have emission lines
    else:
        a = np.array([diff / max_ccf, rv[argmax], 4 * rvdiff, 1])
    # normalise y
    y = ccf / max_ccf - 1 + fit_type
    # x is just the RVs
    x = rv
    # uniform weights
    w = np.ones(len(ccf))
    # get gaussian fit
    nanmask = np.isfinite(y)
    y[~nanmask] = 0.0
    # fit the gaussian
    try:
        with warnings.catch_warnings(record=True) as _:
            result, fit = fitgaussian(x, y, weights=w, guess=a)
    except RuntimeError:
        result = np.repeat(np.nan, 4)
        fit = np.repeat(np.nan, len(x))

    # scale the ccf
    ccf_fit = (fit + 1 - fit_type) * max_ccf

    # return the best guess and the gaussian fit
    return result, ccf_fit


def gauss_function(x, a, x0, sigma, dc):
    """
    A standard 1D gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def fitgaussian(x, y, weights=None, guess=None, return_fit=True,
                return_uncertainties=False):
    """
    Fit a single gaussian to the data "y" at positions "x", points can be
    weighted by "weights" and an initial guess for the gaussian parameters

    :param x: numpy array (1D), the x values for the gaussian
    :param y: numpy array (1D), the y values for the gaussian
    :param weights: numpy array (1D), the weights for each y value
    :param guess: list of floats, the initial guess for the guassian fit
                  parameters in the following order:

                  [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :param return_fit: bool, if True also calculates the fit values for x
                       i.e. yfit = gauss_function(x, *pfit)

    :param return_uncertainties: bool, if True also calculates the uncertainties
                                 based on the covariance matrix (pcov)
                                 uncertainties = np.sqrt(np.diag(pcov))

    :return pfit: numpy array (1D), the fit parameters in the
                  following order:

                [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :return yfit: numpy array (1D), the fit y values, i.e. the gaussian values
                  for the fit parameters, only returned if return_fit = True

    """

    # if we don't have weights set them to be all equally weighted
    if weights is None:
        weights = np.ones(len(x))
    weights = 1.0 / weights
    # if we aren't provided a guess, make one
    if guess is None:
        guess = [np.nanmax(y), np.nanmean(y), np.nanstd(y), 0]
    # calculate the fit using curve_fit to the function "gauss_function"
    with warnings.catch_warnings(record=True) as _:
        pfit, pcov = curve_fit(gauss_function, x, y, p0=guess, sigma=weights,
                               absolute_sigma=True)
    if return_fit and return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit, yfit and efit
        return pfit, yfit, efit
    # if just return fit
    elif return_fit:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # return pfit and yfit
        return pfit, yfit
    # if return uncertainties
    elif return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit and efit
        return pfit, efit
    # else just return the pfit
    else:
        # return pfit
        return pfit


def fwhm(sigma=1.0):
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)

    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # get input telluric corrected file and header
    image, header = fits.getdata(IN_FILE, header=True)
    blaze = fits.getdata(BLAZE_FILE)
    masktable = read_mask()
    wave = fits.getdata(WAVE_FILE)
    # --------------------------------------------------------------------------
    # get berv from header
    berv = header['BERV']
    # --------------------------------------------------------------------------
    # get rv from header (or set to zero)
    if 'OBJRV' in header:
        targetrv = header['OBJRV']
        if np.isnan(targetrv) or targetrv == CCF_RV_NULL:
            targetrv = 0.0
    else:
        targetrv = 0.0
    # --------------------------------------------------------------------------
    # get mask centers, and weights
    _, mask_centers, mask_weights = get_mask(masktable, MASK_WIDTH,
                                             MASK_MIN_WEIGHT)
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # START contents of velocity.general.ccf_calculation
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # get rvmin and rvmax
    rvmin = targetrv - CCF_WIDTH
    rvmax = targetrv + CCF_WIDTH + CCF_STEP
    # get the dimensions
    nbo, nbpix = image.shape
    # create a rv ccf range
    rv_ccf = np.arange(rvmin, rvmax, CCF_STEP)
    # storage of the ccf
    ccf_all = []
    ccf_noise_all = []
    ccf_all_fit = []
    ccf_all_results = []
    ccf_lines = []
    ccf_all_snr = []
    ccf_norm_all = []

    # ----------------------------------------------------------------------
    # loop around the orders
    for order_num in range(nbo):
        # log the process
        print('Order {0}'.format(order_num))
        # ------------------------------------------------------------------
        # get this orders values
        wa_ord = np.array(wave[order_num])
        sp_ord = np.array(image[order_num])
        bl_ord = np.array(blaze[order_num])
        # mask on the blaze
        with warnings.catch_warnings(record=True) as _:
            blazemask = bl_ord > BLAZE_THRESHOLD
        # get order mask centers and mask weights
        min_ord_wav = np.nanmin(wa_ord[blazemask])
        max_ord_wav = np.nanmax(wa_ord[blazemask])
        # adjust for rv shifts
        min_ord_wav = min_ord_wav * (1 + rvmin / SPEED_OF_LIGHT)
        max_ord_wav = max_ord_wav * (1 + rvmax / SPEED_OF_LIGHT)
        # mask the ccf mask by the order length
        mask_wave_mask = (mask_centers > min_ord_wav)
        mask_wave_mask &= (mask_centers < max_ord_wav)
        omask_centers = mask_centers[mask_wave_mask]
        omask_weights = mask_weights[mask_wave_mask]
        # normalize per-ord blaze to its peak value
        # this gets rid of the calibration lamp SED
        bl_ord /= np.nanpercentile(bl_ord, BLAZE_NORM_PERCENTILE)
        # ------------------------------------------------------------------
        # find any places in spectrum or blaze where pixel is NaN
        nanmask = np.isnan(sp_ord) | np.isnan(bl_ord)
        # ------------------------------------------------------------------
        # deal with no valid lines
        if np.sum(mask_wave_mask) == 0:
            print('\tWARNING: MASK INVALID FOR WAVELENGTH RANGE --> NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # deal with all nan
        if np.sum(nanmask) == nbpix:
            print('\tWARNING: ALL SP OR BLZ NAN --> NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # set the spectrum or blaze NaN pixels to zero (dealt with by divide)
        sp_ord[nanmask] = 0
        bl_ord[nanmask] = 0
        # ------------------------------------------------------------------
        # spline the spectrum and the blaze
        # TODO make it tidy with the blaze
        spline_sp = iuv_spline(wa_ord, sp_ord, k=5, ext=1)
        spline_bl = iuv_spline(wa_ord, bl_ord, k=5, ext=1)
        # ------------------------------------------------------------------
        # set up the ccf for this order
        ccf_ord = np.zeros_like(rv_ccf)
        # ------------------------------------------------------------------
        # get the wavelength shift (dv) in relativistic way
        wave_shifts = relativistic_waveshift(rv_ccf - berv)
        # ------------------------------------------------------------------
        # set number of valid lines used to zero
        numlines = 0
        # loop around the rvs and calculate the CCF at this point
        part3 = spline_bl(omask_centers) * omask_weights
        for rv_element in range(len(rv_ccf)):
            wave_tmp = omask_centers * wave_shifts[rv_element]
            part1 = spline_sp(wave_tmp) * omask_weights
            part2 = spline_bl(wave_tmp) * omask_weights
            numlines = np.sum(spline_bl(wave_tmp) != 0)
            # CCF is the division of the sums
            with warnings.catch_warnings(record=True) as _:
                ccf_ord[rv_element] = np.nansum((part1 / part2) * part3)
        # ------------------------------------------------------------------
        # deal with NaNs in ccf
        if np.sum(np.isnan(ccf_ord)) > 0:
            # log all NaN
            print('WARNING: CCF is NAN')
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # TODO -- check that its ok to remove the normalization
        # TODO -- this should preserve the stellar flux weighting
        # normalise each orders CCF to median
        # TODO -- keep track of the norm factor, write a look-up table
        # TODO -- with reasonable mid-M values and use these values for
        # TODO -- all stars. At some point, have a temperature-dependent
        # TODO -- LUT of weights.
        ccf_norm = np.nanmedian(ccf_ord)
        # ccf_ord = ccf_ord / ccf_norm
        # ------------------------------------------------------------------
        # fit the CCF with a gaussian
        fargs = [rv_ccf, ccf_ord, FIT_TYPE]
        ccf_coeffs_ord, ccf_fit_ord = fit_ccf(*fargs)
        # ------------------------------------------------------------------
        # calculate the residuals of the ccf fit
        res = ccf_ord - ccf_fit_ord
        # calculate the CCF noise per order
        ccf_noise = np.array(res)
        # calculate the snr for this order
        ccf_snr = np.abs(ccf_coeffs_ord[0] / np.nanmedian(np.abs(ccf_noise)))
        # ------------------------------------------------------------------
        # append ccf to storage
        ccf_all.append(ccf_ord)
        ccf_all_fit.append(ccf_fit_ord)
        ccf_all_results.append(ccf_coeffs_ord)
        ccf_noise_all.append(ccf_noise)
        ccf_lines.append(numlines)
        ccf_all_snr.append(ccf_snr)
        ccf_norm_all.append(ccf_norm)
    # store outputs in param dict
    props = dict()
    props['RV_CCF'] = rv_ccf
    props['CCF'] = np.array(ccf_all)
    props['CCF_LINES'] = np.array(ccf_lines)
    props['TOT_LINE'] = np.sum(ccf_lines)
    props['CCF_NOISE'] = np.array(ccf_noise_all)
    props['CCF_SNR'] = np.array(ccf_all_snr)
    props['CCF_FIT'] = np.array(ccf_all_fit)
    props['CCF_FIT_COEFFS'] = np.array(ccf_all_results)
    props['CCF_NORM'] = np.array(ccf_norm_all)
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # END contents of velocity.general.ccf_calculation
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Calculate the mean CCF
    # --------------------------------------------------------------------------
    # get the average ccf
    mean_ccf = np.nanmean(props['CCF'][: CCF_N_ORD_MAX], axis=0)
    # get the fit for the normalized average ccf
    mean_ccf_coeffs, mean_ccf_fit = fit_ccf(props['RV_CCF'],
                                            mean_ccf, fit_type=FIT_TYPE)
    # get the RV value from the normalised average ccf fit center location
    ccf_rv = float(mean_ccf_coeffs[1])
    # get the contrast (ccf fit amplitude)
    ccf_contrast = np.abs(100 * mean_ccf_coeffs[0])
    # get the FWHM value
    ccf_fwhm = mean_ccf_coeffs[2] * fwhm()
    # --------------------------------------------------------------------------
    #  CCF_NOISE uncertainty
    ccf_noise_tot = np.sqrt(np.nanmean(props['CCF_NOISE'] ** 2, axis=0))
    # Calculate the slope of the CCF
    average_ccf_diff = (mean_ccf[2:] - mean_ccf[:-2])
    rv_ccf_diff = (props['RV_CCF'][2:] - props['RV_CCF'][:-2])
    ccf_slope = average_ccf_diff / rv_ccf_diff
    # Calculate the CCF oversampling
    ccf_oversamp = IMAGE_PIXEL_SIZE / CCF_STEP
    # create a list of indices based on the oversample grid size
    flist = np.arange(np.round(len(ccf_slope) / ccf_oversamp))
    indexlist = np.array(flist * ccf_oversamp, dtype=int)
    # we only want the unique pixels (not oversampled)
    indexlist = np.unique(indexlist)
    # get the rv noise from the sum of pixels for those points that are
    #     not oversampled
    keep_ccf_slope = ccf_slope[indexlist]
    keep_ccf_noise = ccf_noise_tot[1:-1][indexlist]
    rv_noise = np.nansum(keep_ccf_slope ** 2 / keep_ccf_noise ** 2) ** (-0.5)
    # --------------------------------------------------------------------------
    # log the stats
    wargs = [ccf_contrast, float(mean_ccf_coeffs[1]), rv_noise, ccf_fwhm]
    print('MEAN CCF:')
    print('\tCorrelation: C={0:1f}[%] RV={1:.5f}[km/s] RV_NOISE={2:.5f}[km/s] '
          'FWHM={3:.4f}[km/s]'.format(*wargs))
    # --------------------------------------------------------------------------
    # add to output array
    props['MEAN_CCF'] = mean_ccf
    props['MEAN_RV'] = ccf_rv
    props['MEAN_CONTRAST'] = ccf_contrast
    props['MEAN_FWHM'] = ccf_fwhm
    props['MEAN_CCF_RES'] = mean_ccf_coeffs
    props['MEAN_CCF_FIT'] = mean_ccf_fit
    props['MEAN_RV_NOISE'] = rv_noise
    # --------------------------------------------------------------------------
    # add constants to props
    props['CCF_MASK'] = os.path.basename(MASK_FILE)
    props['CCF_STEP'] = CCF_STEP
    props['CCF_WIDTH'] = CCF_WIDTH
    props['TARGET_RV'] = targetrv
    props['MASK_MIN'] = MASK_MIN_WEIGHT
    props['MASK_WIDTH'] = MASK_WIDTH

    # --------------------------------------------------------------------------
    # plot grid of ccfs
    plt.close()
    fig1, frames = plt.subplots(ncols=7, nrows=7, figsize=(30, 30))
    for order_num in range(nbo):
        i, j = order_num // 7, order_num % 7
        frames[i][j].plot(props['RV_CCF'], props['CCF'][order_num], color='b')
        frames[i][j].plot(props['RV_CCF'], props['CCF_FIT'][order_num],
                          color='r',)
        frames[i][j].text(0.5, 0.8, 'Order {0}'.format(order_num),
                          horizontalalignment='center',
                          transform=frames[i][j].transAxes)

    fig1.subplots_adjust(wspace=0.2, hspace=0.2, top=0.95, bottom=0.05,
                         left=0.05, right=0.95)

    # plot mean ccf and fit
    fig2, frame = plt.subplots(ncols=1, nrows=1)
    frame.plot(props['RV_CCF'], props['MEAN_CCF'], color='b', marker='+',
               ls='None')
    frame.plot(props['RV_CCF'], props['MEAN_CCF_FIT'], color='r')
    frame.set_title('Mean CCF   RV = {0} km/s'.format(props['MEAN_RV']))

    # show plots
    plt.show()
    plt.close()


# ==============================================================================
# End of code
# ==============================================================================