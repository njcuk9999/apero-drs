#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from pathlib import Path
import yaml
from importlib.metadata import version

try:
    from apero._version import __date__
except ImportError:
    __date__ = ''

# =============================================================================
# Define variables
# =============================================================================
__all__ = ["__version__"]

__version__ = version(__name__)


__NAME__ = 'apero'
__STRNAME__ = 'apero'
__PATH__ = Path(__file__).parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
__authors__ = __YAML__['DRS.AUTHORS']
__release__ = __YAML__['DRS.RELEASE']

# =============================================================================
# End of code
# =============================================================================

# =============================================================================
# End of code
# ============================================================================
