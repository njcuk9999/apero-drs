#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-03 at 10:51

@author: cook
"""


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define plotting class
# =============================================================================
class Graph:
    def __init__(self, name, kind='debug', func=None):
        self.name = name
        # set kind
        if kind in ['debug', 'summary']:
            self.kind = kind
        else:
            self.kind = None
        # set function
        self.func = func


# =============================================================================
# Define functions
# =============================================================================
def graph_test_plot_1(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    plotter.start(graph)
    # ------------------------------------------------------------------
    # get plt from plotter (for matplotlib set up)
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = kwargs['x']
    y = kwargs['y']
    colour = kwargs['colour']
    # ------------------------------------------------------------------
    # plot
    fig, frame = plt.subplots(ncols=1, nrows=1)
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
    # get plt from plotter (for matplotlib set up)
    plt = plotter.plt
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
        plt.figure()
        plt.plot(x_arr[ord_num], y_arr[ord_num], color=colour)
        plt.title('Order {0}'.format(ord_num))
        # ------------------------------------------------------------------
        # wrap up using plotter
        plotter.end(graph)


# defined graphing instance
test_plot1 = Graph('TEST1', kind='debug', func=graph_test_plot_1)
test_plot2 = Graph('TEST2', kind='debug', func=graph_test_plot_1)
test_plot3 = Graph('TEST3', kind='debug', func=graph_test_plot_2)




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
