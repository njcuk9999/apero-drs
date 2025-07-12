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

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero'
__STRNAME__ = 'apero'
__PATH__ = Path(__file__).parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
__version__ = __YAML__['DRS.VERSION']
__date__ = __YAML__['DRS.DATE']
__authors__ = __YAML__['DRS.AUTHORS']

# =============================================================================
# End of code
# =============================================================================

# =============================================================================
# End of code
# ============================================================================
