#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-03 at 10:51

@author: cook
"""
import numpy as np
import copy
import os

from terrapipe.core import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.plotting.plot_functions.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# set up definition storage
definitions = []
# -----------------------------------------------------------------------------


# =============================================================================
# Define plotting class
# =============================================================================
class Graph:
    def __init__(self, name, kind='debug', func=None, filename=None,
                 description=None, figsize=None, dpi=None):
        self.name = name
        # set kind
        if kind in ['debug', 'summary']:
            self.kind = kind
        else:
            self.kind = None
        # set function
        self.func = func
        # storage of filename
        self.filename = filename
        # set the description
        if description is None:
            self.description = self.name
        else:
            self.description = str(description)
        # set the figsize
        if figsize is None:
            self.figsize = (6.4, 4.8)
        else:
            self.figsize = figsize
        # set the dots per inch
        if dpi is None:
            self.dpi = 100
        else:
            self.dpi = dpi

    def copy(self):
        """
        Make a copy of the Graph instance (don't ever want to set values to
        the default ones defined below)
        :return:
        """
        name = copy.deepcopy(self.name)
        # deep copy other parameters (deep copy as could be string or None)
        kwargs = dict()
        kwargs['kind'] = copy.deepcopy(self.kind)
        kwargs['func'] = self.func
        kwargs['filename'] = copy.deepcopy(self.filename)
        kwargs['description'] = copy.deepcopy(self.description)
        kwargs['figsize'] = copy.deepcopy(self.figsize)
        kwargs['dpi'] = copy.deepcopy(self.dpi)
        # return new instance
        return Graph(name, **kwargs)

    def set_filename(self, params, location, fiber=None):
        """
        Set the file name for this Graph instance
        :param params:
        :param location:
        :return:
        """
        # get pid
        pid = params['PID']
        # construct filename
        filename = 'plot_{0}_{1}'.format(self.name, pid)
        # make filename all lowercase
        filename = filename.lower()
        # deal with fiber
        if fiber is not None:
            filename += '_{0}'.format(fiber)
        # construct absolute filename
        self.filename = os.path.join(location, filename)

    def set_figure(self, plotter, **kwargs):
        # get plt from plotter (for matplotlib set up)
        plt = plotter.plt
        # get figure and frame
        fig, frames = plt.subplots(**kwargs)
        # set figure parameters
        fig.set_size_inches(self.figsize)
        # return figure and frames
        return fig, frames

    def set_grid(self, plotter, **kwargs):
        # get plt from plotter (for matplotlib set up)
        plt = plotter.plt
        # get figure and frame
        fig = plt.figure()
        # get grid
        gs = fig.add_gridspec(**kwargs)
        # set figure parameters
        fig.set_size_inches(self.figsize)
        # return figure and frames
        return fig, gs


# =============================================================================
# Define user graph functions
# =============================================================================
def ulegend(frame=None, plotter=None, **kwargs):
    # deal with no frame set
    if frame is None:
        frame = plotter.plt.gca()
    # get current legends labels and handles
    all_h, all_l = frame.get_legend_handles_labels()
    # storage
    unique_h, unique_l = [], []
    # loop around labels and only keep unique labels
    for it, label in enumerate(all_l):
        if label not in unique_l:
            unique_l.append(label)
            unique_h.append(all_h[it])
    # plot legend
    frame.legend(unique_h, unique_l, **kwargs)


# =============================================================================
# Define test plotting functions
# =============================================================================
def graph_test_plot_1(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = kwargs['x']
    y = kwargs['y']
    colour = kwargs['colour']
    # ------------------------------------------------------------------
    # plot
    fig, frame = graph.set_figure(plotter)
    frame.plot(x, y, color=colour, label='test')
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def graph_test_plot_2(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    ord = kwargs['ord']
    x_arr = kwargs['x']
    y_arr = kwargs['y']
    colour = kwargs.get('colour', 'k')
    # ------------------------------------------------------------------
    # get the plot generator
    generator = plotter.plotloop(ord)
    # loop aroun the orders
    for ord_num in generator:
        fig, frame = graph.set_figure(plotter)
        frame.plot(x_arr[ord_num], y_arr[ord_num], color=colour)
        frame.set_title('Order {0}'.format(ord_num))
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


# defined graphing instances
test_plot1 = Graph('TEST1', kind='summary', func=graph_test_plot_1,
                   description='This is a test plot',
                   figsize=(10, 10), dpi=150)
test_plot2 = Graph('TEST2', kind='debug', func=graph_test_plot_1)
test_plot3 = Graph('TEST3', kind='debug', func=graph_test_plot_2)
# add to definitions
definitions += [test_plot1, test_plot2, test_plot3]


# =============================================================================
# Define dark plotting functions
# =============================================================================
def plot_dark_image_regions(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # get matplotlib rectange
    Rectangle = plotter.matplotlib.patches.Rectangle
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    image = kwargs['image']
    # get parameters from params
    bxlow = params['IMAGE_X_BLUE_LOW']
    bxhigh = params['IMAGE_X_BLUE_HIGH']
    bylow = params['IMAGE_Y_BLUE_LOW']
    byhigh = params['IMAGE_Y_BLUE_HIGH']
    rxlow = params['IMAGE_X_RED_LOW']
    rxhigh = params['IMAGE_X_RED_HIGH']
    rylow = params['IMAGE_Y_RED_LOW']
    ryhigh = params['IMAGE_Y_RED_HIGH']
    med = kwargs['med']
    # ------------------------------------------------------------------
    # adjust for backwards limits
    if bxlow > bxhigh:
        bxlow, bxhigh = bxhigh - 1, bxlow - 1
    if bylow > byhigh:
        bylow, byhigh = byhigh - 1, bylow - 1
    # adjust for backwards limits
    if rxlow > rxhigh:
        rxlow, rxhigh = rxhigh - 1, rxlow - 1
    if rylow > ryhigh:
        rylow, ryhigh = ryhigh - 1, rylow - 1
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot the image
    clim = (0., 10 * med)
    im = frame.imshow(image, origin='lower', clim=clim, cmap='viridis')
    # plot blue rectangle
    brec = Rectangle((bxlow, bylow), bxhigh - bxlow, byhigh - bylow,
                     edgecolor='b', facecolor='None')
    frame.add_patch(brec)
    # plot blue rectangle
    rrec = Rectangle((rxlow, rylow), rxhigh - rxlow, ryhigh - rylow,
                     edgecolor='r', facecolor='None')
    frame.add_patch(rrec)
    # add colorbar
    plt.colorbar(im)
    # set title
    frame.set_title('Dark image with red and blue regions')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_dark_histogram(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    histo_f, edge_f = kwargs['histograms'][0]
    histo_b, edge_b = kwargs['histograms'][1]
    histo_r, edge_r = kwargs['histograms'][2]
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
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
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


# defined graphing instances
dark_image_regions = Graph('DARK_IMAGE_REGIONS', kind='debug',
                           func=plot_dark_image_regions)
dark_histogram = Graph('DARK_HISTOGRAM', kind='debug',
                       func=plot_dark_histogram)
summary_dark_image_regions = Graph('SUM_DARK_IMAGE_REGIONS', kind='summary',
                                   func=plot_dark_image_regions)
summary_dark_histogram = Graph('SUM_DARK_HISTOGRAM', kind='summary',
                               func=plot_dark_histogram)
# add to definitions
definitions += [dark_image_regions, dark_histogram,
                summary_dark_image_regions, summary_dark_histogram]


# =============================================================================
# Define badpix plotting functions
# =============================================================================
def plot_badpix_map(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    badmap = kwargs['badmap']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot the map
    im = frame.imshow(badmap.astype(int), origin='lower', cmap='viridis')
    # add title
    frame.set_title('Bad pixel map')
    # add colorbar
    plt.colorbar(im, ax=frame)
    # set title
    frame.set_title('Dark image with red and blue regions')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


# defined graphing instances
badpix_map = Graph('BADPIX_MAP', kind='debug', func=plot_badpix_map)
summary_badpix_map = Graph('SUM_BADPIX_MAP', kind='summary',
                           func=plot_badpix_map)
# add to definitions
definitions += [badpix_map, summary_badpix_map]


# =============================================================================
# Define localisation plotting functions
# =============================================================================
def plot_loc_minmax_cents(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    y = kwargs['y']
    miny = kwargs['miny']
    maxy = kwargs['maxy']
    # set up the row number
    rownumber = np.arange(len(y))
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
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
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_loc_min_cents_thres(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    threshold = kwargs['threshold']
    centers = kwargs['centers']
    # set up the row number
    rownumber = np.arange(len(centers))
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot the centers
    frame.plot(rownumber, np.minimum(centers, threshold))
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_loc_finding_orders(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    plotdict = kwargs['plotdict']
    plotlimits = kwargs['plimits']
    # get the plot loop generator (around orders)
    generator = plotter.plotloop(list(plotdict.keys()))
    # prompt to start looper
    plotter.close_plots(loop=True)
    # loop around orders
    for order_num in generator:
        # get this orders values
        col_vals = plotdict[order_num]
        # expand limits
        minxcc, maxxcc, minycc, maxycc = plotlimits[order_num]
        # get the length
        length = len(col_vals)
        # get colours for each line
        colors = plt.cm.jet(np.linspace(0, 1, len(col_vals)))[::-1]
        # get the number of columns
        ncols = int(np.ceil(np.sqrt(length)))
        nrows = int(np.ceil(length / ncols))
        # set up plot
        fig, frames = graph.set_figure(plotter, ncols=ncols, nrows=nrows)
        # loop around col_vals
        for row in range(np.product(frames.shape)):
            # get the correct frame
            jt, it = row % ncols, row // ncols
            frame = frames[it, jt]
            # deal with out of bounds frames
            if row >= length:
                frame.axis('off')
                continue
            # get the col val
            col_val = col_vals[row]
            # get variables for this col_val
            rowcenter, rowtop, rowbottom, center, width, ycc = col_val
            # plot data
            xpix = np.arange(rowtop - center, rowbottom - center, 1.0)
            frame.plot(xpix, ycc, color=colors[row])
            # plot lines
            frame.vlines(-width / 2, ymin=0.0, ymax=maxycc,
                         colors=colors[row])
            frame.vlines(width / 2, ymin=0.0, ymax=maxycc,
                         colors=colors[row])
            # set lim
            frame.set(ylim=[minycc, maxycc], xlim=[minxcc, maxxcc])
            # add center text
            frame.text(0.5, 0.1, 'C={0:.2f}'.format(center),
                       fontdict=dict(fontsize=8), horizontalalignment='center',
                       verticalalignment='center', transform=frame.transAxes)
            # hide certain axis
            if it != nrows - 1:
                frame.set_xticklabels([])
            if jt != 0:
                frame.set_yticklabels([])
        # ------------------------------------------------------------------
        # add title
        plt.suptitle('Order {0}'.format(order_num))
        plt.subplots_adjust(hspace=0, wspace=0, top=0.95, bottom=0.05,
                            left=0.05, right=0.975)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_loc_im_sat_thres(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    axes_grid1 = plotter.axes_grid1
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    threshold = kwargs['threshold']
    xarr = kwargs['xarr']
    yarr = kwargs['yarr']
    coeffs = kwargs['coeffs']
    # get xpix
    xpix = np.arange(image.shape[1])
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot image
    im = frame.imshow(image, origin='lower', clim=(1.0, threshold),
                      cmap='gist_gray', zorder=0, aspect='auto')
    # set the limits
    frame.set(xlim=(0, image.shape[1]), ylim=(0, image.shape[0]))
    # loop around xarr and yarr and plot
    for order_num in range(len(xarr)):
        # x and y
        x, y = xarr[order_num], yarr[order_num]
        # get ypix
        ypix = np.polyval(coeffs[order_num][::-1], xpix)
        # plot full fit
        frame.plot(xpix, ypix, linewidth=1, color='blue', ls='--', label='all',
                   zorder=1)
        # plot valid fit
        frame.plot(x, y, linewidth=1, color='red', label='valid', zorder=2)
    # only keep unique labels
    ulegend(frame, loc=10, ncol=2)
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = axes_grid1.make_axes_locatable(frame)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)
    # adjust plot
    plt.subplots_adjust(top=0.95, bottom=0.05, left=0.075, right=0.925)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_loc_ord_vs_rms(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    rnum = kwargs['rnum']
    rms_center = kwargs['rms_center']
    rms_fwhm = kwargs['rms_fwhm']
    fiber = kwargs['fiber']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot image
    frame.plot(np.arange(rnum), rms_center[0:rnum], label='center')
    frame.plot(np.arange(rnum), rms_fwhm[0:rnum], label='fwhm')
    # construct title
    title = 'Dispersion of localization parameters fiber {0}'.format(fiber)
    # set title labels limits
    frame.set(xlim=(0, rnum), xlabel='Order number', ylabel='RMS [pixel]',
              title=title)
    # Add legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_loc_im_corner(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    axes_grid1 = plotter.axes_grid1
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    image = kwargs['image']
    xarr = kwargs['xarr']
    yarr = kwargs['yarr']
    coeffs = kwargs['coeffs']
    # get xpix
    xpix = np.arange(image.shape[1])
    # get zoom values
    xzoom1 = params.listp('LOC_PLOT_CORNER_XZOOM1', dtype=int)
    xzoom2 = params.listp('LOC_PLOT_CORNER_XZOOM2', dtype=int)
    yzoom1 = params.listp('LOC_PLOT_CORNER_YZOOM1', dtype=int)
    yzoom2 = params.listp('LOC_PLOT_CORNER_YZOOM2', dtype=int)
    # get number of zooms required
    length = len(xzoom1)
    # get the number of columns
    ncols = int(np.ceil(np.sqrt(length)))
    nrows = int(np.ceil(length / ncols))
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=ncols, nrows=nrows)
    # loop around col_vals
    for row in range(np.product(frames.shape)):
        # get the correct frame
        jt, it = row % ncols, row // ncols
        frame = frames[it, jt]
        # deal with out of bounds frames
        if row >= length:
            frame.axis('off')
            continue
        # get limits for zooms
        xmin, xmax = xzoom1[row], xzoom2[row]
        ymin, ymax = yzoom1[row], yzoom2[row]
        # get image zoom
        image_zoom = image[ymin:ymax, xmin:xmax]
        # threshold = percentile
        threshold = np.nanpercentile(image_zoom, 95)
        # ------------------------------------------------------------------
        # plot image
        im = frame.imshow(image_zoom, origin='lower', vmin=0.0, vmax=threshold,
                          cmap='gist_gray', aspect='auto',
                          extent=[xmin, xmax, ymin, ymax])
        # loop around xarr and yarr and plot
        for order_num in range(len(xarr)):
            # x and y
            x, y = xarr[order_num], yarr[order_num]
            # get ypix
            ypix = np.polyval(coeffs[order_num][::-1], xpix)
            # plot full fit
            frame.plot(xpix, ypix, linewidth=1, color='blue', ls='--', zorder=1)
            # plot valid fit
            frame.plot(x, y, linewidth=1, color='red', zorder=2)
        # set the limits
        frame.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = axes_grid1.make_axes_locatable(frame)
        cax = divider.append_axes("top", size="5%", pad=0.05)
        cb = plt.colorbar(im, cax=cax, orientation='horizontal')
        cb.ax.xaxis.set_ticks_position('top')
    # adjust plot
    plt.subplots_adjust(top=0.95, bottom=0.05, left=0.075, right=0.925)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


# define graphing instances
loc_minmax_cents = Graph('LOC_MINMAX_CENTS', kind='debug',
                         func=plot_loc_minmax_cents)
loc_min_cents_thres = Graph('LOC_MIN_CENTS_THRES', kind='debug',
                            func=plot_loc_min_cents_thres)
loc_finding_orders = Graph('LOC_FINDING_ORDERS', kind='debug',
                           func=plot_loc_finding_orders)
loc_im_sat_thres = Graph('LOC_IM_SAT_THRES', kind='debug',
                         func=plot_loc_im_sat_thres)
loc_ord_vs_rms = Graph('LOC_ORD_VS_RMS', kind='debug',
                       func=plot_loc_ord_vs_rms)
description = ('Polynomial fits for localisation (overplotted on '
               'pre-processed image)')
sum_loc_im_sat_thres = Graph('SUM_LOC_IM_THRES', kind='summary',
                             func=plot_loc_im_sat_thres, figsize=(12, 8),
                             dpi=300, description=description)
description = ('Zoom in polynomial fits for localisation (overplotted on '
               'pre-processed image)')
sum_plot_loc_im_corner = Graph('SUM_LOC_IM_CORNER', kind='summary',
                               func=plot_loc_im_corner, figsize=(16, 10),
                               dpi=150, description=description)
# add to definitions
definitions += [loc_minmax_cents, loc_min_cents_thres, loc_finding_orders,
                loc_im_sat_thres, loc_ord_vs_rms, sum_loc_im_sat_thres,
                sum_plot_loc_im_corner]


# =============================================================================
# Define shape plotting functions
# =============================================================================
def plot_shape_dx(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    axes_grid1 = plotter.axes_grid1
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    dx = kwargs['dx']
    dx2 = kwargs['dx2']
    bnum = kwargs['bnum']
    nbanana = kwargs['nbanana']
    # set the zeropoint
    zeropoint = np.nanmedian(dx)
    # get the sig of dx
    sig_dx = np.nanmedian(np.abs(dx - zeropoint))
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=3, nrows=1)
    # set up axis
    frame1, frame2, frame3 = frames
    # ----------------------------------------------------------------------
    # plot dx
    vmin = (-2 * sig_dx) + zeropoint
    vmax = (2 * sig_dx) + zeropoint
    im1 = frame1.imshow(dx, vmin=vmin, vmax=vmax, cmap='viridis')
    # add colour bar
    divider1 = axes_grid1.make_axes_locatable(frame1)
    cax1 = divider1.append_axes("top", size="10%", pad=0.05)
    cb1 = plt.colorbar(im1, cax=cax1, orientation='horizontal')
    # set colorbar tick positions and label
    cb1.ax.xaxis.set_ticks_position('top')
    cb1.ax.xaxis.set_label_position('top')
    cb1.set_label('dx')
    # set labels and title
    frame1.set(xlabel='width [pix]', ylabel='order number', title='dx')
    # ----------------------------------------------------------------------
    # plot dx2
    vmin = (-2 * sig_dx) + zeropoint
    vmax = (2 * sig_dx) + zeropoint
    im2 = frame2.imshow(dx2, vmin=vmin, vmax=vmax, cmap='viridis')
    # add colour bar
    divider2 = axes_grid1.make_axes_locatable(frame2)
    cax2 = divider2.append_axes("top", size="10%", pad=0.05)
    cb2 = plt.colorbar(im2, cax=cax2, orientation='horizontal')
    # set colorbar tick positions and label
    cb2.ax.xaxis.set_ticks_position('top')
    cb2.ax.xaxis.set_label_position('top')
    cb2.set_label('dx2')
    # set labels and title
    frame2.set(xlabel='width [pix]', ylabel='order number', title='dx2')
    # ----------------------------------------------------------------------
    # plot diff
    vmin = (-0.5 * sig_dx) + zeropoint
    vmax = (0.5 * sig_dx) + zeropoint
    im3 = frame3.imshow(dx - dx2, vmin=vmin, vmax=vmax, cmap='viridis')
    # add colour bar
    divider3 = axes_grid1.make_axes_locatable(frame3)
    cax3 = divider3.append_axes("top", size="10%", pad=0.05)
    cb3 = plt.colorbar(im3, cax=cax3, orientation='horizontal')
    # set colorbar tick positions and label
    cb3.ax.xaxis.set_ticks_position('top')
    cb3.ax.xaxis.set_label_position('top')
    cb3.set_label('dx - dx2')
    # set labels and title
    frame3.set(xlabel='width [pix]', ylabel='order number', title='dx - dx2')
    # ----------------------------------------------------------------------
    # title
    # ----------------------------------------------------------------------
    plt.suptitle('Iteration {0} / {1}'.format(bnum + 1, nbanana))
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_shape_angle_offset(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    bnum = kwargs.get('bnum', None)
    nbo = kwargs['nbo']
    nbpix = kwargs['nbpix']
    # get data for plots 1 and 2
    slope_deg_arr = kwargs['slope_deg']
    slope_arr = kwargs['slope']
    skeep_arr = kwargs['skeep']
    xsection_arr = kwargs['xsection']
    ccor_arr = kwargs['ccor']
    ddx_arr = kwargs['ddx']
    dx_arr = kwargs['dx']
    dypix_arr = kwargs['dypix']
    ckeep_arr = kwargs['ckeep']
    # get data for plot 3
    corr_dx_from_fp_arr = kwargs['corr_dx_fp']
    xpeak2_arr = kwargs['xpeak2']
    err_pix_arr = kwargs['err_pix']
    goodmask_arr = kwargs['good']
    # get parameters from params
    sorder = params['SHAPE_PLOT_SELECTED_ORDER']
    nbanana = params['SHAPE_NUM_ITERATIONS']
    width = params['SHAPE_ORDER_WIDTH']
    # ------------------------------------------------------------------
    # if we have a bnum set get the plot loop generator (around orders)
    if bnum is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        banana_gen = [0]
    # else we are loop around bnums for a selected order
    else:
        order_gen = [sorder]
        banana_gen = plotter.plotloop(np.arange(nbanana).astype(int))
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # iterating the correction, from coarser to finer
        for banana_num in banana_gen:
            # --------------------------------------------------------------
            # get this iterations parameters
            slope_deg = slope_deg_arr[banana_num][order_num]
            slope = slope_arr[banana_num][order_num]
            s_keep = skeep_arr[banana_num][order_num]
            xsection = xsection_arr[banana_num][order_num]
            ccor = ccor_arr[banana_num][order_num]
            ddx = ddx_arr[banana_num][order_num]
            dx = dx_arr[banana_num][order_num]
            dypix = dypix_arr[banana_num][order_num]
            c_keep = ckeep_arr[banana_num][order_num]
            corr_dx_from_fp = corr_dx_from_fp_arr[banana_num][order_num]
            xpeak2 = xpeak2_arr[banana_num][order_num]
            err_pix = err_pix_arr[banana_num][order_num]
            good = goodmask_arr[banana_num][order_num]
            # --------------------------------------------------------------
            # set up plot
            fig, frames = graph.set_figure(plotter, ncols=3, nrows=1)
            frame1, frame2, frame3 = frames
            # title
            title = 'Iteration {0}/{1} - Order {2}'
            plt.suptitle(title.format(banana_num, nbanana, order_num))
            # --------------------------------------------------------------
            # frame 1
            # --------------------------------------------------------------
            frame1.plot(xsection[s_keep], slope_deg[s_keep], color='g',
                        marker='o', ls='None')
            frame1.plot(np.arange(nbpix), slope)
            frame1.set(xlabel='x pixel', ylabel='slope [deg]')
            # --------------------------------------------------------------
            # frame 2
            # --------------------------------------------------------------
            frame2.imshow(ccor, aspect=0.2, cmap='viridis')
            frame2.plot(dx - np.min(ddx), dypix, color='r', marker='o',
                        ls='None')
            frame2.plot(dx[c_keep] - np.min(ddx), dypix[c_keep], color='g',
                        marker='o', ls='None')
            frame2.set(ylim=[0.0, width - 1], xlim=[0, len(ddx) - 1])
            # --------------------------------------------------------------
            # plot 3
            # --------------------------------------------------------------
            # add plot
            frame3.plot(xpeak2, err_pix, color='r', linestyle='None',
                        marker='.', label='err pixel')
            frame3.plot(xpeak2[good], err_pix[good], color='g',
                        linestyle='None', marker='.',
                        label='err pixel (for fit)')
            frame3.plot(np.arange(nbpix), corr_dx_from_fp, color='k',
                        label='fit to err pix')
            frame3.set(xlabel='Pixel', ylabel='Err Pixel')
            frame3.legend(loc=0)
            # --------------------------------------------------------------
            # wrap up using plotter
            plotter.plotend(graph)


def plot_shape_local_zoom_shift(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    image = kwargs['image']
    simage = kwargs['simage']
    # get zoom values
    zoom1 = params.listp('SHAPEL_PLOT_ZOOM1', dtype=int)
    zoom2 = params.listp('SHAPEL_PLOT_ZOOM2', dtype=int)
    # ------------------------------------------------------------------
    # get limits for zooms
    xmin1, xmax1, ymin1, ymax1 = zoom1
    xmin2, xmax2, ymin2, ymax2 = zoom2
    # get the image zoom ins
    image1 = image[ymin1:ymax1, xmin1:xmax1]
    simage1 = simage[ymin1:ymax1, xmin1:xmax1]
    image2 = image[ymin2:ymax2, xmin2:xmax2]
    simage2 = simage[ymin2:ymax2, xmin2:xmax2]
    # threshold = percentile
    threshold1 = np.nanpercentile(image1, 95)
    threshold2 = np.nanpercentile(image2, 95)
    # ------------------------------------------------------------------
    skwargs1 = dict(origin='lower', aspect='auto', vmin=0.0, vmax=threshold1,
                    extent=[xmin1, xmax1, ymin1, ymax1])
    skwargs2 = dict(origin='lower', aspect='auto', vmin=0.0, vmax=threshold2,
                    extent=[xmin2, xmax2, ymin2, ymax2])
    # ------------------------------------------------------------------
    # set up plot
    fig1, frames1 = graph.set_figure(plotter, ncols=2, nrows=1,
                                   sharex=True, sharey=True)
    fig2, frames2 = graph.set_figure(plotter, ncols=2, nrows=1,
                                   sharex=True, sharey=True)
    # plot the image zooms
    frames1[0].imshow(image1, **skwargs1)
    frames1[1].imshow(simage1, **skwargs1)
    frames2[0].imshow(image2, **skwargs2)
    frames2[1].imshow(simage2, **skwargs2)
    # set the limits
    frames1[0].set(xlim=(xmin1, xmax1), ylim=(ymin1, ymax1))
    frames1[1].set(xlim=(xmin1, xmax1), ylim=(ymin1, ymax1))
    frames2[0].set(xlim=(xmin2, xmax2), ylim=(ymin2, ymax2))
    frames2[1].set(xlim=(xmin2, xmax2), ylim=(ymin2, ymax2))
    # move y axis
    frames1[1].yaxis.set_ticks_position('right')
    frames2[1].yaxis.set_ticks_position('right')
    # add some titles
    fig1.suptitle('Zoom ({2},{2} to {1},{3})'.format(*zoom1))
    fig2.suptitle('Zoom ({0},{2} to {1},{3})'.format(*zoom2))
    # adjust plot
    fig1.subplots_adjust(top=0.925, bottom=0.05, left=0.1, right=0.9,
                         hspace=0, wspace=0)
    fig2.subplots_adjust(top=0.925, bottom=0.05, left=0.1, right=0.9,
                         hspace=0, wspace=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


shape_dx = Graph('SHAPE_DX', kind='debug', func=plot_shape_dx)
shape_angle_offset_all = Graph('SHAPE_ANGLE_OFFSET_ALL', kind='debug',
                           func=plot_shape_angle_offset)
shape_angle_offset = Graph('SHAPE_ANGLE_OFFSET', kind='debug',
                           func=plot_shape_angle_offset)
sum_shape_angle_offset = Graph('SUM_SHAPE_ANGLE_OFFSET', kind='summary',
                           func=plot_shape_angle_offset)
shape_local_zoom_shift = Graph('SHAPEL_ZOOM_SHIFT', kind='debug',
                               func=plot_shape_local_zoom_shift)
sum_shape_local_zoom_shift = Graph('SUM_SHAPEL_ZOOM_SHIFT', kind='summary',
                                   func=plot_shape_local_zoom_shift)
# add to definitions
definitions += [shape_dx, shape_angle_offset_all, shape_angle_offset,
                sum_shape_angle_offset, shape_local_zoom_shift,
                sum_shape_local_zoom_shift]


# =============================================================================
# Define flat plotting functions
# =============================================================================
def plot_flat_order_fit_edges(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # TODO: remove break point
    constants.breakpoint(plotter.params)

    # get plt
    plt = plotter.plt
    axes_grid1 = plotter.axes_grid1
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    image1 = kwargs['image1']
    image2= kwargs['image2']
    order = kwargs.get('order', None)
    coeffs1 = kwargs['coeffs1']
    coeffs2 = kwargs['coeffs2']
    fiber = kwargs['fiber']
    # get dimensions from coeffs
    nbo = coeffs1.shape[0]
    # get parameters from params
    range1_dict = params.dictp('EXT_RANGE1', dtype=str)
    range2_dict = params.dictp('EXT_RANGE2', dtype=str)
    range1 = float(range1_dict[fiber])
    range2 = float(range2_dict[fiber])
    # ------------------------------------------------------------------
    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # deal with kind
    xfit1 = np.arange(image1.shape[1])
    xfit2 = np.repeat([image2.shape[1] // 2], image2.shape[1])
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # get order coefficients
        ocoeffs1 = coeffs1[order_num]
        ocoeffs2 = coeffs2[order_num]
        # get fit and edge fits (for raw image)
        yfit1 = np.polyval(ocoeffs1[::-1], xfit1)
        yfitlow1 = np.polyval((ocoeffs1)[::-1], xfit1) - range1
        yfithigh1 = np.polyval((ocoeffs1)[::-1], xfit1) + range2
        ylower1 = np.polyval((ocoeffs1)[::-1], xfit1) - 2 * range1
        yupper1 = np.polyval((ocoeffs1)[::-1], xfit1) + 2 * range2
        # get fit and edge fits (for straight image)
        yfit2 = np.polyval(ocoeffs2[::-1], xfit2)
        yfitlow2 = np.polyval((ocoeffs2)[::-1], xfit2) - range1
        yfithigh2 = np.polyval((ocoeffs2)[::-1], xfit2)+ range2
        ylower2 = np.polyval((ocoeffs2)[::-1], xfit2) - 6 * range1
        yupper2 = np.polyval((ocoeffs2)[::-1], xfit2) + 6 * range2
        # get image bounds
        ymin1 = np.max([np.min(ylower1), 0])
        ymax1 = np.min([np.max(yupper1), image1.shape[0]])
        ymin2 = np.max([np.min(ylower2), 0])
        ymax2 = np.min([np.max(yupper2), image1.shape[0]])

        # need to round these values to integers (to cut image)
        xmin, xmax = 0, image1.shape[1]
        ymin1, ymax1 = int(np.floor(ymin1)), int(np.ceil(ymax1))
        ymin2, ymax2 = int(np.floor(ymin2)), int(np.ceil(ymax2))
        # zoom in on image in this region
        imagezoom1 = image1[ymin1:ymax1]
        imagezoom2 = image2[ymin2:ymax2]
        # set threshold
        threshold1 = np.nanpercentile(imagezoom1, 95)
        threshold2 = np.nanpercentile(imagezoom2, 95)
        # ------------------------------------------------------------------
        # set up plot
        fig, frames = graph.set_figure(plotter, ncols=1, nrows=2, sharex=True)
        frame1, frame2 = frames
        # ------------------------------------------------------------------
        # plot image
        im1 = frame1.imshow(imagezoom1, origin='lower', clim=(1.0, threshold1),
                            cmap='gist_gray', zorder=0, aspect='auto',
                            extent=[xmin, xmax, ymin1, ymax1])
        im2 = frame2.imshow(imagezoom2, origin='lower', clim=(1.0, threshold2),
                            cmap='gist_gray', zorder=0, aspect='auto',
                            extent=[xmin, xmax, ymin2, ymax2])
        # ------------------------------------------------------------------
        # plot the fits and fit edges
        frame1.plot(xfit1, yfit1, color='red', label='fit')
        frame1.plot(xfit1, yfitlow1, ls='--', color='blue', label='fit edge')
        frame1.plot(xfit1, yfithigh1, ls='--', color='blue', label='fit edge')
        frame2.plot(xfit1, yfit2, color='red', label='fit')
        frame2.plot(xfit1, yfitlow2, ls='--', color='blue', label='fit edge')
        frame2.plot(xfit1, yfithigh2, ls='--', color='blue', label='fit edge')
        # ------------------------------------------------------------------
        # construct title
        title = ('Image fit (before and after straightening) for '
                 'order = {0} fiber = {1}'.format(order_num, fiber))
        # set the limits
        frame1.set(xlim=(0, imagezoom1.shape[1]), ylim=(ymin1, ymax1),
                  title=title)
        frame2.set(xlim=(0, imagezoom2.shape[1]), ylim=(ymin2, ymax2))
        # ------------------------------------------------------------------
        # add legend
        ulegend(frame1, loc=0)
        ulegend(frame2, loc=0)
        # ------------------------------------------------------------------
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider1 = axes_grid1.make_axes_locatable(frame1)
        cax1 = divider1.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im1, cax=cax1)
        divider2 = axes_grid1.make_axes_locatable(frame2)
        cax2 = divider2.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im2, cax=cax2)
        # adjust plot
        plt.subplots_adjust(top=0.95, bottom=0.05, left=0.075, right=0.925,
                            hspace=0.05)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_flat_blaze_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return

    # TODO: remove break point
    constants.breakpoint(plotter.params)

    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    e2ds = kwargs['eprops']['E2DS']
    blaze = kwargs['eprops']['BLAZE']
    flat =kwargs['eprops']['FLAT']
    fiber = kwargs['fiber']
    nbo = e2ds.shape[0]
    order = kwargs.get('order', None)


    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
    else:
        order_gen = [order]

    # loop around orders
    for order_num in order_gen:
        # get this iterations values
        oe2ds = e2ds[order_num]
        oblaze = blaze[order_num]
        oflat = flat[order_num]
        # get xpix values
        xpix = np.arange(len(oe2ds))
        # ------------------------------------------------------------------
        # set up plot
        gs = dict(height_ratios=[2, 1])
        fig, frames = graph.set_figure(plotter, ncols=1, nrows=2, sharex=True,
                                       gridspec_kw=gs)
        # ------------------------------------------------------------------
        # plot blaze and e2ds
        frames[0].plot(xpix, oe2ds, label='E2DS')
        frames[0].plot(xpix, oblaze, label='Blaze')
        # plot flat
        frames[1].plot(xpix, oflat, label='Flat')
        frames[1].hlines(1, 0, len(oe2ds), color='red', linestyle='--')
        # set title
        title = 'Blaze and Flat (Order {0} Fiber {1})'
        fig.suptitle(title.format(order_num, fiber))
        # set labels
        frames[1].set(xlabel='x pixel position', ylabel='flux',
                      xlim=[-10, len(oe2ds) + 10])
        # add legends
        frames[0].legend(loc=0)
        frames[1].legend(loc=0)
        # ------------------------------------------------------------------
        # adjust plot
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95,
                            wspace=0, hspace=0)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


flat_order_fit_edges1 = Graph('FLAT_ORDER_FIT_EDGES1', kind='debug',
                             func=plot_flat_order_fit_edges)
flat_blaze_order1 = Graph('FLAT_BLAZE_ORDER1', kind='debug',
                         func=plot_flat_blaze_order)
flat_order_fit_edges2 = Graph('FLAT_ORDER_FIT_EDGES2', kind='debug',
                             func=plot_flat_order_fit_edges)
flat_blaze_order2 = Graph('FLAT_BLAZE_ORDER2', kind='debug',
                         func=plot_flat_blaze_order)
description = 'Image fit (before and after straightening)'
sum_flat_order_fit_edges = Graph('SUM_FLAT_ORDER_FIT_EDGES', kind='summary',
                                 func=plot_flat_order_fit_edges,
                                 figsize=(16, 10), dpi=150,
                                 description=description)
description = 'Blaze fit and e2ds (top) and resulting flat (bottom)'
sum_flat_blaze_order = Graph('SUM_FLAT_BLAZE_ORDER', kind='summary',
                             func=plot_flat_blaze_order,
                             figsize=(16, 10), dpi=150,
                             description=description)
# add to definitions
definitions += [flat_order_fit_edges1, flat_order_fit_edges2,
                flat_blaze_order1, flat_blaze_order2,
                sum_flat_order_fit_edges, sum_flat_blaze_order]

# =============================================================================
# Define thermal plotting functions
# =============================================================================

# =============================================================================
# Define extraction plotting functions
# =============================================================================

# =============================================================================
# Define wave plotting functions
# =============================================================================

# =============================================================================
# Define telluric plotting functions
# =============================================================================

# =============================================================================
# Define velocity plotting functions
# =============================================================================

# =============================================================================
# Define polarisation plotting functions
# =============================================================================


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
