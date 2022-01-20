.. _deep:

************************************************************************************
APERO in depth
************************************************************************************


===========================================
The base module
===========================================

The base module contains very basic functionality and is kept at a bare
minimum, in general sub-modules and scripts in here cannot use other APERO
functionality (hence the less functionality in here the better).

===========================================
The core module
===========================================

This is where the core functionality is stored. In general all core functionality
should be instrument independent, however there is a separate sub-module specifically
for instrument dependent code (and default settings).

===========================================
The io module
===========================================

This is the input/output module. In general these should not use any functionality
from APERO and instead are modules that have independent pieces of code or use
other python modules related to the input and output of files (reading, writing etc.).

===========================================
The language module
===========================================

This module has all the functionality referring to the language database (except
the database itself which is a base module). The language functionality refers to
the use of the print codes and relating them to a specific language - i.e. no user
text should be written into the codes instead should be referred to via codes to
text in the langauge database.

===========================================
The plotting module
===========================================

All plotting functionality should be located in here and called from any recipe
when required. In theory no plotting code should be located elsewhere in APERO.

===========================================
The Recipe module
===========================================

This is where the recipes for each instrument are stored.

===========================================
The science module
===========================================

The science module contains all functionality related to astrophysics
algorithms. It is divided into sub-modules as follows: calibration
functionality ("calib"), extraction functionality ("extract"), polarimetry
functionality ("polar"), pre-processing functionality ("preprocessing"),
atmospheric correction functionality ("telluric") and radial velocity
functionality ("velocity").

.. toctree::
   :maxdepth: 1

   ../science/calib.rst
   ../science/preprocessing.rst



===========================================
The tools module
===========================================

This is where the tools are stored - their recipes and the sub-module
functionality to use them.