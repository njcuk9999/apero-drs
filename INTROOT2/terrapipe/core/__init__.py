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
# deal with copying input keyword arguments from one main to another
copy_kwargs = drs_startup.copy_kwargs

# Exit function
end = drs_startup.exit_script

# Ending main function
end_main = drs_startup.main_end_script

# file processing message
file_processing_update = drs_startup.file_processing_update

# get the local variables
get_locals = drs_startup.get_local_variables

# get a file defintion from a filetype name
get_file_definition = drs_startup.get_file_definition

# param checking function
pcheck = drs_log.find_param

# Run __main__ function
run = drs_startup.run

# Setup function
setup = drs_startup.setup

# The logging script
wlog = drs_log.wlog


# =============================================================================
# End of code
# =============================================================================
