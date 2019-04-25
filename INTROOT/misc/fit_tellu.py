# noinspection PyPep8
import numpy as np
import os
import glob
from astropy.io import fits as pyfits

import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
from SpirouDRS.spirouCore.spirouMath import linear_minimization as lin_mini

##############################################################################
# speed of light expressed in km/s. May be defined as a DRS parameter elsewhere
c = 2.99792458e5

obj = 'Gl699'

# should be derived from the target name in the headers. Star without tellurics
template_name = 'templates/' + obj + '.fits'

# files that will serve as references for telluric absorption -- hot stars
fic = np.asarray(glob.glob('tellu_e2ds/*e2ds*AB.fits'))

# wavelength solution to be used for RV shifting of the template and masking
# of zones expected to be affected by absorption
waves = pyfits.getdata('spirou_wave_H4RG_v1.fits')

# level above which the blaze is high enough to accurately measure telluric
cut_blaze_norm = 0.2

# blaze shape
blaze = pyfits.getdata('180528_2279507f_flat_flat_pp_blaze_AB.fits')

# number of principal components to be used
npc = 5

# plot intermediate results for debugging
flag_do_plot = False

# files to be corrected
fics = np.asarray(glob.glob('corr_oh/*' + obj + '*e2ds*.fits'))

# list of absorbers in the tapas fits table
molecules = ['combined', 'h2o', 'o3', 'n2o', 'o2', 'co2', 'ch4']

# fit the derivatives instead of the principal components
fit_deriv = True

# add the first derivative and broadening factor to the principal components
# this allows a variable resolution and velocity offset of the PCs
# this is performed in the pixel space and NOT the velocity space
# as this is should be due to an instrument shift
add_deriv_pc = True

wave_file = 'spirou_wave_H4RG_v1.fits'

###############################################################################

# we mask domains that have <20% of the peak blaze of their respective order
blaze_norm = blaze + 0
for iord in range(49):
    blaze_norm[iord, :] /= np.nanpercentile(blaze_norm[iord, :], 95)

blaze_norm[blaze_norm < cut_blaze_norm] = np.nan

# loading all relevant files in the tellu_db
trans_files = np.asarray(glob.glob('transmission/*trans.fits'))

# reconstructing a 2D image of the PIX vs Nfile cube
abso = np.zeros([len(trans_files), 4088 * 49])
for ific in range(len(trans_files)):
    # here we will need to properly interpolate to the relevant vector grid
    abso[ific, :] = (pyfits.getdata(trans_files[ific])).reshape(4088 * 49)

# determining the pixels relevant for PCA construction
keep = np.isfinite(np.nansum(abso, axis=0))

#
print('fraction of valid pixels (not NaNs in abso) : ', np.mean(keep))

# expressing absorption as a log and not a linear measure
labso = np.log(abso)

keep &= (np.min(labso, axis=0) > (-1))

print('fraction of valid pixles with transmission greater than 1-1/e : ',
      np.mean(keep))

# the PCA magic starts here!
U, s, Vt = np.linalg.svd(labso[:, keep], full_matrices=False)

if add_deriv_pc:
    # the npc+1 term will be the derivative of the first PC
    # the npc+2 term will be the broadning factor the first PC
    pc = np.zeros([4088 * 49, npc + 2])
else:
    pc = np.zeros([4088 * 49, npc])

for i in range(npc):
    for j in range((np.shape(labso))[0]):
        pc[:, i] += U[j, i] * labso[j, :]

if add_deriv_pc:
    pc[:, npc] = np.gradient(pc[:, 0])
    pc[:, npc + 1] = np.gradient(np.gradient(pc[:, 0]))
    npc += 2

if fit_deriv:
    fit_pc = np.gradient(pc, axis=0)

#
# we plot the PCs
# if the "add_deriv_pc" flag is true, then we add the first (dx shift) and
# second (resolution) derivatites of the first PC (largest variance contributor)
# this will provide a measurement of the offset of absorbers relative to input
# components
#
if flag_do_plot:
    for i in range(npc):
        label = 'pc ' + str(i + 1)
        if add_deriv_pc:
            if i == (npc - 2):
                label = 'd[pc1]'
            if i == (npc - 1):
                label = 'd$^2$[pc1]'

        plt.plot(waves.ravel(), pc[:, i], label=label)
    plt.legend()
    plt.show()

flag_template = os.path.exists(template_name)

if flag_template:
    # if the template is used, read it
    template = pyfits.getdata(template_name) / blaze_norm  # .reshape(4088*49)

# recovering the expected atmospheric transmission
tapas_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')

tapas_all_species = np.load(tapas_file_name)

for fic in fics:

    recon_abso = np.zeros(4088 * 49) + 1
    amps_abso_total = np.zeros(npc)

    # name of file containing the telluric-free spectrum
    outname = 'corr_tellu/' + (fic.split('/'))[1]

    # name of file containing the applied telluric correction
    outname_abso = 'corr_tellu/' + ((fic.split('/'))[1].split('.'))[
        0] + '_tellu.fits'

    # skip if file exists
    if not os.path.isfile(outname):

        hdr = pyfits.getheader(fic)
        sp = pyfits.getdata(fic) / blaze_norm

        if flag_template:
            dv = hdr['BERV']
            template2 = np.zeros([4088 * 49])

            for iord in range(49):
                # noinspection PyUnboundLocalVariable
                keep = np.isfinite(template[iord, :])
                if np.nansum(keep) > 20:
                    s = InterpolatedUnivariateSpline(waves[iord, keep],
                                                     template[iord, keep],
                                                     ext=3)
                    template2[iord * 4088:iord * 4088 + 4088] = s(
                        waves[iord, :] * (1 + dv / c))  # *blaze[iord,:]

        hdr = pyfits.getheader(fic)
        # sp=sp/blaze+0

        sp2 = np.zeros([4088 * 49])
        # recon2=np.zeros([4088*49])

        for iord in range(49):
            sp2[iord * 4088:iord * 4088 + 4088] = sp[iord, :]

        norm = np.nanmedian(sp2)

        keep = (tapas_all_species[0, :] > 0.2)  # *(trans<0.99)
        keep = keep * (waves.ravel() > 1000) * (waves.ravel() < 2100)

        if flag_do_plot:
            all_mask = np.zeros([4088 * 49])

        # noinspection PyPep8,PyPep8
        for ite in range(4):

            if not flag_template:
                template2 = np.zeros([4088 * 49])

                ew = 30 / 2.2 / 2.354  # gaussian ew for vinsi km/s
                xx = np.arange(ew * 6) - ew * 3
                ker2 = np.exp(-.5 * (xx / ew) ** 2)
                ker2 /= np.nansum(ker2)

                for iord in range(49):
                    # print(iord)

                    mask = tapas_all_species[0, iord * 4088:iord * 4088 + 4088]
                    mask = (mask > 0.98)

                    # noinspection PyPep8
                    sp2b = np.convolve(sp[iord, :] * mask /
                                       recon_abso[iord * 4088:iord * 4088 + 4088],
                                       ker2, mode='same')
                    ww = np.convolve(mask.astype(float), ker2, mode='same')
                    template2[iord * 4088:iord * 4088 + 4088] = sp2b / ww

                    if flag_do_plot:
                        # noinspection PyUnboundLocalVariable
                        all_mask[iord * 4088:iord * 4088 + 4088] = mask

            #

            # noinspection PyUnboundLocalVariable
            dd = (sp2 / template2) / recon_abso

            if flag_template:
                dd *= blaze.reshape([4088 * 49])

                # print(iord)
                ew = 30 / 2.2 / 2.354  # gaussian ew of smoothing kernel km/s
                xx = np.arange(ew * 6) - ew * 3
                ker2 = np.exp(-.5 * (xx / ew) ** 2)
                ker2 /= np.nansum(ker2)

                for iord in range(49):

                    mask = tapas_all_species[0, iord * 4088:iord * 4088 + 4088]
                    mask = (mask > 0.98)

                    # noinspection PyPep8
                    sp2b = np.convolve(
                        dd[iord * 4088:iord * 4088 + 4088] * mask / recon_abso[
                                                                    iord * 4088:iord * 4088 + 4088],
                        ker2, mode='same')
                    ww = np.convolve(mask.astype(float), ker2, mode='same')

                    dd[iord * 4088:iord * 4088 + 4088] /= (sp2b / ww)

                    if flag_do_plot:
                        all_mask[iord * 4088:iord * 4088 + 4088] = mask

            log_dd = np.log(dd)

            for i in range(49):
                log_dd[i * 4088:i * 4088 + 4088] -= np.nanmedian(
                    log_dd[i * 4088:i * 4088 + 4088])

            # we can use the derivative of the PCA components for the fit, or the components themselves
            # it is unclear which version will work best. We have a keyword to switch from one to the other

            if fit_deriv:
                fit_dd = np.gradient(log_dd)
            else:
                fit_dd = log_dd

            keep &= np.isfinite(fit_dd)
            # noinspection PyUnboundLocalVariable
            keep &= (np.nansum(np.isfinite(fit_pc), axis=1) == npc)

            print('total keep : ', np.nansum(keep))

            amps, recon = lin_mini(fit_dd[keep], fit_pc[keep, :])

            abso2 = np.zeros([len(dd)])
            for ipc in range(len(amps)):
                abso2 += pc[:, ipc] * amps[ipc]
                amps_abso_total[ipc] += amps[ipc]
            #
            recon_abso *= np.exp(abso2)
            #
            print(amps)

        if flag_do_plot:
            plt_order = 31

            print('flag_template : ', flag_template)
            plt.plot(waves[plt_order, :],
                     sp[plt_order, :] / np.nanmedian(sp[plt_order, :]), 'k-',
                     label='input SP')

            # noinspection PyPep8,PyPep8
            plt.plot(waves[plt_order, :], (
            sp2[plt_order * 4088:plt_order * 4088 + 4088]) / np.nanmedian(
                sp2[plt_order * 4088:plt_order * 4088 + 4088]) / recon_abso[
                                                                 plt_order * 4088:plt_order * 4088 + 4088],
                     'g-', label='cleaned sp')
            # noinspection PyPep8
            plt.plot(waves[plt_order, :], (
            template2[plt_order * 4088:plt_order * 4088 + 4088]) / np.nanmedian(
                template2[plt_order * 4088:plt_order * 4088 + 4088]), 'y-',
                     label='template')
            plt.plot(waves[plt_order, :],
                     recon_abso[plt_order * 4088:plt_order * 4088 + 4088],
                     'c--', label='recon abso')
            mask_plt = np.zeros(4088) + np.nan
            mask_plt[
                all_mask[plt_order * 4088:plt_order * 4088 + 4088] == 1] = 1
            plt.plot(waves[plt_order, :], mask_plt, 'r.',
                     label='continuum region')
            plt_keep = keep + .005
            plt_keep[~keep] = np.nan
            plt.plot((waves.ravel())[plt_order * 4088:plt_order * 4088 + 4088],
                     plt_keep[plt_order * 4088:plt_order * 4088 + 4088], 'g.',
                     label='PCA fit region')

            plt.legend()
            plt.show()  # block=False)

        # recon_abso[recon_abso<0.02]=np.nan

        sp_out = (sp2 / recon_abso).reshape([49, 4088])

        pyfits.writeto(outname, sp_out, header=hdr, clobber=True)

        recon_abso2 = np.zeros([49, 4088])
        for iord in range(49):
            recon_abso2[iord, :] = recon_abso[4088 * iord:4088 * iord + 4088]

        log_recon_abso2 = np.log(recon_abso)
        log_tapas_abso = np.log(tapas_all_species[1:, :])

        keep = np.min(log_tapas_abso, axis=0) > (-.5)
        keep *= (log_recon_abso2 > (-.5))
        keep *= np.isfinite(recon_abso)

        amps_recon, recon = lin_mini(log_recon_abso2[keep],
                                     log_tapas_abso[:, keep])

        log_recon = np.zeros([4088 * 49])
        for i in range(len(amps_recon)):
            log_recon += log_tapas_abso[i, :] * amps_recon[i]

        recon_tapas = np.exp(log_recon)

        i = 0
        for molecule in molecules[1:]:
            hdr['abso_' + molecule] = amps_recon[i]
            i += 1

        if add_deriv_pc:
            for i in range(npc - 2):
                hdr['AMP_PC' + str(i + 1)] = amps_abso_total[i]
            hdr['DV_TELL1'] = amps_abso_total[npc - 1]
            hdr['DV_TELL2'] = amps_abso_total[npc - 2]

        pyfits.writeto(outname_abso, recon_abso2, header=hdr, clobber=True)

    else:
        print(outname + ' exists...')
