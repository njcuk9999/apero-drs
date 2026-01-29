#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
module init file

Created on 2024-10-16 at 10:57


@author: cook
"""
from pathlib import Path
import yaml
from importlib.metadata import version

try:
    from aperocore._version import __date__
except ImportError:
    __date__ = ''

# =============================================================================
# Define variables
# =============================================================================
__all__ = ["__version__"]

__version__ = version(__name__)
__NAME__ = 'aperocore'
__STRNAME__ = 'aperocore'
__PATH__ = Path(__file__).parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
__authors__ = __YAML__['AUTHORS']
__release__ = __YAML__['RELEASE']

# =============================================================================
# End of code
# =============================================================================
