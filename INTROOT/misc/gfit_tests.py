#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-06-07 at 15:49

@author: cook
"""

import numpy as np
from SpirouDRS.fortran import fitgaus as fitgausf
from SpirouDRS.fortran import gfit
from SpirouDRS.spirouCore.spirouMath import gauss_function
import matplotlib.pyplot as plt
import time

# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    xx = np.linspace(-4, 4, 100)
    dd = gauss_function(xx, 5, 0, 1, 0.05)
    gcoeffs = np.array([4.9, 0.2, 0.9, 0])

    # arguments
    args = [xx, dd, np.ones_like(xx), gcoeffs]

    # mode 0
    time0 = time.time()
    siga0 = np.zeros_like(gcoeffs)
    cfit0 = np.zeros_like(xx)
    fitgausf.fitgaus(xx, dd, np.ones_like(xx), gcoeffs, siga0, cfit0)
    time1 = time.time()

    # mode 1
    time2 = time.time()
    a1, siga1, cfit1 = gfit.fitgaus(*args, mode=0)
    time3 = time.time()

    # mode 2
    time4 = time.time()
    a2, siga2, cfit2 = gfit.fitgaus(*args, mode=1)
    time5 = time.time()

    # mode 3
    time6 = time.time()
    a3, siga3, cfit3 = gfit.fitgaus(*args, mode=2)
    time7 = time.time()



    # timings
    output = '{0:10s} = {1:.4e}'
    print('=' * 50, '\nTimings\n', '='*50)
    print(output.format('Fortran', time1 - time0))
    print(output.format('Python (gaussj_fortran)', time3-time2))
    print(output.format('Python (gaussj melissa)', time5-time4))
    print(output.format('Python (gaussj neil)', time7-time6))

    # plot
    plt.close()
    fig, frames = plt.subplots(nrows=2, ncols=1)
    frames[0].scatter(xx, dd, color='k', label='input')
    frames[0].plot(xx, cfit0, color='r', label='Fortran')
    frames[0].plot(xx, cfit1, color='b', label='Python (gaussj_fortran)')
    frames[0].plot(xx, cfit2, color='g', label='Python (gaussj melissa)')
    frames[0].plot(xx, cfit2, color='m', label='Python (gaussj neil)')
    frames[0].legend(loc=0)
    frames[1].plot(cfit0 - cfit1, label='Fortan - gaussj_fortran')
    frames[1].plot(cfit0 - cfit2, label='Fortan - gaussj melissa')
    frames[1].plot(cfit1 - cfit2, label='gaussj_fortran - gaussj melissa')
    frames[1].plot(cfit1 - cfit3, label='gaussj_fortran - gaussj neil')
    frames[1].plot(cfit2 - cfit3, label='gaussj melissa - gaussj neil')
    frames[1].legend(loc=0)
    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================
