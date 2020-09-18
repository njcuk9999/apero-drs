
.. _todo:

************************************************************************************
TODO
************************************************************************************

This is the currently list of items that need to still be completed.
Last updated: 2020-05-04 (NJC).

.. note:: bullet points are not ordered

=========================================
APERO
=========================================

For all instruments / in general.

High priority:

* fix headers for having bad wave and loc keys (remove?) [NEEDS DISCUSSION]

Low priority:

* go through all summary plots and decide which plots, write figure captions, improve plots, write quality control description, decide which header keys to print
* add all functions doc strings
* write documentation

  * code to write constants/keywords
  * write doc strings
  * autodoc with sphinx once doc strings are in
  * assign people to write constant descriptions
  * add authors to constants

* newprofile.py outpaths for setup files are not correct (missing directory)
* add more debug printouts
* deal with all python warnings
* display func for all functions
* add doc strings to all functions, descriptions to all constants, review all constant min/max/dtypes
* proper SNR calculation
* add option to set template for mk_tellu and fit_tellu
* add flag for parellel / non parellel mode - can disable locking then?
* named break points
* add trigger option to drs where processing script stops when it cannot get any further with current set of files
* data separate download from DRS

    * this includes copying this data to the user data directory for adding
      things like custom masks etc - this could also be a solution to
      where to put the `object_query_list.fits` file

Later:

* CCF wrapper for weighting?
* persistence correction
* add EA mask generation from templates
* add EA template matching
* uncertainty propagation

* add `plot== 3` (all debug plots shown) and `plot==4` (all debug plots saved) modes
* move `object_query_list.fits` to `calibDB`
* co-production of e2ds and e2dsff still needed?
* write  paper
* setup instrument tool
* Windows compatibility
* add `cal_drift` recipe?


=========================================
SPIRou specific
=========================================
High priority:

* bisector for CCF (new extension in CCF outputs?)
* object database (in preprocessing?)
* polar code update
* EA masks from templates

Low priority:

* output files like CFHT (e.fits, p.fits, v.fits etc)
* finish `obj_spec_spirou` and `obj_pol_spirou` [Do not use them now]

=========================================
NIRPS specific
=========================================
High priority:

* convert/adapt cal_preprocessing
* convert/adapt cal_wave / cal_wave_master

Low priority:

* convert obj_mk_tellu
* convert obj_fit_tellu
* convert obj_mk_template
* convert cal_ccf

Later:

* T.B.D.


.. only:: html

  :ref:`Back to top <todo>`
