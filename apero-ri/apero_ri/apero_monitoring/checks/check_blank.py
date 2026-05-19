#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Blank example test do not modify this.

Copy this to create your test

Created on 2023-07-03 at 14:37

@author: cook

Rules: No imports from apero-drs, apero-ri

Only apero-core imports allowed

Exception is apero_checks.core.py
"""
from typing import Tuple

from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts

# =============================================================================
# Define variables
# =============================================================================
# This must be the same as the name of the check in the CHECKS 
# dictionary in __init__.py
CHECK_NAME = 'BLANK'

# This is the human readable name of the check (for displaying in ARI)
CHECK_HUMAN_NAME = 'Blank Check'

# Define the check ('raw', 'red')
CHECK_TYPE = 'raw'

# Define instruments this test is valid for
INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA', 'SPIP', 'ILOCATER']

# Construct the check object
CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)

# Set the dependencies for this check (e.g. other checks that must pass 
# before this one can be run)
CHECK.dependencies = []

# Define the description of this check (for displaying in documentation)
CHECK.description = """
This is a blank check used as an example. 
It always passes and does not perform any actual checks.
"""

# Define the what to do text for this check (for displaying in documentation)
CHECK.what_to_do = """
If FALSE there is a problem. Please contact the contacts immediately.
"""

# Define contact information for this check (for displaying in documentation)
clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC)
clist1.add(contacts.LM)


CHECK.contact_list = dict()
CHECK.contact_list[None] = clist1



# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> (bool, str):
    """Function to run for this check."""
    # This is where you would implement the logic to run the check
    # For example, you could call a function that performs the check
    # and returns the results
    
    _ = instrument, obs_dir, aparams, dbparams
    # True or False based on the check logic
    passed = True  
    # A message to display for this check (e.g. success message if passed, 
    # or an error message if failed)
    message = 'This is a blank check. Always passes.'
    
    # must return a tuple of (passed: bool, message: str)
    return passed, message


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # Define a valid example instrument
    _instrument = 'SPIROU'
    # For blank test this can be empty
    _aparams = {}
    _dbparams = {}
    # Run the check
    _obs_dir = '2021-01-01'
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict={})

    # print a report
    CHECK.report()

# =============================================================================
# End of code
# =============================================================================