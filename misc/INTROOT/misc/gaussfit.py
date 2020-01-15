
import numpy as np
from SpirouDRS.spirouCore.spirouMath import linear_minimization as lin_mini


def gauss_funct(x, a):
    #
    # translated from IDL'S gaussfit function
    # used to generate a Gaussian but also returns its derivaties for
    # function fitting
    #
    # parts of the comments from the IDL version of the code --
    #
    # NAME:
    #   GAUSS_FUNCT
    #
    # PURPOSE:
    #   EVALUATE THE SUM OF A GAUSSIAN AND A 2ND ORDER POLYNOMIAL
    #   AND OPTIONALLY RETURN THE VALUE OF IT'S PARTIAL DERIVATIVES.
    #   NORMALLY, THIS FUNCTION IS USED BY CURVEFIT TO FIT THE
    #   SUM OF A LINE AND A VARYING BACKGROUND TO ACTUAL DATA.
    #
    # CATEGORY:
    #   E2 - CURVE AND SURFACE FITTING.
    # CALLING SEQUENCE:
    #   FUNCT,X,A,F,pder
    # INPUTS:
    #   X = VALUES OF INDEPENDENT VARIABLE.
    #   A = PARAMETERS OF EQUATION DESCRIBED BELOW.
    # OUTPUTS:
    #   F = VALUE OF FUNCTION AT EACH X(I).
    #   pder = matrix with the partial derivatives for function fitting
    #
    # PROCEDURE:
    #   F = A(0)*EXP(-Z^2/2) + A(3) + A(4)*X + A(5)*X^2
    #   Z = (X-A(1))/A(2)
    #   Elements beyond A(2) are optional.
    #

    n = len(a)
    nx = len(x)
    #
    zz = (x - a[1]) / a[2]  #
    ezz = np.exp(-zz ** 2 / 2.)  # GAUSSIAN PART
    #
    if n == 3:
        ff = a[0] * ezz
    if n == 4:
        ff = a[0] * ezz + a[3]
    if n == 5:
        ff = a[0] * ezz + a[3] + a[4] * x
    if n == 6:
        ff = a[0] * ezz + a[3] + a[4] * x + a[5] * x ^ 2
    #
    pder = np.zeros([nx, n])
    pder[:, 0] = ezz  # COMPUTE PARTIALS
    pder[:, 1] = a[0] * ezz * zz / a[2]
    pder[:, 2] = pder[:, 1] * zz
    if n > 3:
        pder[:, 3] = 1.0
    if n > 4:
        pder[:, 4] = x
    if n > 5:
        pder[:, 5] = x ** 2
    # noinspection PyUnboundLocalVariable
    return ff, pder


def gaussfit(xpix, ypix, nn):
    # fits a Gaussian function to xpix and ypix without prior
    # knowledge of parameters. The gaussians are expected to have
    # their peaks within the min/max range of xpix
    # the are expected to be reasonably close to Nyquist-sampled
    # nn must be an INT in the range between 3 and 6
    #
    # nn=3 -> the Gaussian has a floor of 0, the output will have 3 elements
    # nn=4 -> the Gaussian has a floor that is non-zero
    # nn=5 -> the Gaussian has a slope
    # nn=6 -> the Guassian has a 2nd order polynomial floor
    #
    # outputs ->
    # [ amplitude , center of peak, amplitude of peak, [dc level], [slope],
    # [2nd order tern] ]
    #

    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * np.nanmedian(np.gradient(xpix)) / 2.354

    if nn == 3:
        # only amp, cen and ew
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess]
    if nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix)]
    if nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix), 0]
    if nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix), 0, 0]

    residu_prev = np.array(ypix)

    # noinspection PyUnboundLocalVariable
    gfit, pder = gauss_funct(xpix, a0)

    rms = 99
    nite = 0

    # loops for 20 iterations MAX or an RMS with an RMS change in residual
    # smaller than 1e-6 of peak
    while (rms > 1e-6) & (nite <= 20):
        gfit, pder = gauss_funct(xpix, a0)
        residu = ypix - gfit

        amps, fit = lin_mini(residu, pder)
        a0 += amps
        rms = np.std(residu - residu_prev) / (np.max(ypix) - np.min(ypix))

        residu_prev = residu
        nite += 1

    return a0, gfit
