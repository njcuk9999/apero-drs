# This is the main config file
from .._package import package

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = ['VERSION', 'AUTHOR', 'RELEASE', 'DATE', 'LANGUAGE', 'INSTRUMENT']
# Constants class
Const = package.Const

# =============================================================================
# General properites
# =============================================================================
# Version
VERSION = Const('VERSION', value='0.4.016', dtype=str)

# Authors
AUTHOR = Const('AUTHOR',
               value=['N. Cook', 'F. Bouchy', 'E. Artigau', 'M. Hobson',
                      'C. Moutou', 'I. Boisse', 'E. Martioli'],
               dtype=list, dtypei=str)

# Release version
RELEASE = Const('RELEASE', value='alpha pre-release', dtype=str)

# Date
DATE = Const('DATE', value='2019-01-15', dtype=str)

# Language
LANGUAGE = Const('LANGUAGE', value='ENG', dtype=str, options=['ENG'])


# =============================================================================
# Instrument Constants
# =============================================================================
# Instrument Name
INSTRUMENT = Const('INSTRUMENT', value='None', dtype=str,
                   options=['None', 'SPIROU', 'NIRPS'])