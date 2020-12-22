
.. _todo:

************************************************************************************
TODO
************************************************************************************

This is the currently list of items that need to still be completed.
Last updated: 2020-11-30 (NJC).

.. note:: bullet points are not ordered

=========================================
APERO
=========================================

For all instruments / in general.

Immediate small:

* filter calibrations [Etienne/Neil]
    * we are combining all for a night id bad ones and remove
    * error if not enough - define minimum number of calibrations required

* databases
    * IndexDB: runstring not adding?
    * apero_explorer save not working?

High priority:

* polar code update  [Neil/Eder/Chris]


Medium priority:

* filename from checksums [Neil]
* loc and wave coefficients to tables [Neil]
* add option to set template for mk_tellu and fit_tellu [Neil]
* deal with all python warnings [Neil]
* add NIPRS changes to 0.7 branch
* post processing (i.e. outputs like CADC/ESO)   [Neil/Chris]
    * option to remove all reduced / tmp files (not calib/tellu)
* DRS tests [Charles + Thomas]

Low priority:

* bisector for CCF (new extension in CCF outputs?) [Etienne/Neil]
* proper SNR calculation [Etienne/???]
* test barycorrpy against pyasl and other BERV calculators (precision) [Thomas?]
* apero_processing.py work with CANFAR [Neil/Chris + CANFAR collab]
* CCF masks from SpT/Teff (after masks are more mature)  [Etienne/Neil]
* instead of copying assets download them (clean up github)   [Neil]
* add doc strings/typing to all functions, descriptions to all constants, review all constant min/max/dtypes [Neil]
* display func for all functions  [Neil]
* add more debug printouts [Neil]
* apero_langdb.py - integrate with error/warning finding (tools.module.error.find_error.py)
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



=========================================
APERO utils and analysis
=========================================

This is a list of tasks mainly from `here <http://github.com/njcuk9999/apero-utils/projects/2>`_
Last updated: 2020-11-25 (NJC).

High priority:

* object alias gaia/2mass list [Thomas]
* Preprocessing Recipe test 1 [Charles/Thomas]
* Dark Master recipe test 1 [Charles/Thomas]
* Bad Pixel Corretion Recipe test 1 [Charles/Thomas]
* Localisation Recipe test 1 [Charles/Thomas]
* Shape Master Recipe test 1 [Charles/Thomas]
* Shape (per night) Recipe test 1 [Charles/Thomas]
* Flat/Blaze Correction test 1 [Charles/Thomas]
* Thermal Correction Recipe test 1 [Charles/Thomas]
* Master leak correction Recipe test 1 [Charles/Thomas]
* Master wavelength solution Recipe test 1 [Charles/Thomas]
* Nightly wavelength solution Recipe test 1 [Charles/Thomas]
* Extraction Recipe test 1 [Charles/Thomas]
* Extraction Recipe test 2 [Charles/Thomas]
* Leak correction Recipe test 1 [Charles/Thomas]
* Make Telluric Recipe test 1 [Charles/Thomas]
* Fit Telluric Recipe test 1 [Charles/Thomas]
* Make Template Recipe test 1 [Charles/Thomas]
* CCF Recipe test 1 [Charles/Thomas]

Lower priority:

* Check consistency of README/documentation/wiki for recipes
* BERV comparison
* Telluric templates
* PCA Components
* Timing stats
* Summary plot review / update (html/interactive)




.. only:: html

  :ref:`Back to top <todo>`
