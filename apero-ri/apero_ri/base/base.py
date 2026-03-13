import os
import warnings
from pathlib import Path
import yaml

from aperocore.base import base

from importlib.metadata import version

try:
    from apero._version import __date__
except ImportError:
    __date__ = ''

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'apero'
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
# do this once per drs import
__now__ = base.Time.now()
AstropyTime = base.Time
AstropyTimeDelta = base.TimeDelta
# List of author names
AUTHORS = base.AUTHORS

# Define yaml files
INSTALL_YAML = 'install.yaml'
DATABASE_YAML = 'database.yaml'
USER_ENV = base.USER_ENV
# switch for no db in args
NO_DB = False
# Define instruments (last one should be 'None')
INSTRUMENTS = __YAML__['DRS.INSTRUMENTS']