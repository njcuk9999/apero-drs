#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spirou plotting functions

Created on 2017-11-02 at 16:29

@author: cook

Import rules: Only from spirouConfig and spirouCore
"""
from __future__ import division
import numpy as np
import time
import matplotlib
from astropy import constants as cc
from astropy import units as uu

from SpirouDRS import spirouConfig
from . import spirouLog

# TODO: Is there a better fix for this?
# fix for MacOSX plots freezing
gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui, warn=False, force=True)
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        break
    except:
        continue
if matplotlib.get_backend() == 'MacOSX':
    matplotlib_emsg = ['OSX Error: Matplotlib MacOSX backend not supported and '
                       'Qt5Agg not available']
else:
    matplotlib_emsg = []


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouPlot.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouLog.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# Speed of light
from __future__ import division
import numpy as np
import time
import matplotlib
from astropy import constants as cc
from astropy import units as uu

from SpirouDRS import spirouConfig
from . import spirouLog

# TODO: Is there a better fix for this?
# fix for MacOSX plots freezing
gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui, warn=False, force=True)
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        break
    except:
        continue
if matplotlib.get_backend() == 'MacOSX':
    matplotlib_emsg = ['OSX Error: Matplotlib MacOSX backend not supported and '
                       'Qt5Agg not available']
else:
    matplotlib_emsg = []


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouPlot.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouLog.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# Speed of light
speed_of_light_ms = cc.c.to(uu.m/uu.s).value
speed_of_light = cc.c.to(uu.km/uu.s).value
# -----------------------------------------------------------------------------
INTERACTIVE_PLOTS = spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED()
# check for matplotlib import errors
if len(matplotlib_emsg) > 0:
    WLOG('error', DPROG, matplotlib_emsg)


# =============================================================================
# General plotting functions
# =============================================================================
def start_interactive_session(interactive=False):
    """
    Start interactive plot session, if required and if
    spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED() is True

    :param interactive: bool, if True start interactive session

    :return None:
    """
    if interactive is True:
        # plt.ion()
        matplotlib.interactive(True)
        pass
    # start interactive plot
    elif INTERACTIVE_PLOTS:
        # plt.ion()
        matplotlib.interactive(True)
        pass


def end_interactive_session(interactive=False):
    """
    End interactive plot session, if required and if
    spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED() is True

    :param interactive: bool, if True end interactive session

    :return None:
    """
    if not interactive and not INTERACTIVE_PLOTS:
        plt.show()
        plt.close()


def end_plotting():
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()
    else:
        pass


def define_figure(num=1):
    """
    Define a figure number (mostly for use in interactive mode)

    :param num: int, a figure number

    :return figure: plt.figure instance
    """
    return plt.figure(num)


def closeall():
    """
    Close all matplotlib plots currently open

    :return None:
    """
    plt.close('all')


# =============================================================================
# dark plotting functions
# =============================================================================
def darkplot_image_and_regions(pp, image):
    """
    Plot the image and the red and plot regions

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                med_full: float, the median value of the non-Nan image values
                IC_CCDX_BLUE_LOW: int, the lower extent of the blue window in x
                IC_CCDX_BLUE_HIGH: int, the upper extent of the blue window in x
                IC_CCDY_BLUE_LOW: int, the lower extent of the blue window in y
                IC_CCDY_BLUE_HIGH: int, the upper extent of the blue window in y
                IC_CCDX_RED_LOW: int, the lower extent of the red window in x
                IC_CCDX_RED_HIGH: int, the upper extent of the red window in x
                IC_CCDY_RED_LOW: int, the lower extent of the red window in y
                IC_CCDY_RED_HIGH: int, the upper extent of the red window in y

    :param image: numpy array (2D), the image

    :return None:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot the image
    # TODO: Remove H2RG dependency
    if pp['IC_IMAGE_TYPE'] == 'H2RG':
        clim = (1., 10 * pp['MED_FULL'])
    else:
        clim = (0., 10 * pp['MED_FULL'])
    im = frame.imshow(image, origin='lower', clim=clim, cmap='jet')
    # plot the colorbar
    cbar = plt.colorbar(im, ax=frame)
    cbar.set_label('ADU/s')
    # get the blue region
    bxlow, bxhigh = pp['IC_CCDX_BLUE_LOW'], pp['IC_CCDX_BLUE_HIGH']
    bylow, byhigh = pp['IC_CCDY_BLUE_LOW'], pp['IC_CCDY_BLUE_HIGH']
    # adjust for backwards limits
    if bxlow > bxhigh:
        bxlow, bxhigh = bxhigh-1, bxlow-1
    if bylow > byhigh:
        bylow, byhigh = byhigh-1, bylow-1
    # plot blue rectangle
    brec = Rectangle((bxlow, bylow), bxhigh-bxlow, byhigh-bylow,
                     edgecolor='w', facecolor='None')
    frame.add_patch(brec)
    # get the red region
    rxlow, rxhigh = pp['IC_CCDX_RED_LOW'], pp['IC_CCDX_RED_HIGH']
    rylow, ryhigh = pp['IC_CCDY_RED_LOW'], pp['IC_CCDY_RED_HIGH']
    # adjust for backwards limits
    if rxlow > rxhigh:
        rxlow, rxhigh = rxhigh-1, rxlow-1
    if rylow > ryhigh:
        rylow, ryhigh = ryhigh-1, rylow-1
    # plot blue rectangle
    rrec = Rectangle((rxlow, rylow), rxhigh-rxlow, ryhigh-rylow,
                     edgecolor='r', facecolor='None')
    frame.add_patch(rrec)
    plt.title('Dark image with red and blue regions')

    # TODO: needs axis labels and titles
    # end plotting function properly
    end_plotting()


def darkplot_datacut(imagecut):
    """
    Plot the data cut mask

    :param imagecut: numpy array (2D), the data cut mask

    :return:
    """
    # set up figure
    fig = plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # imagecut need to be integers
    imagecut = imagecut.astype(np.int)
    # plot the image cut
    im = frame.imshow(imagecut, origin='lower', cmap='gray')
    # plot the colorbar
    fig.colorbar(im, ax=frame)
    # make sure image is bounded by shape
    plt.axis([0, imagecut.shape[0], 0, imagecut.shape[1]])
    plt.title('Dark cut mask')

    # TODO: needs axis labels and title
    # end plotting function properly
    end_plotting()


def darkplot_histograms(pp):
    """
    Plot histograms for the dark images

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                histo_full: numpy.histogram tuple (hist, bin_edges) for
                            the full image
                histo_blue: numpy.histogram tuple (hist, bin_edges) for
                            the blue part of the image
                histo_red: numpy.histogram tuple (hist, bin_edges) for
                            the red part of the image

            where:
                hist : numpy array (1D) The values of the histogram.
                bin_edges : numpy array (1D) of floats, the bin edges

    :return None:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get variables from property dictionary
    histo_f, edge_f = pp['HISTO_FULL']
    histo_b, edge_b = pp['HISTO_BLUE']
    histo_r, edge_r = pp['HISTO_RED']
    # plot the main histogram
    xf = np.repeat(edge_f, 2)
#    yf = [0] + list(np.repeat(histo_f*100/np.max(histo_f), 2)) + [0]
    yf = [0] + list(np.repeat(histo_f, 2)) + [0]
    frame.plot(xf, yf, color='green', label='Whole det')
    # plot the blue histogram
    xb = np.repeat(edge_b, 2)
#    yb = [0] + list(np.repeat(histo_b*100/np.max(histo_b), 2)) + [0]
    yb = [0] + list(np.repeat(histo_b, 2)) + [0]
    frame.plot(xb, yb, color='blue', label='Blue part')
    # plot the red histogram
    xr = np.repeat(edge_r, 2)
#    yr = [0] + list(np.repeat(histo_r*100/np.max(histo_r), 2)) + [0]
    yr = [0] + list(np.repeat(histo_r, 2)) + [0]
    frame.plot(xr, yr, color='red', label='Red part')
    frame.set_xlabel('ADU/s')
    frame.set_ylabel('Normalised frequency')
    frame.legend()

    # TODO: Needs axis labels and title
    # end plotting function properly
    end_plotting()


# =============================================================================
# localization plotting functions
# =============================================================================
def locplot_order(frame, x, y, label):
    """
    Simple plot function (added to a larger plot)

    :param frame: the matplotlib axis, e.g. plt.gca() or plt.subplot(111)
    :param x: numpy array (1D) or list, the x-axis data
    :param y: numpy array (1D) or list, the y-axis data
    :param label: string, the label for this line (used in legend)

    :return None:
    """
    frame.plot(x, y, label=label, linewidth=1.5, color='red')
    # end plotting function properly
    end_plotting()


def locplot_y_miny_maxy(y, miny=None, maxy=None):
    """
    Plots the row number against central column pixel value, smoothed minimum
    central pixel value and smoothed maximum, central pixel value

    :param y: numpy array, central column pixel value
    :param miny: numpy array, smoothed minimum central pixel value
    :param maxy: numpy array, smoothed maximum central pixel value

    :return None:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define row number
    rownumber = np.arange(len(y))
    # plot y against row number
    frame.plot(rownumber, y, linestyle='-')
    # plot miny against row number
    if miny is not None:
        frame.plot(rownumber, miny, marker='_')
    # plot maxy against row number
    if maxy is not None:
        frame.plot(rownumber, maxy, marker='_')
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')
    # end plotting function properly
    end_plotting()


def locplot_im_sat_threshold(image, threshold):
    """
    Plots the image (order_profile) below the saturation threshold

    :param image: numpy array (2D), the image
    :param threshold: float, the saturation threshold

    :return None:
    """
    # set up fig
    fig = plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1.0, threshold), cmap='gist_gray')
    # set the limits
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]))

    # TODO: Need axis labels and title

    # return fig and frame
    return fig, frame


def locplot_order_number_against_rms(pp, loc, rnum):
    """
    Plots the dispersion (RMS) of localization parameters for a fiber

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                rms_center: numpy array (1D), the RMS of the center fit for
                            each order
                rms_fwhm: numpy array (1D), the RMS of the width fit for each
                          order

    :param rnum: number of orders to plot (from 0 --> rnum)

    :return None:
    """
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.plot(np.arange(rnum), loc['RMS_CENTER'][0:rnum], label='center')
    frame.plot(np.arange(rnum), loc['RMS_FWHM'][0:rnum], label='fwhm')
    # set title labels limits
    frame.set(xlim=(0, rnum), xlabel='Order number', ylabel='RMS [pixel]',
              title=('Dispersion of localization parameters fiber {0}'
                     '').format(pp['FIBER']))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def debug_locplot_min_ycc_loc_threshold(pp, cvalues):
    """
    Plots the minimum value between the value in ycc and ic_loc_seuil (the
    normalised amplitude threshold to accept pixels for background calculation)

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_LOCSEUIL: float, Normalised amplitude threshold to accept
                             pixels for background calculation
                IC_DISPLAY_TIMEOUT: float, Interval between plots (wait time
                                    after plotting)
    :param cvalues: numpy array, normalised central column pixel values

    :return None:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define row number
    rownumber = np.arange(len(cvalues))
    # plot minimum
    frame.plot(rownumber, np.minimum(cvalues, pp['IC_LOCSEUIL']))
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')
    # turn off interactive plotting
    if not plt.isinteractive():
        pass
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)
    # end plotting function properly
    end_plotting()


def debug_locplot_finding_orders(pp, no, ncol, ind0, ind1, ind2, cgx, wx, ycc):
    """
    Plot one rows boundary conditions for finding the orders, pause after
    plotting to allow user to see this fix, and then move on to next row in
    loop (for use in loop only)

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                IC_DISPLAY_TIMEOUT: float, Interval between plots (wait time
                                    after plotting)
    :param no: int, order number
    :param ncol: int, column number
    :param ind0: int, row center value
    :param ind1: int, row top value
    :param ind2: int, row bottom value
    :param cgx: float, fit center position
    :param wx: float, fit width
    :param ycc: numpy array (1D), the central column values

    :return None:
    """
    # log output for this row
    wargs = [no, ncol, ind0, cgx, wx]
    WLOG('', pp['LOG_OPT'], '{0:d} {0:d}  {0:f}  {0:f}  {0:f}'.format(*wargs))

    xx = np.array([ind1, cgx - wx / 2., cgx - wx / 2., cgx - wx / 2., cgx,
                   cgx + wx / 2., cgx + wx / 2., cgx + wx / 2., ind2])
    yy = np.array([0., 0., max(ycc) / 2., max(ycc), max(ycc), max(ycc),
                   max(ycc) / 2., 0., 0.])
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot orders
    frame.plot(np.arange(ind1, ind2, 1.0), ycc)
    frame.plot(xx, yy)
    frame.set(xlim=(ind1, ind2), ylim=(0, np.max(ycc)))

    # TODO: Need axis labels and title

    # turn off interactive plotting
    if not plt.isinteractive():
        pass
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)
    # end plotting function properly
    end_plotting()


def debug_locplot_fit_residual(pp, loc, rnum, kind):
    """
    Plots the fit residuals against pixel position for either kind='center'
    or kind='width'

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_DISPLAY_TIMEOUT: float, Interval between plots (wait time
                                    after plotting)
    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                x: numpy array (1D), the order numbers
                ctro: numpy array (2D), storage for the center positions
                      shape = (number of orders x number of columns (x-axis)
                res: numpy array (1D), the residual values (data - fit)
    :param rnum: int, number of orders to use (from 0 --> rnum)
    :param kind: string, kind of fit (either 'center' or 'width')

    :return None:
    """
    # get variables from loc dictionary
    x = loc['X']
    xo = loc['CTRO'][rnum]
    y = loc['RES']
    # new fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot residuals of data - fit
    frame.plot(x, y, marker='_')
    # set title and limits
    frame.set(title='{0} fit residual of order {1}'.format(kind, rnum),
              xlim=(0, len(xo)), ylim=(np.min(y), np.max(y)))

    # TODO: Need axis labels
    # turn off interactive plotting
    if not plt.isinteractive():
        pass
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)
    # end plotting function properly
    end_plotting()


# =============================================================================
# slit plotting function
# =============================================================================
def slit_sorder_plot(pp, loc, image):
    """
    Plot the image array and overplot the polyfit for the order defined in
    p['IC_SLIT_ORDER_PLOT']

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_SLIT_ORDER_PLOT: int, the order to plot
                IC_CENT_COL: int, the column number (x-axis) of the central
                             column
                IC_FACDEC: float, the offset multiplicative factor for width

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
    :param image: numpy array (2D), the image

    :return None:
    """
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get selected order
    order = pp['IC_SLIT_ORDER_PLOT']
    # work out offset for this order
    offset = np.polyval(loc['ASS'][order][::-1], pp['IC_CENT_COL'])
    offset *= pp['IC_FACDEC']
    offsetarray = np.zeros(len(loc['ASS'][order]))
    offsetarray[0] = offset
    # plot image
    frame.imshow(image, origin='lower', clim=(0., np.mean(image)))
    # calculate selected order fit
    xfit = np.arange(image.shape[1])
    yfit1 = np.polyval((loc['ACC'][order] + offsetarray)[::-1], xfit)
    yfit2 = np.polyval((loc['ACC'][order] - offsetarray)[::-1], xfit)
    # plot selected order fit
    frame.plot(xfit, yfit1, color='red')
    frame.plot(xfit, yfit2, color='red')
    # set axis limits to image
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]))

    # TODO: Need axis labels and title

    # end plotting function properly
    end_plotting()


def slit_tilt_angle_and_fit_plot(pp, loc):
    """
    Plot the slit tilt angle and its fit

    :param pp: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                xfit_tilt: numpy array (1D), the order numbers
                tilt: numpy array (1D), the tilt angle of each order
                yfit_tilt: numpy array (1D), the fit for the tilt angle of each
                           order

    :return None:
    """
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot tilt
    frame.plot(loc['XFIT_TILT'], loc['TILT'], label='tilt')
    # plot tilt fit
    frame.plot(loc['XFIT_TILT'], loc['YFIT_TILT'], label='tilt fit')
    # set title and labels
    frame.set(title='SLIT TILT ANGLE', xlabel='Order number',
              ylabel='Slit angle [deg]')
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


# =============================================================================
# ff plotting function
# =============================================================================
def ff_sorder_fit_edges(p, loc, image):
    """
    Plot a selected order (defined in "IC_FF_ORDER_PLOT") on the image
    with fit edges also plotted

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                IC_EXT_RANGE1: float, the upper edge of the order in rows
                               (y-axis) - half-zone width (lower)
                IC_EXT_RANGE2: float, the lower edge of the order in rows
                               (y-axis) - half-zone width (upper)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image to plot the fit on

    :return None:
    """

    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']

    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='gray')
    # loop around the order numbers
    acc = loc['ACC'][selected_order]
    # work out offsets for this order
    offsetarraylow = np.zeros(len(acc))
    offsetarrayhigh = np.zeros(len(acc))
    offsetarraylow[0] = range2
    offsetarrayhigh[0] = range1
    # get fit and edge fits
    xfit = np.arange(image.shape[1])
    yfit = np.polyval(acc[::-1], xfit)
    yfitlow = np.polyval((acc + offsetarraylow)[::-1], xfit)
    yfithigh = np.polyval((acc - offsetarrayhigh)[::-1], xfit)
    # plot fits
    frame.plot(xfit, yfit, color='red', label='fit')
    frame.plot(xfit, yfitlow, color='blue', label='Fit edge',
               linestyle='--')
    frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image fit for order {0} fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def ff_aorder_fit_edges(p, loc, image):
    """
    Plots all orders and highlights selected order (defined in
    "IC_FF_ORDER_PLOT") on the image with fit edges also plotted

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)
                IC_EXT_RANGE1: float, the upper edge of the order in rows
                               (y-axis) - half-zone width (lower)
                IC_EXT_RANGE2: float, the lower edge of the order in rows
                               (y-axis) - half-zone width (upper)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image to plot the fit on

    :return None:
    """
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']

    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='gray')

    # loop around the order numbers
    for order_num in range(len(loc['ACC'])//p['NBFIB']):
        acc = loc['ACC'][order_num]

        # work out offsets for this order
        offsetarraylow = np.zeros(len(acc))
        offsetarrayhigh = np.zeros(len(acc))
        offsetarraylow[0] = range2
        offsetarrayhigh[0] = range1

        # get fit and edge fits
        xfit = np.arange(image.shape[1])
        yfit = np.polyval(acc[::-1], xfit)
        yfitlow = np.polyval((acc + offsetarraylow)[::-1], xfit)
        yfithigh = np.polyval((acc - offsetarrayhigh)[::-1], xfit)
        # plot fits
        if order_num == selected_order:
            frame.plot(xfit, yfit, color='orange', label='Selected Order fit')
            frame.plot(xfit, yfitlow, color='green', linestyle='--',
                       label='Selected Order fit edge')
            frame.plot(xfit, yfithigh, color='green', linestyle='--')
        elif order_num == 0:
            frame.plot(xfit, yfit, color='red', label='fit')
            frame.plot(xfit, yfitlow, color='blue', label='fit edge',
                       linestyle='--')
            frame.plot(xfit, yfithigh, color='blue', linestyle='--')
        else:
            frame.plot(xfit, yfit, color='red')
            frame.plot(xfit, yfitlow, color='blue', linestyle='--')
            frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image fit for orders (highlighted order={0}) fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # turn off interactive plotting
    # end plotting function properly
    end_plotting()


def ff_sorder_tiltadj_e2ds_blaze(p, loc):
    """
    Plot (for the selected order defined in "IC_FF_ORDER_PLOT") the extracted
    e2ds and blaze function

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                e2ds: numpy array (2D), the extracted orders
                blaze: numpy array (2D), the blaze image
                      shape = (number of orders x number of columns (x-axis))

    :return None:
    """

    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']
    e2ds = loc['E2DS'][selected_order]
    blaze = loc['BLAZE'][selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get xrange
    x = np.arange(len(e2ds))
    # plot e2ds for selected order
#    frame.plot(x, e2ds, label='E2DS')
    frame.plot(x[e2ds>0], e2ds[e2ds>0], label='E2DS')
    # plot blaze function
#    frame.plot(x, blaze, label='Blaze')
    frame.plot(x[blaze>1], blaze[blaze>1], label='Blaze')
    # set title labels limits
    title = 'E2DS + BLAZE spectral order {0} fiber {1}'
    frame.set(title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def ff_sorder_flat(p, loc):
    """
    Plot the flat profile (for selected order defined in "IC_FF_ORDER_PLOT"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                flat: numpy array (2D), the flat image
                      shape = (number of orders x number of columns (x-axis))

    :return None:
    """
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']
    flat = loc['FLAT'][selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get xrange
    x = np.arange(len(flat))
    # plot e2ds for selected order
    frame.plot(x, flat, label='E2DS')
    # set title labels limits
    title = 'FLAT spectral order {0} fiber {1}'
    frame.set(title=title.format(selected_order, fiber))

    # TODO: Need x and y labels

    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def ff_rms_plot(p, loc):

    # get constants from p
    remove_orders = np.array(p['FF_RMS_PLOT_SKIP_ORDERS'])
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define a mask to select certain orders
    mask = np.in1d(np.arange(len(loc['RMS'])), remove_orders)
    # apply mask to RMS array
    rmsc = np.where(mask, 0, loc['RMS'])
    # plot
    frame.plot(np.arange(len(loc['RMS'])), rmsc)
    # plot a statistic for mean SNR and mean RMS
    wmsg = 'Mean S/N= {0:.1f} - Mean RMS = {1:.5f}'
    wargs = [np.mean(loc['SNR']), np.mean(rmsc)]
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(*wargs))
    # end plotting function properly
    end_plotting()


# =============================================================================
# extract plotting function
# =============================================================================
def ext_sorder_fit(p, loc, image, cut=20000):
    """
    Plot a selected order (defined in "IC_EXT_ORDER_PLOT") on the image

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image to plot the fit on

    :param cut: int, the upper cut to apply to the image

    :return None:
    """

    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., cut), cmap='gray')
    # loop around the order numbers
    acc = loc['ACC'][selected_order]
    # work out offsets for this order
    offsetarraylow = np.zeros(len(acc))
    offsetarrayhigh = np.zeros(len(acc))
    offsetarraylow[0] = range2
    offsetarrayhigh[0] = range1
    # get fit and edge fits
    xfit = np.arange(image.shape[1])
    yfit = np.polyval(acc[::-1], xfit)
    yfitlow = np.polyval((acc + offsetarraylow)[::-1], xfit)
    yfithigh = np.polyval((acc - offsetarrayhigh)[::-1], xfit)
    # plot fits
    frame.plot(xfit, yfit, color='red', label='fit')
    frame.plot(xfit, yfitlow, color='blue', label='Fit edge',
               linestyle='--')
    frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image fit for order {0} fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def ext_aorder_fit(p, loc, image, cut=20000):
    """
    Plots all orders and highlights selected order (defined in
    "IC_FF_ORDER_PLOT") on the image

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_FF_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                    acc: numpy array (2D), the fit coefficients array for
                         the centers fit
                         shape = (number of orders x number of fit coefficients)

    :param image: numpy array (2D), the image to plot the fit on

    :return None:
    """
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., cut), cmap='gray')
    # loop around the order numbers
    for order_num in range(len(loc['ACC'])//p['NBFIB']):
        acc = loc['ACC'][order_num]
        # work out offsets for this order
        offsetarraylow = np.zeros(len(acc))
        offsetarrayhigh = np.zeros(len(acc))
        offsetarraylow[0] = range2
        offsetarrayhigh[0] = range1
        # get fit and edge fits
        xfit = np.arange(image.shape[1])
        yfit = np.polyval(acc[::-1], xfit)
        yfitlow = np.polyval((acc + offsetarraylow)[::-1], xfit)
        yfithigh = np.polyval((acc - offsetarrayhigh)[::-1], xfit)
        # plot fits
        if order_num == selected_order:
            frame.plot(xfit, yfit, color='orange', label='Selected Order fit')
            frame.plot(xfit, yfitlow, color='green', linestyle='--',
                       label='Selected Order fit edge')
            frame.plot(xfit, yfithigh, color='green', linestyle='--')
        elif order_num == 0:
            frame.plot(xfit, yfit, color='red', label='fit')
            frame.plot(xfit, yfitlow, color='blue', label='fit edge',
                       linestyle='--')
            frame.plot(xfit, yfithigh, color='blue', linestyle='--')
        else:
            frame.plot(xfit, yfit, color='red')
            frame.plot(xfit, yfitlow, color='blue', linestyle='--')
            frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image fit for orders (highlighted order={0}) fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def ext_spectral_order_plot(p, loc):
    """
    Plot extracted order against wavelength solution (for selected order
    defined in "IC_EXT_ORDER_PLOT"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_EXT_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                wave: numpy array (2D), the wave solution image
                e2ds: numpy array (2D), the extracted orders

    :return None:
    """
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    # get data from loc
    extraction = loc['E2DS'][selected_order]
    # select wavelength solution
    wave = loc['WAVE'][selected_order]
    xlabel = 'Wavelength [nm]'  #[$\AA$]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(wave, extraction, color='red')
    # set title labels limits
    title = 'Spectral order {0} fiber {1}'

    frame.set(xlabel=xlabel, ylabel='flux',
              title=title.format(selected_order, fiber))
    # end plotting function properly
    end_plotting()


def ext_1d_spectrum_plot(p, x, y):
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(x, y)
    # set title
    targs = [p['IC_START_ORDER_1D'], p['IC_END_ORDER_1D']]
    title = 'Spectrum (1D) Order {0} to {1}'.format(*targs)
    # set labels
    frame.set(xlabel='Wavelength [nm]', ylabel='flux', title=title)
    # end plotting function properly
    end_plotting()


# =============================================================================
# drift plotting function
# =============================================================================
def drift_plot_selected_wave_ref(p, loc, x=None, y=None):
    """
    Plot the reference extracted spectrum against wavelength solution for the
    selected order (defined in "IC_DRIFT_ORDER_PLOT")

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                IC_DRIFT_ORDER_PLOT: int, defines the order to plot
                fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least: (if x and y are not defined)
                wave: numpy array (2D), the wave solution image
                speref: numpy array (2D), the reference spectrum

    :param x: numpy array (2D) or None, the wavelength solution for all order
              if None uses "WAVE" from "loc"
    :param y: numpy array (2D) or None, the extracted spectrum to plot for all
              orders, if None uses "SPEREF" from "loc"

    :return None:
    """
    # get constants
    selected_order = p['IC_DRIFT_ORDER_PLOT']
    fiber = p['FIBER']
    # get data from loc
    if x is None:
        wave = loc['WAVE'][selected_order]
    else:
        wave = np.array(x)[selected_order]
    if y is None:
        extraction = loc['SPEREF'][selected_order]
    else:
        extraction = np.array(y)[selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(wave, extraction)
    # set title labels limits
    title = 'spectral order {0} fiber {1}'
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title=title.format(selected_order, fiber))
    # end plotting function properly
    end_plotting()


def drift_plot_photon_uncertainty(p, loc, x=None, y=None):
    """
    Plot the photo noise uncertainty against spectral order number

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least: (if x and y are None)
                number_orders: int, the number of orders in reference spectrum
                dvrmsref: numpy array (1D), the reference spectrum
                          photon noise uncertainty

    :param x: numpy array (1D) or None, the order numbers, if None uses
              "NUMBER_ORDERS" from "loc" to define a list of orders
    :param y: numpy array (1D) or None, the photon uncertainties for each order
              if None uses "DVRMSREF" from "loc" to define a list of orders

    :return None:
    """
    # get data from loc
    if x is None:
        x = np.arange(loc['NUMBER_ORDERS'])
    if y is None:
        y = loc['DVRMSREF']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(x, y)
    # set title labels limits
    title = 'Photon noise uncertainty versus spectral order'
    frame.set(xlabel='Order number', ylabel='Photon noise uncertainty',
              title=title)
    # end plotting function properly
    end_plotting()


def drift_plot_dtime_against_mdrift(p, loc, kind=None):
    """
    Plot drift (with uncertainties) against time from reference

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                drift_type_raw: string, "median" or "mean" the way to combine
                                the drifts for "kind" == "raw" (or None)
                or
                drift_type_e2ds: string, "median" or "mean" the way to combine
                                the drifts for "kind" == "e2ds"
                log_opt: string, log option, normally the program name


    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                deltatime: numpy array (1D), time difference between reference
                           and all comparison files (len=number of comparison
                           files)
                mdrift: numpy array (1D), mean/median RV drift between reference
                        and all comparison files (len=number of comparison
                        files)
                merrdrift: numpy array (1D), error in mean/median RV drift
                           between reference and all comparison files
                           (len=number of comparison files)

    :param kind: string or None, the way drift was calculated, currently
                 accepted are "median" or "mean", if define then drift plotted
                 comes from "DRIFT_TYPE_MEDIAN" or "DRIFT_TYPE_MEAN" depending
                 on value of kind (i.e. "median" or "mean")

    :return None:
    """
    func_name = __NAME__ + '.drift_plot_dtime_against_mdrift()'
    # get data from loc
    deltatime = loc['DELTATIME']
    mdrift = loc['MDRIFT']
    merrdrift = loc['MERRDRIFT']

    if kind is None:
        kindstr = p['DRIFT_TYPE_RAW']
    elif kind in ['raw', 'e2ds']:
        kindstr = p['drift_type_{0}'.format(kind)]
    else:
        emsg1 = 'kind="{0}" not understood'.format(kind)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        kindstr = None
    # get mstr from kindstr
    if kindstr == 'median':
        mstr = 'Median'
    else:
        mstr = 'Mean'
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.errorbar(deltatime, mdrift, yerr=merrdrift, linestyle='none',
                   marker='x')
    # set title labels limits
    title = '{0} drift (with uncertainties) against time from reference'
    frame.set(xlabel='$\Delta$ time [hours]',
              ylabel='{0} drift [m/s]'.format(mstr),
              title=title.format(mstr))
    # end plotting function properly
    end_plotting()


def drift_peak_plot_dtime_against_drift(p, loc):
    """
    Plot mean drift against time from reference

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                deltatime: numpy array (1D), time difference between reference
                           and all comparison files (len=number of comparison
                           files)
                meanrv: numpy array (1D), mean RV drift between reference
                        and all comparison files (len=number of comparison
                        files)
                meanrv_left: numpy array (1D), mean RV drift for left half of
                        order between reference and all comparison files
                        (len=number of comparison files)
                meanrv_right: numpy array (1D), mean RV drift for right half of
                        order between reference and all comparison files
                        (len=number of comparison files)

    :return None:
    """
    # get data from loc
    deltatime = loc['DELTATIME']
    meanvr = loc['MEANRV']
    meanvrleft = loc['MEANRV_LEFT']
    meanvrright = loc['MEANRV_RIGHT']
    # set up masks
    mask1 = meanvr > -999
    mask2 = meanvrleft > -999
    mask3 = meanvrright > -999

    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot mask1
    frame.plot(deltatime[mask1], meanvr[mask1], linestyle='none',
               marker='o', label='All orders', color='b')
    # plot mask2
    frame.plot(deltatime[mask2], meanvrleft[mask2], linestyle='none',
               marker='x', label='half-left', color='g')
    # plot mask3
    frame.plot(deltatime[mask3], meanvrright[mask3], linestyle='none',
               marker='x', label='half-right', color='r')
    # set title labels limits
    title = 'Mean drift against time from reference'
    frame.set(xlabel='$\Delta$ time [hours]', ylabel='Mean drift [m/s]',
              title=title)
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def drift_plot_correlation_comp(p, loc, cc, iteration):
    """
    Plot correlation comparison plot (comparing value good and bad orders that
    pass and fail the Pearson R tests

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            drift_peak_pearsonr_cut: float, the minimum Pearson R coefficient
                                     allowed in a file to obtain drifts from
                                     that order

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum
                spe: numpy array (2D), the comparison spectrum
                speref: numpy array (2D), the reference spectrum

    :param cc: numpy array (1D), the correlation coefficients from the
               Pearson R test

    :return None:
    """

    # get constants
    prcut = p['DRIFT_PEAK_PEARSONR_CUT']
    nbo = loc['NUMBER_ORDERS']
    # get data
    spe = loc['SPE']
    speref = loc['SPEREF']

    # scale images
    spe_image, spe_scale = create_separated_scaled_image(spe)
    speref_image, speref_scale = create_separated_scaled_image(speref)

    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame1 = plt.subplot2grid((2, 3), (0, 0))
    frame2 = plt.subplot2grid((2, 3), (1, 0))
    frame3 = plt.subplot2grid((2, 3), (0, 1), colspan=2)
    frame4 = plt.subplot2grid((2, 3), (1, 1), colspan=2)
    # -------------------------------------------------------------------------
    # order selection
    # -------------------------------------------------------------------------
    # mask
    mask = cc > prcut
    # select bad order
    bad_orders = np.arange(nbo)[~mask]
    bad_order = np.argmin(cc)
    # select worse good order
    good_order = np.argmin(cc[mask])
    # select best order
    best_order = np.argmax(cc[mask])

    # -------------------------------------------------------------------------
    # plot good order
    label = 'Order {0} - Passes PearsonR test (best pass)'
    frame4.plot(spe[best_order], color='green', zorder=0,
                label=label.format(best_order), alpha=0.5)
    frame3.plot(speref[best_order], color='green', zorder=0,
                label=label.format(best_order), alpha=0.5)
    # -------------------------------------------------------------------------
    # plot good order
    label = 'Order {0} - Passes PearsonR test (worst pass)'
    frame4.plot(spe[good_order], color='orange', zorder=1,
                label=label.format(good_order), alpha=0.5)
    frame3.plot(speref[good_order], color='orange', zorder=1,
                label=label.format(good_order), alpha=0.5)
    # -------------------------------------------------------------------------
    # plot worst order
    label = 'Order {0} - Fails PearsonR test'
    frame4.plot(spe[bad_order], zorder=2, color='r',
                label=label.format(bad_order), alpha=1)
    frame3.plot(speref[bad_order], zorder=2, color='r',
                label=label.format(bad_order), alpha=1)
    # -------------------------------------------------------------------------
    # set titles
    frame3.set_title('Reference frame')
    frame4.set_title('Iteration frame')
    # -------------------------------------------------------------------------
    # set legends
    frame3.legend(loc=0)
    frame4.legend(loc=0)
    # -------------------------------------------------------------------------
    # set xlimits
    frame3.set_xlim(0, speref.shape[1])
    frame4.set_xlim(0, spe.shape[1])
    # set ylimits
    frame3.set_ylim(0)
    frame4.set_ylim(0)
    # -------------------------------------------------------------------------
    # highlight good and bad orders
    yticks, ytext = [], []
    # add best order
    ypos = speref_scale * (best_order + 0.5)
    yticks.append(ypos)
    ytext.append('Order {0} = PASSED (BEST)'.format(best_order))
    # add good order
    ypos = speref_scale * (good_order + 0.5)
    yticks.append(ypos)
    ytext.append('Order {0} = PASSED (WORST)'.format(good_order))
    # add bad orders
    for bad_order in bad_orders:
        ypos = speref_scale * (bad_order + 0.5)
        yticks.append(ypos)
        ytext.append('Order {0} = FAILED'.format(bad_order))
    # -------------------------------------------------------------------------
    # plot the reference frame
    frame1.imshow(speref_image)
    frame1.set(title='Reference frame')
    # turn off axis labels
    frame1.set_yticks(yticks)
    frame1.set_yticklabels(ytext)
    frame1.set_xticklabels([])
    # -------------------------------------------------------------------------
    # plot the science frame
    frame2.imshow(spe_image)
    frame2.set(title='Iteration frame')
    # turn off axis labels
    frame2.set_yticks(yticks)
    frame2.set_yticklabels(ytext)
    frame2.set_xticklabels([])
    # -------------------------------------------------------------------------
    # set title
    title = ('Pearson R test File {0} - example passed order vs failed order\n'
             'PearsonR cut: {1}\n'
             'Best result (Order {2}): {3}\n'
             'Good result (Order {4}): {5}\n'
             'Failed result (Order {6}): {7}')
    targs = [iteration + 1, prcut, best_order, cc[best_order],  good_order,
             cc[good_order], bad_order, cc[bad_order]]
    plt.suptitle(title.format(*targs))

    # -------------------------------------------------------------------------
    # end plotting function properly
    end_plotting()


def create_separated_scaled_image(image, axis=0):
    """
    Function for scaling up one axis for plotting using imshow. If one axis
    is vastly less than the other images will be hard to see (i.e. a very
    thin rectangle. Scaling up the smaller axis by repeating the rows/columns
    helps for visualizing any image plotted.

    :param image: numpy array (2D), image to scale
    :param axis: int, the axis to scale (i.e. 0 or 1)

    :return newimage: numpy array (2D), the scaled image
    :return scale: float, the scale factor between old and new images in
                   dimension = axis
    """

    if axis == 0:
        dim1, dim2 = 0, 1
    else:
        dim1, dim2 = 1, 0
    # get a scale for the pixels
    scale = int(np.ceil(image.shape[dim2]/(image.shape[dim1])))
    # get a new image
    newimage = np.zeros((image.shape[dim1]*scale, image.shape[dim2]))
    newimage -= np.max(image)
    # add the old pixels, repeated

    for pixel in range(image.shape[dim1]):

        start = pixel*scale
        end = scale*(pixel + 1)

        if axis == 0:
            repeat = np.tile(image[pixel, :], scale)
            repeat = repeat.reshape((scale, image.shape[dim2]))
            newimage[start:end, :] = repeat
        if axis == 1:
            repeat = np.tile(image[:, pixel], scale)
            repeat = repeat.reshape((scale, image.shape[dim2]))
            newimage[:, start:end] = repeat

    return newimage, scale


def drift_peak_plot_llpeak_amps(p, loc):
    """
    Plot the line-list peak amplitudes against their position on top of a
    plot of the extraction (against wavelength) for a selected peak (defined
    by "DRIFT_PEAK_SELECTED_ORDER".

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRIFT_PEAK_SELECTED_ORDER: int, which peak to plot in the
                linelist vs amp plot
    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                wave: numpy array (2D), the wave solution image
                speref: numpy array (2D), the reference spectrum
                llpeak: numpy array (1D), the delta wavelength of each FP peak
                amppeak: numpy array (1D), the maximum amplitude of the
                         normalised pixel values for each FP peak
                dv: numpy array (1D), the delta v for each FP peak

    :return None:
    """
    # get selected peak from
    selected_order = p['DRIFT_PEAK_SELECTED_ORDER']
    # get data from loc
    wave = loc['WAVE'][selected_order]
    extraction = loc['SPEREF'][selected_order]
    llpeak = loc['LLPEAK']
    logamppeak = np.log10(loc['AMPPEAK'])
    dv = loc['DV']
    # calculate different thresholds
    mask1 = abs(dv) < 1000
    mask2 = abs(dv) < 100
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(wave, extraction)
    frame.plot(llpeak[mask1], logamppeak[mask1], linestyle='none')
    frame.plot(llpeak[mask2], logamppeak[mask2], linestlye='none')
    # set title labels limits
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title='$log_{10}$(Max Amplitudes)')
    # end plotting function properly
    end_plotting()


# =============================================================================
# CCF plotting function
# =============================================================================
def ccf_rv_ccf_plot(x, y, yfit, order=None, fig=None, pause=True):
    """
    Plot the CCF plot. RV against CCF and RV against CCF fit, for a specific
    order number "order"

    :param x: numpy array (1D), the RV values
    :param y: numpy array (1D), the CCF values
    :param yfit: numpy array (1D), the CCF fit values
    :param order: int, the order to plot
    :param fig: matplotlib figure instance, i.e. plt.figure() passed to allow
                same axis to plot each order of this function
    :param pause: bool, if True allow for a pause after plotting (to allow user
                  to view this order before moving to next order

    :return None:
    """
    if fig is None:
        fig = plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(x, y, label='data', marker='x', linestyle='none', color='k')
    frame.plot(x, yfit, label='fit', color='r')
    # set title labels limits
    title = 'CCF plot'
    if order is not None:
        title += 'Order {0}'.format(order)
    frame.set(xlabel='Rv [km/s]', ylabel='CCF', title=title)
    # set legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()
    # pause
    if pause:
        time.sleep(1.0)


# =============================================================================
# wave solution plotting function
# =============================================================================
def wave_littrow_extrap_plot(loc, iteration=0):

    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # define the x axis data
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    x_points = np.arange(xdim)
    # define the y axis data
    yfit_x_cut = loc['LITTROW_EXTRAP_{0}'.format(iteration)]
    yfit = loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # colours
    colours = np.tile(['r', 'b', 'g', 'y', 'm', 'k', 'c'], ydim)
    # loop around the orders and plot each line
    for order_num in range(ydim):
        # plot the solution for all x points
        frame.plot(x_points, yfit[order_num],
                   color=colours[order_num])
        # plot the solution at the chosen cut points
        frame.scatter(x_cut_points, yfit_x_cut[order_num],
                      marker='o', s=10, color=colours[order_num])
    # set axis labels
    frame.set(xlabel='Pixel number', ylabel='Wavelength [nm]')
    # end plotting function properly
    end_plotting()


def wave_littrow_check_plot(p, loc, iteration=0):
    # get data from loc
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    # set up colors
    import matplotlib.cm as cm
    colors = cm.rainbow(np.linspace(0, 1, len(x_cut_points)))
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # loop around the xcut points
    for it in range(len(x_cut_points)):
        # get x and y data
        xx = loc['LITTROW_XX_{0}'.format(iteration)][it]
        yy = loc['LITTROW_YY_{0}'.format(iteration)][it]
        # plot graph
        frame.plot(xx, yy, label='x = {0}'.format(x_cut_points[it]),
                   color=colors[it])
    # set axis labels and title
    targs = [iteration, p['FIBER']]
    title = 'Wavelength Solution Littrow Check {0} fiber {1}'.format(*targs)
    frame.set(xlabel='Order number', ylabel='Diff/Littrow [km/s]',
              title=title)
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def wave_plot_instrument_drift(p, x, spe, speref):
    # get constants from parameter file
    selected_order = p['IC_WAVE_IDRIFT_PLOT_ORDER']
    fiber = p['FIBER']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot
    frame.plot(x[selected_order], spe[selected_order], label='data')
    frame.plot(x[selected_order], speref[selected_order], label='reference')
    # add legend
    frame.legend(loc=0)
    # set title labels limits
    title = 'Comparison between data and reference order={0} fiber={1}'
    frame.set(xlabel='Wavelength [Angstrom]', ylabel='e-',
              title=title.format(selected_order, fiber))
    # end plotting function properly
    end_plotting()


def wave_plot_final_fp_order(p, loc, iteration=0):
    """
    Plot the FP extracted spectrum against wavelength solution for the
    final fitted order (defined in "IC_WAVE_FP_N_ORD_FINAL")

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_WAVE_FP_N_ORD_FINAL: int, defines the order to plot
            fiber: string, the fiber used for this recipe (eg. AB or A or C)

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FPDATA: numpy array (2D), the fp spectrum
            LITTROW_EXTRAP_SOL_{0}: the wavelength solution derived from the
                                    HC and Littrow-constrained where {0} is the
                                    iteration number

    :return None:
    """
    # get constants
    selected_order = p['IC_FP_N_ORD_FINAL']
    fiber = p['FIBER']
    # get data from loc
    wave = loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)][selected_order]
    fp_data = loc['FPDATA'][selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot
    frame.plot(wave, fp_data)
    # set title labels limits
    title = 'spectral order {0} fiber {1} (iteration = {2})'
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title=title.format(selected_order, fiber, iteration))
    # end plotting function properly
    end_plotting()


def wave_local_width_offset_plot(loc):
    """
    Plot the measured FP cavity width offset against line number

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FP_M: numpy array, the fp line numbers
            FP_DOPD_OFFSET: numpy array, the measured cavity width offsets
            FP_DOPD_OFFSET_COEFF: numpy array, the fit coefficients
                                  for the cavity width offsets

    :return None:
    """
    # get data from loc
    fp_m = loc['FP_M']
    fp_dopd = loc['FP_DOPD_OFFSET']
    fp_dopd_coeff = loc['FP_DOPD_OFFSET_COEFF']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.scatter(fp_m, fp_dopd, label='Measured')
    frame.plot(np.sort(fp_m), np.polyval(fp_dopd_coeff[::-1], np.sort(fp_m)),
               label='fit', color='red')
    # set title labels limits
    title = 'FP cavity width offset'
    frame.set(xlabel='FP peak number',
              ylabel='Local cavity width offset [micron]',
              title=title)
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def wave_fp_wavelength_residuals(loc):
    """
    Plot the FP line wavelength residuals

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                FP_LL_POS: numpy array, the FP line initial wavelengths
                FP_LL_POS_NEW: numpy array, the FP line updated wavelengths

    :return None:
    """
    # get data from loc
    fp_ll = loc['FP_LL_POS']
    fp_ll_new = loc['FP_LL_POS_NEW']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.scatter(fp_ll, fp_ll - fp_ll_new)
    # set title labels limits
    title = 'FP lines wavelength residuals'
    frame.set(xlabel='Initial wavelength [nm]',
              ylabel='New - Initial wavelength [nm]',
              title=title)
    # end plotting function properly
    end_plotting()


# =============================================================================
# wave solution plotting function (EA)
# =============================================================================
def wave_ea_plot_per_order_hcguess(p, loc, order_num):

    # get data from loc
    wave = loc['INITIAL_WAVE_MAP']
    hc_sp = loc['HCDATA']
    # get data from loc
    xpix_ini = loc['XPIX_INI']
    g2_ini = loc['G2_INI']

    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot spectrum for order
    frame.plot(wave[order_num, :], hc_sp[order_num, :], color='k')
    # over plot all fits
    for line_it in range(len(xpix_ini)):
        xpix = xpix_ini[line_it]
        g2 = g2_ini[line_it]
        plt.plot(wave[order_num, xpix], g2)

    # set title and labels
    frame.set(title='Per-order spectrum, Order={0}'.format(order_num),
              xlabel='Wavelength [nm]',
              ylabel='Normalized flux')

    # show, close and turn interactive on
    plt.show()
    plt.close()



def wave_ea_plot_wave_cat_all_and_brightest(p, wave_c, dv, bmask, iteration):
    # get constants from p
    n_iterations = p['HC_NITER_FIT_TRIPLET']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot all lines
    frame.scatter(wave_c[~bmask], dv[~bmask], color='g', s=5,
                  label='All lines')
    # plot brightest lines
    frame.scatter(wave_c[bmask], dv[bmask], color='r', s=5,
                  label='Brightest per order')
    # plot legend
    frame.legend(loc=0)
    # plot title and labels
    title = 'Delta-v error for matched lines (Iteration {0} of {1})'
    frame.set(title=title.format(iteration + 1, n_iterations),
              xlabel='Wavelength [nm]',
              ylabel='dv [km/s]')
    # end plotting function properly
    end_plotting()


def wave_ea_plot_tfit_grid(p, orders, wave_catalog, recon0, gauss_rms_dev,
                           xgau, ew, iteration):
    # get constants from p
    n_iterations = p['HC_NITER_FIT_TRIPLET']
    # get all orders
    all_orders = np.unique(orders)
    # calculate dv values
    dv = ((wave_catalog/recon0) - 1) * speed_of_light
    # get colours
    colours = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # repeat colours to match all_orders
    colours = np.tile(colours, len(all_orders))
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame1 = plt.subplot(221)
    frame2 = plt.subplot(222)
    frame3 = plt.subplot(223)
    frame4 = plt.subplot(224)
    # loop around orders
    for order_num in all_orders:
        # identify this orders good values
        good = orders == order_num
        # get colour for this order
        colour = colours[order_num]
        # plot frame1
        frame1.scatter(wave_catalog[good], dv[good], s=5, color=colour)
        # plot frame2
        frame2.scatter(1.0/gauss_rms_dev[good], dv[good], s=5, color=colour)
        # plot frame3
        frame3.scatter(xgau[good] % 1, dv[good], s=5, color=colour)
        # plot frame4
        frame4.scatter(ew[good], dv[good], s=5, color=colour)
    # set up labels
    frame1.set(xlabel='Wavelength [nm]', ylabel='dv [km/s]')
    frame2.set(xlabel='Line SNR estimate', ylabel='dv [km/s]')
    frame3.set(xlabel='Modulo pixel position', ylabel='dv [km/s]')
    frame4.set(xlabel='e-width of fitted line', ylabel='dv [km/s]')
    # add title
    plt.suptitle('Iteration {0} of {1}'.format(iteration + 1, n_iterations))
    # end plotting function properly
    end_plotting()


# =============================================================================
# telluric plotting function
# =============================================================================
def tellu_trans_map_plot(loc, order_num, fmask, sed, trans, sp, ww, outfile):

    # get data from loc
    wave = loc['WAVE'][order_num, :]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot trans_map and spectra
    frame.plot(wave, sp[order_num, :], 'r.')
    frame.plot(wave[fmask], sp[order_num][fmask], 'b.')
    frame.plot(wave, sed, 'r-')
    frame.plot(wave, trans, 'c-')
    frame.plot(wave, sp[order_num, :] / sed[:], 'g-')
    frame.plot(wave, np.ones_like(sed), 'r-')
    frame.plot(wave, ww, 'k-')
    frame.set_title(outfile)
    # set limit
    frame.set(ylim=[0.75, 1.15])
    # end plotting function properly
    end_plotting()


def tellu_pca_comp_plot(p, loc):

    # get constants from p
    npc = loc['NPC']
    # get data from loc
    wave = loc['WAVE'].ravel()
    pc = loc['PC']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot principle components
    for it in range(npc):
        # define the label for the component
        if p['ADD_DERIV_PC']:
            if it == npc - 2:
                label = 'd[pc1]'
            elif it == npc - 1:
                label = 'd[pc2]'
            else:
                label = 'pc {0}'.format(it + 1)
        else:
            label = 'pc {0}'.format(it + 1)
        # plot the component with correct label
        frame.plot(wave, pc[:, it], label=label)
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def tellu_fit_tellu_spline_plot(p, loc):
    # get constants from p
    selected_order = p['TELLU_PLOT_ORDER']
    # get data from loc
    data = loc['DATA']
    ydim, xdim = data.shape
    wave = loc['WAVE_IT']
    sp = loc['SP']
    template2 = loc['TEMPLATE2']
    # get selected order wave lengths
    swave = wave[selected_order, :]
    # get selected order for sp
    ssp = sp[selected_order, :]
    # get template2 at selected order
    start, end = selected_order * xdim, selected_order * xdim + xdim
    stemp = np.array(template2[start: end])
    # recovered absorption
    srecov = ssp/stemp
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot spectra for selected order
    frame.plot(swave, ssp/np.nanmedian(ssp), label='Observed SP')
    frame.plot(swave, stemp/np.nanmedian(stemp), label='Template SP')
    frame.plot(swave, srecov/np.nanmedian(srecov), label='Recov abso SP')
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def tellu_fit_recon_abso_plot(p, loc):

    # get constants from p
    selected_order = p['TELLU_FIT_RECON_PLT_ORDER']
    # get data dimensions
    ydim, xdim = loc['DATA'].shape
    # get selected order wave lengths
    swave = loc['WAVE_IT'][selected_order, :]
    # get the data from loc for selected order
    start, end = selected_order * xdim, selected_order * xdim + xdim
    ssp2 = np.array(loc['SP2'][start:end])
    stemp2 = np.array(loc['TEMPLATE2'][start:end])
    srecon_abso = np.array(loc['RECON_ABSO'][start:end])
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot spectra for selected order
    frame.plot(swave, ssp2/np.nanmedian(ssp2)/srecon_abso, color='g',
               label='Cleaned SP')
    frame.plot(swave, stemp2/np.nanmedian(stemp2), color='c', label='Template')
    frame.plot(swave, srecon_abso, color='r', label='recon abso')
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


# =============================================================================
# Polarimetry plotting functions
# =============================================================================
def polar_continuum_plot(loc, in_wavelengths=True):

    # get data from loc
    wl, pol = loc['FLAT_X'], loc['FLAT_POL']
    contpol = loc['CONT_POL']
    contxbin, contybin = loc['CONT_XBIN'], loc['CONT_YBIN']
    stokes = loc['STOKES']
    method, nexp = loc['METHOD'], loc['NEXPOSURES']
    # ---------------------------------------------------------------------
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # ---------------------------------------------------------------------
    # set up labels
    if in_wavelengths:
        xlabel = 'wavelength (nm)'
    else:
        xlabel = 'order number + col (pixel)'
    ylabel = 'Degree of polarization for Stokes {0} (%)'.format(stokes)
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ---------------------------------------------------------------------
    # plot polarimetry data
    frame.plot(wl, pol, linestyle='None', marker='.',
               label='Degree of Polarization')
    # plot continuum sample points
    frame.plot(contxbin, contybin, linestyle='None', marker='o',
               label='Continuum Sampling')
    # plot continuum fit
    frame.plot(wl, contpol, label='Continuum Polarization')
    # ---------------------------------------------------------------------
    # set title and labels
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # ---------------------------------------------------------------------
    # end plotting function properly
    end_plotting()


def polar_result_plot(loc, in_wavelengths=True):
    # get data from loc
    wl, pol = loc['FLAT_X'], 100.0*loc['FLAT_POL']
    null1, null2 = 100.0*loc['FLAT_NULL1'], 100.0*loc['FLAT_NULL2']
    stokes = loc['STOKES']
    method, nexp = loc['METHOD'], loc['NEXPOSURES']
    # ---------------------------------------------------------------------
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # ---------------------------------------------------------------------
    # set up labels
    if in_wavelengths:
        xlabel = 'wavelength (nm)'
    else:
        xlabel = 'order number + col (pixel)'
    ylabel = 'Degree of polarization for Stokes {0} (%)'.format(stokes)
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ---------------------------------------------------------------------
    # plot polarimetry data
    plt.plot(wl, pol, label='Degree of Polarization')
    # plot null1 data
    plt.plot(wl, null1, label='Null Polarization 1')
    # plot null2 data
    plt.plot(wl, null2, label='Null Polarization 2')
    # ---------------------------------------------------------------------
    # set title and labels
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # ---------------------------------------------------------------------
    # end plotting function properly
    end_plotting()


def polar_stokesI_plot(loc, in_wavelengths=True):
    # get data from loc
    wl, stokesI = loc['FLAT_X'], loc['FLAT_STOKESI']
    stokesIerr = loc['FLAT_STOKESIERR']
    stokes = 'I'
    method, nexp = loc['METHOD'], loc['NEXPOSURES']
    # ---------------------------------------------------------------------
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # ---------------------------------------------------------------------
    # set up labels
    if in_wavelengths:
        xlabel = 'wavelength (nm)'
    else:
        xlabel = 'order number + col (pixel)'
    ylabel = 'Stokes {0} total flux (ADU)'.format(stokes)
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ---------------------------------------------------------------------
    # plot polarimetry data
    plt.errorbar(wl, stokesI, yerr=stokesIerr, fmt='-', label='Stokes I', 
                 alpha=0.5)
    # ---------------------------------------------------------------------
    # set title and labels
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting()


def polar_lsd_plot(loc) :
    
    # get data from loc
    vels = loc['LSD_VELOCITIES']
    Z = loc['LSD_STOKESI']
    Zgauss = loc['LSD_STOKESI_MODEL']
    Zp = loc['LSD_STOKESVQU']
    Znp = loc['LSD_NULL']
    stokes = loc['STOKES']
    
    # ---------------------------------------------------------------------
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    
    # ---------------------------------------------------------------------
    frame = plt.subplot(3, 1, 1)
    plt.plot(vels, Z, '-')
    plt.plot(vels, Zgauss, '-')
    title = 'LSD Analysis'
    ylabel = 'Stokes I profile'
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    
    # ---------------------------------------------------------------------
    frame = plt.subplot(3, 1, 2)
    title = ''
    plt.plot(vels, Zp, '-')
    ylabel = 'Stokes {0} profile'.format(stokes)
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    frame = plt.subplot(3, 1, 3)
    plt.plot(vels, Znp, '-')
    xlabel = 'velocity (km/s)'
    ylabel = 'Null profile'
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # turn off interactive plotting
    # end plotting function properly
    end_plotting()


# =============================================================================
# test functions (remove later)
# =============================================================================
# TODO: remove later
def __test_smoothed_boxmean_image(image, image1, image2, size,
                                  row=1000, column=1000):
    """
    This is a test code for comparison between smoothed_boxmean_image1 "manual"
    and smoothed_boxmean_image2 "convovle"

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param column: int, the column number to plot for
    :return None:
    """

    # set up the plot
    fsize = (4, 6)
    plt.figure()
    frames = [plt.subplot2grid(fsize, (0, 0), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 2), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 4), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (2, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (2, 3), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 3), colspan=3, rowspan=1)]
    # plot the images and image diff
    frames[0].imshow(image1)
    frames[0].set_title('Image Old method')
    frames[1].imshow(image2)
    frames[1].set_title('Image New method')
    frames[2].imshow(image1 - image2)
    frames[2].set_title('Image1 - Image2')
    # plot the column plot
    frames[3].plot(image[:, column], label='Original')
    frames[3].plot(image1[:, column], label='Old method')
    frames[3].plot(image2[:, column], label='New method')
    frames[3].legend()
    frames[3].set_title('Column {0}'.format(column))
    frames[4].plot(image1[:, column] - image2[:, column])
    frames[4].set_title('Column {0}  Image1 - Image2'.format(column))
    # plot the row plot
    frames[5].plot(image[row, :], label='Original')
    frames[5].plot(image1[row, :], label='Old method')
    frames[5].plot(image2[row, :], label='New method')
    frames[5].legend()
    frames[5].set_title('Row {0}'.format(row))
    frames[6].plot(image1[row, :] - image2[row, :])
    frames[6].set_title('Row {0}  Image1 - Image2'.format(row))
    plt.subplots_adjust(hspace=0.5)

    if not plt.isinteractive():
        plt.show()
        plt.close()

# =============================================================================
# End of code
# =============================================================================
