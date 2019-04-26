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
import os
import warnings
from astropy import constants as cc
from astropy import units as uu

from SpirouDRS import spirouConfig
from . import spirouLog
from . import spirouMath

# TODO: Is there a better fix for this?
# fix for MacOSX plots freezing
gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
for gui in gui_env:
    # noinspection PyBroadException
    try:
        matplotlib.use(gui, warn=False, force=True)
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        break
    except Exception as e:
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
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value
# -----------------------------------------------------------------------------
INTERACTIVE_PLOTS = spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED()
# check for matplotlib import errors
if len(matplotlib_emsg) > 0:
    WLOG(None, 'error', matplotlib_emsg)
# -----------------------------------------------------------------------------
# set plot parameters
font = spirouConfig.Constants.FONT_DICT()
matplotlib.rc('font', **font)
# set plot style
PLOT_STYLE = spirouConfig.Constants.PLOT_STYLE()
if PLOT_STYLE != 'None':
    plt.style.use(PLOT_STYLE)
else:
    PLOT_STYLE = ''
# get fig size
FIGSIZE = spirouConfig.Constants.PLOT_FIGSIZE()


# =============================================================================
# General plotting functions
# =============================================================================
def start_interactive_session(p, interactive=False):
    """
    Start interactive plot session, if required and if
    spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED() is True

    :param p: ParamDict, the constants parameter dictionary
    :param interactive: bool, if True start interactive session

    :return None:
    """
    if p['DRS_PLOT'] == 2:
        # make sure interactive plotting is off if we are saving figures
        plt.ioff()
        return 0

    if interactive is True:
        # plt.ion()
        matplotlib.interactive(True)
        pass
    # start interactive plot
    elif INTERACTIVE_PLOTS:
        # plt.ion()
        matplotlib.interactive(True)
        pass


def end_interactive_session(p, interactive=False):
    """
    End interactive plot session, if required and if
    spirouConfig.Constants.INTERACITVE_PLOTS_ENABLED() is True

    :param p: ParamDict, the constants parameter dictionary
    :param interactive: bool, if True end interactive session

    :return None:
    """
    if p['DRS_PLOT'] == 2:
        return 0

    if not interactive and not INTERACTIVE_PLOTS:
        plt.show()
        plt.close()


def end_plotting(p, plot_name):
    """
    End plotting properly (depending on DRS_PLOT and interactive mode)

    :param p: ParamDict, the constants parameter dictionary
    :param plot_name:
    :return:
    """
    if p['DRS_PLOT'] == 2:
        # get plotting figure names (as a list for multiple formats)
        snames = define_save_name(p, plot_name)
        # loop around formats
        for sname in snames:
            # log plot saving
            wmsg = 'Saving plot to {0}'
            WLOG(p, '', wmsg.format(sname))
            # save figure
            plt.savefig(sname)
        # close figure cleanly
        plt.close()
        # do not contibue with interactive tests --> return here
        return 0

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


def define_save_name(p, plotname):
    # construct save path
    path = os.path.join(p['DRS_DATA_PLOT'], p['ARG_NIGHT_NAME'])
    # test that path exists
    if not os.path.exists(path):
        os.makedirs(path)
    # construct filename

    filename = p['ARG_FILE_NAMES'][0].split('.fits')[0]
    recipename = p['LOG_OPT']
    filetypes = spirouConfig.Constants.PLOT_EXTENSIONS()

    # loop around file types
    paths = []
    for filetype in filetypes:
        # construct paths
        sargs = [filename, recipename, plotname, filetype]
        sfilename = '{0}_{1}_{2}.{3}'
        paths.append(os.path.join(path, sfilename.format(*sargs)))
    # return paths
    return paths


def setup_figure(p, figsize=FIGSIZE, ncols=1, nrows=1):
    """
    Extra steps to setup figure. On some OS getting error

    "TclError" when using TkAgg. A possible solution to this is to
    try switching to Agg

    :param p:
    :param figsize:
    :param ncols:
    :param nrows:
    :return:
    """
    fix = True
    while fix:
        if ncols == 0 and nrows == 0:
            try:
                fig = plt.figure()
                plt.clf()
                return fig
            except Exception as e:
                if fix:
                    attempt_tcl_error_fix()
                    fix = False
                else:
                    emsg1 = 'An matplotlib error occured'
                    emsg2 = '\tBackend = {0}'.format(plt.get_backend())
                    emsg3 = '\tError {0}: {1}'.format(type(e), e)
                    WLOG(p, 'error', [emsg1, emsg2, emsg3])
        else:
            try:
                fig, frames = plt.subplots(ncols=ncols, nrows=nrows,
                                           figsize=figsize)
                return fig, frames
            except Exception as e:
                if fix:
                    attempt_tcl_error_fix()
                    fix = False
                else:
                    emsg1 = 'An matplotlib error occured'
                    emsg2 = '\tBackend = {0}'.format(plt.get_backend())
                    emsg3 = '\tError {0}: {1}'.format(type(e), e)
                    WLOG(p, 'error', [emsg1, emsg2, emsg3])


# TODO: Need a better fix for this
def attempt_tcl_error_fix():
    plt.switch_backend('agg')


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
    plot_name = 'darkplot_image_and_regions'
    # set up figure
    fig, frame = setup_figure(pp)
    # plot the image
    clim = (0., 10 * pp['MED_FULL'])
    im = frame.imshow(image, origin='lower', clim=clim, cmap='viridis')
    # plot the colorbar
    cbar = plt.colorbar(im, ax=frame)
    cbar.set_label('ADU/s')
    # get the blue region
    bxlow, bxhigh = pp['IC_CCDX_BLUE_LOW'], pp['IC_CCDX_BLUE_HIGH']
    bylow, byhigh = pp['IC_CCDY_BLUE_LOW'], pp['IC_CCDY_BLUE_HIGH']
    # adjust for backwards limits
    if bxlow > bxhigh:
        bxlow, bxhigh = bxhigh - 1, bxlow - 1
    if bylow > byhigh:
        bylow, byhigh = byhigh - 1, bylow - 1
    # plot blue rectangle
    brec = Rectangle((bxlow, bylow), bxhigh - bxlow, byhigh - bylow,
                     edgecolor='w', facecolor='None')
    frame.add_patch(brec)
    # get the red region
    rxlow, rxhigh = pp['IC_CCDX_RED_LOW'], pp['IC_CCDX_RED_HIGH']
    rylow, ryhigh = pp['IC_CCDY_RED_LOW'], pp['IC_CCDY_RED_HIGH']
    # adjust for backwards limits
    if rxlow > rxhigh:
        rxlow, rxhigh = rxhigh - 1, rxlow - 1
    if rylow > ryhigh:
        rylow, ryhigh = ryhigh - 1, rylow - 1
    # plot blue rectangle
    rrec = Rectangle((rxlow, rylow), rxhigh - rxlow, ryhigh - rylow,
                     edgecolor='r', facecolor='None')
    frame.add_patch(rrec)
    plt.title('Dark image with red and blue regions')

    # TODO: needs axis labels and titles
    # end plotting function properly
    end_plotting(pp, plot_name)


def darkplot_datacut(p, imagecut):
    """
    Plot the data cut mask

    :param p: ParamDict, the constants parameter dictionary
    :param imagecut: numpy array (2D), the data cut mask

    :return:
    """
    plot_name = 'darkplot_datacut'
    # set up figure
    fig, frame = setup_figure(p)
    # imagecut need to be integers
    imagecut = imagecut.astype(np.int)
    # plot the image cut
    im = frame.imshow(imagecut, origin='lower', cmap='viridis')
    # plot the colorbar
    fig.colorbar(im, ax=frame)
    # make sure image is bounded by shape
    plt.axis([0, imagecut.shape[0], 0, imagecut.shape[1]])
    plt.title('Dark cut mask')

    # TODO: needs axis labels and title
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'darkplot_histograms'
    # set up figure
    fig, frame = setup_figure(pp)
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
    end_plotting(pp, plot_name)


# =============================================================================
# localization plotting functions
# =============================================================================
# TODO: Why is this still here?
def locplot_order(frame, x, y, label):
    """
    Simple plot function (added to a larger plot)

    :param frame: the matplotlib axis, e.g. plt.gca() or plt.subplot(111)
    :param x: numpy array (1D) or list, the x-axis data
    :param y: numpy array (1D) or list, the y-axis data
    :param label: string, the label for this line (used in legend)

    :return None:
    """
    pass


def locplot_y_miny_maxy(p, y, miny=None, maxy=None):
    """
    Plots the row number against central column pixel value, smoothed minimum
    central pixel value and smoothed maximum, central pixel value

    :param p: ParamDict, the constants parameter dictionary
    :param y: numpy array, central column pixel value
    :param miny: numpy array, smoothed minimum central pixel value
    :param maxy: numpy array, smoothed maximum central pixel value

    :return None:
    """
    plot_name = 'locplot_y_miny_maxy'
    # set up figure
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def locplot_im_sat_threshold(p, loc, image, threshold):
    """
    Plots the image (order_profile) below the saturation threshold

    :param p: ParamDict, the constants parameter dictionary
    :param loc: ParamDict, the data parameter dictionary
    :param image: numpy array (2D), the image
    :param threshold: float, the saturation threshold

    :return None:
    """
    plot_name = 'locplot_im_sat_threshold'
    # get x and y data from loc
    xarr, yarr = loc['XPLOT'], loc['YPLOT']

    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1.0, threshold), cmap='viridis')
    # set the limits
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]))

    # loop around xarr and yarr and plot
    for order_num in range(len(xarr)):
        # x and y
        x, y = xarr[order_num], yarr[order_num]
        # plot
        frame.plot(x, y, label=order_num, linewidth=1.5, color='red')

    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'locplot_order_number_against_rms'
    # set up fig
    fig, frame = setup_figure(pp)
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
    end_plotting(pp, plot_name)


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
    plot_name = 'debug_locplot_min_ycc_loc_threshold'
    # set up figure
    fig, frame = setup_figure(pp)
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
    end_plotting(pp, plot_name)


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
    plot_name = 'debug_locplot_finding_orders'
    plt.ioff()
    # log output for this row
    wargs = [no, ncol, ind0, cgx, wx]
    WLOG(pp, '', '{0:d} {0:d}  {0:f}  {0:f}  {0:f}'.format(*wargs))

    xx = np.array([ind1, cgx - wx / 2., cgx - wx / 2., cgx - wx / 2., cgx,
                   cgx + wx / 2., cgx + wx / 2., cgx + wx / 2., ind2])
    yy = np.array([0., 0., max(ycc) / 2., max(ycc), max(ycc), max(ycc),
                   max(ycc) / 2., 0., 0.])
    # setup figure
    fig, frame = setup_figure(pp)
    # plot orders
    frame.plot(np.arange(ind1, ind2, 1.0), ycc)
    frame.plot(xx, yy)
    frame.set(xlim=(ind1, ind2), ylim=(0, np.max(ycc)+0.01*np.max(ycc)))

    # TODO: Need axis labels and title

    # turn off interactive plotting
    if not plt.isinteractive():
        pass
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)
    plt.show()
    plt.close()
    plt.ion()
    # end plotting function properly
    end_plotting(pp, plot_name)


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
    plot_name = 'debug_locplot_fit_residual_rnun{0}'.format(rnum)
    # get variables from loc dictionary
    x = loc['X']
    xo = loc['CTRO'][rnum]
    y = loc['RES']
    # new fig
    fig, frame = setup_figure(pp)
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
    end_plotting(pp, plot_name)


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
    plot_name = 'slit_sorder_plot'
    # set up fig
    fig, frame = setup_figure(pp)
    # get selected order
    order = pp['IC_SLIT_ORDER_PLOT']
    # work out offset for this order
    offset = np.polyval(loc['ASS'][order][::-1], pp['IC_CENT_COL'])
    offset *= pp['IC_FACDEC']
    offsetarray = np.zeros(len(loc['ASS'][order]))
    offsetarray[0] = offset
    # plot image
    frame.imshow(image, origin='lower', clim=(0., np.mean(image)),
                 cmap='viridis')
    # calculate selected order fit
    xfit = np.arange(image.shape[1])
    yfit1 = np.polyval((loc['ACC'][order] + offsetarray)[::-1], xfit)
    yfit2 = np.polyval((loc['ACC'][order] - offsetarray)[::-1], xfit)
    # plot selected order fit
    frame.plot(xfit, yfit1, color='red')
    frame.plot(xfit, yfit2, color='red')
    # construct title
    title = 'Order {0}'.format(order)
    # set axis limits to image
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title)

    # TODO: Need axis labels and title

    # end plotting function properly
    end_plotting(pp, plot_name)


def slit_tilt_angle_and_fit_plot(p, loc):
    """
    Plot the slit tilt angle and its fit

    :param p: ParamDict, the constants parameter dictionary
    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                xfit_tilt: numpy array (1D), the order numbers
                tilt: numpy array (1D), the tilt angle of each order
                yfit_tilt: numpy array (1D), the fit for the tilt angle of each
                           order

    :return None:
    """
    plot_name = 'slit_tilt_angle_and_fit_plot'
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def slit_shape_angle_plot(p, loc, bnum=None, order=None):
    plot_name = 'slit_shape_angle_plot_it{0}_order{1}'.format(bnum, order)
    # get constants from p
    sorder = p['SHAPE_SELECTED_ORDER']
    nbanana = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']

    # get data from loc
    slope_deg_arr, slope_arr = loc['SLOPE_DEG'], loc['SLOPE']
    s_keep_arr, xsection_arr = loc['S_KEEP'], loc['XSECTION']
    ccor_arr, ddx_arr = loc['CCOR'], loc['DDX']
    dx_arr, dypix_arr, c_keep_arr = loc['DX'], loc['DYPIX'], loc['C_KEEP']
    # get the dimensions
    dim0, dim1 = loc['HCDATA'].shape

    if (bnum is not None) and (order is not None):
        orders = np.array([order])
        bananas = np.array([bnum])
        special = True
    else:
        orders = np.array([sorder])
        bananas = range(nbanana)
        special = False

    # loop around orders
    for order_num in orders:
        # iterating the correction, from coarser to finer
        for banana_num in bananas:
            # get this iterations parameters
            if special:
                slope_deg = slope_deg_arr
                slope = slope_arr
                s_keep = s_keep_arr
                xsection = xsection_arr
                ccor = ccor_arr
                ddx = ddx_arr
                dx = dx_arr
                dypix = dypix_arr
                c_keep = c_keep_arr
            else:
                slope_deg = slope_deg_arr[banana_num][order_num]
                slope = slope_arr[banana_num][order_num]
                s_keep = s_keep_arr[banana_num][order_num]
                xsection = xsection_arr[banana_num][order_num]
                ccor = ccor_arr[banana_num][order_num]
                ddx = ddx_arr[banana_num][order_num]
                dx = dx_arr[banana_num][order_num]
                dypix = dypix_arr[banana_num][order_num]
                c_keep = c_keep_arr[banana_num][order_num]

            # set up fig
            fig, frames = setup_figure(p, ncols=2, nrows=1)
            # set up axis
            frame1, frame2 = frames
            # ----------------------------------------------------------------
            # frame 1
            # ----------------------------------------------------------------
            frame1.plot(xsection[s_keep], slope_deg[s_keep], color='g',
                        marker='o', ls='None')
            frame1.plot(np.arange(dim1), slope)
            # ylim = [np.nanmin(slope_deg[s_keep]) - 0.2,
            #         np.nanmin(slope_deg[s_keep]) + 0.2]
            frame1.set(xlabel='x pixel', ylabel='slope [deg]')
            # ----------------------------------------------------------------
            # frame 2
            # ----------------------------------------------------------------
            frame2.imshow(ccor, aspect=0.2, cmap='viridis')
            frame2.plot(dx - np.min(ddx), dypix, color='r', marker='o',
                        ls='None')
            frame2.plot(dx[c_keep] - np.min(ddx), dypix[c_keep], color='g',
                        marker='o', ls='None')
            frame2.set(ylim=[0.0, width - 1], xlim=[0, len(ddx) - 1])

            # ----------------------------------------------------------------
            # title
            # ----------------------------------------------------------------
            title = 'Iteration {0} - Order {1}'
            plt.suptitle(title.format(banana_num, order_num))

    # if mode is single end properly else if all turn back on interactive mode
    if special:
        pass
    else:
        # end plotting function properly
        end_plotting(p, plot_name)


def slit_shape_dx_plot(p, dx, dx2, bnum):
    plot_name = 'slit_shape_dx_plot_it{0}'.format(bnum)
    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']

    # set the zeropoint
    zeropoint = np.nanmedian(dx)
    # get the sig of dx
    sig_dx = np.nanmedian(np.abs(dx - zeropoint))
    # set up fig
    fig, frames = setup_figure(p, ncols=3, nrows=1)
    # set up axis
    frame1, frame2, frame3 = frames
    # ----------------------------------------------------------------------
    # plot dx
    vmin = (-2 * sig_dx) + zeropoint
    vmax = (2 * sig_dx) + zeropoint
    im1 = frame1.imshow(dx, vmin=vmin, vmax=vmax, cmap='viridis')

    divider1 = make_axes_locatable(frame1)
    cax1 = divider1.append_axes("top", size="10%", pad=0.05)

    cb1 = plt.colorbar(im1, cax=cax1, orientation='horizontal')
    cb1.ax.xaxis.set_ticks_position('top')
    cb1.ax.xaxis.set_label_position('top')
    cb1.set_label('dx')

    frame1.set(xlabel='width [pix]', ylabel='order number', title='dx')
    # ----------------------------------------------------------------------
    # plot dx2
    vmin = (-2 * sig_dx) + zeropoint
    vmax = (2 * sig_dx) + zeropoint
    im2 = frame2.imshow(dx2, vmin=vmin, vmax=vmax, cmap='viridis')

    divider2 = make_axes_locatable(frame2)
    cax2 = divider2.append_axes("top", size="10%", pad=0.05)

    cb2 = plt.colorbar(im2, cax=cax2, orientation='horizontal')
    cb2.ax.xaxis.set_ticks_position('top')
    cb2.ax.xaxis.set_label_position('top')
    cb2.set_label('dx2')

    frame2.set(xlabel='width [pix]', ylabel='order number', title='dx2')
    # ----------------------------------------------------------------------
    # plot diff
    vmin = (-0.5 * sig_dx) + zeropoint
    vmax = (0.5 * sig_dx) + zeropoint
    im3 = frame3.imshow(dx - dx2, vmin=vmin, vmax=vmax, cmap='viridis')

    divider3 = make_axes_locatable(frame3)
    cax3 = divider3.append_axes("top", size="10%", pad=0.05)

    cb3 = plt.colorbar(im3, cax=cax3, orientation='horizontal')
    cb3.ax.xaxis.set_ticks_position('top')
    cb3.ax.xaxis.set_label_position('top')
    cb3.set_label('dx - dx2')

    frame3.set(xlabel='width [pix]', ylabel='order number', title='dx - dx2')

    # ----------------------------------------------------------------------
    # title
    # ----------------------------------------------------------------------
    plt.suptitle('Iteration {0} / {1}'.format(bnum + 1, nbanana))
    # ----------------------------------------------------------------------
    # end plotting function properly
    end_plotting(p, plot_name)


def slit_shape_offset_plot(p, loc, bnum=None, order=None):
    plot_name = 'slit_shape_offset_plot_it{0}_order{1}'.format(bnum, order)
    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']
    # get data from loc
    corr_err_xpix_arr = loc['CORR_DX_FROM_FP']
    xpeak2_arr = loc['XPEAK2']
    err_pix_arr = loc['ERR_PIX']
    goodmask_arr = loc['GOOD_MASK']
    dim0, dim1 = loc['HCDATA'].shape
    order_num, banana_num = order, bnum

    # get this iterations parameters
    corr_err_xpix = corr_err_xpix_arr[order_num]
    xpeak2 = xpeak2_arr[order_num]
    err_pix = err_pix_arr[order_num]
    good = goodmask_arr[order_num]
    # set up fig
    fig, frame = setup_figure(p)
    # ----------------------------------------------------------------
    # plot
    # ----------------------------------------------------------------
    frame.plot(xpeak2, err_pix, color='r', linestyle='None', marker='.',
               label='err pixel')
    frame.plot(xpeak2[good], err_pix[good], color='g', linestyle='None',
               marker='.', label='err pixel (for fit)')
    frame.plot(np.arange(dim1), corr_err_xpix, color='k',
               label='fit to err pix')
    # ----------------------------------------------------------------
    # labels, title, and legend
    # ----------------------------------------------------------------
    title = 'Iteration {0}/{1} - Order {2}'.format(banana_num, nbanana,
                                                   order_num)
    frame.set(xlabel='Pixel', ylabel='Err Pixel', title=title)
    frame.legend(loc=0)
    # ----------------------------------------------------------------------
    # end plotting function properly
    end_plotting(p, plot_name)


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

    plot_name = 'ff_sorder_fit_edges'
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']

    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='viridis')
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
    end_plotting(p, plot_name)


def ff_debanana_plot(p, loc, image):
    plot_name = 'ff_debanana_plot'
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    dim1, dim2 = image.shape
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='viridis')
    # loop around the order numbers
    acc = loc['ACC'][selected_order]
    # work out offsets for this order
    offsetarraylow = np.zeros(len(acc))
    offsetarrayhigh = np.zeros(len(acc))
    offsetarraylow[0] = range2
    offsetarrayhigh[0] = range1
    # get fit and edge fits
    xfit = np.arange(dim2)
    yfit = np.repeat(np.polyval(acc[::-1], dim2 // 2), dim2)
    yfitlow = np.repeat(np.polyval((acc + offsetarraylow)[::-1], dim2 // 2),
                        dim2)
    yfithigh = np.repeat(np.polyval((acc - offsetarrayhigh)[::-1], dim2 // 2),
                         dim2)
    # plot fits
    frame.plot(xfit, yfit, color='red', label='fit')
    frame.plot(xfit, yfitlow, color='blue', label='Fit edge',
               linestyle='--')
    frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image debananafied fit for order {0} fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'ff_aorder_fit_edges'
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']

    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='viridis')

    # loop around the order numbers
    for order_num in range(len(loc['ACC']) // p['NBFIB']):
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
    end_plotting(p, plot_name)


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
    plot_name = 'ff_sorder_tiltadj_e2ds_blaze'
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']
    e2ds = loc['E2DS'][selected_order]
    blaze = loc['BLAZE'][selected_order]
    # set up fig
    fig, frame = setup_figure(p)
    # get xrange
    x = np.arange(len(e2ds))
    # plot e2ds for selected order
    #    frame.plot(x, e2ds, label='E2DS')
    frame.plot(x, e2ds, label='E2DS', marker='.', markersize=2)
    # plot blaze function
    #    frame.plot(x, blaze, label='Blaze')
    frame.plot(x, blaze, label='Blaze')
    # set title labels limits
    title = 'E2DS + BLAZE spectral order {0} fiber {1}'
    frame.set(title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'ff_sorder_flat'
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['FIBER']
    flat = loc['FLAT'][selected_order]
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def ff_rms_plot(p, loc):
    plot_name = 'ff_rms_plot'
    # get constants from p
    remove_orders = np.array(p['FF_RMS_PLOT_SKIP_ORDERS'])
    # set up fig
    fig, frame = setup_figure(p)
    # define a mask to select certain orders
    mask = np.in1d(np.arange(len(loc['RMS'])), remove_orders)
    # apply mask to RMS array
    rmsc = np.where(mask, 0, loc['RMS'])
    # plot
    frame.plot(np.arange(len(loc['RMS'])), rmsc)
    # plot a statistic for mean SNR and mean RMS
    wmsg = 'Mean S/N= {0:.1f} - Mean RMS = {1:.5f}'
    wargs = [np.mean(loc['SNR']), np.mean(rmsc)]
    WLOG(p, '', wmsg.format(*wargs))
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'ext_sorder_fit'
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., cut), cmap='viridis')
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
    end_plotting(p, plot_name)


def ext_debanana_plot(p, loc, image, cut=20000):
    plot_name = 'ext_debanana_plot'
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    dim1, dim2 = image.shape
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., cut), cmap='viridis')
    # loop around the order numbers
    acc = loc['ACC'][selected_order]
    # work out offsets for this order
    offsetarraylow = np.zeros(len(acc))
    offsetarrayhigh = np.zeros(len(acc))
    offsetarraylow[0] = range2
    offsetarrayhigh[0] = range1
    # get fit and edge fits
    xfit = np.arange(dim2)
    yfit = np.repeat(np.polyval(acc[::-1], dim2 // 2), dim2)
    yfitlow = np.repeat(np.polyval((acc + offsetarraylow)[::-1], dim2 // 2),
                        dim2)
    yfithigh = np.repeat(np.polyval((acc - offsetarrayhigh)[::-1], dim2 // 2),
                         dim2)
    # plot fits
    frame.plot(xfit, yfit, color='red', label='fit')
    frame.plot(xfit, yfitlow, color='blue', label='Fit edge',
               linestyle='--')
    frame.plot(xfit, yfithigh, color='blue', linestyle='--')
    # set title labels limits
    title = 'Image debananafied fit for order {0} fiber {1}'
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]),
              title=title.format(selected_order, fiber))
    # Add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)


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

    :param cut: int, the upper cut to apply to the image

    :return None:
    """
    plot_name = 'ext_aorder_fit'
    # get upper and lower bounds
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    # set up fig
    fig, frame = setup_figure(p)
    # plot image
    frame.imshow(image, origin='lower', clim=(1., cut), cmap='viridis')
    # loop around the order numbers
    for order_num in range(len(loc['ACC']) // p['NBFIB']):
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
    end_plotting(p, plot_name)


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
    plot_name = 'ext_spectral_order_plot'
    # get constants
    selected_order = p['IC_EXT_ORDER_PLOT']
    fiber = p['FIBER']
    # get data from loc
    extraction = loc['E2DS'][selected_order]
    # select wavelength solution
    wave = loc['WAVE'][selected_order]
    xlabel = 'Wavelength [nm]'  # [$\AA$]
    # set up fig
    fig, frame = setup_figure(p)
    # plot fits
    frame.plot(wave, extraction, color='red')
    # set title labels limits
    title = 'Spectral order {0} fiber {1}'

    frame.set(xlabel=xlabel, ylabel='flux',
              title=title.format(selected_order, fiber))
    # end plotting function properly
    end_plotting(p, plot_name)


def ext_1d_spectrum_plot(p, x, y):
    plot_name = 'ext_1d_spectrum_plot'
    # set up fig
    fig, frame = setup_figure(p)
    # plot fits
    frame.plot(x, y)
    # set title
    targs = [p['IC_START_ORDER_1D'], p['IC_END_ORDER_1D']]
    title = 'Spectrum (1D) Order {0} to {1}'.format(*targs)
    # set labels
    frame.set(xlabel='Wavelength [nm]', ylabel='flux', title=title)
    # end plotting function properly
    end_plotting(p, plot_name)


def ext_1d_spectrum_debug_plot(p, x, y, w, kind):
    plot_name = 'ext_1d_spectrum_debug_plot'
    # set up fig
    fig, frame = setup_figure(p)
    # get weighted y
    with warnings.catch_warnings(record=True) as _:
        yw = y / w
    # plot lines
    frame.plot(x, y / np.nanmedian(y), color='r', label='prior to division')
    frame.plot(x, w / np.nanmedian(w), color='c', label='weight vector')
    frame.plot(x, yw / np.nanmedian(yw), color='k', label='after division')
    # add legend
    frame.legend(loc=0)
    # set title
    title = 'Debug plot for producing 1D spectrum. Kind = {0}'.format(kind)
    # set labels
    frame.set(xlabel='Wavelength [nm]', ylabel='flux', title=title,
              ylim=[-1, 3])
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'drift_plot_selected_wave_ref'
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
    fig, frame = setup_figure(p)
    # plot fits
    frame.plot(wave, extraction)
    # set title labels limits
    title = 'spectral order {0} fiber {1}'
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title=title.format(selected_order, fiber))
    # end plotting function properly
    end_plotting(p, plot_name)


def drift_plot_photon_uncertainty(p, loc, x=None, y=None):
    """
    Plot the photo noise uncertainty against spectral order number

    :param p: ParamDict, the constants parameter dictionary
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
    plot_name = 'drift_plot_photon_uncertainty'
    # get data from loc
    if x is None:
        x = np.arange(loc['NUMBER_ORDERS'])
    if y is None:
        y = loc['DVRMSREF']
    # set up fig
    fig, frame = setup_figure(p)
    # plot fits
    frame.plot(x, y)
    # set title labels limits
    title = 'Photon noise uncertainty versus spectral order'
    frame.set(xlabel='Order number', ylabel='Photon noise uncertainty',
              title=title)
    # end plotting function properly
    end_plotting(p, plot_name)


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
    plot_name = 'drift_plot_dtime_against_mdrift'
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
        WLOG(p, 'error', [emsg1, emsg2])
        kindstr = None
    # get mstr from kindstr
    if kindstr == 'median':
        mstr = 'Median'
    else:
        mstr = 'Mean'
    # set up fig
    fig, frame = setup_figure(p)
    # plot fits
    frame.errorbar(deltatime, mdrift, yerr=merrdrift, linestyle='none',
                   marker='x')
    # set title labels limits
    title = '{0} drift (with uncertainties) against time from reference'
    frame.set(xlabel='$\Delta$ time [hours]',
              ylabel='{0} drift [m/s]'.format(mstr),
              title=title.format(mstr))
    # end plotting function properly
    end_plotting(p, plot_name)


def drift_peak_plot_dtime_against_drift(p, loc):
    """
    Plot mean drift against time from reference

    :param p: ParamDict, the constants parameter dictionary

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
    plot_name = 'drift_peak_plot_dtime_against_drift'
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
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def drift_plot_correlation_comp(p, loc, ccoeff, iteration):
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

    :param ccoeff: numpy array (1D), the correlation coefficients from the
               Pearson R test

    :param iteration: int, the iteration number

    :return None:
    """
    plot_name = 'drift_plot_correlation_comp_{0}'.format(iteration)
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
    setup_figure(p, ncols=0, nrows=0)
    # set up axis
    frame1 = plt.subplot2grid((2, 3), (0, 0))
    frame2 = plt.subplot2grid((2, 3), (1, 0))
    frame3 = plt.subplot2grid((2, 3), (0, 1), colspan=2)
    frame4 = plt.subplot2grid((2, 3), (1, 1), colspan=2)
    # -------------------------------------------------------------------------
    # order selection
    # -------------------------------------------------------------------------
    # mask
    mask = ccoeff > prcut
    # select bad order
    bad_orders = np.arange(nbo)[~mask]
    bad_order = np.argmin(ccoeff)
    # select worse good order
    good_order = np.argmin(ccoeff[mask])
    # select best order
    best_order = np.argmax(ccoeff[mask])

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
    frame1.imshow(speref_image, cmap='viridis')
    frame1.set(title='Reference frame')
    # turn off axis labels
    frame1.set_yticks(yticks)
    frame1.set_yticklabels(ytext)
    frame1.set_xticklabels([])
    # -------------------------------------------------------------------------
    # plot the science frame
    frame2.imshow(spe_image, cmap='viridis')
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
    targs = [iteration + 1, prcut, best_order, ccoeff[best_order], good_order,
             ccoeff[good_order], bad_order, ccoeff[bad_order]]
    plt.suptitle(title.format(*targs))

    # -------------------------------------------------------------------------
    # end plotting function properly
    end_plotting(p, plot_name)


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
    scale = int(np.ceil(image.shape[dim2] / (image.shape[dim1])))
    # get a new image
    newimage = np.zeros((image.shape[dim1] * scale, image.shape[dim2]))
    newimage -= np.max(image)
    # add the old pixels, repeated

    for pixel in range(image.shape[dim1]):

        start = pixel * scale
        end = scale * (pixel + 1)

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
    plot_name = 'drift_peak_plot_llpeak_amps'
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
    fig, frame = setup_figure(p)
    # plot fits
    frame.plot(wave, extraction)
    frame.plot(llpeak[mask1], logamppeak[mask1], linestyle='none')
    frame.plot(llpeak[mask2], logamppeak[mask2], linestlye='none')
    # set title labels limits
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title='$log_{10}$(Max Amplitudes)')
    # end plotting function properly
    end_plotting(p, plot_name)


# =============================================================================
# CCF plotting function
# =============================================================================
def ccf_rv_ccf_plot(p, x, y, yfit, order=None, fig=None, pause=True,
                    kind=''):
    """
    Plot the CCF plot. RV against CCF and RV against CCF fit, for a specific
    order number "order"

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            OBJNAME: string, the object name from header
            TARGET_RV: float, the target RV from run time/call arguments
            CCF_MASK: float, the CCF Mask from run time/call arguments
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
    plot_name = 'ccf_rv_ccf_plot_order{0}_{1}'.format(order, kind)
    if 'dark' in PLOT_STYLE:
        black = 'w'
    else:
        black = 'k'

    # set up fig
    if fig is None:
        fig, frame = setup_figure(p)
    else:
        frame = plt.subplot(111)
    # plot fits
    frame.plot(x, y, label='data', marker='x', linestyle='none', color=black)
    frame.plot(x, yfit, label='fit', color='r')
    # set title labels limits
    targs = ['({0})'.format(kind), p['TARGET_RV'], p['CCF_MASK']]
    title = 'CCF plot {0}\n Target RV={1} km/s Mask={2}'.format(*targs)

    if order is not None:
        title += ' Order {0}'.format(order)
    frame.set(xlabel='Rv [km/s]', ylabel='CCF', title=title)
    # set legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)
    # pause
    if pause:
        time.sleep(1.0)


# =============================================================================
# wave solution plotting function
# =============================================================================
def wave_littrow_extrap_plot(p, loc, iteration=0):
    plot_name = 'wave_littrow_extrap_plot_{0}'.format(iteration)
    # style
    if 'dark' in PLOT_STYLE:
        black = 'w'
    else:
        black = 'k'
    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # define the x axis data
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    x_points = np.arange(xdim)
    # define the y axis data
    yfit_x_cut = loc['LITTROW_EXTRAP_{0}'.format(iteration)]
    yfit = loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)]
    # set up fig
    fig, frame = setup_figure(p)
    # colours
    colours = np.tile(['r', 'b', 'g', 'y', 'm', black, 'c'], ydim)
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
    end_plotting(p, plot_name)


def wave_littrow_check_plot(p, loc, iteration=0):
    plot_name = 'wave_littrow_check_plot_{0}'.format(iteration)
    # get data from loc
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    # set up colors
    import matplotlib.cm as cm
    # noinspection PyUnresolvedReferences
    colors = cm.rainbow(np.linspace(0, 1, len(x_cut_points)))
    # set up fig
    fig, frame = setup_figure(p)
    # loop around the xcut points
    yy = None
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
    # set frame limits
    if yy is not None:
        ylim_low = np.min((-p['QC_HC_DEV_LITTROW_MAX'], np.min(yy)))
        ylim_up = np.max((p['QC_HC_DEV_LITTROW_MAX'], np.max(yy)))
        frame.set(ylim=(ylim_low, ylim_up))
    # add legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)


def wave_plot_instrument_drift(p, x, spe, speref):
    plot_name = 'wave_plot_instrument_drift'
    # get constants from parameter file
    selected_order = p['IC_WAVE_IDRIFT_PLOT_ORDER']
    fiber = p['FIBER']
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


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

    :param iteration: int, the iteration number

    :return None:
    """
    plot_name = 'wave_plot_final_fp_order_{0}'.format(iteration)
    # get constants
    selected_order = p['IC_FP_N_ORD_FINAL']
    fiber = p['FIBER']
    # get data from loc
    wave = loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)][selected_order]
    fp_data = loc['FPDATA'][selected_order]
    # set up fig
    fig, frame = setup_figure(p)
    # plot
    frame.plot(wave, fp_data)
    # set title labels limits
    title = 'spectral order {0} fiber {1} (iteration = {2})'
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title=title.format(selected_order, fiber, iteration))
    # end plotting function properly
    end_plotting(p, plot_name)


def wave_local_width_offset_plot(p, loc):
    """
    Plot the measured FP cavity width offset against line number

    :param p: ParamDict, the constants parameter dictionary
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FP_M: numpy array, the fp line numbers
            FP_DOPD_OFFSET: numpy array, the measured cavity width offsets
            FP_DOPD_OFFSET_COEFF: numpy array, the fit coefficients
                                  for the cavity width offsets

    :return None:
    """
    plot_name = 'wave_local_width_offset_plot'
    # get data from loc
    fp_m = loc['FP_M']
    fp_dopd = loc['FP_DOPD_OFFSET']
    fp_dopd_coeff = loc['FP_DOPD_OFFSET_COEFF']
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def wave_fp_wavelength_residuals(p, loc):
    """
    Plot the FP line wavelength residuals

    :param p: ParamDict, the constants parameter dictionary
    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                FP_LL_POS: numpy array, the FP line initial wavelengths
                FP_LL_POS_NEW: numpy array, the FP line updated wavelengths

    :return None:
    """
    plot_name = 'wave_fp_wavelength_residuals'
    # get data from loc
    fp_ll = loc['FP_LL_POS']
    fp_ll_new = loc['FP_LL_POS_NEW']
    # set up fig
    fig, frame = setup_figure(p)
    # plot fits
    frame.scatter(fp_ll, fp_ll - fp_ll_new)
    # set title labels limits
    title = 'FP lines wavelength residuals'
    frame.set(xlabel='Initial wavelength [nm]',
              ylabel='New - Initial wavelength [nm]',
              title=title)
    # end plotting function properly
    end_plotting(p, plot_name)


# =============================================================================
# wave solution plotting function (EA)
# =============================================================================
def wave_ea_plot_per_order_hcguess(p, loc, order_num):
    plot_name = 'wave_ea_plot_per_order_hcguess_order_{0}'.format(order_num)
    if p['DRS_PLOT'] < 2:
        plt.ioff()

    if 'dark' in PLOT_STYLE:
        black = 'w'
    else:
        black = 'k'

    # get data from loc
    wave = loc['INITIAL_WAVE_MAP']
    hc_sp = loc['HCDATA']
    # get data from loc
    xpix_ini = np.array(loc['XPIX_INI'])
    g2_ini = np.array(loc['G2_INI'])
    ord_ini = np.array(loc['ORD_INI'])

    # set up mask for the order
    gg = ord_ini == order_num
    # keep only lines for the order
    xpix_ini = xpix_ini[gg]
    g2_ini = g2_ini[gg]

    # set up fig
    fig, frame = setup_figure(p)
    # plot spectrum for order
    frame.plot(wave[order_num, :], hc_sp[order_num, :], color=black)
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
    if p['DRS_PLOT'] == 2:
        end_plotting(p, plot_name)
    else:
        plt.show()
        plt.close()


def wave_ea_plot_allorder_hcguess(p, loc):
    #    plt.ioff()

    plot_name = 'wave_ea_plot_allorder_hcguess'

    if 'dark' in PLOT_STYLE:
        black = 'white'
    else:
        black = 'black'

    # get data from loc
    wave = loc['INITIAL_WAVE_MAP']
    hc_sp = loc['HCDATA']
    # get data from loc
    xpix_ini = np.array(loc['XPIX_INI'])
    g2_ini = np.array(loc['G2_INI'])
    ord_ini = np.array(loc['ORD_INI'])
    nbo = loc['NBO']

    # set up fig
    fig, frame = setup_figure(p)

    # define spectral order colours
    col1 = [black, 'grey']
    label1 = ['Even order data', 'Odd order data']
    col2 = ['green', 'purple']
    label2 = ['Even order fit', 'Odd order fit']

    # loop through the orders
    for order_num in range(nbo):
        # set up mask for the order
        gg = ord_ini == order_num
        # keep only lines for the order
        xpix_p = xpix_ini[gg]
        xpix_p = xpix_p  # + 4088*order_num
        g2_p = g2_ini[gg]

        # get colours from order parity
        col1_1 = col1[np.mod(order_num, 2)]
        col2_1 = col2[np.mod(order_num, 2)]
        label1_1 = label1[np.mod(order_num, 2)]
        label2_1 = label2[np.mod(order_num, 2)]

        # plot spectrum for order
        frame.plot(wave[order_num, :], hc_sp[order_num, :], color=col1_1,
                   label=label1_1)
        # over plot all fits
        for line_it in range(len(xpix_p)):
            xpix = xpix_p[line_it]
            g2 = g2_p[line_it]
            frame.plot(wave[order_num, xpix], g2, color=col2_1,
                       label=label2_1)

    # keep only unique labels and add legend
    handles, labels = frame.get_legend_handles_labels()
    handles1, labels1 = [], []
    for l_it in range(len(labels)):
        if labels[l_it] not in labels1:
            labels1.append(labels[l_it]), handles1.append(handles[l_it])
    frame.legend(handles1, labels1, loc=0, fontsize=12)

    # set title and labels
    frame.set(title='Fitted gaussians on spectrum',
              xlabel='Wavelength [nm]',
              ylabel='Normalized flux')

    # end plotting function properly
    end_plotting(p, plot_name)


def wave_ea_plot_wave_cat_all_and_brightest(p, wave_c, dv, bmask, iteration):
    plot_name = 'wave_ea_plot_wave_cat_all_and_brightest_{0}'.format(iteration)
    # get constants from p
    n_iterations = p['HC_NITER_FIT_TRIPLET']
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def wave_ea_plot_tfit_grid(p, orders, wave_catalog, recon0, gauss_rms_dev,
                           xgau, ew, iteration):
    plot_name = 'wave_ea_plot_tfit_grid_{0}'.format(iteration)
    # get constants from p
    n_iterations = p['HC_NITER_FIT_TRIPLET']
    # get all orders
    all_orders = np.unique(orders)
    # calculate dv values
    dv = ((wave_catalog / recon0) - 1) * speed_of_light
    # get colours
    colours = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # repeat colours to match all_orders
    colours = np.tile(colours, len(all_orders))
    # set up fig
    fig, frames = setup_figure(p, ncols=2, nrows=2)
    # set up axis
    frame1, frame2 = frames[0]
    frame3, frame4 = frames[1]
    # loop around orders
    for order_num in all_orders:
        # identify this orders good values
        good = orders == order_num
        # get colour for this order
        colour = colours[order_num]
        # plot frame1
        frame1.scatter(wave_catalog[good], dv[good], s=5, color=colour)
        # plot frame2
        frame2.scatter(1.0 / gauss_rms_dev[good], dv[good], s=5, color=colour)
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
    end_plotting(p, plot_name)


def wave_ea_plot_line_profiles(p, loc):
    plot_name = 'wave_ea_plot_line_profiles'
    # get style
    if 'dark' in PLOT_STYLE:
        black = 'w'
    else:
        black = 'k'
    # get constants from p
    resmap_size = p['HC_RESMAP_SIZE']
    fit_span = p['HC_RESMAP_DV_SPAN']
    xlim, ylim = p['HC_RESMAP_PLOT_XLIM'], p['HC_RESMAP_PLOT_YLIM']
    # get constants from loc
    map_dvs = loc['RES_MAP_DVS']
    map_lines = loc['RES_MAP_LINES']
    map_params = loc['RES_MAP_PARAMS']
    resolution_map = loc['RES_MAP']
    # get dimensions
    nbo, nbpix = loc['NBO'], loc['NBPIX']
    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))

    # set up fig (double the fig size)
    fig, frames = setup_figure(p, nrows=resmap_size[0], ncols=resmap_size[1],
                               figsize=np.array(FIGSIZE) * 2)

    order_range = np.arange(0, nbo, bin_order)
    x_range = np.arange(0, nbpix // bin_x)
    # loop around the order bins
    for order_num in order_range:
        # loop around the x position
        for xpos in x_range:
            # get the correct frame
            frame = frames[order_num // bin_order, xpos]
            # get the correct data
            all_dvs = map_dvs[order_num // bin_order][xpos]
            all_lines = map_lines[order_num // bin_order][xpos]
            params = map_params[order_num // bin_order][xpos]
            resolution = resolution_map[order_num // bin_order][xpos]
            # get fit data
            xfit = np.linspace(fit_span[0], fit_span[1], 100)
            yfit = spirouMath.gauss_fit_s(xfit, *params)
            # plot data
            frame.scatter(all_dvs, all_lines, color='g', s=5, marker='x')
            frame.plot(xfit, yfit, color=black, ls='--')

            # set frame limits
            frame.set(xlim=xlim, ylim=ylim)

            # add label in legend (for sticky position
            largs = [order_num, order_num + bin_order - 1, xpos, resolution]
            handle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                               edgecolor='none', linewidth=0)
            label = 'Orders {0}-{1} region={2} R={3:.0f}'.format(*largs)
            frame.legend([handle], [label], loc=9, fontsize=10)

            # remove white space and some axis ticks
            if order_num == 0:
                frame = remove_first_last_ticks(frame, axis='x')
                frame.xaxis.tick_top()
                frame.xaxis.set_label_position('top')
                frame.set_xlabel('dv [km/s]')
            elif order_num == np.max(order_range):
                frame = remove_first_last_ticks(frame, axis='x')
                frame.set_xlabel('dv [km/s]')
            else:
                frame.set_xticklabels([])
            if xpos == 0:
                frame = remove_first_last_ticks(frame, axis='y')
                frame.set_ylabel('Amp')
            elif xpos == np.max(x_range):
                frame = remove_first_last_ticks(frame, axis='y')
                frame.yaxis.tick_right()
                frame.yaxis.set_label_position('right')
                frame.set_ylabel('Amp')
            else:
                frame.set_yticklabels([])

    plt.subplots_adjust(hspace=0, wspace=0)
    plt.suptitle('Line Profiles for resolution grid')
    # end plotting function properly
    end_plotting(p, plot_name)


def wave_ea_plot_single_order(p, loc):
    plot_name = 'wave_ea_plot_single_order'
    # set order to plot
    plot_order = p['IC_WAVE_EA_PLOT_ORDER']
    # get the correct order to plot for all_lines
    #    (which is sized n_ord_final-n_ord_start)
    plot_order_line = plot_order - p['IC_HC_N_ORD_START_2']
    # set up fig
    fig, frame = setup_figure(p)
    # plot order and flux
    frame.plot(loc['LL_OUT_2'][plot_order], loc['HCDATA'][plot_order],
               label='HC spectrum - order ' + str(plot_order))
    # plot found lines
    # first line separate for labelling purposes
    x0i = loc['ALL_LINES_1'][plot_order_line][0][0]
    x0ii = loc['ALL_LINES_1'][plot_order_line][0][3]
    x0 = x0i + x0ii
    ymax0 = loc['ALL_LINES_1'][plot_order_line][0][2]
    frame.vlines(x0, 0, ymax0, color='m', label='fitted lines')
    # plot lines to the top of the figure
    maxpoint = np.max(loc['HCDATA'][plot_order])
    plt.vlines(x0, 0, maxpoint, color='gray', linestyles='dotted')
    # rest of lines
    for i in range(1, len(loc['ALL_LINES_1'][plot_order_line])):
        # get x and y
        x = loc['ALL_LINES_1'][plot_order_line][i][0] + \
            loc['ALL_LINES_1'][plot_order_line][i][3]
        ymaxi = loc['ALL_LINES_1'][plot_order_line][i][2]
        # plot lines to their corresponding amplitude
        frame.vlines(x, 0, ymaxi, color='m')
        # plot lines to the top of the figure
        frame.vlines(x, 0, maxpoint, color='gray', linestyles='dotted')
    # plot
    frame.legend(loc=0)
    frame.set(xlabel='Wavelength', ylabel='Flux')
    # end plotting function properly
    end_plotting(p, plot_name)


# =============================================================================
# telluric plotting function
# =============================================================================
def mk_tellu_wave_flux_plot(p, order_num, wave, tau1, sp, sp3, sed,
                            sed_update, keep):
    plot_name = 'mk_tellu_wave_flux_plot_order_{0}'.format(order_num)
    # get order values
    good = keep[order_num]
    x = wave[order_num]
    y1 = tau1[order_num]
    y2 = sp[order_num]
    y3 = sp[order_num] / sed[order_num]
    y4 = sp3
    y5 = sed_update

    # deal with no good values
    if np.sum(good) == 0:
        y4 = np.repeat(np.nan, len(x))
        good = np.ones(len(x), dtype=bool)

    # set up fig
    fig, frame = setup_figure(p)
    # plot data
    frame.plot(x, y1, color='c', label='tapas fit')
    frame.plot(x, y2, color='k', label='input spectrum')
    frame.plot(x, y3, color='b', label='measured transmission')

    frame.plot(x[good], y4[good], color='r', marker='.', linestyle='None',
               label='SED calculation value')
    frame.plot(x, y5, color='g', linestyle='--', label='SED best guess')

    # get max / min y
    values = list(y1) + list(y2) + list(y3) + list(y4[good]) + list(y5)
    mins = 0.95 * np.nanmin([0, np.nanmin(values)])
    maxs = 1.05 * np.nanmax(values)

    # plot legend and set up labels / limits / title
    frame.legend(loc=0)
    frame.set(xlim=(np.min(x[good]), np.max(x[good])),
              ylim=(mins, maxs),
              xlabel='Wavelength [nm]', ylabel='Normalised flux',
              title='Order: {0}'.format(order_num))
    # end plotting function properly
    end_plotting(p, plot_name)


def tellu_trans_map_plot(p, loc, order_num, fmask, sed, trans, sp, ww, outfile):
    plot_name = 'tellu_trans_map_plot_order_{0}'.format(order_num)
    # get data from loc
    wave = loc['WAVE'][order_num, :]
    # set up fig
    fig, frame = setup_figure(p)
    # plot trans_map and spectra
    frame.plot(wave, sp[order_num, :], 'r.', label='Spectrum')
    frame.plot(wave[fmask], sp[order_num][fmask], 'b.', label='Spectrum (kept)')
    frame.plot(wave, sed, 'r-', label='Fitted SED')
    frame.plot(wave, trans, 'c-', label='Transmission')
    frame.plot(wave, sp[order_num, :] / sed[:], 'g-', label='Spectrum/SED')
    frame.plot(wave, np.ones_like(sed), color='purple', ls='-')
    frame.plot(wave, ww, 'k-', label='Weights')
    frame.set_title(outfile)
    # set limit
    frame.set(ylim=[0.6, 1.4])
    # add legend
    frame.legend(loc=0)
    # add labels
    title = 'Tranmission map plot (Order {0})'
    frame.set(title=title.format(order_num),
              xlabel='Wavelength [nm]', ylabel='Normalised flux')
    # end plotting function properly
    end_plotting(p, plot_name)


def tellu_pca_comp_plot(p, loc):
    plot_name = 'tellu_pca_comp_plot'
    # get constants from p
    npc = loc['NPC']
    # get data from loc
    wave = loc['WAVE'].ravel()
    pc = loc['PC']
    # set up fig
    fig, frame = setup_figure(p)
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
    # add labels
    title = 'Principle component plot'
    frame.set(title=title, xlabel='Wavelength [nm]',
              ylabel='Principle component power')
    # end plotting function properly
    end_plotting(p, plot_name)


def tellu_fit_tellu_spline_plot(p, loc):
    plot_name = 'tellu_fit_tellu_spline_plot'
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
    srecov = ssp / stemp
    # set up fig
    fig, frame = setup_figure(p)
    # plot spectra for selected order
    frame.plot(swave, ssp / np.nanmedian(ssp), label='Observed SP')
    frame.plot(swave, stemp / np.nanmedian(stemp), label='Template SP')
    frame.plot(swave, srecov / np.nanmedian(srecov), label='Recov abso SP')
    # add legend
    frame.legend(loc=0)
    # add labels
    title = 'Reconstructed Spline Plot (Order = {0})'
    frame.set(title=title.format(selected_order),
              xlabel='Wavelength [nm]', ylabel='Normalised flux')
    # end plotting function properly
    end_plotting(p, plot_name)


def tellu_fit_debug_shift_plot(p, loc):
    plot_name = 'tellu_fit_debug_shift_plot'
    # get constants from p
    s_order = p['TELLU_PLOT_ORDER']

    ydim, xdim = loc['DATA'].shape
    # get data from loc
    tdata = loc['SP']
    tapas_before = loc['TAPAS_ALL_PRESHIFT'][0]
    tapas_after = loc['TAPAS_ALL_SPECIES'][0]
    pc1_before = loc['PC_PRESHIFT'][:, 0]
    pc1_after = loc['PC'][:, 0]
    # only show selected order
    # get start and end points
    start = s_order * xdim
    end = s_order * xdim + xdim
    # get this orders data
    tdata_s = tdata[s_order, :] / np.nanmedian(tdata[s_order, :])
    tapas_before_s = tapas_before[start:end]
    tapas_after_s = tapas_after[start:end]
    pc1_before_s = pc1_before[start:end]
    pc1_after_s = pc1_after[start:end]
    # setup fig
    fig, frame = setup_figure(p)
    # plot the data vs pixel number
    frame.plot(tdata_s, color='k', label='Spectrum')
    frame.plot(pc1_before_s, color='g', marker='x', label='PC (before)')
    frame.plot(tapas_before_s, color='0.5', marker='o', label='TAPAS (before)')
    frame.plot(pc1_after_s, color='r', label='PC (After)')
    frame.plot(tapas_after_s, color='b', label='TAPAS (After)')

    frame.legend(loc=0)
    title = ('Wavelength shift (Before and after) compared to the data '
             '(Order {0})')
    frame.set(title=title.format(s_order), xlabel='Pixel number',
              ylabel='Normalised flux')
    # end plotting function properly
    end_plotting(p, plot_name)


def tellu_fit_recon_abso_plot(p, loc):
    plot_name = 'tellu_fit_recon_abso_plot'
    # get style
    if 'dark' in PLOT_STYLE:
        black = 'w'
    else:
        black = 'k'

    nbo = loc['WAVE_IT'].shape[0]

    # get constants from p
    selected_order = p['TELLU_FIT_RECON_PLT_ORDER']

    if selected_order == 'all':
        sorders = list(range(0, nbo))
    else:
        sorders = [selected_order]

    for selected_order in sorders:
        # get data dimensions
        ydim, xdim = loc['DATA'].shape
        # get selected order wave lengths
        swave = loc['WAVE_IT'][selected_order, :]
        # get the data from loc for selected order
        start, end = selected_order * xdim, selected_order * xdim + xdim
        ssp = np.array(loc['SP'][selected_order, :])
        ssp2 = np.array(loc['SP2'][start:end])
        stemp2 = np.array(loc['TEMPLATE2'][start:end])
        srecon_abso = np.array(loc['RECON_ABSO'][start:end])
        # set up fig
        fig, frame = setup_figure(p)
        # plot spectra for selected order
        frame.plot(swave, ssp / np.nanmedian(ssp), color=black,
                   label='input SP')
        frame.plot(swave, ssp2 / np.nanmedian(ssp2) / srecon_abso, color='g',
                   label='Cleaned SP')
        frame.plot(swave, stemp2 / np.nanmedian(stemp2), color='c',
                   label='Template')
        frame.plot(swave, srecon_abso, color='r', label='recon abso')
        # add legend
        frame.legend(loc=0)
        # add labels
        title = 'Reconstructed Absorption (Order = {0})'
        frame.set(title=title.format(selected_order),
                  xlabel='Wavelength [nm]', ylabel='Normalised flux')

    # end plotting function properly
    end_plotting(p, plot_name)


# =============================================================================
# Polarimetry plotting functions
# =============================================================================
def polar_continuum_plot(p, loc, in_wavelengths=True):
    plot_name = 'polar_continuum_plot'
    # get data from loc
    wl, pol = loc['FLAT_X'], 100.0 * loc['FLAT_POL']
    contpol = 100.0 * loc['CONT_POL']
    contxbin, contybin = np.array(loc['CONT_XBIN']), np.array(loc['CONT_YBIN'])
    contybin = 100. * contybin
    stokes = loc['STOKES']
    method, nexp = loc['METHOD'], loc['NEXPOSURES']

    # ---------------------------------------------------------------------
    # set up fig
    fig, frame = setup_figure(p)
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
    end_plotting(p, plot_name)


def polar_result_plot(p, loc, in_wavelengths=True):
    plot_name = 'polar_result_plot'
    # get data from loc
    wl, pol = loc['FLAT_X'], 100.0 * loc['FLAT_POL']
    null1, null2 = 100.0 * loc['FLAT_NULL1'], 100.0 * loc['FLAT_NULL2']
    stokes = loc['STOKES']
    method, nexp = loc['METHOD'], loc['NEXPOSURES']
    # ---------------------------------------------------------------------
    # set up fig
    fig, frame = setup_figure(p)
    # clear the current figure
    plt.clf()
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
    end_plotting(p, plot_name)


def polar_stokes_i_plot(p, loc, in_wavelengths=True):
    plot_name = 'polar_stokes_i_plot'
    # get data from loc
    wl, stokes_i = loc['FLAT_X'], loc['FLAT_STOKESI']
    stokes_ierr = loc['FLAT_STOKESIERR']
    stokes = 'I'
    method, nexp = loc['METHOD'], loc['NEXPOSURES']
    # ---------------------------------------------------------------------
    # set up fig
    fig, frame = setup_figure(p)
    # clear the current figure
    plt.clf()
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
    plt.errorbar(wl, stokes_i, yerr=stokes_ierr, fmt='-', label='Stokes I',
                 alpha=0.5)
    # ---------------------------------------------------------------------
    # set title and labels
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # end plotting function properly
    end_plotting(p, plot_name)


def polar_lsd_plot(p, loc):
    plot_name = 'polar_lsd_plot'
    # get data from loc
    vels = loc['LSD_VELOCITIES']
    zz = loc['LSD_STOKESI']
    zgauss = loc['LSD_STOKESI_MODEL']
    z_p = loc['LSD_STOKESVQU']
    z_np = loc['LSD_NULL']
    stokes = loc['STOKES']

    # ---------------------------------------------------------------------
    # set up fig
    fig, frames = setup_figure(p, ncols=1, nrows=3)
    # clear the current figure
    plt.clf()

    # ---------------------------------------------------------------------
    frame = frames[0]
    plt.plot(vels, zz, '-')
    plt.plot(vels, zgauss, '-')
    title = 'LSD Analysis'
    ylabel = 'Stokes I profile'
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    frame = frames[1]
    title = ''
    plt.plot(vels, z_p, '-')
    ylabel = 'Stokes {0} profile'.format(stokes)
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    frame = frames[2]
    plt.plot(vels, z_np, '-')
    xlabel = 'velocity (km/s)'
    ylabel = 'Null profile'
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # turn off interactive plotting
    # end plotting function properly
    end_plotting(p, plot_name)


# =============================================================================
# worker functions
# =============================================================================
def remove_first_last_ticks(frame, axis='x'):
    if axis == 'x' or axis == 'both':
        xticks = frame.get_xticks()
        xticklabels = xticks.astype(str)
        xticklabels[0], xticklabels[-1] = '', ''
        frame.set_xticks(xticks)
        frame.set_xticklabels(xticklabels)
    if axis == 'y' or axis == 'both':
        yticks = frame.get_xticks()
        yticklabels = yticks.astype(str)
        yticklabels[0], yticklabels[-1] = '', ''
        frame.set_xticks(yticks)
        frame.set_xticklabels(yticklabels)
    return frame

# =============================================================================
# End of code
# =============================================================================
