#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 at 17:28

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings



# =============================================================================
# Define functions
# =============================================================================
def polyval(p, x):
    """
    Faster version of numpy.polyval
    From here: https://stackoverflow.com/a/32527284
    :param p:
    :param x:
    :return:
    """
    y = np.zeros(x.shape, dtype=float)
    for i, v in enumerate(p):
        y *= x
        y += v
    return y


# =============================================================================
# End of code
# =============================================================================
