#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fitgaus.py

Fit gaussian to a line. Non-linear 4-parameter gaussian fit by the
Levenberg-Marquardt method.


Created on 2018-06-02 at 11:40

@author: mhobson

Last modified:

Python copy of the fitgaus.f routine by F Bouchy
"""

import numpy as np


__NAME__ = 'fitgaus.py'  # temp


def fitgaus(x, y, wei, a, mode=0):
    """
    Iterative gaussian fit.
    Inputs:
        x: numpy array, the x data points
        y: numpy array, the y data points
        wei: numpy array, the weights to the data points
        a: numpy array, first guess coefficients (amplitude, mean, fwhm, 0.0)

    Outputs:
        a: coefficients (amplitude, mean, fwhm, ?)
        siga: uncertainty on the coefficients
        fit: value of the fitted gaussian function

    """
    func_name = __NAME__ + '.fitgaus()'

    # get the sizes
    ndata = len(y)
    m = len(a)

    # get the inverse of the weights
    sig = 1 / wei

    # First iteration
    alamda = -1.
    # define dummy alpha and beta matrix, ochisq for first call
    alpha = np.zeros((4, 4))
    beta = np.zeros((4))
    ochisq = 0
    a, covar, alpha, chisq, alamda, beta, ochisq = mrqmin(x, y, sig, ndata, a,
                                                          m, alpha, alamda,
                                                          beta, ochisq, mode)
    # set small alambda0 term and iterate until alambda is better than this
    alamda0 = 1.e-8
    cpt = 0
    # Iterate to convergence
    while ((alamda > alamda0) and (cpt < 100)):
        cpt = cpt + 1
        #    print(cpt) # test
        a, covar, alpha, chisq, alamda, beta, ochisq = mrqmin(x, y, sig, ndata,
                                                              a, m, alpha,
                                                              alamda, beta,
                                                              ochisq, mode)
    # Last iteration to calculate errors
    alamda = 0.
    # === all this does is expand the covar matrix via covsrt to account
    #     for fixed parameters
    # === as we don't have any it's ignored
    # a, covar, alpha, chisq, alamda = mrqmin(x, y, sig, ndata, a,
    #                                         m, alpha, alamda)
    # define degrees of freedom
    if ndata > 4:
        nfree = ndata - 4
    else:
        nfree = ndata
    # calculate errors
    siga = np.sqrt(np.diag(covar)) * np.sqrt(chisq / nfree)
    # evaluate the gaussian fit
    arg = (x - a[1]) / a[2]
    ex = np.exp(-(arg ** 2) / 2.)
    fit = a[0] * ex + a[3]

    return a, siga, fit


def gfuncs(x, a):
    """
    Evaluates the (gaussian) function and derivatives
    Inputs
        x: numpy array, the x data
        a: numpy array, the coefficients
    Outputs
        y: numpy array, the evaluated gaussian
        dyda: numpy array, the derivatives
    """
    func_name = __NAME__ + '.gfuncs()'
    # auxiliary variables (tbc)
    arg = (x - a[1]) / a[2]
    ex = np.exp(-(arg ** 2) / 2.)
    # calculate modified y values
    y = a[0] * ex + a[3]
    # define dyda array
    dyda = np.zeros((4))
    # calculate dyda
    dyda[0] = ex
    dyda[1] = a[0] * ex * arg / a[2]
    dyda[2] = a[0] * ex * arg ** 2 / a[2]
    dyda[3] = 1.
    return y, dyda


def mrqmin(x, y, sig, ndata, a, ma, alpha, alamda, beta, ochisq, mode):
    """
    Levenberg-Marquardt method

    Inputs:
        x: array, x data
        y: array, y data
        sig: array, weights on the data
        ndata: number of data points (not used?)
        a: initial parameters
        ma: number of parameters to fit (set to 4, not used?)
        alpha: workspace, eventually curvature matrix
        alamda: initial fitting step

    Outputs:
        a: updated parameters
        covar: covariance matrix
        alpha: workspace, eventually curvature matrix
        chisq: chi square
        alamda: updated fitting step

    """

    func_name = __NAME__ + '.mrqmin()'
    # set ma
    ma = 4
    # call mrqcof
    if alamda < 0:
        alamda = 0.001
        alpha, beta, chisq = mrqcof(x, y, sig, ndata, a, ma)
        ochisq = chisq
        atry = a
    # define the covariance matrix
    covar = np.copy(alpha)
    # multiply the diagonal of the covariance matrix by 1+alamda
    np.fill_diagonal(covar, covar.diagonal() * (1 + alamda))
    # define da
    da = np.copy(beta)
    # call gaussj
    if mode == 0:
        covar, da = gaussj_fortran(covar, ma, da, 1, 1)
    elif mode == 1:
        covar, da = gaussj0(covar, ma, da, 1, 1)
    elif mode == 2:
        covar, da = gaussj1(covar, ma, da, 1, 1)
    else:
        raise ValueError('mode="{0}" not understood'.format(mode))

    # ----- this section not needed, to be removed
    # (applies only if you have fixed parameters which we don't)
    # check value of alamda -
    # if alamda == 0:
    # call covsrt
    #   dummy2 = covsrt(covar, ma)
    # -----

    # redefine atry, the new fit parameters
    atry = a + da
    # run mrqcof again on updated a values
    covar, da, chisq = mrqcof(x, y, sig, ndata, atry, ma)
    # if new chisq is an improvement, update values
    if chisq < ochisq:
        alamda = 0.1 * alamda
        ochisq = chisq
        alpha = np.copy(covar)
        beta = np.copy(da)
        a = np.copy(atry)
    # if new chisq is not an improvement, increase value of alamda
    else:
        alamda = 10. * alamda
        chisq = ochisq

    return a, covar, alpha, chisq, alamda, beta, ochisq


def covsrt(covar, ma):
    """
    NOT NEEDED to be removed

    :param covar: np array, 4x4
    :param ma: number of parameters to fit (set to 4?)
    :return:
    """

    k = ma - 1
    for j in range(ma - 1, -1, -1):
        for i in range(ma):
            covar[i, k], covar[i, j] = swap(covar[i, k], covar[i, j])
        for i in range(ma):
            covar[k, i], covar[j, i] = swap(covar[k, i], covar[j, i])
        k = k - 1


def gausstest(a, n, b):
    # test function for combining old and new versions
    indxc = np.zeros((4))
    indxr = np.zeros((4))
    # define ipiv as zeros
    ipiv = np.zeros((n))
    for i in range(n):
        big = 0.
        for j in range(n):
            if ipiv[j] != 1:
                for k in range(n):
                    if ipiv[k] == 0:
                        if abs(a[j, k] > big):
                            big = abs(a[j, k])
                            irow = j
                            icol = k
        # update ipiv
        ipiv[icol] = ipiv[icol] + 1
        # move pivot element to the diagonal
        a[irow, :], a[icol, :] = swap(a[irow, :], a[icol, :])
        b[irow], b[icol] = swap(b[irow], b[icol])
        indxr[i] = irow
        indxc[i] = icol
        pivinv = 1. / a[icol, icol]
        a[icol, icol] = 1.
        # divide pivot row by pivot element
        a[icol, :] = a[icol, :] * pivinv
        b[icol] = b[icol] * pivinv
        # reduce the rows (except for pivot row)
        for ll in range(n):
            if ll != icol:
                dum = a[ll, icol]
                a[ll, icol] = 0.
                a[ll, :] = a[ll, :] - a[icol, :] * dum
                b[ll] = b[ll] - b[icol] * dum
    # unscramble the solution by permuting in reverse order
    for l in range(n - 1, -1, -1):
        if indxr[l] != indxc[l]:
            out = swap(a[:, int(indxr[l])], a[:, int(indxc[l])])
            a[:, int(indxr[l])], a[:, int(indxc[l])] = out

    return a, b


def mrqcof(x, y, sig, ndata, a, ma=4):
    """
    "Used by mrqin to evaluate the linearized fitting matrix alpha,
    and vector beta, and calculate chisq"

    Inputs:
        x: array, x data
        y: array, y data
        sig: array, weights on the data
        ndata: length of data (not used?)
        a: fit parameters
        ma: length of coefficients, seems to be set to 4?

    Ouptuts:
        alpha: array, 4x4
        beta: array
        chisq: float

    """
    func_name = __NAME__ + '.mrqcof()'

    # define alpha as a 4x4 zeroes matrix
    alpha = np.zeros((4, 4))
    # define beta as a 1x4 zeroes array
    beta = np.zeros((4))
    # set chisq to 0
    chisq = 0
    # TODO loop over data length may be arrayable
    for i in range(ndata):
        # call funcs - is called for each x in data, this is arrayed,
        # returns new y and dyda
        ymod, dyda = gfuncs(x[i], a)
        # calculate inverse of weight squared
        sig2i = 1 / (sig[i] ** 2)
        dy = y[i] - ymod
        wt = dyda * sig2i
        # do the matrix product of wt and dyda, add it to alpha
        alpha = alpha + np.matrix(wt).getT() * np.matrix(dyda)
        # calculate the new value of beta
        beta = beta + dy * wt
        # calculate new chisq value
        chisq = chisq + np.nansum(dy * dy * sig2i)
    # TODO loops may be possible to eliminate?
    for j in range(1, 4):
        for k in range(0, j):
            alpha[k, j] = alpha[j, k]

    return alpha, beta, chisq


def swap(v1, v2):
    # get the type of v1
    kind = type(v1)
    # copy v1 into tmp holder
    tmp = kind(v1)
    # copy v2 into v1
    v1 = kind(v2)
    # copy tmp into v2
    v2 = kind(tmp)
    # return v1 and v2 swapped
    return v1, v2


# =============================================================================
# Exact copy of fortran gaussj structure (all loops)
# =============================================================================
def gaussj0(a, n, b, m=1, mp=1):
    """
    Linear equation solution by Gauss-Jordan elimination
    Inputs:
        a: matrix to be reduced
        n: dimensions of the matrix
        b: matrix containing the m right-hand side vectors
        m:
        mp:

    Outputs:
        a: inverse of the input matrix
        b:
    """
    func_name = __NAME__ + '.gaussj()'
    # dummy arrays (check)
    indxc = np.zeros((4))
    indxr = np.zeros((4))
    # define ipiv as zeros
    ipiv = np.zeros((n))
    for i in range(n):
        # find pivot element
        # select only rows of a corresponding to ipiv != 1
        row_mask = np.matrix(np.where(ipiv != 1, 1, 0))
        # select only columns of a corresponding to ipiv == 0
        col_mask = np.matrix(np.where(ipiv == 0, 1, 0))
        # define the full mask
        mask = np.logical_not(row_mask.getT() * col_mask)
        # apply the mask
        a2 = np.ma.masked_array(a, mask)
        # get the maximum value of the masked array
        big = np.max(a2)
        # get the location of the maximum
        irow, icol = np.where(a2 == np.max(a2))
        # if more than one maximum, get location of last
        irow = irow[-1]
        icol = icol[-1]
        # update ipiv
        ipiv[icol] = ipiv[icol] + 1
        # move pivot element to the diagonal
        a[irow, :], a[icol, :] = swap(a[irow, :], a[icol, :])
        b[irow], b[icol] = swap(b[irow], b[icol])
        indxr[i] = irow
        indxc[i] = icol
        pivinv = 1. / a[icol, icol]
        a[icol, icol] = 1.
        # divide pivot row by pivot element
        a[icol, :] = a[icol, :] * pivinv
        b[icol] = b[icol] * pivinv
        # reduce the rows (except for pivot row)
        for ll in range(n):
            if ll != icol:
                dum = a[ll, icol]
                a[ll, icol] = 0.
                a[ll, :] = a[ll, :] - a[icol, :] * dum
                b[ll] = b[ll] - b[icol] * dum
    # unscramble the solution by permuting in reverse order
    for l in range(n - 1, -1, -1):
        if indxr[l] != indxc[l]:
            out = swap(a[:, int(indxr[l])], a[:, int(indxc[l])])
            a[:, int(indxr[l])], a[:, int(indxc[l])] = out
    return a, b


def gaussj1(a, n, b, m=1, mp=1):
    """
    Linear equation solution by Gauss-Jordan elimination
    Inputs:
        a: matrix to be reduced
        n: dimensions of the matrix
        b: matrix containing the m right-hand side vectors
        m:
        mp:

    Outputs:
        a: inverse of the input matrix
        b:
    """
    func_name = __NAME__ + '.gaussj()'
    # dummy arrays (check)
    indxc = np.zeros((4))
    indxr = np.zeros((4))
    # define ipiv as zeros
    ipiv = np.zeros((n))
    # find pivot element
    # loop around all elements in a
    for i in range(n):
        # select only rows where ipiv is 1
        row_mask = (ipiv != 1)
        # select only columns where ipiv == 0
        col_mask = (ipiv == 0)
        # define the full mask
        mask = ~np.outer(row_mask, col_mask)
        # apply the mask
        a2 = np.copy(a)
        a2[mask] = np.nan
        # get the location of the maximum
        irow, icol = np.where(a2 == np.nanmax(a2))
        # if more than one maximum, get location of last
        irow, icol = irow[-1], icol[-1]
        # update ipiv
        ipiv[icol] = ipiv[icol] + 1
        # move pivot element to the diagonal
        a[irow, :], a[icol, :] = swap(a[irow, :], a[icol, :])
        b[irow], b[icol] = swap(b[irow], b[icol])
        # add indices to dummy arrays
        indxr[i], indxc[i] = irow, icol
        # calculate pivot value
        pivinv = 1. / a[icol, icol]
        a[icol, icol] = 1.0
        # divide pivot row by pivot element
        a[icol, :] = a[icol] * pivinv
        b[icol] = b[icol] * pivinv
        # reduce the rows (except for pivot row)
        # reduce the rows (except for pivot row)
        for ll in range(n):
            if ll != icol:
                dum = a[ll, icol]
                a[ll, icol] = 0.
                a[ll, :] = a[ll, :] - a[icol, :] * dum
                b[ll] = b[ll] - b[icol] * dum
    # unscramble the solution by permuting in reverse order
    for l in range(n - 1, -1, -1):
        if indxr[l] != indxc[l]:
            out = swap(a[:, int(indxr[l])], a[:, int(indxc[l])])
            a[:, int(indxr[l])], a[:, int(indxc[l])] = out

    return a, b


def gaussj_fortran(a, n, b, m=1, mp=1):
    """
    Linear equation solution by Gauss-Jordan elimination
    Inputs:
        a: matrix to be reduced
        n: dimensions of the matrix
        b: matrix containing the m right-hand side vectors
        m:
        mp:

    Outputs:
        a: inverse of the input matrix
        b:
    """
    func_name = __NAME__ + '.gaussj_fortran()'
    # dummy arrays (check)
    indxc = np.zeros((4))
    indxr = np.zeros((4))
    # define ipiv as zeros
    ipiv = np.zeros((n))
    # find pivot element
    for i in range(n):
        big = 0.
        for j in range(n):
            if ipiv[j] != 1:
                for k in range(n):
                    if ipiv[k] == 0:
                        if abs(a[j, k] >= big):
                            big = abs(a[j, k])
                            irow = j
                            icol = k
        ipiv[icol] = ipiv[icol] + 1
        # move pivot element to the diagonal
        if irow != icol:
            for l in range(n):
                dum = a[irow, l]
                a[irow, l] = a[icol, l]
                a[icol, l] = dum
            dum = b[irow]
            b[irow] = b[icol]
            b[icol] = dum
        indxr[i] = irow
        indxc[i] = icol
        pivinv = 1. / a[icol, icol]
        a[icol, icol] = 1.
        for l in range(n):
            a[icol, l] = a[icol, l] * pivinv
        b[icol] = b[icol] * pivinv
        # reduce all rows except the pivot one
        for ll in range(n):
            if ll != icol:
                dum = a[ll, icol]
                a[ll, icol] = 0.
                for l in range(n):
                    a[ll, l] = a[ll, l] - a[icol, l] * dum
                b[ll] = b[ll] - b[icol] * dum
    # unscramble the solution by permuting in reverse order
    for l in range(n - 1, -1, -1):
        if indxr[l] != indxc[l]:
            for k in range(n):
                dum = a[k, int(indxr[l])]
                a[k, int(indxr[l])] = a[k, int(indxc[l])]
                a[k, int(indxc[l])] = dum
    return a, b
