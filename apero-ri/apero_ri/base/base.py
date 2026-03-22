import os
import warnings
from pathlib import Path
import yaml

from importlib.metadata import version

try:
    from apero_ri._version import __date__
except ImportError:
    __date__ = ''

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero_ri'
__version__ = version(__PACKAGE__)
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)

# =============================================================================
# Get variables from info.yaml
# =============================================================================
__authors__ = __YAML__['DRS.AUTHORS']
__release__ = __YAML__['DRS.RELEASE']

# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'

# switch for no db in args
NO_DB = False

# =============================================================================
# Maps BLOCK_KIND SQL values to profile PATH_* configuration keys.
# Shared by apero_object_query and basket_funcs to keep the mapping canonical.
# =============================================================================
BLOCK_KIND: dict = {
    'raw':   'PATH_RAW',
    'tmp':   'PATH_PP',
    'calib': 'PATH_CALIB',
    'red':   'PATH_RED',
    'tellu': 'PATH_TELLU',
    'out':   'PATH_OUT',
    'lbl':   'PATH_LBL',
}