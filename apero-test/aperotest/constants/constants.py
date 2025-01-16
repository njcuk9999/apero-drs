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
cgroup = 'GLOBAL'
CDict.add_group(cgroup, description='global settings (generally '
                                    'don\'t touch these)',
                source=__NAME__, user=True, active=True)

# Yaml file
CDict.add('YAML_FILE', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup, not_none=True,
                 cmd_arg='yamlfile',
                 cmd_kwargs=dict(nargs='?', type=str, default=None,
                                 action='store'),
                 description='Yaml file used')

# Plotting mode (0-3)
CDict.add('PLOTTING', value=0, dtype=int,
          source=__NAME__, user=True,
          active=True, group=cgroup, options=[0, 1, 2, 3],
          description='Plotting mode: '
                      '\n\t0: No plots'
                      '\n\t1: Only show plots '
                      '\n\t2: Only save plots to file '
                      '\n\t3: Show and save plots to file')

# Plotting types
CDict.add('PLOT_TYPES', value=['png', 'pdf'], dtype=list,
          source=__NAME__, user=True,
          active=True, group=cgroup,
          description='List of plot types to save (e.g. [\'png\', \'pdf\'])')

# Debug mode
CDict.add('DEBUG', value=False, dtype=bool,
          source=__NAME__, user=True,
          active=True, group=cgroup,
          description='Show debug messages')


# =============================================================================
# path settings (generally don't touch these)
# =============================================================================
cgroup = 'PATHS'
CDict.add_group(cgroup, description='Definition of inputs related to the data',
                source=__NAME__, user=True, active=True)

# Define data path
CDict.add('DATA_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True, cmd_arg='data_path',
          description='The data directory (required)')

# Define plot path
CDict.add('PLOT_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True, cmd_arg='plot_path',
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
