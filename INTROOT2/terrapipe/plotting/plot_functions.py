#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-03 at 10:51

@author: cook
"""
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
        self.description = description
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
    plotter.start(graph)
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
    plotter.end(graph)


def graph_test_plot_2(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    plotter.start(graph)
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
        plotter.end(graph)


# defined graphing instance
test_plot1 = Graph('TEST1', kind='summary', func=graph_test_plot_1,
                   description='This is a test plot',
                   figsize=(10, 4), dpi=300)
test_plot2 = Graph('TEST2', kind='debug', func=graph_test_plot_1)
test_plot3 = Graph('TEST3', kind='debug', func=graph_test_plot_2)


# =============================================================================
# Define dark plotting functions
# =============================================================================





# =============================================================================
# Add to definitions
# =============================================================================
definitions = [test_plot1, test_plot2, test_plot3]


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
