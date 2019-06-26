#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""

from .core import drs_log
from .core import drs_startup

__all__ = ['setup', 'end_main', 'end', 'wlog']

# =============================================================================
# Define functions
# =============================================================================
# Setup function
setup = drs_startup.setup

# Run __main__ function
run = drs_startup.run

# file processing message
file_processing_update = drs_startup.file_processing_update

# Ending main function
end_main = drs_startup.main_end_script

# get the local variables
get_locals = drs_startup.get_local_variables

# get a file defintion from a filetype name
get_file_definition = drs_startup.get_file_definition

# Exit function
end = drs_startup.exit_script

# The logging script
wlog = drs_log.wlog

# param checking function
pcheck = drs_log.find_param


# =============================================================================
# End of code
# =============================================================================
