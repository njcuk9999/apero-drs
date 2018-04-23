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
import sys
import time
import matplotlib

# TODO: Is there a better fix for this?
# fix for MacOSX plots freezing
gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui, warn=False, force=True)
        break
    except:
        continue
if matplotlib.get_backend() == 'MacOSX':
    emsg = ('OSX Error: Matplotlib MacOSX backend not supported and '
            'Qt5Agg not available')
    print('\n\n{0}\n{1}\n{0}\n\n'.format('='*50, emsg))
    sys.exit()

# now can import matplotlib properly
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from SpirouDRS import spirouConfig
from . import spirouLog


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
WLOG = spirouLog.logger
# -----------------------------------------------------------------------------
INTERACTIVE_PLOTS = spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED()


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
        plt.ion()
    # start interactive plot
    elif INTERACTIVE_PLOTS:
        plt.ion()


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
    im = frame.imshow(image, origin='lower', clim=(1., 10 * pp['med_full']),
                      cmap='jet')
    # plot the colorbar
    plt.colorbar(im, ax=frame)
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
                     edgecolor='b', facecolor='None')
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

    # TODO: needs axis labels and titles


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

    # TODO: needs axis labels and title


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
    histo_f, edge_f = pp['histo_full']
    histo_b, edge_b = pp['histo_blue']
    histo_r, edge_r = pp['histo_red']
    # plot the main histogram
    xf = np.repeat(edge_f, 2)
    yf = [0] + list(np.repeat(histo_f*100/np.max(histo_f), 2)) + [0]
    frame.plot(xf, yf, color='green')
    # plot the blue histogram
    xb = np.repeat(edge_b, 2)
    yb = [0] + list(np.repeat(histo_b*100/np.max(histo_b), 2)) + [0]
    frame.plot(xb, yb, color='blue')
    # plot the red histogram
    xr = np.repeat(edge_r, 2)
    yr = [0] + list(np.repeat(histo_r*100/np.max(histo_r), 2)) + [0]
    frame.plot(xr, yr, color='red')

    # TODO: Needs axis labels and title


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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    frame.plot(np.arange(rnum), loc['rms_center'][0:rnum], label='center')
    frame.plot(np.arange(rnum), loc['rms_fwhm'][0:rnum], label='fwhm')
    # set title labels limits
    frame.set(xlim=(0, rnum), xlabel='Order number', ylabel='RMS [pixel]',
              title=('Dispersion of localization parameters fiber {0}'
                     '').format(pp['fiber']))
    # Add legend
    frame.legend(loc=0)
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


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
    WLOG('', pp['log_opt'], '{0:d} {0:d}  {0:f}  {0:f}  {0:f}'.format(*wargs))

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
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


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
    x = loc['x']
    xo = loc['ctro'][rnum]
    y = loc['res']
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
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


# =============================================================================
# slit plotting function
# =============================================================================
def slit_sorder_plot(pp, loc, image):
    """
    Plot the image array and overplot the polyfit for the order defined in
    p['ic_slit_order_plot']

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
    offset = np.polyval(loc['ass'][order][::-1], pp['IC_CENT_COL'])
    offset *= pp['IC_FACDEC']
    offsetarray = np.zeros(len(loc['ass'][order]))
    offsetarray[0] = offset
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 30000.))
    # calculate selected order fit
    xfit = np.arange(image.shape[1])
    yfit1 = np.polyval((loc['acc'][order] + offsetarray)[::-1], xfit)
    yfit2 = np.polyval((loc['acc'][order] - offsetarray)[::-1], xfit)
    # plot selected order fit
    frame.plot(xfit, yfit1, color='red')
    frame.plot(xfit, yfit2, color='red')
    # set axis limits to image
    frame.set(xlim=(0, image.shape[0]), ylim=(0, image.shape[1]))

    # TODO: Need axis labels and title

    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    frame.plot(loc['xfit_tilt'], loc['tilt'], label='tilt')
    # plot tilt fit
    frame.plot(loc['xfit_tilt'], loc['yfit_tilt'], label='tilt fit')
    # set title and labels
    frame.set(title='SLIT TILT ANGLE', xlabel='Order number',
              ylabel='Slit angle [deg]')
    # Add legend
    frame.legend(loc=0)
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']

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
    acc = loc['acc'][selected_order]
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']

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
    for order_num in range(len(loc['acc'])//2):
        acc = loc['acc'][order_num]

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
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']
    e2ds = loc['e2ds'][selected_order]
    blaze = loc['blaze'][selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get xrange
    x = np.arange(len(e2ds))
    # plot e2ds for selected order
    frame.plot(x, e2ds, label='E2DS')
    # plot blaze function
    frame.plot(x, blaze, label='Blaze')
    # set title labels limits
    title = 'E2DS + BLAZE spectral order {0} fiber {1}'
    frame.set(title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']
    flat = loc['flat'][selected_order]
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


# =============================================================================
# extract plotting function
# =============================================================================
def ext_sorder_fit(p, loc, image):
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

    :return None:
    """

    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['fiber']
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
    acc = loc['acc'][selected_order]
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


def ext_aorder_fit(p, loc, image):
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
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['fiber']
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='gray')
    # loop around the order numbers
    for order_num in range(len(loc['acc'])//2):
        acc = loc['acc'][order_num]
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
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']
    # get data from loc
    wave = loc['wave'][selected_order]
    extraction = loc['e2ds'][selected_order]
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
    frame.set(xlabel='Wavelength [$\AA$]', ylabel='flux',
              title=title.format(selected_order, fiber))
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    fiber = p['fiber']
    # get data from loc
    if x is None:
        wave = loc['wave'][selected_order]
    else:
        wave = np.array(x)[selected_order]
    if y is None:
        extraction = loc['speref'][selected_order]
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
    frame.set(xlabel='Wavelength [$\AA$]', ylabel='flux',
              title=title.format(selected_order, fiber))
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
        x = np.arange(loc['number_orders'])
    if y is None:
        y = loc['dvrmsref']
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    deltatime = loc['deltatime']
    mdrift = loc['mdrift']
    merrdrift = loc['merrdrift']

    if kind is None:
        kindstr = p['drift_type_raw']
    elif kind in ['raw', 'e2ds']:
        kindstr = p['drift_type_{0}'.format(kind)]
    else:
        emsg1 = 'kind="{0}" not understood'.format(kind)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['log_opt'], [emsg1, emsg2])
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    deltatime = loc['deltatime']
    meanvr = loc['meanrv']
    meanvrleft = loc['meanrv_left']
    meanvrright = loc['meanrv_right']
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
    frame.plot(deltatime[mask1], meanvr[mask1],
               marker='x', label='All orders', color='b')
    # plot mask2
    frame.plot(deltatime[mask2], meanvrleft[mask2],
               marker='x', label='half-left', color='g')
    # plot mask3
    frame.plot(deltatime[mask3], meanvrright[mask3],
               marker='x', label='half-right', color='r')
    # set title labels limits
    title = 'Mean drift against time from reference'
    frame.set(xlabel='$\Delta$ time [hours]', ylabel='Mean drift [m/s]',
              title=title)
    # add legend
    frame.legend(loc=0)
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


def drift_plot_correlation_comp(p, loc, cc):
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
    prcut = p['drift_peak_pearsonr_cut']
    nbo = loc['number_orders']
    # get data
    spe = loc['spe']
    speref = loc['speref']

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
    title = ('Pearson R test - example passed order vs failed order\n'
             'PearsonR cut: {0}\n'
             'Best result (Order {1}): {2}\n'
             'Good result (Order {3}): {4}\n'
             'Failed result (Order {5}): {6}')
    targs = [prcut, best_order, cc[best_order],  good_order, cc[good_order],
             bad_order, cc[bad_order]]
    plt.suptitle(title.format(*targs))

    # -------------------------------------------------------------------------
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    wave = loc['wave'][selected_order]
    extraction = loc['speref'][selected_order]
    llpeak = loc['llpeak']
    logamppeak = np.log10(loc['amppeak'])
    dv = loc['dv']
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
    frame.set(xlabel='Wavelength [$\AA$]', ylabel='flux',
              title='$log_{10}$(Max Amplitudes)')
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()
    # pause
    if pause:
        time.sleep(1.0)

# =============================================================================
# test functions (rewmove later)
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
