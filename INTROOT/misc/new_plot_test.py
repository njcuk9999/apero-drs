#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 13:38

@author: cook
"""
import matplotlib
from time import sleep
import numpy as np


# =============================================================================
# Define variables
# =============================================================================

# Plot modes = 0, 1, 2
#     0:  plot to file (default) using Agg
#     1:  plot interactively - (i.e. use plt.ion() )
#     2:  plot and stop the flow (i.e. using plt.show() )
PLOT_MODE = 0
# interactive mode: if 0 PLOT_MODE = 0
INT_MODE = 1
# Available backends in order of preference
GUI_ENV = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg', 'Agg']
# initial plt import is None (done in setup plotting)
plt = None
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def setup_plotting(params):
    global plt

    # deal with interactiveness
    if params['DRS_INTERACTIVE'] == 0:
        params['DRS_PLOT'] = 0

    # deal with the matplotlib backend
    if params['DRS_PLOT'] == 0:
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        #from matplotlib.patches import Rectangle
        #from mpl_toolkits.axes_grid1 import make_axes_locatable
    elif params['DRS_PLOT'] > 0:
        gui = None
        for gui in GUI_ENV:
            # noinspection PyBroadException
            try:
                matplotlib.use(gui, warn=False, force=True)
                import matplotlib.pyplot as plt
                from matplotlib.patches import Rectangle
                from mpl_toolkits.axes_grid1 import make_axes_locatable
                break
            except Exception as e:
                continue
        print('Using backend = {0}'.format(gui))

    # deal with interactiveness
    if params['DRS_PLOT'] == 0:
        plt.ioff()
    elif params['DRS_PLOT'] == 1:
        plt.ion()
    elif params['DRS_PLOT'] == 2:
        plt.ioff()

    # deal with backend still being MacOSX
    if matplotlib.get_backend() == 'MacOSX':
        print('OSX Error: Matplotlib MacOSX backend not supported and '
              'Qt5Agg/Qt4Agg/GTKAgg/TKAgg/WXAgg/Agg not available')

    # deal with plt not set
    if plt is None:
        raise ValueError('Cannot plot')


def plot_wrapper(params, target, **kwargs):

    kwargs['params'] = params
    # if we cannot plot continue
    if plt is None:
        return None
    # if we are in mode 1 need to use multi-process
    elif params['DRS_PLOT'] == 1:
        outname = target(**kwargs)
        plt.pause(0.1)
    elif params['DRS_PLOT'] == 2:
        outname = target(**kwargs)
        plt.show()
        plt.close()
    else:
        outname = target(**kwargs)
        plt.savefig(outname)
        plt.close()


def test_plot(params, x, y, power):
    fig, frame = plt.subplots(ncols=1, nrows=1)
    frame.scatter(x, y, label=power)
    frame.legend(loc=0)
    plt.show()
    return 'test_plot.png'


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'

    params = dict()
    params['DRS_PLOT'] = PLOT_MODE
    params['DRS_INTERACTIVE'] = INT_MODE

    # set up plotting
    setup_plotting(params)

    # test plot using the plot wrapper
    # should plot every 500 iterations
    it = 1
    x = np.arange(-30, 31)
    while it < 10000:
        print('Iteration {0}'.format(it))
        power = it // 500
        if it % 500 == 0:
            plot_wrapper(params, test_plot, x=x, y=x**it, power=it)
        it += 1
        sleep(0.005)


# =============================================================================
# End of code
# =============================================================================
