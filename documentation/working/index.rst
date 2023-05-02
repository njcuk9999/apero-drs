.. APERO documentation master file, created by
   sphinx-quickstart on Mon Dec 30 16:01:43 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. only:: html



.. _apero_doc_main:

******************************************
APERO Documentation
******************************************



.. _apero_doc_main_latest:

===========================================
Latest version: 0.7.282
===========================================

  APERO is a pipeline designed to reduce astrophysical observations (specifically from echelle spectrographs).
  It is the official pipeline for:

  * `SPIROU <https://www.cfht.hawaii.edu/Instruments/SPIRou/>`_ (SPectropolarimeter InfraROUge) on the Canada-France-Hawaii Telescope `CFHT <https://www.cfht.hawaii.edu/>`_.

  APERO Publications:

  * `APERO: A PipelinE to Reduce Observations -- Demonstration with SPIRou <https://arxiv.org/abs/2211.01358>`_

  APERO can also be used for:

  * NIRPS HE (Currently under construction)
  * NIRPS HA (Currently under construction)


===========================================
Overview
===========================================

.. toctree::
   :maxdepth: 2

   main/general/main_general.rst

===========================================
Instrument documentation
===========================================

.. toctree::
   :maxdepth: 3

   main/spirou/main_spirou.rst
   main/nirps_he/main_nirps_he.rst
   main/nirps_ha/main_nirps_ha.rst

===========================================
Developer documentation
===========================================

.. toctree::
   :maxdepth: 2

   main/developer/main_dev.rst



.. _apero_doc_main_other:

===========================================
Other
===========================================

*  :ref:`genindex`
*  :ref:`modindex`
*  :ref:`search`

.. toctree::
   :maxdepth: 1
   :titlesonly:

   main/misc/pythoninstallation.rst
   main/misc/glossary.rst
   main/misc/updates.rst
