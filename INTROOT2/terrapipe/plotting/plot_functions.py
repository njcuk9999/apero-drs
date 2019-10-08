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

# =============================================================================
# Define variables
# =============================================================================

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

    def set_filename(self, params, location):
        """
        Set the file name for this Graph instance
        :param params:
        :param location:
        :return:
        """
        # get pid
        pid = params['PID']
        plot_ext = params['DRS_PLOT_EXT']
        # construct filename
        filename = 'plot_{0}_{1}.{2}'.format(self.name, pid, plot_ext)
        # make filename all lowercase
        filename = filename.lower()
        # construct absolute filename
        self.filename = os.path.join(location, filename)

    def set_figure(self, plotter, **kwargs):
        # get plt from plotter (for matplotlib set up)
        plt = plotter.plt
        # get figure and frame
        fig, frames = plt.subplots(**kwargs)
        # set figure parameters
        fig.set_size_inches(self.figsize)
        fig.set_dpi(self.dpi)
        # return figure and frames
        return fig, frames


# =============================================================================
# Define test functions
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
    map = kwargs['map']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    # plot the map
    im = frame.imshow(map.astype(int), origin='lower', cmap='viridis')
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


# =============================================================================
# Define localisation plotting functions
# =============================================================================

# =============================================================================
# Define shape plotting functions
# =============================================================================

# =============================================================================
# Define flat plotting functions
# =============================================================================

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
# Add to definitions
# =============================================================================
definitions = [test_plot1, test_plot2, test_plot3,
               # dark plots
               dark_image_regions, dark_histogram,
               summary_dark_histogram, summary_dark_image_regions,
               # bad pixel map plots
               badpix_map, summary_badpix_map,
               # localisation plots

               # shape plots

               # flat plots

               # thermal plots

               # extraction plots

               # wave plots

               # telluric plots

               # velocity plots

               # polarisation plots

               ]


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
