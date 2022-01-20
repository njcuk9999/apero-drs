The precheck recipe allows the user to check the current raw data stored in the
:term:`DRS_DATA_RAW` directory. These checks are split into two parts a
file check and a object check. The checks are based on a supplied :term:`run-ini-file`
which controls which recipes are and are not being used for a specific apero_processing
run.

The file checks are as follows:

1. The number of calibrations in each :term:`observation-directory` and whether
   this meets the minimum number of calibrations required for the sequence
   defined in the :term:`run-ini-file`. A list of observation-directories that
   will cause problems due to missing calibrations is printed during the
   precheck recipe run.

   .. note:: Note if the observation-directory is sorted by observation night
             this will correctly flag if there are nights without calibrations
             within +/- the required time frame (controlled by :term:`MAX_CALIB_DTIME`)
             but will not be able to assess whether calibrations pass quality
             control during processing.

2. The number of science and telluric files found (note if the run-in-file has
   `USE_ENGINEERING = False` any observation-directory without science files will
   be ignored by the apero_processing recipe. The list of engineering observation-directories
   is also printed during the precheck recipe run.

The object check is done as follows:

1. The object database is checked for all valid entries (and any ignore entries)
2. All unique object names in raw files are checked against the object database
   object names (and associated aliases of each object name)
3. Any object name not in the current database and not in the current ignore list
   are printed for the user to decide whether object must be added to the
   database or left to use the header values

.. note:: Objects are only required in the database for accurate BERV calculations,
          as such only objects required precision radial velocity must be in the
          database, however we recommend all objects be added.

