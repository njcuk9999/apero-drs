#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
func.py

Base level functions for use in config/constants/keywords only.

Created on 2019-01-21 at 12:42

@author: cook
"""


# =============================================================================
# Define functions
# =============================================================================
def copyall(self, module):
    # loop around all attributes in module
    for name in module.__all__:
        attr = getattr(module, name)
        # check that we have attribute "validate"
        if hasattr(attr, 'validate'):
            # fill dictionary with a copy (must be a copy)
            setattr(self, name, attr.copy())


# =============================================================================
# End of code
# =============================================================================
