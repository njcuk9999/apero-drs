#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
visu_WAVE_spirou.py [night_directory] [*e2ds.fits]

Recipe to display hc e2ds file, plus wavelength catalogue and fitted lines

Created on 2018-06-22 at 15:30

@author: melissa-hobson

Last modified: 2018-06-22


"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'visu_WAVE_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    # TODO add this recipe to recipe control
    p = spirouStartup.Begin(recipe='cal_HC_E2DS_spirou.py')
    # get parameters from configuration files and run time arguments
    customargs = spirouStartup.GetCustomFromRuntime([0], [str], ['reffile'])
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')
    # setup files and get fiber
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    gfkwargs = dict(path=p['REDUCED_DIR'], filename=p['REFFILE'])
    p['REFFILENAME'] = spirouStartup.GetFile(p, **gfkwargs)
    p.set_source('REFFILENAME', __NAME__ + '/main()')
    # get the fiber type
    p['FIBER'] = 'AB'
    e2ds, hdr, cmt, nx, ny = spirouImage.ReadImage(p)
    wave = spirouImage.ReadWaveFile(p)
    blaze = spirouImage.ReadBlazeFile(p)

    # ----------------------------------------------------------------------
    # Get lamp params
    # ----------------------------------------------------------------------

    # get relevant (cass/ref) fiber position (for lamp identification)
    p['FIB_TYP'] = [p['FIBER']]
    gkwargs = dict(return_value=True, dtype=str)
    if p['FIB_TYP'] == ['C']:
        p['FIB_POS'] = spirouImage.ReadParam(p, hdr, 'kw_CREF',
                                             **gkwargs)
    elif p['FIB_TYP'] in (['AB'], ['A'], ['B']):
        p['FIB_POS'] = spirouImage.ReadParam(p, hdr, 'kw_CCAS',
                                             **gkwargs)
    else:
        emsg1 = ('Fiber position cannot be identified for fiber={0}'
                 .format(p['FIB_TYP']))
        emsg2 = '    function={0}'.format(__NAME__)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p)

    # ----------------------------------------------------------------------
    # Get catalogue and fitted line list
    # ----------------------------------------------------------------------
    # load line file (from p['IC_LL_LINE_FILE'])
    ll_line_cat, ampl_line_cat = spirouImage.ReadLineList(p)
    # construct fitted lines table filename
    wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE(p)
    WLOG('', p['LOG_OPT'], wavelltbl)
    # read fitted lines
    ll_line_fit, ampl_line_fit = np.genfromtxt(wavelltbl, skip_header=4,
                                               skip_footer=2, unpack=True,
                                               usecols=(1, 3))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------

    plt.ion()
    plt.figure()

    for order_num in np.arange(nx):
        plt.plot(wave[order_num], e2ds[order_num])

    for line in range(len(ll_line_cat)):
        plt.vlines(ll_line_cat[line],0,100000+
                   max(np.min(e2ds), ampl_line_cat[line]),
                   colors='darkgreen', linestyles='dashed')

    for line in range(len(ll_line_fit)):
        plt.vlines(ll_line_fit[line],0,100000+
                   max(np.min(e2ds), ampl_line_fit[line]),
                   colors = 'magenta', linestyles='dashdot')


    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Flux e-')


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
