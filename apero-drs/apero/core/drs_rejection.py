#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO rejection "database" (csv, no SQL)


"""
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc

# fcntl is POSIX-only; on Windows we silently fall back to lock-file polling
try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - Windows fallback
    _fcntl = None

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.drs_astrometrics.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time from aperocore base
Time = base.Time
# get ParamDict
ParamDict = param_functions.ParamDict
# get exceptions / warnings
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define classes
# =============================================================================


# =============================================================================
# Define worker functions
# =============================================================================

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
