#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""

from .core import drs_file
from .core import drs_log
from .core import drs_recipe
from .core import drs_startup

__all__ = []

# =============================================================================
# Define functions
# =============================================================================
# Setup function
setup = drs_startup.setup

# Ending main function
end_main = drs_startup.main_end_script

# Exit function
end = drs_startup.exit_script

# The logging script
wlog = drs_log.wlog


# =============================================================================
# End of code
# =============================================================================
