#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""

from aperocore.constants import constant_functions

from aperotest.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.constants.constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict
CDict = ConstDict(__NAME__)

# set the title for output yaml files
CDict.title = CDict.yaml_title('APERO TEST', setup_program='test_setup.py',
                               version=__version__, date=__date__)


# =============================================================================
# global settings (generally don't touch these)
# =============================================================================
cgroup = 'APEROTEST.GLOBAL'
CDict.add_group(cgroup, description='global settings (generally '
                                    'don\'t touch these)')
CDict_global = ConstDict(cgroup)
CDict.add('GLOBAL', value=CDict_global, dtype=ConstDict,
          source=__NAME__, user=True,
          active=True, group=cgroup, description='')

# Yaml file
CDict_global.add('YAML_FILE', value=None, dtype=str, source=__NAME__, user=False,
          active=False, group=cgroup,
          description='Yaml file used')

# Plotting mode (0-3)
CDict_global.add('PLOTTING', value=0, dtype=int,
          source=__NAME__, user=True,
          active=True, group=cgroup, options=[0, 1, 2, 3],
          description='Plotting mode: '
                      '\n\t0: No plots'
                      '\n\t1: Only show plots '
                      '\n\t2: Only save plots to file '
                      '\n\t3: Show and save plots to file')

# Plotting types
CDict_global.add('PLOT_TYPES', value=['png', 'pdf'], dtype=list,
          source=__NAME__, user=True,
          active=True, group=cgroup,
          description='List of plot types to save (e.g. [\'png\', \'pdf\'])')

# Debug mode
CDict_global.add('DEBUG', value=False, dtype=bool,
          source=__NAME__, user=True,
          active=True, group=cgroup,
          description='Show debug messages')


# =============================================================================
# path settings (generally don't touch these)
# =============================================================================
cgroup = 'APEROTEST.PATHS'
CDict.add_group(cgroup, description='Definition of inputs related to the data')

# Define data path
CDict.add('DATA_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True,
          description='The data directory (required)')

# Define plot path
CDict.add('PLOT_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True,
          description='Plot path (required)')


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
