#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-02-09 at 14:00

@author: cook
"""
import numpy as np
from astropy.table import Table


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def no_mask_table(table: Table) -> Table:
    """
    Deal with masked tables by converting them to normal tables.
    This is needed for some functions that do not work with masked tables.
    """
    # deal with non tables
    if not isinstance(table, Table):
        return table
    # loop around columns and look for "mask"
    for col in table.columns:
        if hasattr(table[col], 'mask'):
            # copy the table to remove the "mask" - they are set to NaNs
            table[col] = np.array(table[col].data)
    # return the table
    return table


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
