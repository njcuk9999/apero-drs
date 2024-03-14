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
Latest version: 0.8.001
===========================================

  .. |date| date::

  Last Updated on |date|

  APERO is a pipeline designed to reduce astrophysical observations (specifically from echelle spectrographs).
  It is the official pipeline for:

  * `SPIROU <https://www.cfht.hawaii.edu/Instruments/SPIRou/>`_ (SPectropolarimeter InfraROUge) on the Canada-France-Hawaii Telescope `CFHT <https://www.cfht.hawaii.edu/>`_.

  APERO Publications:

  * `APERO: A PipelinE to Reduce Observations -- Demonstration with SPIRou <https://iopscience.iop.org/article/10.1088/1538-3873/ac9e74>`_

  APERO is also be used by:

  * `NIRPS HE <https://www.astro.umontreal.ca/nirps>`_
  * `NIRPS HA <https://www.astro.umontreal.ca/nirps>`_


  The Line-by-line code for precision radial velocity (`Artigau et al. 2022 <https://iopscience.iop.org/article/10.3847/1538-3881/ac7ce6>`_) is also integrated into APERO.

===========================================
Overview
===========================================

.. toctree::
   :maxdepth: 2

   main/general/main_general.rst

* `Known issues <https://docs.google.com/spreadsheets/d/15Gu_aY6h9Esw1uTF8Y5JCHl6m7191AviJNTPkbeTiQE/edit#gid=1844191498>`_
* `TODO <https://github.com/users/njcuk9999/projects/7/>`_

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

===========================================
UdeM
===========================================

* `APERO Reduction Interface (ARI) <http://apero.exoplanets.ca/ari/home/index.html>`_

.. toctree::
   :maxdepth: 2
   :titlesonly:

   main/misc/udem.rst