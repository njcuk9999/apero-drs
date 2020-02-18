
.. _known_issues:

************************************************************************************
Known Issues
************************************************************************************

Currently known issues and problems with APERO.
Last updated: 2020-02-07 (NJC).

=======================================
Recipes
=======================================

- s1d for FP_FP and HCONE_HCONE files does not have the updated wave solution
  as files are extracted before wave solution produced
- wave solution and loc solutions are never updated in headers once a new
  solution is present - should they be? should they be removed from headers?
- FP of fiber C is contaminating fiber A and B - Etienne has a solution, but
  far from being implemented yet
- CCF still showing problems --> due to not weighting the orders, but cannot
  do this per file as must have the same weights
- BERV file gets locked - WHY?



=======================================
External
=======================================

- can't use barycorrpy --> update astropy (version 4.0) and barycorrpy (version 0.3))

.. only:: html

  :ref:`Back to top <known_issues>`
