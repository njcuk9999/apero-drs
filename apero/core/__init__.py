#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""

from apero.core.core import drs_log
from apero.core.core import drs_startup

__all__ = ['setup', 'end_main', 'wlog']

# =============================================================================
# Define functions
# =============================================================================
# deal with copying input keyword arguments from one main to another
copy_kwargs = drs_startup.copy_kwargs

# Ending __main__ function
return_locals = drs_startup.return_locals

# Ending main function
end_main = drs_startup.main_end_script

# file processing message
file_processing_update = drs_startup.file_processing_update

# fiber processing update
fiber_processing_update = drs_startup.fiber_processing_update

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

# the group name (based on pid)
group_name = drs_startup.group_name


# =============================================================================
# End of code
# =============================================================================
