The processing script is the recommended way to run the reduction.
It takes a :term:`run-ini-file` which contains parameters specific to the users
needs for that processing session. Based on these run-ini-file parameters and the
raw data (stored in the :term:`DRS_DATA_RAW` directory) a set of recipes or a
:term:`recipe-sequences` will determine which recipes are run for which raw files.

The run-ini-files are an important part of the processing script and have
many options to control the processing run.

.. note:: Some of the following arguments can also be added to the command-line or python function call
          (see section 4)


Options are:

- RUN_NAME: the name of the run
- SEND_EMAIL: whether to send an email on start/finish
- EMAIL_ADDRESS: the email address to send an email to
- RUN_OBS_DIR: Whether to limit processing to a single :term:`observation-directory`
- EXCLUDE_OBS_DIRS: Whether to ignore certain observation-directories
- INCLUDE_OBS_DIRS: Whether to limit processing to a set of observation-directories
- PI_NAMES: Whether to limit processing to a single or list of PI_NAMES (must match the header key :term:`KW_PI_NAME`)
- MASTER_OBS_DIR: The :term:`observation-directory` to use as the master

                  .. note:: this should not be changed in general but does require calibrations from this night to be
                            present in the raw directory.

                  .. warning:: Currently we do not support multiple master_obs_dir and a full reduction should never mix
                               different master observation-directories
- CORES: The number of cores to use
         .. warning:: This should always be at least N-1 less than the total number of cores available
- STOP_AT_EXCEPTION: The processing code will not continue past an error and will stop
- TEST_RUN: Runs the processing script without running any recipes
            .. note:: This is highly recommended, please check that you are reducing the expected data before running
                      without TEST_RUN = False
- USE_ENGINEERING: If True engineering observation-directories (those without science observation).
                   .. note:: In general we do not recommend to reduce these nights as they may
                             reduce the quality of reduced data

- TRIGGER_RUN: For use in online reductions only

- USE_ODO_REJECTLIST: If True checks that odometer code aren't already flagged as bad files

- RECAL_TEMPLATES: If True recalculates the templates that are already present.
                   .. warning:: This should only be done when re-reducing all data for a single object.
                                Recalculating the template for only new observations will greatly affect RV precision
                                and we do not recommend doing any time series analysis with a varying template.
                   .. note:: A template hash key is available in the header of files that have used a template. If
                             unsure check that the template hash matches for all observations.

- UPDATE_OBJ_DATABASE: If True the locally stored object database is updated from online.
                       .. warning:: Do not do this unless you are re-reducing all the data. If the object database
                                    has updated parameters this could affect RV precision (as the BERV calculation may
                                    change).

- RUN_XXX: For each recipe (or recipe in a sequence) there is a :term:`shortname` associated with it. A user can
           turn on and off recipes within a sequence without having to create a new sequence.
           i.e. setting `RUN_PP = False` will turn of the `PP` recipe (apero_preprocessing) all recipe-runs in an
           apero_processing run will be skipped.

- SKIP_XXX: Similar to RUN_XXX there is a :term:`shortname` that can be skipped, if and only if the recipe-run can be
            found in the logging database (i.e. all required arguments are identical) and it has successfully completed
            in a previous apero_processing run, or when run individually

- TELLURIC_TARGETS: A filter for certain recipes that use hot star observations to only use certain hot star object names
                     (and thus only use certain observations). The default value is "All" which uses all telluric objects
                     in a pre-configured list of telluric object.

- SCIENCE_TARGETS: A filter for certain recipes that use science observations. Using this a user can only reduced data
                   for a single object name or a list of object names (separated by a comma).
                   For example if one sets `SCIENCE_TARGETS=Gl699` and had `RUN_EXTOBJ=True` only extractions of Gl699
                   would be reduced

The very last piece of information required is the sequences (or individual recipe runs) that are required.
The should be numbered id00000, id00001, id00002 etc and should only contain an individual recipe run (with all correct
arguments) or a sequence name. For sequence names see the sequences page for an instrument
(e.g. for spirou click :ref:`here <sequences_SPIROU>`).
