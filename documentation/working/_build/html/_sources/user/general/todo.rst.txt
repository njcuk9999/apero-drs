
.. _todo:

************************************************************************************
TODO
************************************************************************************

This is the currently list of items that need to still be completed.
Last updated: 2020-11-25 (NJC).

.. note:: bullet points are not ordered

=========================================
APERO
=========================================

For all instruments / in general.

High priority:

* calibration merge (drs processing)  [Neil]
* polar code update  [Neil/Eder/Chris]
* CCF weights adjustment (once Pia has results)  [Pia/Neil]
* tellurics templates - minimum number of files for template creation [Neil]

Medium priority:

* database import/export (append/replace) [Neil]
* filenmae from checksums [Neil]
* bisector for CCF (new extension in CCF outputs?) [Etienne/Neil]
* loc and wave coefficients to tables [Neil]
* add option to set template for mk_tellu and fit_tellu [Neil]
* proper SNR calculation [Etienne/???]
* deal with all python warnings [Neil]
* post processing (i.e. outputs like CADC/ESO)   [Neil/Chris]
* DRS tests [Charles + Thomas]
* test barycorrpy against pyasl and other BERV calculators (precision) [Thomas?]
* apero_processing.py work with CANFAR [Neil/Chris + CANFAR collab]

Low priority:

* CCF masks from SpT/Teff (after masks are more mature)  [Etienne/Neil]
* instead of copying assets download them (clean up github)   [Neil]
* add doc strings/typing to all functions, descriptions to all constants, review all constant min/max/dtypes [Neil]
* display func for all functions  [Neil]
* add more debug printouts [Neil]
* go through all summary plots and decide which plots, write figure captions, improve plots, write quality control description, decide which header keys to print [Charles/Thomas]
* write documentation [Neil/Etienne/Charles/Thomas]

  * code to write constants/keywords
  * write doc strings
  * autodoc with sphinx once doc strings are in
  * assign people to write constant descriptions
  * add authors to constants

Later:

* persistence correction [Olivia/Etienne/Neil]
* add EA mask generation from templates [???]
* add EA template matching [???]
* uncertainty propagation [???]
* add `plot== 3` (all debug plots shown) and `plot==4` (all debug plots saved) modes [Neil]
* co-production of e2ds and e2dsff still needed? [???]
* write  paper [Neil/Etienne]
* setup instrument tool [Neil/Thomas/Charles]
* Windows compatibility [Neil]


=========================================
SPIRou specific
=========================================
High priority:

* EA masks from templates [???]

Low priority:

* finish `obj_spec_spirou` and `obj_pol_spirou` (Do not use them now) [Neil]

=========================================
NIRPS specific
=========================================
High priority:

* convert/adapt cal_wave / cal_wave_master [Etienne/Neil]

Low priority:

* convert obj_mk_tellu (should just be a direct convert) [Etienne/Neil]
* convert obj_fit_tellu (should just be a direct convert) [Etienne/Neil]
* convert obj_mk_template (should just be a direct convert) [Etienne/Neil]
* convert cal_ccf (should just be a direct convert) [Etienne/Neil]

Later:

* T.B.D.


.. only:: html

  :ref:`Back to top <todo>`
