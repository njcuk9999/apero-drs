import numpy as np
from lin_mini import *
import os
import glob
import pyfits
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
import scipy.ndimage
from PyAstronomy import pyasl
from PyAstronomy import funcFit as fuf
from astropy.table import Table

# some variables needed later on

# smoothing parameter for the interpolation of the hot star continuum. Needs to be reasonably matched to the true width
vsini = 250.0

# speed of light expressed in km/s. May be defined as a DRS parameter elsewhere
c = 2.99792458e5

# should be derived from the target name in the headers. Star without tellurics
template_name = 'templates/Gl699.fits'

# files that will serve as references for telluric absorption -- hot stars
fic = np.asarray(glob.glob('tellu_e2ds/*e2ds*AB.fits'))

# wavelength solution to be used for RV shifting of the template and masking
# of zones expected to be affected by absorption
wave_file = 'spirou_wave_H4RG_v1.fits'
waves = pyfits.getdata(wave_file)

# level above which the blaze is high enough to accurately measure telluric
cut_blaze_norm = 0.2

# blaze shape
blaze = pyfits.getdata('180528_2279507f_flat_flat_pp_blaze_AB.fits')

# fits table containing N columns
# col 1 : wavelength (nm)
# col 2 : total absorption spectrum
# col 3-N : absorption per chemical species
file_tapas_spectra = 'tapas_all_sp.fits'

# list of absorbers in the tapas fits table
molecules = ['combined', 'h2o', 'o3', 'n2o', 'o2', 'co2', 'ch4']

# min transmission in tapas models to consider an element part of continuum
transmission_cut = 0.98

# number of iterations to find the SED of hot stars + sigma clipping
n_iterations_sed_hotstar = 5

FWHM_pixel_lsf = 2.1  # mean line width expressed in pix

flag_do_plot = False

# we expand the wavelength vector in a 48*4088 form
waves2 = waves.reshape([49, 4088])

# we mask domains that have <20% of the peak blaze of their respective order
blaze_norm = blaze + 0
for iord in range(49):
    blaze_norm[iord, :] /= np.percentile(blaze_norm[iord, :], 95)

blaze_norm[blaze_norm < cut_blaze_norm] = np.nan

# representative atmospheric transmission
# tapas = pyfits.getdata('tapas_model.fits')
tapas = Table.read(file_tapas_spectra)

# tapas spectra resampled onto our data wavelength vector
tapas_all_species = np.zeros([len(molecules), 4088 * 49])
n_species = 0

NPIX_ker = int(np.ceil(3 * FWHM_pixel_lsf * 1.5 / 2) * 2 + 1)
ker = np.arange(NPIX_ker) - NPIX_ker // 2
ker = np.exp(-0.5 * (ker / (FWHM_pixel_lsf / 2.354)) ** 2)
# we only want an approximation of the absorption to find the continuum and estimate chemical abundances.
# there's no need for a varying kernel shape
ker /= np.sum(ker)

tapas_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')

if not os.path.exists(tapas_file_name):
    for molecule in molecules:
        print('molecule --> ' + molecule)
        spline_tapas_specie = InterpolatedUnivariateSpline(tapas['wavelength'],
                                                           tapas[
                                                               'trans_' + molecule])
        print('mean trans level : ', np.mean(tapas['trans_' + molecule]))

        # convolve all tapas absorption to the SPIRou approximate resolution
        for iord in range(49):
            tapas_all_species[n_species,
            iord * 4088:iord * 4088 + 4088] = spline_tapas_specie(
                waves[iord, :])
            tapas_all_species[n_species,
            iord * 4088:iord * 4088 + 4088] = np.convolve(
                tapas_all_species[n_species, iord * 4088:iord * 4088 + 4088],
                ker, mode='same')
        n_species += 1

    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0

    np.save(tapas_file_name, tapas_all_species)
else:
    print('loading ' + tapas_file_name)
    tapas_all_species = np.load(tapas_file_name)

outnames = ["" for x in range(len(fic))]

# median sampling
med_sampling = 2.2  # expressed in km/s / pix
ew = vsini / med_sampling / 2.354  # gaussian ew for vinsi km/s
xx = np.arange(ew * 6) - ew * 3
ker2 = np.exp(-.5 * (xx / ew) ** 2)
ker2 /= np.sum(ker2)

for ific in range(len(fic)):
    # removing the stellar SED to determine transmission
    outnames[ific] = 'transmission/' + ((fic[ific].split('/'))[1].split('.'))[
        0] + '_trans.fits'
    if os.path.isfile(outnames[ific]) == False:

        transmission_map = np.zeros([49, 4088])

        sp = pyfits.getdata(fic[ific]) / blaze

        for iord in range(0, 49):
            trans = tapas_all_species[0, iord * 4088:iord * 4088 + 4088]

            # mask1 keeps track of pixels that are considered valid for SED determination
            mask1 = trans > transmission_cut
            mask1 &= np.isnifite(blaze_norm[iord, :])
            sp[iord, :] /= np.nanmedian(sp[iord, :])
            #
            mask = np.array(mask1, dtype=float)
            #
            sed = np.ones(4088)
            #
            for ite in range(n_iterations_sed_hotstar):
                sp2 = sp[iord, :]
                sp2 *= mask

                sp2b = np.convolve(sp2 / sed, ker2, mode='same')
                ww = np.convolve(mask, ker2, mode='same')

                sp2bw = sp2b / ww
                sp2bw[sp2b == 0] = 1

                dev = (sp2bw - sp[iord, :] / sed)
                dev /= np.nanmedian(np.abs(dev))

                mask = mask1 * (np.abs(dev) < 5)

                sed *= sp2bw

            bad = (sp[iord, :] / sed[:] > 1.2)
            sed[bad] = np.nan

            if flag_do_plot:  # iord == 45:
                print('toto')
                plt.ylim([0.75, 1.15])
                plt.plot(waves[iord, :], sp[iord, :], 'r.')
                plt.plot(waves[iord, mask], sp[iord, mask], 'b.')
                plt.plot(waves[iord, :], sed, 'r-')
                plt.plot(waves[iord, :], trans, 'c-')
                plt.plot(waves[iord, :], sp[iord, :] / sed[:], 'g-')
                plt.plot(waves[iord, :], sed * 0 + 1, 'r-')
                plt.plot(waves[iord, :], ww, 'k-')
                plt.title(outnames[ific])
                plt.show()
                plt.clf()

            sed[ww < 0.2] = np.nan
            transmission_map[iord, :] = sp[iord, :] / sed

        # writing to the telluric data base
        pyfits.writeto(outnames[ific], transmission_map, clobber=True)
    else:
        print(outnames[ific] + ' exists')

# tool outside online DRS
abso = np.zeros([len(outnames), 4088 * 49])

for ific in range(len(outnames)):
    abso[ific, :] = (pyfits.getdata(outnames[ific])).reshape(4088 * 49)

abso[abso < 0.01] = 0.01
abso[abso > 1.05] = 1
abso[blaze_norm < 0.2] = np.nan

pyfits.writeto('abso_map.fits', abso.reshape(39, 49, 4088), clobber=True)
# abso=pyfits.getdata('abso_map.fits')

abso2 = np.array(abso)

log_abso = np.log(abso2)

for ite in range(5):
    absmed = np.nanmedian(log_abso, axis=0)
    for i in range(len(fic)):
        tmp = log_abso[i, :]
        gg = (tmp > (-1)) * (absmed > (-1))
        ratio = np.sum(tmp[gg] * absmed[gg]) / np.sum(absmed[gg] ** 2)
        log_abso[i, :] /= ratio

pyfits.writeto('abso_median.fits',
               np.exp((np.nanmedian(log_abso, axis=0)).reshape([49, 4088])),
               clobber=True)
pyfits.writeto('abso_map_norm.fits', np.exp(log_abso), clobber=True)

dv_order_sanity = 33

absmed2 = np.exp(
    absmed[4088 * dv_order_sanity + 5:+4088 * dv_order_sanity + 4088 - 5])
for i in range(len(fic)):
    cc = np.zeros([5])

    j = 0
    for dv in range(-2, 3):
        tmp = log_abso[i,
              4088 * dv_order_sanity + 5 + dv:+4088 * dv_order_sanity + 4088 - 5 + dv]
        tmp = np.exp(tmp)
        gg = (tmp > (.2)) * (absmed2 > (.2))

        cc[j] = np.sum(tmp[gg] * absmed2[gg]) / np.sum(absmed2[gg] ** 2)
        j += 1
    fit = np.polyfit(np.array(range(-2, 3)), cc, 2)
    dvpix = -.5 * fit[1] / fit[0]
    print(fic[i], ', dv = ', dvpix)
    print(cc)
