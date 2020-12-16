.. _glossary:

Glossary
========


.. _glossary_constants:

Constants
===========

These are usually defined in the instruments :file:`default_config.py` and
:file:`default_constants.py` scripts and are overwritten in the :file:`user_config.ini` and
:file`user_constant.ini` files.

.. glossary::

  DRS_ROOT

    * This is the path where apero-drs was installed (via github)
    * a suggested directory is :file:`/home/user/bin/apero-drs`

  DRS_UCONFIG

    * The directory containing the users configurations files
    * default is :file:`/home/user/apero/{PROFILE}`
       
  INSTRUMENT

    * This is the instrument used at a specific telescope. Some settings are instrument specific.
    * Currently supported instruments are::
      SPIROU

  OBJ_LIST_RESOLVE_FROM_DATABASE
    * Switch (True/False) whether to resolve targets from local database

  OBJ_LIST_RESOLVE_FROM_GAIAID
    * Switch (True/False) whether to resolve targets from Gaia ID if False
      astrophysical parameters always come from the header

  OBJ_LIST_RESOLVE_FROM_GLIST
    * Switch (True/False) whether to get Gaia ID / Teff/ RV from googlesheets
      if not found in the local database

  OBJ_LIST_RESOLVE_FROM_COORDS
    * Switch (True/False) whether to get Gaia ID from RA / Dec coordinates
      (This is not generally recommended as there can be mismatches)


  PROFILE

    * This is a short descriptive name given to a specific set of installation configurations
    * Each profile contains setup files: :file:`{PROFILE}.bash.setup file`, :file:`{PROFILE}.sh.setup file`
    * Each profile contains an instrument directory for each instrument. These contain user_config.ini and user_constant.ini files for said instrument.


Keywords
===========

These are usually defined in the instruments :file:`default_keywords.py` script.
These keywords control what keys are read from fits headers and also what
keys and comments are saved to fits headers.

.. glossary::

    KW_GAIA_ID

        * This is the gaia id key from the header
        * The header value should contain a valid gaia id
        * This key is used to cross-match with the object database and with
          gaia online database to get position and velocity data precise enough
          for a good BERV correction
        * If key is missing or invalid the BERV calculation defers to the header
          values for position and velocity (may be less precise).

    KW_OBJECTNAME

        * This is the object name used from the header
        * This is the unmodified value from the fits file creation
        * It is cleaned and then added to a new header key (:term:`KW_OBJNAME`)

    KW_OBJNAME

        * This is the cleaned object name - suitable for use throughout APERO.
        * Currently it is cleaned using and instruments :term:`PseudoConst` cleaning function
          e.g. :meth:`apero.core.instruments.spirou.pseudo_const.clean_obj_name`


.. _glossary_main:

General
======== 

.. glossary::  

  DrsInputFile

    * This is a class controlling how files are defined - it comes in three
      flavors - a generic file type (:meth:`apero.core.core.drs_file.DrsInputFile`),
      a fits file type (:meth:`apero.core.core.drs_file.DrsFitsFile`) and a
      temporary numpy file type (:meth:`apero.core.core.drs_file.DrsNPYFile`)

  ds9

    * An astronomical imaging and data visualization application
    * see `ds9.si.edu <http://ds9.si.edu/site/Home.html>`_
      
  file-definitions

    * This is an instrument specific python script that defines all the
      file types for use with this instrument (raw, preprocessed, output).
    * Each file definition is a :term:`DrsInputFile` instance


  pdflatex

    * The pdf latex compiler
    * see `www.latex-project.org <https://www.latex-project.org/get/>`_

  pre-processing-coordinate-system

    * This is the standard coordinate system for pre-processed images
    * It consists of the bluest wavelength at the top right and the reddest
      order in the bottom left

  PseudoConst

    * This is an instrument specific class that has functions that cannot be
      simply defined by an integer, float or string
    * Sometimes pseudo constant methods require input and are hence dynamic
    * They are located in the instrument directory
      e.g. :meth:`apero.core.instruments.spirou.psuedo_const`
    * There is also a default psuedo constant class which all instruments
      inherit from - if no instrument is defined, or a method is not defined
      for a specific instrument it will default to this method - this is stored
      in :meth:`apero.core.instruments.default.psuedo_const`
      
      
      
      
      
      
      
      
      
      
      
      
      
      