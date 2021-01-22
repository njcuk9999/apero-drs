
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

Current known Issues/ small immediate tasks:

* 0.6.132 log.fits flat get A,B,C,AB,A,B,C entries (PLOTDIR different)?? not seen in 0.7
* need to check databases exist when resseting tmp/red etc - may not exist and then crashes [Neil]
* need to deal with installing mysql-connector-python and sqlalchemy [Neil]
* processing - need to id polar files (distinguish from spectro files) [Neil/Chris]
* file outputs - need to check all files [Neil]
    * primary header only - other headers should be minimal [Neil]
    * no image / table in primary extension (affects reading/writing) [Neil]
* EA pre-processing code for cosmics [Etienne/Neil]
* review comsic extraction code changes by EA [Etienne/Neil]
* raw index should check last modified and update if new


High priority:

* polar code update  [Neil/Eder/Chris]

Medium priority:

* add NIPRS changes to 0.7 branch
* DRS tests [Charles + Thomas]

Low priority:

* bisector for CCF (new extension in CCF outputs?) [Etienne/Neil]
* proper SNR calculation [Etienne/???]
* test barycorrpy against pyasl and other BERV calculators (precision) [Thomas?]
* apero_processing.py work with CANFAR [Neil/Chris + CANFAR collab]
* CCF masks from SpT/Teff (after masks are more mature)  [Etienne/Neil]
* instead of copying assets download them (clean up github)   [Neil]
* add doc strings/typing to all functions, descriptions to all constants, review all constant min/max/dtypes [Neil]
* apero_langdb.py - integrate with error/warning finding (tools.module.error.find_error.py)
* go through all summary plots and decide which plots, write figure captions, improve plots, write quality control description, decide which header keys to print [Charles/Thomas]
* write documentation [Neil/Etienne/Charles/Thomas]

  * code to write constants/keywords
  * write doc strings
  * autodoc with sphinx once doc strings are in
  * assign people to write constant descriptions
  * add authors to constants

* write paper [Neil/Etienne]

Coding only tasks:

* deal with all python warnings [Neil]
* display func for all functions  [Neil]
* add more debug printouts [Neil]
* code to find unused functions/constants [Neil]
* setup instrument tool [Neil/Thomas/Charles]
* Windows compatibility [Neil]

Later:

* persistence correction [Olivia/Etienne/Neil]
* add EA mask generation from templates [???]
* add EA template matching [???]
* uncertainty propagation [???]
* co-production of e2ds and e2dsff still needed? [???]


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
* push 0.6 code to 0.7 [Neil]
* cut at Y=2880 norders=46
    * problem with localisation (coefficient consistency) [Etienne/Neil]

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
