#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-03 at 10:51

@author: cook
"""
import numpy as np
from astropy import constants as cc
from astropy import units as uu
import copy
import os
import warnings

from apero.core import constants
from apero.core import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.plotting.plot_functions.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# set up definition storage
definitions = []
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# -----------------------------------------------------------------------------


# =============================================================================
# Define plotting class
# =============================================================================
class Graph:
    def __init__(self, name, kind='debug', func=None, filename=None,
                 description=None, figsize=None, dpi=None):
        self.name = name
        # set kind
        if kind in ['debug', 'summary', 'show']:
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

    def set_filename(self, params, location, suffix=None):
        """
        Set the file name for this Graph instance
        :param params:
        :param location:
        :param suffix:
        :return:
        """
        # get pid
        pid = params['PID']
        # construct filename
        filename = 'plot_{0}_{1}'.format(self.name, pid)
        # make filename all lowercase
        filename = filename.lower()
        # deal with fiber
        if suffix is not None:
            filename += '_{0}'.format(suffix)
        # construct absolute filename
        self.filename = os.path.join(location, filename)

    def set_figure(self, plotter, figsize=None, **kwargs):
        # get plt from plotter (for matplotlib set up)
        plt = plotter.plt
        # get figure and frame
        fig, frames = plt.subplots(**kwargs)
        # set figure parameters
        if figsize is None:
            fig.set_size_inches(self.figsize)
        else:
            fig.set_size_inches(figsize)
        # return figure and frames
        return fig, frames

    def set_grid(self, plotter, figsize=None, **kwargs):
        # get plt from plotter (for matplotlib set up)
        plt = plotter.plt
        # get figure and frame
        fig = plt.figure()
        # get grid
        gs = fig.add_gridspec(**kwargs)
        # set figure parameters
        if figsize is None:
            fig.set_size_inches(self.figsize)
        else:
            fig.set_size_inches(figsize)
        # return figure and frames
        return fig, gs


class CrossCursor(object):
    def __init__(self, frame, color='r', alpha=0.5):
        self.frame = frame
        # the horizontal line
        self.lx = frame.axhline(color=color, alpha=alpha)
        # the vertical line
        self.ly = frame.axvline(color=color, alpha=alpha)
        # set up the text box
        bbox = dict(facecolor='white', edgecolor='blue', pad=5.0)
        # text location in axes coords
        self.txt = frame.text(0.8, 0.9, '', horizontalalignment='center',
                              verticalalignment='center', color='blue',
                              transform=frame.transAxes, bbox=bbox)
        # start off the text without values
        self.txt.set_text('x=NaN, y=NaN')

    def mouse_move(self, event):
        if not event.inaxes:
            return
        # get the new x and y locations
        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)
        # set the text
        self.txt.set_text('x={0:.2f}, y={1:.2f}'.format(x, y))
        # update canvas
        self.frame.figure.canvas.draw()


class ClickCursor(object):
    def __init__(self, fig, frame):
        self.fig = fig
        self.frame = frame

    def mouse_click(self, event):
        # noinspection PyProtectedMember
        if self.fig.canvas.manager.toolbar._active:
            return
        if not event.inaxes:
            return
        # get the new x and y locations
        x, y = event.xdata, event.ydata
        # print the position of the cursor
        print('PLOT x={0:.2f}, y={1:.2f}'.format(x, y))


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


def mc_line(frame, plt, line, x, y, z, norm=None, cmap=None):
    """
    Create a line coloured by vector "z"
    From here:
        https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/
            multicolored_line.html

    :param frame:
    :param plt:
    :param line:
    :param x:
    :param y:
    :param z:
    :param norm:
    :param cmap:
    :return:
    """
    # deal with no colormap
    if cmap is None:
        cmap = 'viridis'
    # Create a continuous norm to map from data points to colors
    if norm is None:
        norm = plt.Normalize(np.nanmin(z), np.nanmax(z))
    # Create a set of line segments so that we can color them individually
    # This creates the points as a N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line
    # collection needs to be (numlines) x (points per line) x 2 (for x and y)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    # plot the segments
    lc = line(segments, cmap=cmap, norm=norm)
    # Set the values used for colormapping
    lc.set_array(z)
    # return the line
    return frame.add_collection(lc)


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


def add_grid(frame):
    frame.minorticks_on()
    # Don't allow the axis to be on top of your data
    frame.grid(which='major', linestyle='-', linewidth='0.5', color='black',
               alpha=0.75, zorder=1)
    frame.grid(which='minor', linestyle=':', linewidth='0.5', color='black',
               alpha=0.5, zorder=0)


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
    orders = kwargs['ord']
    x_arr = kwargs['x']
    y_arr = kwargs['y']
    colour = kwargs.get('colour', 'k')
    # ------------------------------------------------------------------
    # get the plot generator
    generator = plotter.plotloop(orders)
    # prompt to start looper
    plotter.close_plots(loop=True)
    # loop aroun the orders
    for ord_num in generator:
        fig, frame = graph.set_figure(plotter)
        frame.plot(x_arr[ord_num], y_arr[ord_num], color=colour)
        frame.set_title('Order {0}'.format(ord_num))
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(ord_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


# defined graphing instances
test_plot1 = Graph('TEST1', kind='summary', func=graph_test_plot_1,
                   description='This is a test plot',
                   figsize=(10, 10), dpi=150)
test_plot2 = Graph('TEST2', kind='debug', func=graph_test_plot_1)
test_plot3 = Graph('TEST3', kind='debug', func=graph_test_plot_2)
test_plot4 = Graph('TEST4', kind='summary', func=graph_test_plot_2)
# add to definitions
definitions += [test_plot1, test_plot2, test_plot3, test_plot4]


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
    rectangle = plotter.matplotlib.patches.Rectangle
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
    brec = rectangle((bxlow, bylow), bxhigh - bxlow, byhigh - bylow,
                     edgecolor='b', facecolor='None')
    frame.add_patch(brec)
    # plot blue rectangle
    rrec = rectangle((rxlow, rylow), rxhigh - rxlow, ryhigh - rylow,
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
sum_desc = 'Plot to show dark image regions (blue, red and full)'
summary_dark_image_regions = Graph('SUM_DARK_IMAGE_REGIONS', kind='summary',
                                   func=plot_dark_image_regions, dpi=150,
                                   description=sum_desc, figsize=(10, 10))
sum_desc = 'Plot to show the dark image regions as histograms'
summary_dark_histogram = Graph('SUM_DARK_HISTOGRAM', kind='summary',
                               func=plot_dark_histogram, dpi=150,
                               description=sum_desc, figsize=(10, 10))
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
sum_desc = 'Bad pixel map'
summary_badpix_map = Graph('SUM_BADPIX_MAP', kind='summary',
                           func=plot_badpix_map, description=sum_desc,
                           figsize=(10, 10), dpi=150)
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
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
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
        frame.plot(xpix, ypix, linewidth=1, color='blue', ls='--', label='all')
        # plot valid fit
        frame.plot(x, y, linewidth=1, color='red', label='valid')
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


def plot_loc_fit_residuals(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = kwargs['x']
    y = kwargs['y']
    xo = kwargs['xo']
    rnum = kwargs['rnum']
    kind = kwargs['kind']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # ------------------------------------------------------------------
    # plot residuals of data - fit
    frame.plot(x, y, marker='_')
    # set title and limits
    frame.set(title='{0} fit residual of order {1}'.format(kind, rnum),
              xlim=(0, len(xo)), ylim=(np.min(y), np.max(y)))
    # ------------------------------------------------------------------
    # update suffix
    suffix = 'kind{0}_order{1}'.format(kind, rnum)
    graph.set_filename(plotter.params, plotter.location, suffix=suffix)
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


def plot_loc_check_coeffs(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    good_arr = kwargs['good']
    xpix = kwargs['xpix']
    ypix = kwargs['ypix']
    ypix0 = kwargs['ypix0']
    image = kwargs['image']
    order = kwargs.get('order', None)
    kind = kwargs.get('kind', None)
    # ------------------------------------------------------------------
    # get order generator
    # ------------------------------------------------------------------
    if order is None:
        order_gen = plotter.plotloop(np.arange(len(good_arr)))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # get this iterations values
        good = good_arr[order_num]
        ypixgo = ypix[order_num, good]
        ypix0go = ypix0[order_num, good]
        residual = ypixgo - ypix0go
        # get the y limits
        ymax = np.ceil(np.nanmax([np.nanmax(ypixgo), np.nanmax(ypix0go)]))
        ymin = np.floor(np.nanmin([np.nanmin(ypixgo), np.nanmin(ypix0go)]))
        ydiff = np.ceil(ymax - ymin)
        ymax = np.min([int(ymax + 0.25 * ydiff), image.shape[0]])
        ymin = np.max([int(ymin - 0.25 * ydiff), 0])
        # mask the image between y limits
        imagezoom = image[ymin:ymax]
        # normalise zoom image
        imagezoom = imagezoom / np.nanpercentile(imagezoom, 85)
        # ------------------------------------------------------------------
        # set up plot
        if kind == 'center':
            fig, frames = graph.set_figure(plotter, nrows=2, ncols=1,
                                           sharex=True)
            frame1, frame2 = frames
        else:
            fig, frame2 = graph.set_figure(plotter, nrows=1, ncols=1)
            frame1 = None
        # ------------------------------------------------------------------
        # plot the image fits (if we are dealing with a center plot)
        if kind == 'center':
            frame1.imshow(imagezoom, aspect='auto', origin='lower', zorder=0,
                          cmap='gist_gray', vmin=0, vmax=1,
                          extent=[0, image.shape[1], ymin, ymax])
            frame1.plot(xpix[good], ypix0go, color='b', ls='--', label='old',
                        zorder=2)
            frame1.plot(xpix[good], ypixgo, color='r', ls='-', label='new',
                        zorder=1)
            frame1.legend(loc=0)
            # force x limits
            frame1.set_xlim(0, image.shape[1])
        # ------------------------------------------------------------------
        # plot the residuals
        frame2.plot(xpix[good], residual, marker='x')
        # add legend
        frame2.legend(loc=0)
        # force x limits
        frame2.set_xlim(0, image.shape[1])
        # ------------------------------------------------------------------
        # construct frame title
        if kind is None:
            title = 'Coefficient Residuals (New - Original) Order={1}'
        else:
            title = '{0} coefficient residuals (New - Original) Order={1}'
        # ------------------------------------------------------------------
        # set title and labels
        if kind == 'center':
            frame1.set(title=title.format(kind, order_num),
                       ylabel='y pixel position')
            frame2.set(xlabel='x pixel position',
                       ylabel=r'$\Delta$y pixel position')
        else:
            frame2.set(title=title.format(kind, order_num),
                       xlabel='x pixel position',
                       ylabel=r'$\Delta$y pixel position')
        # ------------------------------------------------------------------
        # adjust plot
        plt.subplots_adjust(top=0.925, bottom=0.125, left=0.1, right=0.975,
                            hspace=0.05)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
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
loc_fit_residuals = Graph('LOC_FIT_RESIDUALS', kind='debug',
                          func=plot_loc_fit_residuals)
loc_ord_vs_rms = Graph('LOC_ORD_VS_RMS', kind='debug',
                       func=plot_loc_ord_vs_rms)
loc_check_coeffs = Graph('LOC_CHECK_COEFFS', kind='debug',
                         func=plot_loc_check_coeffs)
sum_desc = ('Polynomial fits for localisation (overplotted on '
            'pre-processed image)')
sum_loc_im_sat_thres = Graph('SUM_LOC_IM_THRES', kind='summary',
                             func=plot_loc_im_sat_thres, figsize=(12, 8),
                             dpi=300, description=sum_desc)
sum_desc = ('Zoom in polynomial fits for localisation (overplotted on '
            'pre-processed image)')
sum_plot_loc_im_corner = Graph('SUM_LOC_IM_CORNER', kind='summary',
                               func=plot_loc_im_corner, figsize=(16, 10),
                               dpi=150, description=sum_desc)
# add to definitions
definitions += [loc_minmax_cents, loc_min_cents_thres, loc_finding_orders,
                loc_im_sat_thres, loc_ord_vs_rms, loc_check_coeffs,
                loc_fit_residuals,
                sum_loc_im_sat_thres, sum_plot_loc_im_corner]


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


def plot_shape_linear_tparams(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    x1 = kwargs['x1']
    x2 = kwargs['x2']
    y1 = kwargs['y1']
    y2 = kwargs['y2']
    # ------------------------------------------------------------------
    # get image shape
    dim1, dim2 = image.shape
    # get calculated parameters
    diffx = x1 - x2
    diffy = y1 - y2
    xrange1 = [0, dim2]
    xrange2 = [0, dim1]
    ylim = np.max([np.nanmedian(np.abs(diffx)), np.nanmedian(np.abs(diffy))])
    yrange = [-10 * ylim, 10 * ylim]
    nbins = 50
    pstep = 100
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=2, nrows=2)
    # set up mean points plot
    mkwargs = dict(color='w', linestyle='None', marker='.')
    # ----------------------------------------------------------------------
    # plot[0,0] x1 vs x1 - x2
    # ----------------------------------------------------------------------
    frames[0, 0].hist2d(x1, diffx, bins=nbins, range=[xrange1, yrange])
    frames[0, 0].set(xlabel='x1', ylabel='x1 - x2')
    # calculate bin mean
    for pbin in range(0, dim2, pstep):
        with warnings.catch_warnings(record=True) as _:
            keep = np.abs(x1 - pbin < nbins)
            nanmed = mp.nanmedian(diffx[keep])
        if np.sum(keep) > 100:
            frames[0, 0].plot([pbin], nanmed, **mkwargs)
    # ----------------------------------------------------------------------
    # plot[0,1] y1 vs x1 - x2
    # ----------------------------------------------------------------------
    frames[0, 1].hist2d(y1, diffx, bins=nbins, range=[xrange2, yrange])
    frames[0, 1].set(xlabel='y1', ylabel='x1 - x2')
    # calculate bin mean
    for pbin in range(0, dim2, pstep):
        with warnings.catch_warnings(record=True) as _:
            keep = np.abs(y1 - pbin < nbins)
            nanmed = mp.nanmedian(diffx[keep])
        if np.sum(keep) > 100:
            frames[0, 0].plot([pbin], nanmed, **mkwargs)
    # ----------------------------------------------------------------------
    # plot[1,0] x1 vs y1 - y2
    # ----------------------------------------------------------------------
    frames[1, 0].hist2d(x1, diffy, bins=nbins, range=[xrange1, yrange])
    frames[1, 0].set(xlabel='x1', ylabel='y1 - y2')
    # calculate bin mean
    for pbin in range(0, dim2, pstep):
        with warnings.catch_warnings(record=True) as _:
            keep = np.abs(x1 - pbin < nbins)
            nanmed = mp.nanmedian(diffy[keep])
        if np.sum(keep) > 100:
            frames[0, 0].plot([pbin], nanmed, **mkwargs)
    # ----------------------------------------------------------------------
    # plot[1,1] y1 vs y1 - y2
    # ----------------------------------------------------------------------
    frames[1, 1].hist2d(y1, diffy, bins=nbins, range=[xrange2, yrange])
    frames[1, 1].set(xlabel='y1', ylabel='y1 - y2')
    # calculate bin mean
    for pbin in range(0, dim2, pstep):
        with warnings.catch_warnings(record=True) as _:
            keep = np.abs(y1 - pbin < nbins)
            nanmed = mp.nanmedian(diffy[keep])
        if np.sum(keep) > 100:
            frames[0, 0].plot([pbin], nanmed, **mkwargs)
    # ----------------------------------------------------------------------
    # title
    # ----------------------------------------------------------------------
    plt.suptitle('Linear transform parameters')
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
    # get parameters from params
    sorder = params['SHAPE_PLOT_SELECTED_ORDER']
    nbanana = params['SHAPE_NUM_ITERATIONS']
    width = params['SHAPE_ORDER_WIDTH']
    # ------------------------------------------------------------------
    # if we have a bnum set get the plot loop generator (around orders)
    if bnum is not None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        banana_gen = [0]
        banana_numbers = [bnum]
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we are loop around bnums for a selected order
    else:
        order_gen = [sorder]
        banana_numbers = np.arange(nbanana).astype(int)
        banana_gen = plotter.plotloop(banana_numbers)
        # prompt to start looper
        plotter.close_plots(loop=True)
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # iterating the correction, from coarser to finer
        for banana_num in banana_gen:
            # get this iterations banana_numbers
            bnum_it = banana_numbers[banana_num]
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
            # --------------------------------------------------------------
            # set up plot
            fig, frames = graph.set_figure(plotter, ncols=2, nrows=1)
            frame1, frame2 = frames
            # title
            title = 'Iteration {0}/{1} - Order {2}'
            plt.suptitle(title.format(bnum_it + 1, nbanana, order_num))
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
            frame2.imshow(ccor, aspect='auto', origin='lower', cmap='viridis')
            frame2.plot(dx - np.min(ddx), dypix, color='r', marker='o',
                        ls='None')
            frame2.plot(dx[c_keep] - np.min(ddx), dypix[c_keep], color='g',
                        marker='o', ls='None')
            frame2.set(ylim=[0.0, width - 1], xlim=[0, len(ddx) - 1])
            # ------------------------------------------------------------------
            # update filename (adding order_num to end)
            suffix = 'bnum{0}_order{1}'.format(bnum_it, order_num)
            graph.set_filename(plotter.params, plotter.location, suffix=suffix)
            # --------------------------------------------------------------
            # wrap up using plotter
            plotter.plotend(graph)


def plot_shape_local_zoom_shift(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
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
shape_linear_tparams = Graph('SHAPE_LINEAR_TPARAMS', kind='debug',
                             func=plot_shape_linear_tparams)
shape_angle_offset_all = Graph('SHAPE_ANGLE_OFFSET_ALL', kind='debug',
                               func=plot_shape_angle_offset)
shape_angle_offset = Graph('SHAPE_ANGLE_OFFSET', kind='debug',
                           func=plot_shape_angle_offset)
shape_local_zoom_shift = Graph('SHAPEL_ZOOM_SHIFT', kind='debug',
                               func=plot_shape_local_zoom_shift)
sum_desc = 'Plot to show angle and offset for each iteration'
sum_shape_angle_offset = Graph('SUM_SHAPE_ANGLE_OFFSET', kind='summary',
                               func=plot_shape_angle_offset,
                               figsize=(16, 10), dpi=150, description=sum_desc)
sum_desc = 'Zoom in to show before and after shape corrections.'
sum_shape_local_zoom_shift = Graph('SUM_SHAPEL_ZOOM_SHIFT', kind='summary',
                                   func=plot_shape_local_zoom_shift,
                                   figsize=(16, 10), dpi=150,
                                   description=sum_desc)
# add to definitions
definitions += [shape_dx, shape_linear_tparams, shape_angle_offset_all,
                shape_angle_offset, sum_shape_angle_offset,
                shape_local_zoom_shift, sum_shape_local_zoom_shift]


# =============================================================================
# Define flat plotting functions
# =============================================================================
def plot_flat_order_fit_edges(plotter, graph, kwargs):
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
    image1 = kwargs['image1']
    image2 = kwargs['image2']
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
        # prompt to start looper
        plotter.close_plots(loop=True)
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
        yfitlow1 = np.polyval(ocoeffs1[::-1], xfit1) - range1
        yfithigh1 = np.polyval(ocoeffs1[::-1], xfit1) + range2
        ylower1 = np.polyval(ocoeffs1[::-1], xfit1) - 2 * range1
        yupper1 = np.polyval(ocoeffs1[::-1], xfit1) + 2 * range2
        # get fit and edge fits (for straight image)
        yfit2 = np.polyval(ocoeffs2[::-1], xfit2)
        yfitlow2 = np.polyval(ocoeffs2[::-1], xfit2) - range1
        yfithigh2 = np.polyval(ocoeffs2[::-1], xfit2) + range2
        ylower2 = np.polyval(ocoeffs2[::-1], xfit2) - 6 * range1
        yupper2 = np.polyval(ocoeffs2[::-1], xfit2) + 6 * range2
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
        frame1.plot(xfit1, yfit1, color='orange', label='fit')
        frame1.plot(xfit1, yfitlow1, ls='--', color='orange', label='fit edge')
        frame1.plot(xfit1, yfithigh1, ls='--', color='orange', label='fit edge')
        frame2.plot(xfit1, yfit2, color='orange', label='fit')
        frame2.plot(xfit1, yfitlow2, ls='--', color='orange', label='fit edge')
        frame2.plot(xfit1, yfithigh2, ls='--', color='orange', label='fit edge')
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
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_flat_blaze_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    e2ds = kwargs['eprops']['E2DS']
    blaze = kwargs['eprops']['BLAZE']
    flat = kwargs['eprops']['FLAT']
    fiber = kwargs['fiber']
    nbo = e2ds.shape[0]
    order = kwargs.get('order', None)

    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        # prompt to start looper
        plotter.close_plots(loop=True)
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
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
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
sum_desc = 'Image fit (before and after straightening)'
sum_flat_order_fit_edges = Graph('SUM_FLAT_ORDER_FIT_EDGES', kind='summary',
                                 func=plot_flat_order_fit_edges, dpi=150,
                                 figsize=(16, 10), description=sum_desc)
sum_desc = 'Blaze fit and e2ds (top) and resulting flat (bottom)'
sum_flat_blaze_order = Graph('SUM_FLAT_BLAZE_ORDER', kind='summary',
                             func=plot_flat_blaze_order,
                             figsize=(16, 10), dpi=150, description=sum_desc)
# add to definitions
definitions += [flat_order_fit_edges1, flat_order_fit_edges2,
                flat_blaze_order1, flat_blaze_order2,
                sum_flat_order_fit_edges, sum_flat_blaze_order]


# =============================================================================
# Define thermal plotting functions
# =============================================================================
def plot_thermal_background(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    wavemap = kwargs['wave']
    image = kwargs['image']
    thermal = kwargs['thermal']
    torder = kwargs['torder']
    tmask = kwargs['tmask']
    fiber = kwargs['fiber']
    kind = kwargs['kind']
    # get properties from params
    startorder = params['THERMAL_PLOT_START_ORDER']
    # correct data for graph
    rwave = np.ravel(wavemap[startorder:])
    rimage = np.ravel(image[startorder:])
    rthermal = np.ravel(thermal[startorder:])
    swave = wavemap[torder, tmask]
    sthermal = thermal[torder][tmask]
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot data
    frame.plot(rwave, rimage, color='k', label='input spectrum')
    frame.plot(rwave, rthermal, color='r', label='scaled thermal')
    frame.plot(swave, sthermal, color='b', marker='o', ls='None',
               label='background sample region')
    # set graph properties
    frame.legend(loc=0)
    title = 'Thermal scaled background ({0}Fiber {1})'.format(kind, fiber)
    frame.set(xlabel='Wavelength [nm]', ylabel='Flux', title=title)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


thermal_background = Graph('THERMAL_BACKGROUND', kind='debug',
                           func=plot_thermal_background)
# add to definitions
definitions += [thermal_background]


# =============================================================================
# Define extraction plotting functions
# =============================================================================
def plot_extract_spectral_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    e2ds = kwargs['eprops']['E2DS']
    e2dsff = kwargs['eprops']['E2DSFF']
    blaze = kwargs['eprops']['BLAZE']
    wavemap = kwargs['wave']
    fiber = kwargs['fiber']
    # get optional arguments
    order = kwargs.get('order', None)
    # get size from image
    nbo = e2ds.shape[0]
    # get blaze corrected values
    with warnings.catch_warnings(record=True) as _:
        e2dsb = e2ds / blaze
        e2dsffb = e2dsff / blaze
    # ------------------------------------------------------------------
    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        # prompt to start looper
        plotter.close_plots(loop=True)
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around order
    for order_num in order_gen:
        # set up plot
        fig, frames = graph.set_figure(plotter, ncols=1, nrows=2, sharex=True)
        # get normalised values
        e2dsn = e2ds[order_num] / np.nanmedian(e2ds[order_num])
        e2dsffn = e2dsff[order_num] / np.nanmedian(e2ds[order_num])
        blazen = blaze[order_num] / np.nanmedian(blaze[order_num])
        # plot fits
        frames[0].plot(wavemap[order_num], e2dsn, label='e2ds')
        frames[0].plot(wavemap[order_num], e2dsffn, label='e2dsff')
        frames[0].plot(wavemap[order_num], blazen, label='blaze')
        # plot blaze corrected
        frames[1].plot(wavemap[order_num], e2dsb[order_num], label='e2ds')
        frames[1].plot(wavemap[order_num], e2dsffb[order_num], label='e2dsff')
        # add legends
        frames[0].legend(loc=0)
        frames[1].legend(loc=0)
        # set title labels limits
        title = 'Spectral order {0} fiber {1}'
        frames[0].set(title=title.format(order_num, fiber), ylabel='flux')
        frames[1].set(xlabel='Wavelength [nm]', ylabel='flux')
        # ------------------------------------------------------------------
        # adjust plot
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.075, right=0.95,
                            wspace=0, hspace=0)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_extract_s1d(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    linecollection = plotter.matplotlib.collections.LineCollection
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    stable = kwargs['props']['S1DTABLE']
    fiber = kwargs['fiber']
    kind = kwargs.get('kind', None)
    # get zoom in parameters from params
    zoom1 = params.listp('EXTRACT_S1D_PLOT_ZOOM1', dtype=float)
    zoom2 = params.listp('EXTRACT_S1D_PLOT_ZOOM2', dtype=float)
    # get data from s1d table
    wavemap = stable['wavelength']
    flux = stable['flux']
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=1, nrows=len(zoom1))
    # get the normalised colours based on the full wavelength range
    norm = plt.Normalize(np.nanmin(wavemap), np.nanmax(wavemap))
    # loop around frames
    for row in range(len(zoom1)):
        # get bounds
        lowerbound = zoom1[row]
        upperbound = zoom2[row]
        # get frame
        frame = frames[row]
        # mask data between bounds
        mask = (wavemap >= lowerbound) & (wavemap <= upperbound)
        # if first figure add title
        if row == 0:
            if kind is not None:
                title = 'Spectrum {0} (1D) fiber {1}'
            else:
                title = 'Spectrum (1D) fiber {1}'
            frame.set_title(title.format(kind, fiber))
        # plot 1d spectrum
        mc_line(frame, plt, linecollection, wavemap[mask], flux[mask],
                z=wavemap[mask], norm=norm, cmap='jet')
        frame.set_xlim(lowerbound, upperbound)
        # set the y limits to 5 and 95 percentiles (to avoid outliers)
        with warnings.catch_warnings(record=True) as _:
            ylow, yhigh = np.nanpercentile(flux[mask], [2, 98])
        # only set ylimit if whole region is not NaN
        if np.isfinite(ylow) and np.isfinite(yhigh):
            frame.set_ylim(ylow, yhigh)
        # set the ylabel
        frame.set_ylabel('Flux')
        # if last row then plot x label
        if row == len(zoom1) - 1:
            frame.set_xlabel('Wavelength [nm]')
    # update filename (adding order_num to end)
    if kind is not None:
        suffix = kind.lower()
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
    # ------------------------------------------------------------------
    # adjust plot
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_extract_s1d_weights(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    wavemap = kwargs['wave']
    flux = kwargs['flux']
    weight = kwargs['weight']
    kind = kwargs['kind']
    fiber = kwargs.get('fiber', None)
    stype = kwargs['stype']
    # get zoom in parameters from params
    zoom1 = params.listp('EXTRACT_S1D_PLOT_ZOOM1', dtype=float)
    zoom2 = params.listp('EXTRACT_S1D_PLOT_ZOOM2', dtype=float)
    # ------------------------------------------------------------------
    # correct data for plotting
    flux1 = flux / np.nanmedian(flux)
    weight = weight / np.nanmedian(weight)
    with warnings.catch_warnings(record=True) as _:
        flux2 = (flux / weight) / np.nanmedian(flux / weight)
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=1, nrows=len(zoom1))
    # loop around frames
    for row in range(len(zoom1)):
        # get bounds
        lowerbound = zoom1[row]
        upperbound = zoom2[row]
        # get frame
        frame = frames[row]
        # mask data between bounds
        mask = (wavemap >= lowerbound) & (wavemap <= upperbound)
        # plot 1d spectrum
        frame.plot(wavemap[mask], weight[mask], label='weight vector')
        frame.plot(wavemap[mask], flux1[mask], label='prior to division')
        frame.plot(wavemap[mask], flux2[mask], label='after division')
        # add legend (only for first row)
        if row == 0:
            frame.legend(loc=0, ncol=3)
        # set lower bound
        frame.set_xlim(lowerbound, upperbound)
        # set the ylabel
        frame.set_ylabel('Flux')
        # deal with fiber string
        if fiber is None:
            fiberstr = ''
        else:
            fiberstr = 'fiber={0} '.format(fiber)
        # if first row plot title
        if row == 0:
            if stype is not None:
                title = ('Producing the 1D spectrum for {0} '
                         '(before and after with weights) {1}grid={2}')
            else:
                title = ('Producing the 1D spectrum '
                         '(before and after with weights) {1}grid={2}')
            frame.set_title(title.format(stype, fiberstr, kind))
        # if last row then plot x label
        if row == len(zoom1) - 1:
            frame.set_xlabel('Wavelength [nm]')
    # update filename (adding order_num to end)
    suffix = stype.lower()
    graph.set_filename(plotter.params, plotter.location, suffix=suffix)
    # ------------------------------------------------------------------
    # adjust plot
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


extract_spectral_order1 = Graph('EXTRACT_SPECTRAL_ORDER1', kind='debug',
                                func=plot_extract_spectral_order)
extract_spectral_order2 = Graph('EXTRACT_SPECTRAL_ORDER2', kind='debug',
                                func=plot_extract_spectral_order)
extract_s1d = Graph('EXTRACT_S1D', kind='debug', func=plot_extract_s1d)
extract_s1d_weights = Graph('EXTRACT_S1D_WEIGHT', kind='debug',
                            func=plot_extract_s1d_weights)
sum_desc = ('Wavelength against spectrum top: non blaze-corrected, '
            'bottom: blaze corrected')
sum_extract_sp_order = Graph('SUM_EXTRACT_SP_ORDER', kind='summary',
                             func=plot_extract_spectral_order,
                             figsize=(16, 10), dpi=150, description=sum_desc)
sum_desc = '1D spectrum after blaze weighting (S1D)'
sum_extract_s1d = Graph('SUM_EXTRACT_S1D', kind='summary',
                        func=plot_extract_s1d,
                        figsize=(16, 10), dpi=150, description=sum_desc)
# add to definitions
definitions += [extract_spectral_order1, extract_spectral_order2,
                extract_s1d, extract_s1d_weights, sum_extract_sp_order,
                sum_extract_s1d]


# =============================================================================
# Define wave plotting functions
# =============================================================================
def plot_wave_hc_guess(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    wavemap = kwargs['wave']
    spec = kwargs['spec']
    llprops = kwargs['llprops']
    nbo = kwargs['nbo']
    order = kwargs.get('order', None)
    # ------------------------------------------------------------------
    # get data from llprops
    xfit = llprops['XPIX_INI']
    gfit = llprops['GFIT_INI']
    ofit = llprops['ORD_INI']
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # ------------------------------------------------------------------
    # define spectral order colours
    col1 = [black, 'grey']
    label1 = ['Even order data', 'Odd order data']
    col2 = ['green', 'purple']
    label2 = ['Even order fit', 'Odd order fit']
    # ------------------------------------------------------------------
    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        # prompt to start looper
        plotter.close_plots(loop=True)
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, ncols=1, nrows=1)
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # set up mask for the order
        ordermask = ofit == order_num
        # keep only lines for this order
        oxfit = xfit[ordermask]
        ogfit = gfit[ordermask]
        # get colours from order parity
        col1_1 = col1[np.mod(order_num, 2)]
        col2_1 = col2[np.mod(order_num, 2)]
        label1_1 = label1[np.mod(order_num, 2)]
        label2_1 = label2[np.mod(order_num, 2)]
        # plot spectrum for order
        frame.plot(wavemap[order_num, :], spec[order_num, :], color=col1_1,
                   label=label1_1)
        # over plot all fits
        for line_it in range(len(oxfit)):
            xpix = oxfit[line_it]
            g2 = ogfit[line_it]
            frame.plot(wavemap[order_num, xpix], g2, color=col2_1,
                       label=label2_1)
        # plot unique legend
        ulegend(frame, plotter, loc=0, fontsize=12)
        # set title and labels
        title = 'Fitted gaussians on spectrum (Order {0})'
        frame.set(title=title.format(order_num),
                  xlabel='Wavelength [nm]', ylabel='Normalized flux')
        # ------------------------------------------------------------------
        # adjust plot
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_wave_hc_brightest_lines(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    wavemap = kwargs['wave']
    dv = kwargs['dv']
    mask = kwargs['mask']
    iteration = kwargs['iteration']
    niters = kwargs['niters']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, ncols=1, nrows=1)
    # ------------------------------------------------------------------
    # plot all lines
    frame.scatter(wavemap[~mask], dv[~mask], color='g', s=5, label='All lines')
    # plot brightest lines
    frame.scatter(wavemap[mask], dv[mask], color='r', s=5, label='Brightest lines')
    # plot legend
    frame.legend(loc=0)
    # plot title and labels
    # plot title and labels
    title = 'Delta-v error for matched lines (Iteration {0} of {1})'
    frame.set(title=title.format(iteration + 1, niters),
              xlabel='Wavelength [nm]', ylabel='dv [m/s]')
    # ------------------------------------------------------------------
    # adjust plot
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_hc_tfit_grid(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    orders = kwargs['orders']
    wavemap = kwargs['wave']
    recon = kwargs['recon']
    rms = kwargs['rms']
    xgau = kwargs['xgau']
    ew = kwargs['ew']
    iteration = kwargs['iteration']
    niters = kwargs['niters']
    # ------------------------------------------------------------------
    # get all orders
    all_orders = np.unique(orders)
    # calculate dv values
    dv = ((wavemap / recon) - 1) * speed_of_light
    # ------------------------------------------------------------------
    # get colours
    colours = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # repeat colours to match all_orders
    colours = np.tile(colours, len(all_orders))
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, ncols=2, nrows=2)
    # ------------------------------------------------------------------
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
        frame1.scatter(wavemap[good], dv[good], s=5, color=colour)
        # plot frame2
        frame2.scatter(np.log10(1.0 / rms[good]), dv[good], s=5, color=colour)
        # plot frame3
        frame3.scatter(xgau[good] % 1, dv[good], s=5, color=colour)
        # plot frame4
        frame4.scatter(ew[good], dv[good], s=5, color=colour)
    # set up labels
    frame1.set(xlabel='Wavelength [nm]', ylabel='dv [km/s]')
    frame2.set(xlabel='log_{10}(Line SNR estimate)', ylabel='dv [km/s]')
    frame3.set(xlabel='Modulo pixel position', ylabel='dv [km/s]')
    frame4.set(xlabel='e-width of fitted line', ylabel='dv [km/s]')
    # add title
    plt.suptitle('Iteration {0} of {1}'.format(iteration + 1, niters))
    # ------------------------------------------------------------------
    # adjust plot
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_hc_resmap(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    plt = plotter.plt
    # get matplotlib rectange
    rectangle = plotter.matplotlib.patches.Rectangle
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    resmap_size = kwargs['resmap_size']
    map_dvs = kwargs['map_dvs']
    map_lines = kwargs['map_lines']
    map_params = kwargs['map_params']
    res_map = kwargs['res_map']
    nbo = kwargs['nbo']
    nbpix = kwargs['nbpix']
    # get parameters from params
    fit_span = params.listp('WAVE_HC_RESMAP_DV_SPAN', dtype=float)
    xlim = params.listp('WAVE_HC_RESMAP_XLIM', dtype=float)
    ylim = params.listp('WAVE_HC_RESMAP_YLIM', dtype=float)
    # ------------------------------------------------------------------
    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))
    # get order and bin range
    order_range = np.arange(0, nbo, bin_order)
    x_range = np.arange(0, nbpix // bin_x)
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, nrows=resmap_size[0],
                                   ncols=resmap_size[1], sharex=True,
                                   sharey=True)
    # ------------------------------------------------------------------
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
            resolution = res_map[order_num // bin_order][xpos]
            # get fit data
            xfit = np.linspace(fit_span[0], fit_span[1], 100)
            yfit = mp.gauss_fit_s(xfit, *params)
            # plot data
            frame.scatter(all_dvs, all_lines, color='g', s=5, marker='x')
            frame.plot(xfit, yfit, color=black, ls='--')
            # set frame limits
            frame.set(xlim=xlim, ylim=ylim)
            # add label in legend (for sticky position)
            largs = [order_num, order_num + bin_order - 1, xpos, resolution]
            handle = rectangle((0, 0), 1, 1, fc="w", fill=False,
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
    # add titles
    plt.suptitle('Line Profiles for resolution grid')
    # adjust spaces between plots
    plt.subplots_adjust(hspace=0, wspace=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_littrow_check(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get matplotlib imports
    cm = plotter.matplotlib.cm
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    llprops = kwargs['llprops']
    iteration = kwargs['iteration']
    fiber = kwargs['fiber']
    # get values from params
    ylower = -params['WAVE_LITTROW_QC_DEV_MAX']
    yupper = params['WAVE_LITTROW_QC_DEV_MAX']
    # ------------------------------------------------------------------
    # get data from llprops
    x_cut_points = llprops['X_CUT_POINTS_{0}'.format(iteration)]
    littrow_xx = llprops['LITTROW_XX_{0}'.format(iteration)]
    littrow_yy = llprops['LITTROW_YY_{0}'.format(iteration)]
    # ------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    colors = cm.rainbow(np.linspace(0, 1, len(x_cut_points)))
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    for it in range(len(x_cut_points)):
        # get x and y data
        xx = littrow_xx[it]
        yy = littrow_yy[it]
        # plot graph
        frame.plot(xx, yy, label='x = {0}'.format(x_cut_points[it]),
                   color=colors[it])
        # get y limits
        if np.min(yy) < ylower:
            ylower = np.min(yy)
        if np.max(yy) > yupper:
            yupper = np.max(yy)
    # set axis labels and title
    title = 'Wavelength Solution Littrow Check {0} fiber {1}'
    frame.set(xlabel='Order number', ylabel='Diff/Littrow [km/s]',
              title=title.format(iteration, fiber))
    # set frame limits
    frame.set(ylim=(ylower, yupper))
    # add legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_littrow_extrap(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    llprops = kwargs['llprops']
    iteration = kwargs['iteration']
    fiber = kwargs['fiber']
    ydim, xdim = kwargs['image'].shape
    # get data from llprops
    x_cut_points = llprops['X_CUT_POINTS_{0}'.format(iteration)]
    x_points = np.arange(xdim)
    yfit_x_cut = llprops['LITTROW_EXTRAP_{0}'.format(iteration)]
    yfit = llprops['LITTROW_EXTRAP_SOL_{0}'.format(iteration)]
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # colours
    colours = np.tile(['r', 'b', 'g', 'y', 'm', black, 'c'], ydim)
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # loop around the orders and plot each line
    for order_num in range(ydim):
        # plot the solution for all x points
        frame.plot(x_points, yfit[order_num],
                   color=colours[order_num])
        # custom marker
        marker = '$' + str(order_num) + '$'
        # plot the solution at the chosen cut points
        frame.scatter(x_cut_points, yfit_x_cut[order_num],
                      marker=marker, s=75, color=colours[order_num])
    # set title
    title = 'Wavelength Solution Littrow Extrapolation {0} fiber {1}'
    # set axis labels
    frame.set(xlabel='Pixel number', ylabel='Wavelength [nm]',
              title=title.format(iteration, fiber))
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_final_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    llprops = kwargs['llprops']
    fiber = kwargs['fiber']
    iteration = kwargs['iteration']
    selected_order = kwargs['end']
    fpdata = kwargs['fpdata']

    # get data from llprops
    wavemap = llprops['LITTROW_EXTRAP_SOL_{0}'.format(iteration)][selected_order]
    fp_data = fpdata[selected_order]
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # plot
    frame.plot(wavemap, fp_data)
    # set title labels limits
    title = 'spectral order {0} fiber {1} (iteration = {2})'
    frame.set(xlabel='Wavelength [nm]', ylabel='flux',
              title=title.format(selected_order, fiber, iteration))
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_lwid_offset(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    llprops = kwargs['llprops']
    # get data from llprops
    fp_m = llprops['FP_M']
    fp_dopd = llprops['FP_DOPD_OFFSET']
    fp_dopd_coeff = llprops['FP_DOPD_OFFSET_COEFF']
    # get fit values
    fp_dopd_fit = np.polyval(fp_dopd_coeff[::-1], np.sort(fp_m))
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # plot fits
    frame.scatter(fp_m, fp_dopd, label='Measured')
    frame.plot(np.sort(fp_m), fp_dopd_fit, label='fit', color='red')
    # set title labels limits
    title = 'FP cavity width offset'
    frame.set(xlabel='FP peak number',
              ylabel='Local cavity width offset [micron]',
              title=title)
    # Add legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_wave_res(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    llprops = kwargs['llprops']
    # get data from llprops
    fp_ll = llprops['FP_LL_POS']
    fp_ll_new = llprops['FP_LL_POS_NEW']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # plot fits
    frame.scatter(fp_ll, fp_ll - fp_ll_new)
    # set title labels limits
    title = 'FP lines wavelength residuals'
    frame.set(xlabel='Initial wavelength [nm]',
              ylabel='New - Initial wavelength [nm]', title=title)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_m_x_res(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    fp_order = kwargs['fp_order']
    fp_xx = kwargs['fp_xx']
    m_vec = kwargs['m_vec']
    xm_mask = kwargs['xm_mask']
    coeff_xm_all = kwargs['coeff_xm_all']
    n_init = kwargs['n_init']
    n_fin = kwargs['n_fin']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    for ord_num in range(n_fin - n_init):
        # create order mask
        ind_ord = np.where(np.concatenate(fp_order).ravel() == ord_num + n_init)
        # get FP line pixel positions for the order
        fp_x_ord = fp_xx[ord_num]
        # get FP line numbers for the order
        m_ord = m_vec[ind_ord]
        # get m(x) mask for the order
        mask = xm_mask[ord_num]
        # get coefficients for the order
        coeff_xm = coeff_xm_all[ord_num]
        # plot residuals
        frame.plot(fp_x_ord[mask], m_ord[mask] -
                   np.polyval(coeff_xm, fp_x_ord[mask]) + 0.01 * ord_num, '.')
    frame.set(xlabel='FP pixel position',
              ylabel='m(x) residuals (shifted +0.01*Order)')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_ipt_cwid_1mhc(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    one_m_d = kwargs['one_m_d']
    d_arr = kwargs['d_arr']
    m_init = kwargs['m_init']
    fit_1m_d_func = kwargs['fit_1m_d_func']
    res_d_final = kwargs['res_d_final']
    dopd0 = kwargs['dopd0']
    # ------------------------------------------------------------------
    # set up plot
    gs = dict(height_ratios=[2, 1])
    fig, frames = graph.set_figure(plotter, nrows=2, ncols=1,
                                   gridspec_kw=gs, sharex=True)
    frame1, frame2 = frames
    # ------------------------------------------------------------------
    # plot values
    frame1.plot(one_m_d, d_arr, marker='.')
    # plot initial cavity width value
    frame1.hlines(dopd0 / 2., min(one_m_d), max(one_m_d), label='original d')
    # plot reference peak of reddest order
    frame1.plot(1. / m_init, dopd0 / 2., 'D')
    # plot fit
    frame1.plot(one_m_d, fit_1m_d_func(one_m_d), label='polynomial fit')
    # plot residuals - separate subplot
    frame2.plot(one_m_d, res_d_final, '.')
    # set labels
    frame1.set(ylabel='cavity width d')
    frame2.set(xlabel='1/m', ylabel='residuals [nm]')
    # plot legend
    frame1.legend(loc='best')
    # add title
    fig.suptitle('Interpolated cavity width vs 1/m for HC lines')
    # ------------------------------------------------------------------
    # adjust plot
    fig.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95,
                        hspace=0, wspace=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_ipt_cwid_llhc(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    hc_ll = kwargs['hc_ll']
    fp_ll = kwargs['fp_ll']
    fitval = kwargs['fitval']
    d_arr = kwargs['d_arr']
    dopd0 = kwargs['dopd0']
    fiber = kwargs['fiber']
    # ------------------------------------------------------------------
    # set up plot
    gs = dict(height_ratios=[2, 1])
    fig, frames = graph.set_figure(plotter, nrows=2, ncols=1,
                                   gridspec_kw=gs, sharex=True)
    frame1, frame2 = frames
    # ------------------------------------------------------------------
    frame1.plot(hc_ll, d_arr, '.')
    # plot initial cavity width value
    frame1.hlines(dopd0 / 2., min(hc_ll), max(hc_ll), label='original d')
    # plot reference peak of reddest order
    frame1.plot(fp_ll[-1][-1], dopd0 / 2., 'D')
    # plot fit
    frame1.plot(hc_ll, fitval, label='polynomial fit')
    # plot residuals - separate subplot
    frame2.plot(hc_ll, d_arr - fitval, '.')
    # set labels
    frame1.set(ylabel='cavity width d')
    frame2.set(xlabel='wavelength', ylabel='residuals [nm]')
    # plot legend
    frame1.legend(loc='best')
    # add title
    fig.suptitle('Interpolated cavity width vs wavelength for HC lines. '
                 'Fiber={0}'.format(fiber))
    # ------------------------------------------------------------------
    # adjust plot
    fig.subplots_adjust(top=0.9, bottom=0.1, left=0.05, right=0.95,
                        hspace=0, wspace=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_ll_diff(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    cm = plotter.matplotlib.cm
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    llprops = kwargs['llprops']
    n_init = kwargs['n_init']
    n_fin = kwargs['n_fin']
    # get data from llprops
    poly_wave_sol = llprops['POLY_WAVE_SOL']
    fp_ord_new = llprops['FP_ORD_NEW']
    fp_xx_new = llprops['FP_XX_NEW']
    fp_ll_new = llprops['FP_LL_NEW']
    # ------------------------------------------------------------------
    # get colours
    # noinspection PyUnresolvedReferences
    col = cm.rainbow(np.linspace(0, 1, n_fin))
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # loop through the orders
    for ind_ord in range(n_fin - n_init):
        # get parameters for initial wavelength solution
        c_aux = np.poly1d(poly_wave_sol[ind_ord + n_init][::-1])
        # order mask
        ord_mask = np.where(fp_ord_new == ind_ord + n_init)
        # get FP line pixel positions for the order
        fp_x_ord = fp_xx_new[ord_mask]
        # derive FP line wavelengths using initial solution
        fp_ll_orig = c_aux(fp_x_ord)
        # get new FP line wavelengths for the order
        fp_ll_new_ord = fp_ll_new[ord_mask]
        # plot old-new wavelengths
        frame.plot(fp_x_ord, fp_ll_orig - fp_ll_new_ord + 0.001 * ind_ord,
                   marker='.', color=col[ind_ord],
                   label='order ' + str(ind_ord))
    # define labels
    ylabel = ('FP old-new wavelength difference [nm] '
              '(shifted +0.001 per order)')
    frame.set(xlabel='FP peak position [pix]', ylabel=ylabel)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_multi_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    hc_ll = kwargs['hc_ll']
    hc_ord = kwargs['hc_ord']
    hcdata = kwargs['hcdata']
    wave_map = kwargs['wave']
    n_plot_init = kwargs['init']
    n_fin = kwargs['fin']
    nbo = kwargs['nbo']
    # compute final plotting order
    n_plot_fin = np.min([n_plot_init + nbo, n_fin])
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # define colours and line types for alternate order fitted lines
    col = [black, 'grey']
    lty = ['--', ':']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    for order_num in range(n_plot_init, n_plot_fin):
        # select lines for the order
        hc_ll_plot = hc_ll[hc_ord == order_num]
        # get colour and style from order parity
        col_plot = col[np.mod(order_num, 2)]
        lty_plot = lty[np.mod(order_num, 2)]

        # log hc data
        with warnings.catch_warnings(record=True) as _:
            loghcdata = np.log10(hcdata[order_num])
        # plot hc spectra
        frame.plot(wave_map[order_num], loghcdata)
        # plot used HC lines
        frame.vlines(hc_ll_plot, 0, np.nanmax(loghcdata),
                     color=col_plot, linestyles=lty_plot)
        # set axis labels
    frame.set(xlabel='Wavelength [nm]', ylabel='log_{10}(Normalised flux)',
              title='HC spectra + used HC lines')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fp_single_order(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    llprops = kwargs['llprops']
    order = kwargs.get('order', None)
    hcdata = kwargs['hcdata']
    # get data from llprops
    all_lines = llprops['ALL_LINES_1']
    wavemap = llprops['LL_OUT_2']
    # get number of orders
    nbo = llprops['LL_OUT_2'].shape[0]
    # ------------------------------------------------------------------
    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        # prompt to start looper
        plotter.close_plots(loop=True)
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
        # get the maximum point for this order
        maxpoint = mp.nanmax(hcdata[order_num])
        # plot order and flux
        frame.plot(wavemap[order_num], hcdata[order_num], label='HC Spectrum')
        # loop around lines in order
        for it in range(0, len(all_lines[order_num])):
            # get x and y
            x = all_lines[order_num][it][0] + all_lines[order_num][it][3]
            ymaxi = all_lines[order_num][it][2]
            # log ydata
            with warnings.catch_warnings(record=True) as _:
                logydata = np.log10(ymaxi)
            # plot lines to their corresponding amplitude
            frame.vlines(x, 0, logydata, color='m', label='fitted lines')
            # plot lines to the top of the figure
            frame.vlines(x, 0, np.log10(maxpoint), color='gray',
                         linestyles='dotted')
        # plot
        ulegend(frame, plotter, loc=0)
        # set limits and title
        title = 'Order {0}'.format(order_num)
        frame.set(xlabel='Wavelength', ylabel='Flux', title=title)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_waveref_expected(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    orders = kwargs['orders']
    wavemap = kwargs['wavemap']
    diff = kwargs['diff']
    fiber = kwargs['fiber']
    fibtype = kwargs['fibtype']
    nbo = kwargs['nbo']
    iteration = kwargs.get('iteration', None)
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    for order_num in range(nbo):
        # get order mask
        omask = order_num == orders
        # plot points
        frame.scatter(wavemap[omask], diff[omask], s=5)
    # add title (with or without iteration)
    if iteration is not None:
        if isinstance(iteration, int) or isinstance(iteration, float):
            title = 'Pixel difference Fiber {0} Type {1} (Iteration = {2})'
        else:
            title = 'Pixel difference Fiber {0} Type {1} ({2})'
    else:
        title = 'Pixel difference Fiber {0} Type {1}'
    # set labels
    frame.set(xlabel='Wavelength [nm]', ylabel='Pixel difference',
              title=title.format(fiber, fibtype, iteration))
    # ------------------------------------------------------------------
    # update filename (adding order_num to end)
    suffix = 'mode{0}_fiber{1}'.format(fibtype, fiber)
    graph.set_filename(plotter.params, plotter.location, suffix=suffix)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wave_fiber_comparison(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    master_fiber = kwargs['masterfiber']
    solutions = kwargs['solutions']
    master = kwargs['master']
    order = kwargs.get('order', None)
    # get number of orders and fibers
    nbo = master['NBO']
    fibers = list(solutions.keys())
    # get master values
    m_coeffs = master['COEFFS']
    # ------------------------------------------------------------------
    # get order generator
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo).astype(int))
        # prompt to start looper
        plotter.close_plots(loop=True)
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # ------------------------------------------------------------------
        # set up plot
        fig, frames = graph.set_figure(plotter, nrows=1, ncols=len(fibers))
        # ------------------------------------------------------------------
        for it, fiber in enumerate(fibers):
            # get this fibers lines
            rfpl = solutions[fiber]['FPLINES']
            r_waveref = rfpl['WAVE_REF']
            r_pixel = rfpl['PIXEL_MEAS']
            r_order = rfpl['ORDER']
            r_coeffs = solutions[fiber]['COEFFS']
            # get the order mask
            good = (r_order == order_num) & np.isfinite(r_pixel)
            # get the x values for the graph
            xvals = r_waveref[good]
            # get the line fit values
            fit1 = np.polyval(m_coeffs[order_num][::-1], r_pixel[good])
            fit2 = np.polyval(r_coeffs[order_num][::-1], r_pixel[good])
            # get the y values
            y1vals = speed_of_light * (1 - r_waveref[good] / fit1)
            y2vals = speed_of_light * (1 - r_waveref[good] / fit2)
            # plot
            frames[it].scatter(xvals, y1vals, color='r', s=5,
                               label='Fiber {0}'.format(master_fiber))
            frames[it].scatter(xvals, y2vals, color='g', s=5,
                               label='Fiber {0}'.format(fiber))
            frames[it].set(title='Order {0} Fiber {1}'.format(order_num, fiber),
                           xlabel='wavelength [nm]',
                           ylabel='dv [km/s]')
            frames[it].legend(loc=0)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_wavenight_iterplot(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    waverefs = kwargs['waverefs']
    pixdiffs = kwargs['pixdiffs']
    fiber = kwargs['fiber']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    for it in range(len(pixdiffs)):
        frame.plot(waverefs[it], pixdiffs[it], label='Iteration {0}'.format(it),
                   marker='.', linestyle='None')
    frame.legend(loc=0)
    frame.set(xlabel='Reference wavelength', ylabel='Pixel difference')
    # ------------------------------------------------------------------
    # update filename (adding fiber to the end)
    graph.set_filename(plotter.params, plotter.location, suffix=fiber)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_wavenight_histplot(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    rhcl = kwargs['rhcl']
    rhcl_prev = kwargs['rhcl_prev']
    rfpl = kwargs['rfpl']
    dcavity = kwargs['dcavity']
    rms = kwargs['rms']
    binl = kwargs['binl']
    binu = kwargs['binu']
    nbins = kwargs['nbins']
    fiber = kwargs['fiber']
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, nrows=2, ncols=1)
    # hist setup
    hkwargs = dict(bins=nbins, range=[binl * rms, binu * rms], alpha=0.5)
    # ------------------------------------------------------------------
    # plot 1
    # ------------------------------------------------------------------
    # calculate data for binning
    y1 = (1 - (rfpl['WAVE_REF'] / rfpl['WAVE_MEAS']))
    y2 = (1 - (rfpl['WAVE_REF'] * (1 + dcavity) / rfpl['WAVE_MEAS']))
    y1 = y1 * speed_of_light_ms
    y2 = y2 * speed_of_light_ms
    # plot hist
    frames[0].hist(y1, label='FP before', **hkwargs)
    frames[0].hist(y2, label='FP after', **hkwargs)
    frames[0].axvline(0)
    frames[0].legend(loc=0)
    frames[0].set(xlabel='dv [m/s]', ylabel='Number of lines')
    # ------------------------------------------------------------------
    # plot 2
    # ------------------------------------------------------------------
    # calculate data for binning
    y3 = (1 - (rhcl_prev['WAVE_REF'] / rhcl_prev['WAVE_MEAS']))
    y4 = (1 - (rhcl['WAVE_REF'] / rhcl['WAVE_MEAS']))
    y3 = y3 * speed_of_light_ms
    y4 = y4 * speed_of_light_ms
    # plot hist
    frames[1].hist(y3, label='HC before', **hkwargs)
    frames[1].hist(y4, label='HC after', **hkwargs)
    frames[1].axvline(0)
    frames[1].legend(loc=0)
    frames[1].set(xlabel='dv [m/s]', ylabel='Number of lines')
    # ------------------------------------------------------------------
    # update filename (adding fiber to the end)
    graph.set_filename(plotter.params, plotter.location, suffix=fiber)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


wave_hc_guess = Graph('WAVE_HC_GUESS', kind='debug',
                      func=plot_wave_hc_guess)
wave_hc_brightest_lines = Graph('WAVE_HC_BRIGHTEST_LINES', kind='debug',
                                func=plot_wave_hc_brightest_lines)
wave_hc_tfit_grid = Graph('WAVE_HC_TFIT_GRID', kind='debug',
                          func=plot_wave_hc_tfit_grid)
wave_hc_resmap = Graph('WAVE_HC_RESMAP', kind='debug',
                       func=plot_wave_hc_resmap,
                       figsize=(20, 16))
wave_littrow_check1 = Graph('WAVE_LITTROW_CHECK1', kind='debug',
                            func=plot_wave_littrow_check)
wave_littrow_extrap1 = Graph('WAVE_LITTROW_EXTRAP1', kind='debug',
                             func=plot_wave_littrow_extrap)
wave_littrow_check2 = Graph('WAVE_LITTROW_CHECK2', kind='debug',
                            func=plot_wave_littrow_check)
sum_desc = 'Littrow check for the final solution'
sum_wave_littrow_check = Graph('SUM_WAVE_LITTROW_CHECK', kind='summary',
                               func=plot_wave_littrow_check,
                               figsize=(16, 10), dpi=150, description=sum_desc)
wave_littrow_extrap2 = Graph('WAVE_LITTROW_EXTRAP2', kind='debug',
                             func=plot_wave_littrow_extrap)
sum_desc = 'Littrow extrapolation for the final solution'
sum_wave_littrow_extrap = Graph('SUM_WAVE_LITTROW_EXTRAP', kind='summary',
                                func=plot_wave_littrow_extrap,
                                figsize=(16, 10), dpi=150, description=sum_desc)
wave_fp_final_order = Graph('WAVE_FP_FINAL_ORDER', kind='debug',
                            func=plot_wave_fp_final_order)
wave_fp_lwid_offset = Graph('WAVE_FP_LWID_OFFSET', kind='debug',
                            func=plot_wave_fp_lwid_offset)
wave_fp_wave_res = Graph('WAVE_FP_WAVE_RES', kind='debug',
                         func=plot_wave_fp_wave_res)
wave_fp_m_x_res = Graph('WAVE_FP_M_X_RES', kind='debug',
                        func=plot_wave_fp_m_x_res)
wave_fp_ipt_cwid_1mhc = Graph('WAVE_FP_IPT_CWID_1MHC', kind='debug',
                              func=plot_wave_fp_ipt_cwid_1mhc)
wave_fp_ipt_cwid_llhc = Graph('WAVE_FP_IPT_CWID_LLHC', kind='debug',
                              func=plot_wave_fp_ipt_cwid_llhc)
sum_desc = 'FP peak number against cavity width offset'
sum_wave_fp_ipt_cwid_1mhc = Graph('SUM_WAVE_FP_IPT_CWID_LLHC', kind='summary',
                                  func=plot_wave_fp_ipt_cwid_llhc,
                                  figsize=(16, 10), dpi=150,
                                  description=sum_desc)
wave_fp_ll_diff = Graph('WAVE_FP_LL_DIFF', kind='debug',
                        func=plot_wave_fp_ll_diff)
wave_fp_multi_order = Graph('WAVE_FP_MULTI_ORDER', kind='debug',
                            func=plot_wave_fp_multi_order)
wave_fp_single_order = Graph('WAVE_FP_SINGLE_ORDER', kind='debug',
                             func=plot_wave_fp_single_order)
waveref_expected = Graph('WAVEREF_EXPECTED', kind='debug',
                         func=plot_waveref_expected)

wave_fiber_comparison = Graph('WAVE_FIBER_COMPARISON', kind='debug',
                              func=plot_wave_fiber_comparison)
wave_fiber_comp = Graph('WAVE_FIBER_COMP', kind='debug',
                        func=plot_wave_fiber_comparison)
sum_desc = 'Fiber comparison plot'
sum_wave_fiber_comp = Graph('SUM_WAVE_FIBER_COMP', kind='summary',
                            func=plot_wave_fiber_comparison,
                            figsize=(16, 10), dpi=150,
                            description=sum_desc)
wavenight_iterplot = Graph('WAVENIGHT_ITERPLOT', kind='debug',
                           func=plot_wavenight_iterplot)
sum_desc = 'Wave night iteration plot'
sum_wavenight_iterplot = Graph('SUM_WAVENIGHT_ITERPLOT', kind='summary',
                               func=plot_wavenight_iterplot,
                               figsize=(16, 10), dpi=150,
                               description=sum_desc)
wavenight_histplot = Graph('WAVENIGHT_HISTPLOT', kind='debug',
                           func=plot_wavenight_histplot)
sum_desc = 'Wave night histogram plot'
sum_wavenight_histplot = Graph('SUM_WAVENIGHT_HISTPLOT', kind='summary',
                               func=plot_wavenight_histplot,
                               figsize=(16, 10), dpi=150,
                               description=sum_desc)
# add to definitions
definitions += [wave_hc_guess, wave_hc_brightest_lines, wave_hc_tfit_grid,
                wave_hc_resmap, wave_littrow_check1, wave_littrow_extrap1,
                wave_littrow_check2, wave_littrow_extrap2, wave_fp_final_order,
                wave_fp_lwid_offset, wave_fp_wave_res, wave_fp_m_x_res,
                wave_fp_ipt_cwid_1mhc, wave_fp_ipt_cwid_llhc, wave_fp_ll_diff,
                wave_fp_multi_order, wave_fp_single_order,
                sum_wave_littrow_check, sum_wave_littrow_extrap,
                sum_wave_fp_ipt_cwid_1mhc, waveref_expected, wavenight_iterplot,
                sum_wavenight_iterplot, wavenight_histplot,
                sum_wavenight_histplot, wave_fiber_comparison,
                wave_fiber_comp, sum_wave_fiber_comp]


# =============================================================================
# Define telluric plotting functions
# =============================================================================
def plot_tellup_wave_trans(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    dd_arr = kwargs['dd_arr']
    ccf_water_arr = kwargs['ccf_water_arr']
    ccf_others_arr = kwargs['ccf_others_arr']
    n_iterations = len(dd_arr)
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, nrows=1, ncols=2)
    # ------------------------------------------------------------------
    # plot ccfs
    for n_it in range(n_iterations):
        # plot water ccf
        frames[0].plot(dd_arr[n_it], ccf_water_arr[n_it])
        frames[0].set(xlabel='dv [km/s]', ylabel='CCF power',
                      title='Water CCF')
        # plot other species ccf
        frames[1].plot(dd_arr[n_it], ccf_others_arr[n_it])
        frames[1].set(xlabel='dv [km/s]', ylabel='CCF power',
                      title='Dry CCF')
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_tellup_abso_spec(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    trans = kwargs['trans']
    wavemap = kwargs['wave']
    thres = kwargs['thres']
    spectrum = kwargs['spectrum']
    spectrum_ini = kwargs['spectrum_ini']
    objname = kwargs['objname']
    clean_ohlines = kwargs['clean_ohlines']
    # ------------------------------------------------------------------
    # calculate normalisation
    median = np.nanmedian(spectrum)
    spectrum = spectrum / median
    spectrum_ini = spectrum_ini / median
    # calculate mask for transmissiong
    mask = np.ones_like(trans)
    # set lower tranmission to NaNs in mask
    mask[trans < np.exp(thres)] = np.nan
    # set NaN values in spectrum to NaNs in mask
    mask[~np.isfinite(spectrum)] = np.nan
    # work out a scaling
    scale = np.nanpercentile(spectrum/trans*mask, 99.5)
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # plot input spectrum
    frame.plot(wavemap, spectrum / scale, color='red', label='input')
    # plot oh lines
    if clean_ohlines:
        frame.plot(wavemap, spectrum_ini / (trans * mask) / scale,
                   color='magenta', alpha=0.5, label='prior to OH')
    # plot input/derived_trans
    frame.plot(wavemap, spectrum / trans * mask / scale, color='green',
               label='input/derived_trans')
    # plot abso
    frame.plot(wavemap, trans, color='orange', label='abso', alpha=0.3)
    # add legend
    frame.legend(loc=0)
    # get ymax value
    ymax = mp.nanmax(spectrum_ini / (trans * mask) / scale) * 1.05
    # set limits
    frame.set(xlabel='Wavelength [nm]', ylabel='Normalized flux\n transmission',
              title='OBJECT = {0}'.format(objname), ylim=[0, ymax])
    # make figure tight
    fig.tight_layout()
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_mktellu_wave_flux(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    wavemap = kwargs['wavemap']
    sp = kwargs['sp']
    sed = kwargs['sed']
    oimage = kwargs['oimage']
    order = kwargs.get('order', None)
    has_template = kwargs.get('has_template', False)
    template = kwargs.get('template', None)
    # ------------------------------------------------------------------
    if order is None:
        order_gen = plotter.plotloop(np.arange(len(wavemap)))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # get this orders values
        x = wavemap[order_num]
        y2 = sp[order_num]
        y3 = (sp[order_num] / template[order_num]) / sed[order_num]
        y4 = oimage[order_num] * template[order_num]
        y5 = sed[order_num] * template[order_num]

        # normalise to match for plotting
        corr_norm = mp.nanmedian(y2 / y4)
        y3 = y3 / corr_norm
        y2 = y2 / corr_norm

        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
        # plot data
        frame.plot(x, y2, color='k', label='input spectrum')
        frame.plot(x, y3, color='b', label='measured transmission')

        # deal with labels with and without template
        if has_template:
            label4 = 'Update to SED (with Template)'
        else:
            label4 = 'SED calculation value (No template)'

        frame.plot(x, y4, color='r', marker='.', linestyle='None',
                   label='SED calculation value')
        frame.plot(x, y5, color='g', linestyle='--', label=label4)

        # get max / min y
        values = list(y2) + list(y3) + list(y4) + list(y5)
        mins = 0.95 * np.nanmin([0, np.nanmin(values)])
        maxs = 1.05 * np.nanmax(values)

        # plot legend and set up labels / limits / title
        frame.legend(loc=0)
        frame.set(xlim=(np.min(x), np.max(x)), ylim=(mins, maxs),
                  xlabel='Wavelength [nm]', ylabel='Normalised flux',
                  title='Order: {0}'.format(order_num))
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ftellu_pca_comp(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    wavemap = kwargs['wavemap']
    pc = kwargs['pc']
    add_deriv_pc = kwargs['add_deriv_pc']
    npc = kwargs['npc']
    order = kwargs.get('order', None)
    # get shape from image
    nbo, nbpix = image.shape
    # ------------------------------------------------------------------
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders in order generator
    for order_num in order_gen:
        # get wave map for this order
        swave = wavemap[order_num]
        # get start and end points
        start, end = order_num * nbpix, order_num * nbpix + nbpix
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
        # plot principle components
        for it in range(npc):
            # define the label for the component
            if add_deriv_pc:
                if it == npc - 2:
                    label = 'd[pc1]'
                elif it == npc - 1:
                    label = 'd[pc2]'
                else:
                    label = 'pc {0}'.format(it + 1)
            else:
                label = 'pc {0}'.format(it + 1)
            # plot the component with correct label
            frame.plot(swave, pc[start:end, it], label=label)
        # add legend
        frame.legend(loc=0)
        # add labels
        title = 'Principle component plot. Order = {0}'.format(order_num)
        frame.set(title=title, xlabel='Wavelength [nm]',
                  ylabel='Principle component power')
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ftellu_recon_spline(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    wavemap = kwargs['wavemap']
    template = kwargs['template']
    order = kwargs.get('order', None)
    # get shape from image
    nbo, nbpix = image.shape
    # ------------------------------------------------------------------
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders in order generator
    for order_num in order_gen:
        # get selected order wave lengths
        swave = wavemap[order_num, :]
        # get selected order for sp
        simage = image[order_num, :]
        # get template2 at selected order
        start, end = order_num * nbpix, order_num * nbpix + nbpix
        stemp = np.array(template[start: end])
        # recovered absorption
        srecov = simage / stemp
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
        # plot spectra for selected order
        frame.plot(swave, simage / np.nanmedian(simage), label='Observed SP')
        frame.plot(swave, stemp / np.nanmedian(stemp), label='Template SP')
        frame.plot(swave, srecov / np.nanmedian(srecov),
                   label='Recov abso SP (Observed/Template)')
        # add legend
        frame.legend(loc=0)
        # add labels
        title = 'Reconstructed Spline Plot (Order = {0})'
        frame.set(title=title.format(order_num),
                  xlabel='Wavelength [nm]', ylabel='Normalised flux')
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ftellu_wave_shift(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    tapas_before = kwargs['tapas0'][0]
    tapas_after = kwargs['tapas1'][0]
    pc_before = kwargs['pc0'][:, 0]
    pc_after = kwargs['pc1'][:, 0]
    order = kwargs.get('order', None)
    # get shape from image
    nbo, nbpix = image.shape
    # ------------------------------------------------------------------
    if order is None:
        order_gen = plotter.plotloop(np.arange(nbo))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # loop around orders in order generator
    for order_num in order_gen:
        # get start and end points
        start, end = order_num * nbpix, order_num * nbpix + nbpix
        # get this orders data
        tdata_s = image[order_num, :] / np.nanmedian(image[order_num, :])
        tapas_before_s = tapas_before[start:end]
        tapas_after_s = tapas_after[start:end]
        pc1_before_s = pc_before[start:end]
        pc1_after_s = pc_after[start:end]
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
        # plot the data vs pixel number
        frame.plot(tdata_s, color='k', label='Spectrum')
        frame.plot(pc1_before_s, color='g', marker='x', label='PC (before)')
        frame.plot(tapas_before_s, color='0.5', marker='o',
                   label='TAPAS (before)')
        frame.plot(pc1_after_s, color='r', label='PC (After)')
        frame.plot(tapas_after_s, color='b', label='TAPAS (After)')

        frame.legend(loc=0)
        title = ('Wavelength shift (Before and after) compared to the data '
                 '(Order {0})')
        frame.set(title=title.format(order_num), xlabel='Pixel number',
                  ylabel='Normalised flux')
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ftellu_recon_abso(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    image = kwargs['image']
    wavemap = kwargs['wavemap']
    sp2 = kwargs['sp2']
    template = kwargs['template']
    recon = kwargs['recon']
    orders = kwargs.get('orders', None)
    order = kwargs.get('order', None)
    # get shape from image
    nbo, nbpix = image.shape
    # ------------------------------------------------------------------
    if order is None and orders is None:
        order_gen = plotter.plotloop(np.arange(nbo))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we check whether orders is set
    elif orders is not None:
        order_gen = list(orders)
    # else we just deal with the order specified
    elif order is not None:
        order_gen = [order]
    else:
        order_gen = [0]
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # ------------------------------------------------------------------
    # loop around orders in order generator
    for order_num in order_gen:
        # get selected order wave lengths
        swave = wavemap[order_num, :]
        # get the data for order
        start, end = order_num * nbpix, order_num * nbpix + nbpix
        ssp = np.array(image[order_num, :])
        ssp2 = np.array(sp2[start:end])
        stemp2 = np.array(template[start:end])
        srecon_abso = np.array(recon[start:end])
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
        # ------------------------------------------------------------------
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
        frame.set(title=title.format(order_num),
                  xlabel='Wavelength [nm]', ylabel='Normalised flux')
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


# telluric pre clean graph instances
tellup_wave_trans = Graph('TELLUP_WAVE_TRANS', kind='debug',
                          func=plot_tellup_wave_trans)
sum_desc = ('Plot to show the measured CCF of water and other species '
            'calculated during the telluric pre-cleaning')
sum_tellup_wave_trans = Graph('SUM_TELLUP_WAVE_TRANS', kind='summary',
                              func=plot_tellup_wave_trans,
                              figsize=(16, 10), dpi=150, description=sum_desc)
tellup_abso_spec = Graph('TELLUP_ABSO_SPEC', kind='debug',
                         func=plot_tellup_abso_spec)
sum_desc = 'Plot to the result of the telluric pre-cleaning'
sum_tellup_abso_spec = Graph('SUM_TELLUP_ABSO_SPEC', kind='summary',
                             func=plot_tellup_abso_spec,
                             figsize=(16, 10), dpi=150, description=sum_desc)
# make telluric graph instances
mktellu_wave_flux1 = Graph('MKTELLU_WAVE_FLUX1', kind='debug',
                           func=plot_mktellu_wave_flux)
mktellu_wave_flux2 = Graph('MKTELLU_WAVE_FLUX2', kind='debug',
                           func=plot_mktellu_wave_flux)
sum_desc = ('Plot to show the measured transmission (and calcaulted SED) for'
            ' input rapidly rotating hot star')
sum_mktellu_wave_flux = Graph('SUM_MKTELLU_WAVE_FLUX', kind='summary',
                              func=plot_mktellu_wave_flux,
                              figsize=(16, 10), dpi=150, description=sum_desc)
# fit tellu grpah instances
ftellu_pca_comp1 = Graph('FTELLU_PCA_COMP1', kind='debug',
                         func=plot_ftellu_pca_comp)
ftellu_pca_comp2 = Graph('FTELLU_PCA_COMP2', kind='debug',
                         func=plot_ftellu_pca_comp)
ftellu_recon_spline1 = Graph('FTELLU_RECON_SPLINE1', kind='debug',
                             func=plot_ftellu_recon_spline)
ftellu_recon_spline2 = Graph('FTELLU_RECON_SPLINE2', kind='debug',
                             func=plot_ftellu_recon_spline)
ftellu_wave_shift1 = Graph('FTELLU_WAVE_SHIFT1', kind='debug',
                           func=plot_ftellu_wave_shift)
ftellu_wave_shift2 = Graph('FTELLU_WAVE_SHIFT2', kind='debug',
                           func=plot_ftellu_wave_shift)
ftellu_recon_abso1 = Graph('FTELLU_RECON_ABSO1', kind='debug',
                           func=plot_ftellu_recon_abso)
ftellu_recon_abso2 = Graph('FTELLU_RECON_ABSO2', kind='debug',
                           func=plot_ftellu_recon_abso)
sum_desc = 'Results from the telluric fit'
sum_ftellu_recon_abso = Graph('SUM_FTELLU_RECON_ABSO', kind='summary',
                              func=plot_ftellu_recon_abso, figsize=(16, 10),
                              dpi=150, description=sum_desc)
# add to definitions
definitions += [mktellu_wave_flux1, mktellu_wave_flux2, sum_mktellu_wave_flux,
                ftellu_pca_comp1, ftellu_pca_comp2, ftellu_recon_spline1,
                ftellu_recon_spline2, ftellu_wave_shift1, ftellu_wave_shift2,
                ftellu_recon_abso1, ftellu_recon_abso2, sum_ftellu_recon_abso,
                tellup_wave_trans, sum_tellup_wave_trans,
                tellup_abso_spec, sum_tellup_abso_spec]


# =============================================================================
# Define velocity plotting functions
# =============================================================================
def plot_ccf_rv_fit(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    params = kwargs['params']
    x = kwargs['x']
    y = kwargs['y']
    yfit = kwargs['yfit']
    kind = kwargs['kind']
    found_rv = kwargs['rv']
    ccf_mask = kwargs['ccfmask']
    order = kwargs.get('order', None)
    orders = kwargs.get('orders', None)
    # ------------------------------------------------------------------
    # if orders is None we assume x, y and yfit are just one vector
    if orders is None and order is None:
        # set y, yfit to length-1 lists of themselves
        y, yfit = [y], [yfit]
        found_rv = [found_rv]
        # order gen is just set to a list containing the first
        #     (and only) element
        order_gen = [0]
    # else if orders is None we get all orders
    elif order is None:
        order_gen = plotter.plotloop(orders)
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we just deal with the order specified
    else:
        order_gen = [order]
    # ------------------------------------------------------------------
    # deal with plot style
    if 'dark' in params['DRS_PLOT_STYLE']:
        black = 'white'
    else:
        black = 'black'
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # get this orders values
        y_i = y[order_num]
        yfit_i = yfit[order_num]
        # work out the residuals
        res = y_i - yfit_i
        # ------------------------------------------------------------------
        # set up plot
        gs = dict(height_ratios=[2, 1])
        fig, frames = graph.set_figure(plotter, nrows=2, ncols=1, sharex=True,
                                       gridspec_kw=gs)
        # ------------------------------------------------------------------
        # plot x vs y and yfit
        frames[0].plot(x, y_i, label='data', marker='x', ls='None',
                       color=black)
        frames[0].plot(x, yfit_i, label='fit')
        # plot residuals
        frames[1].plot(x, res, label='residuals')
        # plot legends
        frames[0].legend(loc=0)
        frames[1].legend(loc=0)
        # set labels and title
        targs = ['({0})'.format(kind), found_rv[order_num], ccf_mask]
        title = 'CCF plot {0}\n RV={1:.5f} km/s Mask={2}'.format(*targs)
        if orders is not None:
            title = 'RV Fit plot. Order {0}'.format(order_num)
        frames[0].set(ylabel='CCF', title=title)
        frames[1].set(xlabel='RV [km/s]', ylabel='CCF')
        # ------------------------------------------------------------------
        # adjust size
        fig.subplots_adjust(hspace=0, wspace=0)
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}'.format(order_num)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ccf_swave_ref(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    wavemap = kwargs['wavemap']
    image = kwargs['image']
    fiber = kwargs['fiber']
    nbo = kwargs['nbo']
    # optional arguments
    order = kwargs.get('order', None)
    orders = kwargs.get('orders', None)
    # ------------------------------------------------------------------
    if order is None and orders is None:
        order_gen = plotter.plotloop(np.arange(nbo))
        # prompt to start looper
        plotter.close_plots(loop=True)
    # else we check whether orders is set
    elif orders is not None:
        order_gen = list(orders)
    # else we just deal with the order specified
    elif order is not None:
        order_gen = [order]
    else:
        order_gen = [0]
    # ------------------------------------------------------------------
    # loop around orders
    for order_num in order_gen:
        # ------------------------------------------------------------------
        # set up plot
        fig, frame = graph.set_figure(plotter)
        # ------------------------------------------------------------------
        # plot fits
        frame.plot(wavemap[order_num], image[order_num])
        # set title labels limits
        title = 'spectral order {0} fiber {1}'
        frame.set(xlabel='Wavelength [nm]', ylabel='flux',
                  title=title.format(order_num, fiber))
        # ------------------------------------------------------------------
        # update filename (adding order_num to end)
        suffix = 'order{0}_{1}'.format(order_num, fiber)
        graph.set_filename(plotter.params, plotter.location, suffix=suffix)
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.plotend(graph)


def plot_ccf_photon_uncert(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = kwargs.get('x')
    y_sp = kwargs.get('y_sp')
    y_ccf = kwargs.get('y_cc')
    # get max/min points
    with warnings.catch_warnings(record=True) as _:
        ymin = mp.nanmin(y_ccf)
        ymax = mp.nanmax(y_ccf)
        if not np.isfinite(ymin):
            ymin = mp.nanmin(y_sp)
        if not np.isfinite(ymax):
            ymax = mp.nanmax(y_sp)
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # ------------------------------------------------------------------
    # plot fits
    frame.plot(x, y_sp, label='DVRMS Spectrum', marker='x', linestyle='None')
    # plot ccf noise (unless all NaNs)
    if np.sum(np.isnan(y_ccf)) != len(y_ccf):
        frame.plot(x, y_ccf, label='DVRMS CCF', marker='o', linestyle='None')
    # set title labels limits
    title = 'Photon noise uncertainty versus spectral order'
    frame.set(xlabel='Order number', ylabel='Photon noise uncertainty [m/s]',
              title=title)
    # deal with limits (may be NaN)
    if np.isfinite(ymin) and np.isfinite(ymax):
        frame.set_ylim(bottom=ymin, top=ymax)
    elif np.isfinite(ymin):
        frame.set_ylim(bottom=ymin)
    else:
        frame.set_ylim(top=ymax)

    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


ccf_rv_fit_loop = Graph('CCF_RV_FIT_LOOP', kind='debug', func=plot_ccf_rv_fit)
ccf_rv_fit = Graph('CCF_RV_FIT', kind='debug', func=plot_ccf_rv_fit)
ccf_swave_ref = Graph('CCF_SWAVE_REF', kind='debug', func=plot_ccf_swave_ref)
ccf_photon_uncert = Graph('CCF_PHOTON_UNCERT', kind='debug',
                          func=plot_ccf_photon_uncert)
sum_ccf_rv_fit = Graph('SUM_CCF_RV_FIT', kind='summary', func=plot_ccf_rv_fit)
sum_ccf_photon_uncert = Graph('SUM_CCF_PHOTON_UNCERT', kind='summary',
                              func=plot_ccf_photon_uncert)

# add to definitions
definitions += [ccf_rv_fit, ccf_rv_fit_loop, ccf_swave_ref,
                ccf_photon_uncert, sum_ccf_rv_fit, sum_ccf_photon_uncert]


# =============================================================================
# Define polarisation plotting functions
# =============================================================================
def plot_polar_continuum(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    props = kwargs['props']
    # get data from props
    wl = props['FLAT_X']
    pol = 100 * props['FLAT_POL']
    contpol = 100.0 * props['CONT_POL']
    contxbin = np.array(props['CONT_XBIN'])
    contybin = 100. * np.array(props['CONT_YBIN'])
    stokes = props['STOKES']
    method = props['METHOD']
    nexp = props['NEXPOSURES']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ------------------------------------------------------------------
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
    xlabel = 'wavelength [nm]'
    ylabel = 'Degree of polarization for Stokes {0} [%]'.format(stokes)
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_polar_results(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    props = kwargs['props']
    # get data from props
    wl = props['FLAT_X']
    pol = 100 * props['FLAT_POL']
    null1 = 100.0 * props['FLAT_NULL1']
    null2 = 100.0 * props['FLAT_NULL2']
    stokes = props['STOKES']
    method = props['METHOD']
    nexp = props['NEXPOSURES']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ---------------------------------------------------------------------
    # plot polarimetry data
    frame.plot(wl, pol, label='Degree of Polarization')
    # plot null1 data
    frame.plot(wl, null1, label='Null Polarization 1')
    # plot null2 data
    frame.plot(wl, null2, label='Null Polarization 2')
    # ---------------------------------------------------------------------
    # set title and labels
    xlabel = 'wavelength [nm]'
    ylabel = 'Degree of polarization for Stokes {0} [%]'.format(stokes)
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_polar_stoke_i(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    props = kwargs['props']
    # get data from props
    wl = props['FLAT_X']
    stokes_i = props['FLAT_STOKES_I']
    stokes_ierr = props['FLAT_STOKES_I_ERR']
    stokes = props['STOKES']
    method = props['METHOD']
    nexp = props['NEXPOSURES']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter, nrows=1, ncols=1)
    # ------------------------------------------------------------------
    # set up title
    title = 'Polarimetry: Stokes {0}, Method={1}, for {2} exposures'
    titleargs = [stokes, method, nexp]
    # ---------------------------------------------------------------------
    # plot polarimetry data
    frame.errorbar(wl, stokes_i, yerr=stokes_ierr, fmt='-', label='Stokes I',
                   alpha=0.5)
    # ---------------------------------------------------------------------
    # set title and labels
    xlabel = 'wavelength [nm]'
    ylabel = 'Stokes {0} total flux (ADU)'.format(stokes)
    frame.set(title=title.format(*titleargs), xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    # plot legend
    frame.legend(loc=0)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_polar_lsd(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    pprops = kwargs['pprops']
    lprops = kwargs['lprops']
    # get data from props
    vels = lprops['LSD_VELOCITIES']
    zz = lprops['LSD_STOKES_I']
    zgauss = lprops['LSD_STOKES_I_MODEL']
    z_p = lprops['LSD_STOKES_VQU']
    z_np = lprops['LSD_NULL']
    stokes = pprops['STOKES']
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, nrows=1, ncols=3)
    # ------------------------------------------------------------------
    frame = frames[0]
    frame.plot(vels, zz, '-')
    frame.plot(vels, zgauss, '-')
    title = 'LSD Analysis'
    ylabel = 'Stokes I profile'
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    frame = frames[1]
    title = ''
    frame.plot(vels, z_p, '-')
    ylabel = 'Stokes {0} profile'.format(stokes)
    xlabel = ''
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ---------------------------------------------------------------------
    frame = frames[2]
    frame.plot(vels, z_np, '-')
    xlabel = 'velocity (km/s)'
    ylabel = 'Null profile'
    # set title and labels
    frame.set(title=title, xlabel=xlabel, ylabel=ylabel)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


polar_continuum = Graph('POLAR_CONTINUUM', kind='debug',
                        func=plot_polar_continuum)
polar_results = Graph('POLAR_RESULTS', kind='debug', func=plot_polar_results)
polar_stokes_i = Graph('POLAR_STOKES_I', kind='debug', func=plot_polar_stoke_i)
polar_lsd = Graph('POLAR_LSD', kind='debug', func=plot_polar_lsd)

# add to definitions
definitions += [polar_continuum, polar_results, polar_stokes_i, polar_lsd]


# =============================================================================
# Define tool functions
# =============================================================================
def plot_logstats_bar(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    started = kwargs['started']
    passed = kwargs['passed']
    ended = kwargs['ended']
    urecipes = kwargs['urecipes']
    # make arrays
    x = np.arange(0, len(urecipes))
    # ------------------------------------------------------------------
    # set up plot
    fig, frames = graph.set_figure(plotter, nrows=1, ncols=2)
    # ------------------------------------------------------------------
    width = 0.3
    frames[0].bar(x - width, started, color='b', label='started',
                  align='center', width=width, zorder=5, alpha=0.875)
    frames[0].bar(x, passed, color='r', label='passed QC',
                  align='center', width=width, zorder=5, alpha=0.875)
    frames[0].bar(x + width, ended, color='g', label='finished',
                  align='center', width=width, zorder=5, alpha=0.875)
    frames[0].set_xticks(x, minor=False)
    frames[0].set_xticklabels(urecipes, rotation=90)
    frames[0].legend(loc=0)
    frames[0].set_ylabel('Number of recipes')
    add_grid(frames[0])
    # ------------------------------------------------------------------
    width = 0.4
    frames[1].bar(x - width / 2, 100 * (started - passed) / started,
                  color='r', label='failed QC', align='center',
                  width=width, zorder=5, alpha=0.875)
    frames[1].bar(x + width / 2, 100 * (started - ended) / started,
                  color='g', label='unfinished (error)', align='center',
                  width=width, zorder=5, alpha=0.875)
    frames[1].set_xticks(x)
    frames[1].set_xticklabels(urecipes, rotation=90)
    frames[1].legend(loc=0)
    frames[1].set_ylabel('Percent of total recipes [%]')
    add_grid(frames[1])
    # adjust size
    fig.subplots_adjust(hspace=0, wspace=0.05, bottom=0.3, top=0.98,
                        left=0.05, right=0.99)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


logstats_bar = Graph('LOGSTATS_BAR', kind='show', func=plot_logstats_bar)

# add to definitions
definitions += [logstats_bar]


# =============================================================================
# Define other plotting functions
# =============================================================================
def plot_image(plotter, graph, kwargs):
    """
    Generic image plotter

    :param plotter:
    :param graph:
    :param kwargs:
    :return:
    """
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    image = kwargs['image']
    origin = kwargs.get('origin', 'lower')
    aspect = kwargs.get('aspect', 'auto')
    vmin = kwargs.get('vmin', None)
    vmax = kwargs.get('vmax', None)
    xlabel = kwargs.get('xlabel', None)
    ylabel = kwargs.get('ylabel', None)
    title = kwargs.get('title', None)
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # ------------------------------------------------------------------
    # add cursor
    cursor = ClickCursor(fig, frame)
    fig.canvas.mpl_connect('button_press_event', cursor.mouse_click)
    # ------------------------------------------------------------------
    # plot image
    frame.imshow(image, origin=origin, aspect=aspect, vmin=vmin,
                 vmax=vmax)
    # ------------------------------------------------------------------
    # adjust axes
    if xlabel is not None:
        frame.set_xlabel(xlabel)
    if ylabel is not None:
        frame.set_ylabel(ylabel)
    if title is not None:
        frame.set_title(title)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


def plot_plot(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # copy kwargs
    kwargs = dict(kwargs)
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = np.array(kwargs['x'])
    del kwargs['x']
    y = np.array(kwargs['y'])
    del kwargs['y']
    # ------------------------------------------------------------------
    # we don't want fiber in kwargs
    if 'fiber' in kwargs:
        del kwargs['fiber']

    # ------------------------------------------------------------------
    # get the xlabel and clean from keyword args
    xlabel = kwargs.get('xlabel', None)
    if 'xlabel' in kwargs:
        del kwargs['xlabel']
    # get the ylabel and clean from keyword args
    ylabel = kwargs.get('ylabel', None)
    if 'ylabel' in kwargs:
        del kwargs['ylabel']
    # get the title (and clean from keyword args)
    title = kwargs.get('title', None)
    if 'title' in kwargs:
        del kwargs['title']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # ------------------------------------------------------------------
    # add cursor
    cursor = ClickCursor(fig, frame)
    fig.canvas.mpl_connect('button_press_event', cursor.mouse_click)
    # ------------------------------------------------------------------
    # plot image
    frame.plot(x, y, **kwargs)
    # ------------------------------------------------------------------
    # adjust axes
    if xlabel is not None:
        frame.set_xlabel(xlabel)
    if ylabel is not None:
        frame.set_ylabel(ylabel)
    if title is not None:
        frame.set_title(title)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)


general_image = Graph('IMAGE', kind='show', func=plot_image)
general_plot = Graph('PLOT', kind='show', func=plot_plot)

# add to definitions
definitions += [general_image, general_plot]

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
