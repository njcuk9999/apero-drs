#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 13:45

@author: cook
"""
from __future__ import division
import matplotlib

# TODO: Is there a better fix for this?
# fix for MacOSX plots freezing
gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg', 'Agg']
for gui in gui_env:
    # noinspection PyBroadException
    try:
        matplotlib.use(gui, warn=False, force=True)
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        from mpl_toolkits.axes_grid1 import make_axes_locatable
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

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def closeall():
    """
    Close all matplotlib plots currently open

    :return None:
    """
    plt.close('all')


# =============================================================================
# End of code
# =============================================================================
