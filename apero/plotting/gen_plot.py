#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-24 at 11:14

@author: cook
"""
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerPatch
from matplotlib.patches import FancyArrowPatch

from apero.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'plotting.gen_plot.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
class ArrowHandler(HandlerPatch):
    def __init__(self):
        # get super call
        super().__init__()
        # set arrow props
        self.arrowprops = None

    def create_artists(self, legend, orig_handle, xdescent, ydescent,
                       width, height, fontsize, trans):
        arrow = FancyArrowPatch((0, 3), (25, 3), **self.arrowprops)
        arrow.set_mutation_scale(10)
        return [arrow]


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
