#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-24 at 11:14

@author: cook
"""
from typing import List

from matplotlib.artist import Artist
from matplotlib.legend import Legend
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerPatch
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import Transform

from aperocore.base import base
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'plotting.gen_plot.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__


# =============================================================================
# Define functions
# =============================================================================
class ArrowHandler(HandlerPatch):
    def __init__(self) -> None:
        """Initialize an arrow legend handler without arrow properties."""
        # get super call
        super().__init__()
        # set arrow props
        self.arrowprops = None

    def create_artists(
            self, legend: Legend, orig_handle: Artist,
            xdescent: float, ydescent: float, width: float,
            height: float, fontsize: float,
            trans: Transform) -> List[Artist]:
        """Create the arrow artist displayed in the legend.

        :param legend: Legend requesting the handler artists.
        :param orig_handle: Original plot artist represented in the legend.
        :param xdescent: Horizontal offset of the handler drawing area.
        :param ydescent: Vertical offset of the handler drawing area.
        :param width: Width available for the legend artist.
        :param height: Height available for the legend artist.
        :param fontsize: Legend font size in pixels.
        :param trans: Transform applied to the generated artist.
        :return: Generated arrow artists.
        """
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
