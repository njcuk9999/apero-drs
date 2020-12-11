
.. _science_preprocessing:

************************************************************************************
Preprocessing functionality
************************************************************************************


.. _science_preprocessing_header_fixes:

===========================================
Raw file header fixing
===========================================

The header fixes are controlled via :meth:`apero.core.core.drs_file.fix_header`
which in turn uses the :term:`PseudoConst` method :meth:`HEADER_FIXES`.
This is defined for each instrument
(e.g. :meth:`apero.core.instruments.spirou.pseduo_const.HEADER_FIXES`)

For SPIRou the current header fixes are as follows:

* clean object name (via :meth:`apero.core.instruments.spirou.pseduo_const.clean_obj_name`)
* get target type (via :meth:`apero.core.instruments.spirou.pseduo_const.get_trg_type`)
* get mid observation time (via :meth:`apero.core.instruments.spirou.pseduo_const.get_mid_obs_time`)
* get the raw data type (via :meth:`apero.core.instruments.spirou.pseduo_const.get_dprtype`)


.. _science_preprocessing_file_identification:

===========================================
Raw file identification
===========================================

This takes a given input file and checks it against the instrument :term:`file-definitions`.
The :term:`file-definitions` give all the criteria by which an input file can be
matched as a specific drs file type.

This is done via :meth:`apero.science.preprocessing.identification.drs_infile_id`
which in turn calls :meth:`apero.core.core.drs_file.id_drs_file` and returns
a tuple - whether the file was found in the instruments definition and the
drs file type (:term:`DrsInputFile` instance)



.. _science_preprocessing_object_finding:

===========================================
Gaia ID and object finding
===========================================

We assume the header either has a Gaia ID column (defined by the :term:`KW_GAIA_ID` keyword)
or a valid object name (defined by the :term:`KW_OBJECTNAME` keyword).



  :ref:`Back to top <spirou_main>`