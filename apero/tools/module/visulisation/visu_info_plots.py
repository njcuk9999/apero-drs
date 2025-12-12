#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 14:10

@author: cook
"""
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from astropy.io import fits

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.core import drs_text


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.visulisation.visu_info_plots.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def plotend(params: ParamDict, filename):

    # deal with show vs save
    if params['INPUTS']['INFOSAVE']:
        pkind = 'summary'
    else:
        pkind = 'show'
    # get path
    if drs_text.null_text(params['INPUTS']['INFOPATH'], ['None', 'Null', '']):
        filepath = params['INPUTS']['INFOPATH']
    else:
        filepath = params['INPUTS']['PATH']
    # remove any extension
    basename = os.path.splitext(os.path.basename(filename))[0]
    # get full plot path
    filename = os.path.join(filepath, basename) + '.png'
    # deal with summary plots
    if pkind == 'summary':
        # 1. save to file
        print('Saving figure to {0}'.format(filename))
        plt.savefig(filename)
        plt.close()
    # deal with show plots
    elif pkind == 'show':
        plt.show(block=True)
        plt.close()
    else:
        pass



def plot_drs_post_e(params: ParamDict, filename: str):

    # update instrument
    instrument = str(base.IPARAMS['INSTRUMENT'])
    # load pconst
    pconst = constants.pload(instrument=instrument)
    # get science fiber
    science_fibers, _ = pconst.FIBER_KINDS()

    # create figure
    fig, frame = plt.subplots(1, 1, figsize=(10, 8))
    # loop around science fibers
    for science_fiber in science_fibers:
        wave = fits.getdata(filename, extname='Wave{0}'.format(science_fiber))
        blaze = fits.getdata(filename, extname='Blaze{0}'.format(science_fiber))
        data = fits.getdata(filename, extname='Flux{0}'.format(science_fiber))
        frame.plot(wave.ravel(), data.ravel()/blaze.ravel(),
                   label='Fiber {0}'.format(science_fiber))
    # add legend
    frame.legend()
    frame.set_title('APERO extracted spectrum')
    frame.set_xlabel('Wavelength [nm]')
    frame.set_ylabel('Flux')

    plotend(params, filename)



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
