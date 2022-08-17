The apero_reset recipe resets all (or some) of the data directories defined by the user

.. warning:: Be very careful using this recipe, you can delete a lot of data very quickly
             There is no backup generated once apero_reset has been run.

For a normal run no arguments are required.

The reset recipe will guide you through all the data directories that can be reset and ask
whether you want to reset the directores. You must type "yes" to reset a directory.

If an directory is already empty it will be skipped.

The data directories that can be reset are as follows:

1. Assets directory

    This resets the :term:`DRS_DATA_ASSETS` directory (removes all files, and all databases)

2. Tmp directory

    This resets the :term:`DRS_DATA_WORKING` directory (removes all files) and the index database
    with :term:`block_kind` = "tmp"

3. Reduced directory

    This resets the :term:`DRS_DATA_REDUC` directory (removes all files) and the index database
    with :term:`block_kind` = "red"

4. Calibration directory

    This resets the :term:`DRS_CALIB_DB` directory (removes all files and copies in default ones) and
    resets the calibration database to its default state

5. Telluric directory

    This resets the :term:`DRS_TELLU_DB` directory (removes all files and copies in default ones) and
    resets the telluric database to its default state

6. Log directory

    This reset the :term:`DRS_DATA_MSG` directory (removes all files) and resets the log database.

    .. note:: After this is done, SKIP_XXX in the :term:`run-ini-files` does not skip files even if
              they are still on disk

7. Run directory

    This resets the :term:`DRS_DATA_RUN` directory (removes all files and copies in all default ones)

8. Out directory

    This resets the :term:`DRS_DATA_OUT` directory (removes all files) and the index database
    with :term:`block_kind` = "out"


.. note:: You can use the `--warn=False` argument to avoid having to type "yes". `--warn=False` will reset everything
          without any warning (not recommended)