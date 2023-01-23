The validation recipe confirms that the configuration settings entered during the
installation process (or updated manually in the files afterwards) are correct to at least
setup APERO.

As part of the validation recipe constants are print to the screen, similarly
to when any recipe-run is started.

.. _startup_splash:

startup splash
^^^^^^^^^^^^^^^^^


The configuration values printed are as follows:

- The Instrument, :term:`PID` and current version of APERO
- :term:`DRS_DATA_RAW`: the raw directory
- :term:`DRS_DATA_REDUC`: the reduced data directory
- :term:`DRS_DATA_WORKING`: the preprocessed data directory
- :term:`DRS_CALIB_DB`:
- :term:`DRS_TELLU_DB`:
- :term:`DRS_DATA_ASSETS`:
- :term:`DRS_DATA_MSG`:
- :term:`DRS_DATA_RUN`:
- :term:`DRS_DATA_PLOT`:
- DRS_CONFIG: a list of places parameters and constants are taken from (ordered
  in decending priority
- DATABASE: The database type (MYSQL or SQLITE3)
- DATABASE-CALIB: the address of the calibration database table
- DATABASE-TELLU: the address of the telluric database table
- DATABASE-INDEX: the address of the index database table
- DATABASE-LOG: the address of the log database table
- DATABASE-OBJECT: the address of the object database table
- DATABASE-LANG: the address of the language database table
- :term:`DRS_PRINT_LEVEL`: the standard output (console) level of logging
- :term:`DRS_LOG_LEVEL`: the log file level of logging
- :term:`DRS_PLOT`: the plotting mode (0, 1 or 2)

The splash screen should look similar to this:


.. image:: ../../../_static/images/apero_splash.png
