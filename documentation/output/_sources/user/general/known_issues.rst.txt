
.. _known_issues:

************************************************************************************
Known Issues
************************************************************************************

Currently known issues and problems with APERO.
Last updated: 2020-07-24 (NJC).

=======================================
Recipes
=======================================

* Locking of files means using >5 cores slows down a lot (fix with database)
* Weird residuals left in order_profile after dark_flat (loc)
* Calibrations switch over at different points from PM to AM calibrations (should really only use "older")
* NIRPS breaks in shape

=======================================
External
=======================================

* can't use barycorrpy --> update astropy (version 4.0) and barycorrpy (version >0.3))

.. only:: html

  :ref:`Back to top <known_issues>`
