import numpy as np

try:
    from numba import jit
    HAS_NUMBA = True
except:
    jit = None
    HAS_NUMBA = False

def jitwrapper(**options):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if HAS_NUMBA:
                return jit(func, **options)(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


@jitwrapper(nopython=True)
def test_numba(x):
    y = []
    for i in range(100):
        for j in range(100):
            for k in range(10):
                y.append(np.sqrt(x + i + j + k)**3)
    return y


def lin_mini(vector, sample):
    # wrapper function that sets everything for the @jit later
    # In particular, we avoid the np.zeros that are not handled
    # by numba

    # size of input vectors and sample to be adjusted
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

    # we check if there are NaNs in the vector or the sample
    # if there are NaNs, we'll fit the rest of the domain
    isnan = (np.sum(np.isnan(vector)) != 0) or (np.sum(np.isnan(sample)) != 0)

    if case == 1:

        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=0))
            # redefine the input vector to avoid NaNs
            vector = vector[keep]
            sample = sample[:, keep]

            sz_sample = sample.shape
            sz_vector = vector.shape

        # matrix of covariances
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        # cross-terms of vector and columns of sample
        v = np.zeros(sz_sample[0])
        # reconstructed amplitudes
        amps = np.zeros(sz_sample[0])
        # reconstruted fit
        recon = np.zeros(sz_sample[1])

    if case == 2:
        # same as for case 1, but with axis flipped
        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=1))
            vector = vector[keep]
            sample = sample[keep, :]

            sz_sample = sample.shape
            sz_vector = vector.shape

        mm = np.zeros([sz_sample[1], sz_sample[1]])
        v = np.zeros(sz_sample[1])
        amps = np.zeros(sz_sample[1])
        recon = np.zeros(sz_sample[0])

    # pass all variables and pre-formatted vectors to the @jit part of the code
    amp_out, recon_out = linear_minimization(vector, sample, mm, v, sz_sample,
                                             case,
                                             recon, amps)

    # if we had NaNs in the first place, we create a reconstructed vector
    # that has the same size as the input vector, but pad with NaNs values
    # for which we cannot derive a value
    if isnan:
        recon_out2 = np.zeros_like(keep) + np.nan
        recon_out2[keep] = recon_out
        recon_out = recon_out2

    return amp_out, recon_out


@jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @nji
def linear_minimization(vector,sample,mm,v,sz_sample,case,recon,amps):
    #raise ValueError(emsg.format(func_name))
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
        for i in range(sz_sample[0]):
            recon += amps[i] * sample[i, :]
        return amps, recon

    if case == 2:
        # same as for case 1 but with axis flipped
        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.sum(sample[:, i] * sample[:, j])
                mm[j, i] = mm[i, j]
            v[i] = np.sum(vector * sample[:, i])

        if np.linalg.det(mm) == 0:
            return amps, recon

        inv = np.linalg.inv(mm)
        for i in range(len(v)):
            for j in range(len(v)):
                amps[i]+=inv[i,j]*v[j]

        for i in range(sz_sample[1]):
            recon += amps[i] * sample[:, i]
        return amps, recon


