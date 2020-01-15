#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-09 12:38
@author: ncook
Version 0.0.1
"""
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = './'


# -----------------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    lowf = 16

    x = np.linspace(0, 2048, 512)
    y = np.sin(x / 128.) + np.random.random(size=len(x))


    def func(x1, a1, b1):
        return np.sin(x1 / a1) + b1


    xfit = np.linspace(0, 2048, 4096)

    cs = CubicSpline(x, y)
    f = interp1d(x, y)

    yfft = np.fft.fft(y)
    lowyfft = np.zeros_like(yfft)
    lowyfft[:lowf] = yfft[:lowf]
    y2 = np.fft.ifft(lowyfft).real

    p0 = [100.0, 1.0]
    # noinspection PyTypeChecker
    ppot, pcov = curve_fit(func, x, y, p0=p0)
    yfit3 = func(xfit, *ppot)

    yfit1 = cs(xfit)

    yfit2 = f(xfit)

    plt.scatter(x, y)
    plt.plot(xfit, yfit1, label='CubicSpline')
    plt.plot(xfit, yfit2, label='Interp1D')
    plt.plot(x, y2, label='low pass FFT')
    plt.plot(xfit, yfit3, label='curve fit')

    plt.legend(loc=0)
    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================
