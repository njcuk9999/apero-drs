import numpy as np
import warnings


__NAME__ = 'hotpix_code_ea.py'


def clean_hotpix(image, badpix):
    # Cleans an image by finding pixels that are high-sigma (positive or negative)
    # outliers compared to their immediate neighbours. Bad pixels are
    # interpolated with a 2D surface fit by using valid pixels within the
    # 3x3 pixel box centered on the bad pix.
    #
    # Pixels in big clusters of bad pix (more than 3 bad neighbours)
    # are left as is
    image_rms_measurement = np.array(image)
    # First we construct a 'flattened' image
    # We perform a low-pass filter along the x axis
    # filtering the image so that only pixel-to-pixel structures
    # remain. This is use to find big outliers in RMS.
    # First we apply a median filtering, which removes big outliers
    # and then we smooth the image to avoid big regions filled with zeros.
    # Regions filled with zeros in the low-pass image happen when the local
    # median is equal to the pixel value in the input image.
    #
    # We apply a 5-pix median boxcar in X and a 5-pix boxcar smoothing
    # in x. This blurs along the dispersion over a scale of ~7 pixels.

    # perform a [1,5] median filtering by rolling axis of a 2D image
    # and constructing a 5*N*M cube, then taking a big median along axis=0
    # analoguous to, but faster than :
    #     low_pass = signal.medfilt(image_rms_measurement, [1, 5])

    # make shifted cubes from +/- 2 pixels
    tmp = []
    for d in range(-2, 3):
        tmp.append(np.roll(image, d))
    tmp = np.array(tmp)
    # median along the shifted axis
    tmp = np.nanmedian(tmp, axis=0)
    # same trick but for convolution with a [1,5] boxcar
    low_pass = np.zeros_like(tmp)
    # make a low pass shifted cube from +2/-2 pixels
    for d in range(-2, 3):
        low_pass += np.roll(tmp, d)
    # divide by the number of shifts
    low_pass /= 5
    # residual image showing pixel-to-pixel noise
    # the image is now centered on zero, so we can
    # determine the RMS around a given pixel
    image_rms_measurement -= low_pass

    abs_image_rms_measurement = np.abs(image_rms_measurement)
    # same as a [3,3] median filtering with signal.medfilt but faster
    tmp = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            tmp.append(np.roll(abs_image_rms_measurement, [dx, dy],
                               axis=[0, 1]))
    tmp = np.array(tmp)
    # median the cube
    rms = np.nanmedian(tmp, axis=0)
    # the RMS cannot be arbitrarily small, so  we set
    # a lower limit to the local RMS at 0.5x the median
    # rms
    with warnings.catch_warnings(record=True) as _:
        rms[rms < (0.5 * np.nanmedian(rms))] = 0.5 * np.nanmedian(rms)
        # determining a proxy of N sigma
        nsig = image_rms_measurement / rms
        bad = np.array((np.abs(nsig) > 10), dtype=bool)
    # known bad pixels are also considered bad even if they are
    # within the +-N sigma rejection
    badpix = badpix | bad | ~np.isfinite(image)
    # we remove bad pixels at the periphery of the image
    # badpix[0, :] = False
    # badpix[-1, :] = False
    # badpix[:, 0] = False
    # badpix[:, -1] = False
    # find the pixel locations where we have bad pixels
    x, y = np.where(badpix)
    # set up the boxes
    box3d = np.zeros([len(x), 3, 3])
    keep3d = np.zeros([len(x), 3, 3], dtype=bool)
    # centering on zero
    yy, xx = np.indices([3, 3]) - 1

    sz = image.shape
    # loop around the pixels in x and y
    for ix in range(-1, 2):
        for iy in range(-1, 2):
            # fill in the values for box and keep
            # box3d[:, ix + 1, iy + 1] = image[x + ix, y + iy]
            # keep3d[:, ix + 1, iy + 1] = ~badpix[x + ix, y + iy]
            box3d[:, ix + 1, iy + 1] = image[(x + ix) % sz[0], (y + iy) % sz[1]]
            keep3d[:, ix + 1, iy + 1] = ~badpix[(x + ix) % sz[0], (y + iy) % sz[1]]

    # find valid neighbours
    nvalid = np.sum(np.sum(keep3d, axis=1), axis=1)
    # keep only points with >5 valid neighbours
    box3d = box3d[nvalid > 5]
    keep3d = keep3d[nvalid > 5]
    x = x[nvalid > 5]
    y = y[nvalid > 5]
    nvalid = nvalid[nvalid > 5]
    # copy the original image
    image1 = np.array(image)
    # correcting bad pixels with a 2D fit to valid neighbours
    # pre-computing some values that are needed below
    xx2 = xx ** 2
    yy2 = yy ** 2
    xy = xx * yy
    ones = np.ones_like(xx)
    # loop around the x axis
    for it in range(len(x)):
        # get the keep and box values for this iteration
        keep = keep3d[it]
        box = box3d[it]
        if nvalid[it] == 8:
            # we fall in a special case where there is only a central pixel
            # that is bad surrounded by valid pixel. The central value is
            # straightfward to compute by using the means of 4 immediate
            # neighbours and the 4 corner neighbours.
            m1 = np.mean(box[[0, 1, 1, 2], [1, 0, 2, 1]])
            m2 = np.mean(box[[0, 0, 2, 2], [2, 0, 2, 0]])
            image1[x[it], y[it]] = 2 * m1 - m2
        else:
            # fitting a 2D 2nd order polynomial surface. As the xx=0, yy=0
            # corresponds to the bad pixel, then the first coefficient
            # of the fit (its zero point) corresponds to the value that
            # must be given to the pixel
            a = np.array([ones[keep], xx[keep], yy[keep], xx2[keep], yy2[keep],
                          xy[keep]])
            b = box[keep]
            # perform a least squares fit on a and b
            coeff, _ = linear_minimization(b, a, no_recon=True)
            # this is equivalent to the slower command :
            # coeff = fit2dpoly(xx[keep], yy[keep], box[keep])
            image1[x[it], y[it]] = coeff[0]
    # return the cleaned image
    return image1


def linear_minimization(vector, sample, no_recon=False):
    """
    wrapper function that sets everything for the @jit later
    In particular, we avoid the np.zeros that are not handled
    by numba, size of input vectors and sample to be adjusted

    :param vector: 2d matrix that is N x M or M x N
    :param sample: 1d vector of length N
    :return:
    """
    # setup function name
    func_name = __NAME__ + '.linear_minimization()'

    sz_sample = sample.shape  # 1d vector of length N
    sz_vector = vector.shape  # 2d matrix that is N x M or M x N
    # define which way the sample is flipped relative to the input vector
    if sz_vector[0] == sz_sample[0]:
        case = 2
    elif sz_vector[0] == sz_sample[1]:
        case = 1
    else:
        emsg = ('Neither vector[0]==sample[0] nor vector[0]==sample[1] '
                '(function = {0})')
        print(emsg)
        raise ValueError(emsg.format(func_name))
    # ----------------------------------------------------------------------
    # Part A) we deal with NaNs
    # ----------------------------------------------------------------------
    # set up keep vector
    keep = None
    # we check if there are NaNs in the vector or the sample
    # if there are NaNs, we'll fit the rest of the domain
    isnan = (np.sum(np.isnan(vector)) != 0) or (np.sum(np.isnan(sample)) != 0)
    # ----------------------------------------------------------------------
    # case 1: sample is not flipped relative to the input vector
    if case == 1:
        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=0))
            # redefine the input vector to avoid NaNs
            vector = vector[keep]
            sample = sample[:, keep]
            # re-find shapes
            sz_sample = sample.shape  # 1d vector of length N
        # matrix of covariances
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        # cross-terms of vector and columns of sample
        vec = np.zeros(sz_sample[0])
        # reconstructed amplitudes
        amps = np.zeros(sz_sample[0])
        # reconstruted fit
        recon = np.zeros(sz_sample[1])
    # ----------------------------------------------------------------------
    # case 2: sample is flipped relative to the input vector
    elif case == 2:
        # same as for case 1, but with axis flipped
        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=1))
            vector = vector[keep]
            sample = sample[keep, :]
            # re-find shapes
            sz_sample = sample.shape  # 1d vector of length N
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        vec = np.zeros(sz_sample[1])
        amps = np.zeros(sz_sample[1])
        recon = np.zeros(sz_sample[0])
    # ----------------------------------------------------------------------
    # should not get here (so just repeat the raise from earlier)
    else:
        emsg = ('Neither vector[0]==sample[0] nor vector[0]==sample[1] '
                '(function = {0})')
        raise ValueError(emsg.format(func_name))

    # ----------------------------------------------------------------------
    # Part B) pass to optimized linear minimization
    # ----------------------------------------------------------------------
    # pass all variables and pre-formatted vectors to the @jit part of the code
    amp_out, recon_out = lin_mini(vector, sample, mm, vec, sz_sample,
                                       case, recon, amps, no_recon=no_recon)
    # ----------------------------------------------------------------------
    # if we had NaNs in the first place, we create a reconstructed vector
    # that has the same size as the input vector, but pad with NaNs values
    # for which we cannot derive a value
    if isnan:
        recon_out2 = np.zeros_like(keep) + np.nan
        recon_out2[keep] = recon_out
        recon_out = recon_out2

    return amp_out, recon_out


def lin_mini(vector, sample, mm, v, sz_sample, case, recon, amps,
             no_recon=False):
    #
    # vector of N elements
    # sample: matrix N * M each M column is adjusted in amplitude to minimize
    # the chi2 according to the input vector
    # output: vector of length M gives the amplitude of each column
    #
    if case == 1:
        # fill-in the co-variance matrix
        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                mm[i, j] = np.sum(sample[i, :] * sample[j, :])
                # we know the matrix is symetric, we fill the other half
                # of the diagonal directly
                mm[j, i] = mm[i, j]
            # dot-product of vector with sample columns
            v[i] = np.sum(vector * sample[i, :])
        # if the matrix cannot we inverted because the determinant is zero,
        # then we return a NaN for all outputs
        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon
        # invert coveriance matrix
        inv = np.linalg.inv(mm)
        # retrieve amplitudes
        for i in range(len(v)):
            for j in range(len(v)):
                amps[i]+=inv[i,j]*v[j]
        # reconstruction of the best-fit from the input sample and derived
        # amplitudes
        if not no_recon:
            for i in range(sz_sample[0]):
                recon += amps[i] * sample[i, :]
        return amps, recon
    # same as for case 1 but with axis flipped
    if case == 2:
        # fill-in the co-variance matrix
        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.sum(sample[:, i] * sample[:, j])
                # we know the matrix is symetric, we fill the other half
                # of the diagonal directly
                mm[j, i] = mm[i, j]
            # dot-product of vector with sample columns
            v[i] = np.sum(vector * sample[:, i])
        # if the matrix cannot we inverted because the determinant is zero,
        # then we return a NaN for all outputs
        if np.linalg.det(mm) == 0:
            return amps, recon
        # invert coveriance matrix
        inv = np.linalg.inv(mm)
        # retrieve amplitudes
        for i in range(len(v)):
            for j in range(len(v)):
                amps[i]+=inv[i,j]*v[j]
        # reconstruction of the best-fit from the input sample and derived
        # amplitudes
        if not no_recon:
            for i in range(sz_sample[1]):
                recon += amps[i] * sample[:, i]
        return amps, recon



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # TODO: get bad pixel map file
    badpixmask = None
    # TODO: get image (2D 4096 x 4096)
    image = None

    # ----------------------------------------------------------------------
    # clean hot pixels
    image5 = clean_hotpix(image, badpixmask)

    # ----------------------------------------------------------------------
    # TODO: save files



# =============================================================================
# End of code
# =============================================================================