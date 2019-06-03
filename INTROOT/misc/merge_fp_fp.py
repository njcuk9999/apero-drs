import numpy as np
import glob
from astropy.io import fits
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy import ndimage


def register_fp(im1, im2_ini, doplot=False, wcc=11, niter=3):
    # provide two images and find the cross-correlation
    # peak in 2D. The performs iteratively a 1D correlation
    # in both Y and X direction.
    #
    # im1 -> reference FP image
    # im2 -> FP image to be correlated with im1
    # doplot = True -> plots correlation functions
    # wcc = 15 -> +- offset of the cross-correlation
    # niter = 3 -> number of iterations for the correlation
    #
    # returns :
    # shifted im2 image
    # dx applied to match im1
    # dy applied to match im2

    # we find the shape of image 1
    sz = np.shape(im1)
    # print(sz)
    wwy = (np.array(sz[0]) - wcc * 2) // 2
    wwx = (np.array(sz[1]) - wcc * 2) // 2

    # print(wwx,wwy)

    # generate x/y indices for the entire image
    yy, xx = np.indices([sz[0], sz[1]], dtype=float)  # /10.

    # global offset applied to im2
    dx_ref = 0
    dy_ref = 0

    # extract central regions of array
    im1b = np.array(im1[sz[0] // 2 - wwy:sz[0] // 2 + wwy, sz[1] // 2 - wwx:sz[1] // 2 + wwx])

    # to increase the contribution of low-flux regions, we x-correlate
    # the square root of the images.

    im1b[im1b < 0] = 0
    im1b = np.sqrt(im1b)

    for ite in range(niter):
        # range of dy to be explored the same size of cc offset will be
        # explored in x

        dx = np.arange(-wcc, wcc)
        dy = np.arange(-wcc, wcc)

        # value of x-correlation for all offset
        cc = np.zeros([len(dy), len(dx)])

        if ite != 0:
            im2 = ndimage.map_coordinates(im2_ini, [yy + dy_ref, xx + dx_ref],
                                          order=2, cval=0, output=float,
                                          mode='constant')
        else:
            im2 = np.array(im2_ini)

        # we will extract a varying region within im2, but we just
        # want to compute square root once
        im2tmp = np.array(im2)
        im2tmp[im2tmp < 0] = 0
        im2tmp = np.sqrt(im2tmp)

        # x-correlate im1 with a shifter im2
        for i in tqdm(range(len(dy)), leave=False):
            for j in range(len(dx)):
                # print(i,j)
                im2b = np.array(
                    im2tmp[sz[0] // 2 - wwy + dy[i]:sz[0] // 2 + wwy + dy[i],
                    sz[1] // 2 - wwx + dx[j]:sz[1] // 2 + wwx + dx[j]])

                cc[i, j] = np.sum(im1b * im2b)

        if doplot:
            plt.imshow(cc)
            plt.show()
        imax = np.argmax(cc)
        dy0 = imax // len(dx)
        dx0 = imax % len(dx)

        # 2nd order fit to the cc peak
        if np.abs(dy[dy0]) <= (wcc - 2):
            fit = np.polyfit(dy[dy0 - 1:dy0 + 2], cc[dy0 - 1:dy0 + 2, dx0][:], 2)
            dy_ref += (-.5 * fit[1] / fit[0])
        else:
            dy_ref += (dy[dy0])

        print('increment in dy : ', (-.5 * fit[1] / fit[0]))

        # 2nd order fit to the cc peak
        if np.abs(dx[dx0]) <= (wcc - 2):
            fit = np.polyfit(dx[dx0 - 1:dx0 + 2], cc[dy0, dx0 - 1:dx0 + 2], 2)
            dx_ref += (-.5 * fit[1] / fit[0])
        else:
            dx_ref += (dx[dx0])

        print('increment in dx : ', (-.5 * fit[1] / fit[0]))

        print('DX/DY ref : ', dx_ref, dy_ref)

        if doplot:
            plt.plot(dx, cc, label='dx')
            plt.legend()
            plt.show()

    # shift to the max cc position
    im2 = ndimage.map_coordinates(im2_ini, [yy + dy_ref, xx + dx_ref],
                                  order=2, cval=0, output=float,
                                  mode='constant')  #

    return im2, dx_ref, dy_ref


def trim_image(image):
    # subimage and normalize
    # 4-4092 in x
    # 250-3350 in y
    # flip in x
    # flip in y
    image = image[::-1, ::-1]
    image = image[250:3350, 4:4092]

    return image


def get_master_fp(ref_fp_file, all_fps, N_dt_bin=2):
    # ref_fp_file -> reference file against which all other fps are compared
    # all_fps -> all fps to be combined together to produce the master fp
    # N_dt_bin -> delay in hours for two FP files to be considered as coming
    #             from the same batch

    # ****** TO BE REMOVED ************************************
    ref_fp_file = '2279802a_pp.fits'
    all_fps = np.array(glob.glob('*a_pp.fits'))
    # ****** TO BE REMOVED ************************************

    im1 = fits.getdata(ref_fp_file)

    im1 = trim_image(im1)  # TO BE REMOVED

    # replace all NaNs by zeros
    im1[np.isfinite(im1) == False] = 0

    # we check that only files with FP_FP DPRTYPE are present
    dprtype = np.zeros(len(all_fps), dtype='<U20')
    for i in tqdm(np.arange(len(all_fps)), leave=False):
        hdr = fits.getheader(all_fps[i])
        dprtype[i] = np.array(hdr['DPRTYPE'])

    # only FP_FP should be used here
    all_fps = all_fps[dprtype == 'FP_FP']

    # keep track of timestamps and median-combined the ones
    # that were taken close in time
    fp_time = np.zeros(len(all_fps))
    # looping through the file headers
    for i in tqdm(np.arange(len(all_fps)), leave=False):
        hdr = fits.getheader(all_fps[i])
        fp_time[i] = float(hdr['MJDATE'])

    # ID of matched multiplets of files
    matched_id = np.zeros_like(fp_time, dtype=int)

    # loop until all files are matched with all other files taken within
    # 2 hours
    ii = 1
    while np.min(matched_id) == False:
        gg = (np.where(matched_id == 0))[0]
        g = np.min(gg)
        # same batch if they are within N hours
        gm = np.abs(fp_time[g] - fp_time) < N_dt_bin / 24.0
        matched_id[gm] = ii
        ii += 1

    # find all matched batches
    u_ids = set(matched_id)

    # how many bins of median darks. The 'long' option has 1 bin per
    # epoch of +-N_dt_bin hours
    i = 0

    # will hold the cube that keeps the median of each of the FP sequences
    all_fps_cube = []
    # looping through epochs
    for u_id in u_ids:
        keep = (matched_id == u_id)

        # only combine if 3 or more images were taken
        if np.sum(keep) >= 3:

            # find all files at that epoch
            fp_id = all_fps[keep]

            # read all files within an epoch into a cube
            cube = []
            for fic in fp_id:
                print(fic)
                tmp = fits.getdata(fic)  # -dark

                tmp = trim_image(tmp)  # TO BE REMOVED

                tmp /= np.nanpercentile(tmp, 90)
                cube.append(tmp)

            # median dark for that epoch
            im2 = np.nanmedian(cube, axis=0)
            im2[np.isfinite(im2) == False] = 0

            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            im2, dx_ref, dy_ref = register_fp(im1, im2, doplot=False)

            all_fps_cube.append(im2)

    all_fps_cube = np.array(all_fps_cube)
    # just to check, we save the cube before performing a big mean
    # along dimension 0
    fits.writeto('super_cube.fits', all_fps_cube, overwrite=True)
    fits.writeto('super_mean.fits', np.sum(all_fps_cube, axis=0), overwrite=True)