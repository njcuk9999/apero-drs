
.. _known_issues:

************************************************************************************
Known Issues
************************************************************************************

Currently known issues and problems with APERO.
Last updated: 2020-07-24 (NJC).

=======================================
Recipes
=======================================

Recent:

* FTELLU3 not working (2020-11-25) with RECAL_TEMPLATES
* tempaltes are not being created for all stars (SNR problem?)

Long term:

* Weird residuals left in order_profile after dark_flat (loc)
* Calibrations switch over at different points from PM to AM calibrations (should really only use "older")


Concerns:

* CFHT trigger not using apero_processing.py --> will soon be incompatable (re: merging calibrations)
* CFHT trigger not using pid to get output filenames --> checksum (will soon be incompatable)


=======================================
External
=======================================

Long term:

* can't use barycorrpy in parallel --> update astropy (version 4.1) and barycorrpy (version >0.3.1))

.. only:: html

  :ref:`Back to top <known_issues>`
