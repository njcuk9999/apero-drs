#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-02 at 16:29

@author: cook

Import rules: Only from spirouConfig and spirouCore

Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time

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
    if interactive is True:
        plt.ion()
    # start interactive plot
    elif INTERACTIVE_PLOTS:
        plt.ion()


def end_interactive_session(interactive=False):
    if not interactive and not INTERACTIVE_PLOTS:
        plt.show()
        plt.close()

# =============================================================================
# dark plotting functions
# =============================================================================
def darkplot_image_and_regions(pp, image):
    """
    Plot the image and the red and plot regions

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image

    :return:
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


def darkplot_datacut(imagecut):
    """
    Plot the data cut mask

    :param imagecut: numpy array (2D), the data cut mask

    :return:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot the image cut
    im = frame.imshow(imagecut, origin='lower', cmap='gray')
    # plot the colorbar
    plt.colorbar(im, ax=frame)
    # make sure image is bounded by shape
    plt.axis([0, imagecut.shape[0], 0, imagecut.shape[1]])


def darkplot_histograms(pp):
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


# =============================================================================
# localization plotting functions
# =============================================================================
def locplot_order(frame, x, y, label):
    frame.plot(x, y, label=label)


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
    frame.imshow(image, origin='lower', clim=(1.0, threshold), cmap='pink')
    # set the limits
    frame.set(xlim=(0, image.shape[0]), ylim=(0, image.shape[1]))
    # return fig and frame
    return fig, frame


def locplot_order_number_against_rms(pp, loc, rnum):
    """

    :param pp:
    :param loc:
    :param rnum:
    :return:
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

    :param pp: dictionary, parameter dictionary
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
    frame.plot(rownumber, np.minimum(cvalues, pp['IC_LOC_SEUIL']))
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

    :param pp:
    :param no:
    :param ncol:
    :param ind0:
    :param ind1:
    :param ind2:
    :param cgx:
    :param wx:
    :param ycc:
    :return:
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


def debug_locplot_fit_residual(pp, loc, rnum, kind):
    """

    :param pp:
    :param loc:
    :param rnum:
    :param kind:
    :return:
    """
    # get variables from loc dictionary
    x = loc['x']
    xo = loc['ctro'][rnum]
    if kind == 'center':
        y = loc['pos_diff']
    else:
        y = loc['wid_diff']
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

    :param pp: dictionary, parameter dictionary
    :param loc: dictionary, localisation parameter dictionary
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
    offsetarray[0] = -2*offset
    # plot image
    frame.imshow(image, origin='lower', clim=(1., 30000.))
    # calculate selected order fit
    xfit = np.arange(image.shape[1])
    yfit1 = np.polyval(loc['acc'][order][::-1], xfit)
    yfit2 = np.polyval((loc['acc'][order] + offsetarray)[::-1], xfit)
    # plot selected order fit
    frame.plot(xfit, yfit1, color='red')
    frame.plot(xfit, yfit2, color='red')
    # set axis limits to image
    frame.set(xlim=(0, image.shape[0]), ylim=(0, image.shape[1]))
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


def slit_tilt_angle_and_fit_plot(pp, loc):
    """
    Plot the slit tilt angle and its fit

    :param pp: dictionary, parameter dictionary
    :param loc: dictionary, localisation parameter dictionary
    :return None:
    """
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot tilt
    frame.plot(loc['xfit_tilt'], loc['tilt'])
    # plot tilt fit
    frame.plot(loc['xfit_tilt'], loc['yfit_tilt'])
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
    # get fit and edge fits
    xfit = np.arange(image.shape[1])
    yfit = np.polyval(acc[::-1], xfit)
    yfitlow = np.polyval(acc[::-1], xfit) + range2
    yfithigh = np.polyval(acc[::-1], xfit) - range1
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
    for order_num in range(len(loc['acc'])):
        acc = loc['acc'][order_num]
        # get fit and edge fits
        xfit = np.arange(image.shape[1])
        yfit = np.polyval(acc[::-1], xfit)
        yfitlow = np.polyval(acc[::-1], xfit) + range2
        yfithigh = np.polyval(acc[::-1], xfit) - range1
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


def ff_sorder_tiltadj_e2ds_blaze(p, loc, image):

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
    x = np.arange(image.shape[1])
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


def ff_sorder_flat(p, loc, image):
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
    x = np.arange(image.shape[1])
    # plot e2ds for selected order
    frame.plot(x, flat, label='E2DS')
    # set title labels limits
    title = 'FLAT spectral order {0} fiber {1}'
    frame.set(title=title.format(selected_order, fiber))
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
    frame.imshow(image, origin='lower', clim=(1., 20000), cmap='jet')
    # loop around the order numbers
    acc = loc['acc'][selected_order]
    # get fit and edge fits
    xfit = np.arange(image.shape[1])
    yfit = np.polyval(acc[::-1], xfit)
    # plot fits
    frame.plot(xfit, yfit, color='red', label='fit')
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
    for order_num in range(len(loc['acc'])):
        acc = loc['acc'][order_num]
        # get fit and edge fits
        xfit = np.arange(image.shape[1])
        yfit = np.polyval(acc[::-1], xfit)
        # plot fits
        if order_num == selected_order:
            frame.plot(xfit, yfit, color='orange',
                       label='Selected Order fit')
        elif order_num == 0:
            frame.plot(xfit, yfit, color='red', label='fit')
        else:
            frame.plot(xfit, yfit, color='red')
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
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
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
# extract plotting function
# =============================================================================
def drift_plot_selected_wave_ref(p, loc):
    # get constants
    selected_order = p['IC_FF_ORDER_PLOT']
    fiber = p['fiber']
    # get data from loc
    wave = loc['wave'][selected_order]
    extraction = loc['speref'][selected_order]
    # set up fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot fits
    frame.plot(wave, extraction)
    # set title labels limits
    title = 'FP spectral order {0} fiber {1}'
    frame.set(xlabel='Wavelength [$\AA$]', ylabel='flux',
              title=title.format(selected_order, fiber))
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


def drift_plot_photon_uncertainty(p, loc):
    # get data from loc
    x = np.arange(p['number_orders'])
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
