import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import os
from astropy.table import Table
from apero.core.math import fit_gauss_with_slope
from scipy.interpolate import InterpolatedUnivariateSpline
from apero.core.math import linear_minimization as lin_mini
from apero.core import math as mp


def get_lines(file):
    # input : file name for an HC or FP e2ds

    outname = '_lines.'.join(file.split('.'))

    # min SNR to consider the line
    nsig_min = 15

    # minimum distance to the edge of the array to consider a line
    wmax = 20

    # +- value in pixel for the box size around each HC line to perform fit
    width_hc_fit = 5

    if os.path.isfile(outname):
        # if the fits table exists, we read it and return it
        return Table.read(outname)
    else:
        # read master wavelength grid
        master_wave_file = '/Users/eartigau/apero/data/calibDB/MASTER_WAVE.fits'
        master_wavelength = fits.getdata(master_wave_file)
        sz = master_wavelength.shape

        # read data from file
        sp, hdr = fits.getdata(file, header=True)

        # get DPR type for fiber
        if 'C' in hdr['FIBER']:
            DPRTYPE = (hdr['DPRTYPE'].split('_'))[1]
        else:
            DPRTYPE = (hdr['DPRTYPE'].split('_'))[0]

        # HC, reda the UNe line list and assumes the lines will be
        # within 1 pix of the position
        # predicted from catalog
        if DPRTYPE == 'HCONE':
            # catalog
            tbl = Table.read(
                '/Users/eartigau/apero-drs/apero/data/spirou/calib/catalogue_UNe.dat',
                format='ascii')

            list_waves = []
            list_orders = []
            list_pixels = []

            # get lines that fall within each diffraction ordre
            index = np.arange(sz[1])
            for iord in range(sz[0]):
                # we have a wavelength value, we get an approximate pixel value
                # by fitting wavelength to pixel
                order_wavelength = master_wavelength[iord, :]
                fit_reverse = np.polyfit(order_wavelength, index, 5)

                # we find lines within the ordre
                g = (tbl['wavelength'] > np.min(order_wavelength))
                g &= (tbl['wavelength'] < np.max(order_wavelength))

                # we chech that there's at least 1 line and append
                # our line lists
                if np.sum(g) != 0:
                    list_waves += list(tbl['wavelength'][g])
                    list_orders += list(np.zeros(np.sum(g), dtype=int) + iord)
                    list_pixels += list(np.polyval(fit_reverse,
                                                   tbl['wavelength'][g]))

            # make line lists np arrays
            list_waves = np.array(list_waves)
            list_orders = np.array(list_orders)
            list_pixels = np.array(list_pixels)

            # keep lines that are not too close to image edge
            keep = (list_pixels > wmax) & (list_pixels < (sz[1] - wmax))
            list_waves = list_waves[keep]
            list_orders = list_orders[keep]
            list_pixels = list_pixels[keep]

        if DPRTYPE == 'FP':
            # read the cavity length table
            tbl = Table.read(
                '/Users/eartigau/apero-drs/apero/data/spirou/calib/cavity_length.dat',
                format='ascii')

            cavity_length_poly = np.array(tbl['WAVE2LENGTH_COEFF'])

            # range of N FP peaks
            nth_peak = np.arange(9000, 30000)

            # get wavelength centers
            wave0 = np.ones_like(nth_peak, dtype=float)
            # this is just to start the inversion of the polynomial relation
            wave0 *= np.nanmean(master_wavelength)

            # need a few iteration to invert polynomial relations
            for ite in range(4):
                wave0 = np.polyval(cavity_length_poly[::-1],
                                   wave0) * 2 / nth_peak

            # keep likes within the master_wavelength domain
            keep = (wave0 > np.min(master_wavelength))
            keep &= (wave0 < np.max(master_wavelength))

            wave0 = wave0[keep]
            wave0.sort()

            list_waves = []
            list_orders = []
            list_pixels = []
            list_wfit = []

            # same as for HCs, construct list of relevant lines per order
            index = np.arange(sz[1])
            for iord in range(sz[0]):
                order_wavelength = master_wavelength[iord, :]
                fit_reverse = np.polyfit(order_wavelength, index, 5)

                g = (wave0 > np.min(order_wavelength))
                g &= (wave0 < np.max(order_wavelength))

                xpix = np.polyval(fit_reverse, wave0[g])
                wfit = np.polyval(np.polyfit(xpix[1:],
                                             xpix[1:] - xpix[:-1], 2), xpix)
                wfit = np.ceil(wfit / 2)

                if np.sum(g) != 0:
                    list_waves += list(wave0[g])
                    list_orders += list(np.zeros(np.sum(g), dtype=int) + iord)
                    list_pixels += list(np.polyval(fit_reverse, wave0[g]))
                    list_wfit += list(wfit)

            list_waves = np.array(list_waves)
            list_orders = np.array(list_orders)
            list_pixels = np.array(list_pixels)
            list_wfit = np.array(list_wfit, dtype=int)

            keep = (list_pixels > wmax) & (list_pixels < (sz[1] - wmax))
            list_waves = list_waves[keep]
            list_orders = list_orders[keep]
            list_pixels = list_pixels[keep]
            list_wfit = list_wfit[keep]

        # create table that will contain lines
        tbl = Table()
        # wavelength from catalog
        tbl['WAVELENGTH_REFERENCE'] = list_waves
        # wavelength determined from pixel value and wavelength
        # solution. To be updated in later codes
        tbl['WAVELENGTH_MEASURED'] = np.zeros_like(list_pixels)
        # guess pixel starting point
        tbl['PIXEL_REFERENCE'] = list_pixels
        # fitted pixel position of line
        tbl['PIXEL_MEASURED'] = np.zeros_like(list_pixels)
        # diffraction ordre
        tbl['ORDER'] = list_orders
        # width of the fit. Constant for HCs, variable for FPs

        if DPRTYPE == 'HCONE':
            tbl['WFIT'] = np.zeros_like(list_pixels, dtype=int)
            tbl['WFIT'][:] = width_hc_fit
        if DPRTYPE == 'FP':
            tbl['WFIT'] = list_wfit

        # e width of fitted line expressed in pixels
        tbl['EWIDTH_MEASURED'] = np.zeros_like(list_pixels)
        # line amplitude
        tbl['AMP_MEASURED'] = np.zeros_like(list_pixels)
        # snr of line
        tbl['NSIG'] = np.zeros_like(list_pixels) + np.nan

        # vectors that will be inputed in the table
        AMP_MEASURED = np.array(tbl['AMP_MEASURED'])
        PIXEL_MEASURED = np.array(tbl['PIXEL_MEASURED'])
        EWIDTH_MEASURED = np.array(tbl['EWIDTH_MEASURED'])
        NSIG = np.array(tbl['NSIG'])

        for iord in range(sz[0]):
            # fit a gaussian model on each line
            print('Order #{0} in {1}, DPRTYPE = {2}'.format(
                iord + 1, sz[0], DPRTYPE))
            order_sp = sp[iord, :]
            order_wavelength = master_wavelength[iord, :]

            g_ord = np.where(tbl['ORDER'] == iord)[0]
            order_tbl = tbl[g_ord]

            for i in range(len(order_tbl)):
                xpix = int(np.round(order_tbl['PIXEL_REFERENCE'][i]))
                wfit = int(np.round(order_tbl['WFIT'][i]))
                index = np.arange(xpix - wfit, xpix + wfit + 1)
                ypix = order_sp[index]

                if np.min(np.isfinite(ypix)) == True:
                    # a, x0, sigma, zp, slope
                    guess = [np.max(ypix) - np.min(ypix), xpix, 1, np.min(ypix),
                             0]

                    try:
                        popt, pcov, model = fit_gauss_with_slope(index,
                                                                 ypix,
                                                                 guess,
                                                                 return_fit=True)

                        rms = np.std(ypix - model)

                        if (np.abs(popt[1] - xpix) < 1) & (popt[2] < 2) & (
                                popt[2] > .5):
                            AMP_MEASURED[g_ord[i]] = popt[0]
                            PIXEL_MEASURED[g_ord[i]] = popt[1]
                            EWIDTH_MEASURED[g_ord[i]] = popt[2]
                            NSIG[g_ord[i]] = popt[0] / rms
                    except:
                        pass
        # update table
        tbl['AMP_MEASURED'] = AMP_MEASURED
        tbl['PIXEL_MEASURED'] = PIXEL_MEASURED
        tbl['EWIDTH_MEASURED'] = EWIDTH_MEASURED
        tbl['NSIG'] = NSIG

        # lines that are not at a high enough SNR are flagged as NaN
        # we do NOT remove these lines as we want all tables to have
        # exactly the same length
        keep = NSIG > nsig_min
        bad = ~keep
        tbl['NSIG'][bad] = np.nan
        tbl['PIXEL_MEASURED'][bad] = np.nan
        tbl['EWIDTH_MEASURED'][bad] = np.nan
        tbl['AMP_MEASURED'][bad] = np.nan
        tbl['WAVELENGTH_MEASURED'][bad] = np.nan

        # As a debug plot, we show line expected vs measured positions
        for iord in range(49):
            g = tbl['ORDER'] == iord
            dpix = tbl['PIXEL_MEASURED'] - tbl['PIXEL_REFERENCE']
            plt.plot(tbl['WAVELENGTH_REFERENCE'][g], (dpix)[g], '.')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Pixel difference')
        plt.show()

        tbl.write(outname)
        return tbl


def update_wavelength_measured(tbl, wavelength):
    # udate a line table with a wavelength solution
    # takes the measured pixel values and splines the wavelength solution
    # to derive the equivalent measured wavelength
    for iord in np.unique(np.array(tbl['ORDER'])):
        g = (iord == tbl['ORDER']) & np.isfinite(tbl['PIXEL_MEASURED'])
        ius = InterpolatedUnivariateSpline(np.arange(len(wavelength[iord])),
                                           wavelength[iord])
        tbl['WAVELENGTH_MEASURED'][g] = ius(tbl[g]['PIXEL_MEASURED'])

    return tbl


def map_coefficients(wavelength_map, nth_order):
    sz = np.shape(wavelength_map)

    coefficients = np.zeros([nth_order + 1, sz[0]])

    index = np.arange(sz[1])
    for iord in range(sz[0]):
        coefficients[:, iord] = np.polyfit(index, wavelength_map[iord, :],
                                           nth_order)
        wavelength_map[:, iord] = np.polyval(fit, coefficients[iord, :])

    return wavelength_map, coefficients


# get the master wavelength
waster_wave_file = '/Users/eartigau/apero/data/calibDB/MASTER_WAVE.fits'
master_wavelength = fits.getdata(waster_wave_file)

# files corresponding to the master wavelength
im_fp1 = '2399442a_pp_e2dsff_AB.fits'
im_hc1 = '2399446c_pp_e2dsff_AB.fits'

# files for which we want an updated wavelength grid
im_fp2 = '2426562a_pp_e2dsff_AB.fits'
im_hc2 = '2426564c_pp_e2dsff_AB.fits'

# pixel and ordre indices
order_map, x_map = np.indices(master_wavelength.shape, dtype=float)

# gradients to be used in the linear model
gradient_master_wavelength = np.gradient(master_wavelength, axis=1)

# normalized as this is a simple scaling factor later on
gradient_master_wavelength /= np.mean(gradient_master_wavelength)

# HC and FP line lists for the MASTER night
tbl_hc1 = get_lines(im_hc1)
tbl_fp1 = get_lines(im_fp1)

# update the wavelength of lines with the MASTER solution
tbl_hc1 = update_wavelength_measured(tbl_hc1, master_wavelength)
tbl_fp1 = update_wavelength_measured(tbl_fp1, master_wavelength)

# HC and FP line lists for the night for which we want to derive a
# wavelength solution
tbl_fp2 = get_lines(im_fp2)
tbl_hc2 = get_lines(im_hc2)

# high-order wavelength solution correction
#    cannot be smaller than 2, we remove 0 and 1
high_frequency_correction_order = 7  # could tweak

# size in nm of the median bin of residuals for higher-order correction
d_wave_bin = 50  # could tweak

# min number of lines to be included in a median bin for high-order correction
nmin_lines = 100  # could tweak

# starting points for the  corrections
d_cavity = 0  # FP cavity length change

amps_cumu = np.zeros(4)  # linear model

# sigma clipping for the fit
nsig_fit_cut = 5  # could tweak

# min SNR for including in the model
nsig_min = 30  # could tweak

# number of iterations
nite = 30  # could tweak

# speed of light in m/s
c = 2.99e8  # use the actual one

# red cutoff for fit constraint
red_end_cutoff = 2350  # could tweak

h = fits.getheader(im_fp2)
nth_order = h['WAVEDEGN']

high_order_corr = np.zeros(high_frequency_correction_order + 1)

for ite in range(nite):
    print('Iteration {0} of {1}'.format(ite + 1, nite))
    # model wavelength for the night with linear+HC model
    nigthly_wavelength = (master_wavelength +
                          (amps_cumu[0] +  # constant offset in pixel
                           x_map * amps_cumu[1] +  # scale with x
                           order_map * amps_cumu[2] +  # scale with order
                           x_map * order_map * amps_cumu[3]  # cross term
                           ) * gradient_master_wavelength +  # express as wave
                          # high order dependency on wavelength
                          np.polyval(high_order_corr,
                                     np.log(master_wavelength)))

    # update the nightly tables
    tbl_hc2 = update_wavelength_measured(tbl_hc2, nigthly_wavelength)
    tbl_fp2 = update_wavelength_measured(tbl_fp2, nigthly_wavelength)

    # wave difference for the FP after accounting for the
    # cavity length difference
    dwave = (tbl_fp2['WAVELENGTH_MEASURED'] - tbl_fp1['WAVELENGTH_MEASURED']
             + d_cavity * tbl_fp1['WAVELENGTH_MEASURED'])

    # keep points that are <5 MAD away from median
    keep = (np.abs(dwave) < 5 * np.nanmedian(np.abs(dwave)))
    keep &= (tbl_fp2['NSIG'] > nsig_min)

    # median-binned delta wave for all lines
    wbin = []
    dvbin = []
    for w in np.arange(np.min(master_wavelength), red_end_cutoff, d_wave_bin):
        g = (tbl_fp1['WAVELENGTH_MEASURED'] > w)
        g &= (tbl_fp1['WAVELENGTH_MEASURED'] < (w + d_wave_bin))
        g &= keep
        # if enough lines, add to the binned spectrum
        if np.sum(g) > nmin_lines:
            wbin.append(np.nanmedian(tbl_fp1['WAVELENGTH_MEASURED'][g]))
            dvbin.append(np.nanmedian(dwave[g]))

    wbin = np.array(wbin)
    dvbin = np.array(dvbin)

    # remove zero point and slope from higher-order corrections
    fit, _ = mp.robust_polyfit(np.log(wbin), dvbin, 1, nsig_fit_cut)
    dvbin -= np.polyval(fit, np.log(wbin))

    fit, _ = mp.robust_polyfit(np.log(wbin),  # fit as log(wave)
                               dvbin,  # binned dv
                               high_frequency_correction_order,
                               nsig_fit_cut)
    high_order_corr -= fit

    # on even iterations, we adjust the wavelength model
    if (ite % 2) == 0:
        # sample vectors for the linear model
        sample = np.zeros([len(dwave), 4])
        sample[:, 0] = 1  # zero point
        sample[:, 1] = tbl_fp1['PIXEL_MEASURED']  # x dependency
        sample[:, 2] = tbl_fp1['ORDER']  # ordre dependency
        sample[:, 3] = tbl_fp1['PIXEL_MEASURED'] * tbl_fp1[
            'ORDER']  # cross-term

        # update on linear model
        amps_correction, recon = lin_mini(dwave[keep], sample[keep, :])
        amps_cumu -= amps_correction

    else:  # on odd iterations, we update the cavity lengdth change
        # no update of linear model
        amps_correction = np.zeros(4)
        # correct cavity length with the median HC line difference
        d_cavity_correction = np.nanmedian((tbl_hc1['WAVELENGTH_MEASURED']
                                            - tbl_hc2['WAVELENGTH_MEASURED'])
                                           / tbl_hc1['WAVELENGTH_MEASURED'])
        # update cavity
        d_cavity -= d_cavity_correction

    # some plots at the start and end of the iterations
    if (ite == 0) or (ite == (nite - 1)):
        if (ite == 0):
            fig, ax = plt.subplots(nrows=1, ncols=2, sharex=True,
                                   sharey=True, figsize=[16, 8])
            ax[0].set(xlabel='Wavelength (nm)')
            ax[1].set(xlabel='Wavelength (nm)')
            ax[0].set(ylabel='$\Delta$ Wavelength (nm)')
            ax[1].set(ylabel='$\Delta$ Wavelength (nm)')
            ax[0].set(title='First iteration')
            ax[1].set(title='Last iteration')
            id_plot = 0
        else:
            id_plot = 1
        # on first and last iteration plot
        # fp and hc differences
        dl_fp = tbl_fp1['WAVELENGTH_MEASURED'] - tbl_fp2['WAVELENGTH_MEASURED']
        ax[id_plot].plot(tbl_fp1['WAVELENGTH_MEASURED'], dl_fp, 'r.',
                         label='FP')
        dl_hc = tbl_hc1['WAVELENGTH_MEASURED'] - tbl_hc2['WAVELENGTH_MEASURED']
        ax[id_plot].plot(tbl_hc1['WAVELENGTH_MEASURED'], dl_hc, 'g.',
                         label='HC')
        ax[id_plot].legend()

        if id_plot == 1:
            ylim1 = [np.nanpercentile(dl_fp, 1), np.nanpercentile(dl_fp, 99)]
            ylim2 = [np.nanpercentile(dl_hc, 1), np.nanpercentile(dl_hc, 99)]

            # first cut at finding the y range
            ylim_tmp = [np.min([ylim1, ylim2]), np.max([ylim1, ylim2])]
            # add some margin
            wylim = (ylim_tmp[1] - ylim_tmp[0])
            ylim = [ylim_tmp[0] - .2 * wylim, ylim_tmp[1] + .2 * wylim]

            ax[1].set(ylim=ylim)

            plt.show()

# difference in wavelength for the HC lines
dv = (tbl_hc2['WAVELENGTH_MEASURED'] / tbl_hc1['WAVELENGTH_MEASURED'] - 1) * c

keep = (np.abs(dv) < 5 * np.nanmedian(np.abs(dv)))
keep &= (tbl_hc1['NSIG'] > nsig_min)
keep &= (tbl_hc2['NSIG'] > nsig_min)

wbin = []
dvbin = []

for w in range(900, 2500, 50):
    # pixels within a bin
    g = (tbl_hc1['WAVELENGTH_MEASURED'] > w)
    g &= (tbl_hc1['WAVELENGTH_MEASURED'] < (w + 50))

    if np.sum(g) > 10:  # HC has fewer lines than for FPs
        wbin.append(np.nanmedian(tbl_hc1['WAVELENGTH_MEASURED'][g]))
        dvbin.append(np.nanmedian(dv[g]))

plt.plot(wbin, dvbin, 'go', label='binned HC')

# difference in wavelength for the FP lines
dv = dwave / tbl_fp2['WAVELENGTH_MEASURED'] * c
wbin = []
dvbin = []

for w in np.arange(np.min(master_wavelength), red_end_cutoff, d_wave_bin):
    g = (tbl_fp1['WAVELENGTH_MEASURED'] > w)
    g &= (tbl_fp1['WAVELENGTH_MEASURED'] < (w + d_wave_bin))
    if np.sum(g) > nmin_lines:
        wbin.append(np.nanmedian(tbl_fp1['WAVELENGTH_MEASURED'][g]))
        dvbin.append(np.nanmedian(dv[g]))

wbin = np.array(wbin)
dvbin = np.array(dvbin)
plt.plot(wbin, dvbin, 'ro', label='binned FP')

fit, _ = mp.robust_polyfit(np.log(wbin),
                           dvbin,
                           high_frequency_correction_order,
                           nsig_fit_cut)

plt.plot(wbin, np.polyval(fit, np.log(wbin)), 'k-', label='Model')
plt.xlabel('Wavelength (nm)')
plt.ylabel('dv (m/s)')
plt.ylim([-25, 25])
plt.legend()
plt.show()

fig, ax = plt.subplots(ncols=2, nrows=1, figsize=[16, 8], sharey=True)
keep = np.isfinite(dv) & (dv < 50) & (dv > (-50))
ax[0].hist2d(tbl_fp2['PIXEL_MEASURED'][keep], dv[keep], bins=[100, 10])

for w in np.arange(0, 4088, 200):
    g = (tbl_fp2['PIXEL_MEASURED'] > w) & (
                tbl_fp2['PIXEL_MEASURED'] < (w + 200))
    ax[0].plot(np.nanmedian(tbl_fp2['PIXEL_MEASURED'][g]),
               np.nanmedian(dv[g]), 'ro')
ax[0].set(ylabel='dv (m/s)')
ax[0].set(xlabel='pixel')
ax[0].set(title='pixel histogram')

# plot to search for modulo 256 pixel structures due to amplifies
keep = np.isfinite(dv) & (dv < 50) & (dv > (-50))
ax[1].hist2d(tbl_fp2['PIXEL_MEASURED'][keep] % 256, dv[keep], bins=[100, 10])

x256 = tbl_fp2['PIXEL_MEASURED'] % 256
for w in np.arange(0, 256, 10):
    g = (x256 > w) & (x256 < (w + 10))
    ax[1].plot(np.nanmedian(x256[g]), np.nanmedian(dv[g]), 'ro')
ax[1].set(ylabel='dv (m/s)')
ax[1].set(xlabel='pixel % 256')
ax[1].set(title='pixel modulo 256 histogram')
plt.show()

index = np.arange(4088)
coeffs = []
for iord in range(49):
    # need to update the order of coefficient from DRS value
    fit = np.polyfit(index, nigthly_wavelength[iord], 4)
    nigthly_wavelength[iord] = np.polyval(fit, index)
    coeffs += list(fit[::-1])
coeffs = np.array(coeffs).reshape(49, 5)

fits.writeto('_wavesol.'.join(im_hc2.split('.')), nigthly_wavelength,
             overwrite=True)


