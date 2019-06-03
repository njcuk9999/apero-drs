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
    p = spirouStartup.Begin(recipe=__NAME__)
    # get parameters from configuration files and run time arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str], ['reffile'])
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
    e2ds, hdr, nx, ny = spirouImage.ReadImage(p)

    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    _, wave, _ = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                             fiber=wave_fiber)
    blaze = spirouImage.ReadBlazeFile(p)

    # ----------------------------------------------------------------------
    # Get lamp params
    # ----------------------------------------------------------------------

    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, hdr)

    # ----------------------------------------------------------------------
    # Get catalogue and fitted line list
    # ----------------------------------------------------------------------
    # load line file (from p['IC_LL_LINE_FILE'])
    ll_line_cat, ampl_line_cat = spirouImage.ReadLineList(p)
    # construct fitted lines table filename
    wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE(p)
    WLOG(p, '', wavelltbl)
    # read fitted lines
    ll_ord, ll_line_fit, ampl_line_fit = np.genfromtxt(wavelltbl,
                                                       skip_header=4,
                                                       skip_footer=2,
                                                       unpack=True,
                                                       usecols=(0, 1, 3))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------

    # define line colours
    col = ['magenta', 'purple']
    # get order parity
    ll_ord_par = np.mod(ll_ord, 2)
    print(ll_ord_par)
    col2 = [col[int(x)] for x in ll_ord_par]

    # start interactive plot
    sPlt.start_interactive_session(p)

    plt.figure()

    for order_num in np.arange(nx):
        plt.plot(wave[order_num], e2ds[order_num])

    # get heights
    heights = []
    for line in range(len(ll_line_cat)):
        heights.append(200000 + np.max([np.min(e2ds), ampl_line_cat[line]]))
    # plot ll_line_cat
    plt.vlines(ll_line_cat, 0, heights, colors='darkgreen',
               linestyles='dashed')

    # get heights
    heights = []
    for line in range(len(ll_line_fit)):
        heights.append(200000 + np.max([np.min(e2ds), ampl_line_fit[line]]))
    # plot ll_line_fit
    plt.vlines(ll_line_fit, 0, heights, colors=col2,
               linestyles='dashdot')

    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Flux e-')
    plt.title(p['REFFILENAME'])

    # end interactive session
    #    sPlt.end_interactive_session()

    # old code:
    # plt.ion()
    # plt.figure()
    #
    # for order_num in np.arange(nx):
    #     plt.plot(wave[order_num], e2ds[order_num])
    #
    # for line in range(len(ll_line_cat)):
    #     plt.vlines(ll_line_cat[line], 0, 200000 +
    #                max(np.min(e2ds), ampl_line_cat[line]),
    #                colors='darkgreen', linestyles='dashed')
    #
    # for line in range(len(ll_line_fit)):
    #     plt.vlines(ll_line_fit[line], 0, 200000 +
    #                max(np.min(e2ds), ampl_line_fit[line]),
    #                colors='magenta', linestyles='dashdot')
    #
    # plt.xlabel('Wavelength [nm]')
    # plt.ylabel('Flux e-')

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
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
