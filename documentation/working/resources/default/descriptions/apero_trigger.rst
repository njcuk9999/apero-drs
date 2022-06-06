The apero trigger runs continuiously and tries to accurately reduces night data.

It requires a master night to be processed BEFORE starting.


How it works
^^^^^^^^^^^^^^^^^^

It works as follows:

    - copies files from a "live directory" into a sym-linked directory
      (the live directory is defined be --indir, the sym-lined directory
       is the raw directory defined in installation -- i.e. DRS_DATA_RAW)

    - tries to figure out what has been done previously
        - this is done in two steps

        - first step: calibrations
            - it uses the log database and the `trigger_night_calibrun.ini`
              file to work out (per obs_dir) whether at least one of  each
              recipe has been run (it counts QC failures as done)
            - if all steps are not complete it runs `apero processing` with the
              `trigger_night_calibrun.ini` run.ini file with the standard
              skips in `apero_processing`
            - apero_processing will stop if a recipe finds no runs (this is
              only true in `TRIGGER_RUN=True` mode

        - second step: science
            - this step is only done once all calibrations are deemed to be
              completed
            - it uses the log database, index database and the
              `trigger_night_scirun.ini` file to work out whether all recipes
              with science DPRTYPES have been run (per obs_dir)
            - if there aren't the same number of raw science files as recipe
              runs (in the log database) it will attempt to re-run
              `apero processing` with the `trigger_night_scirun.ini` run.ini
              file with the standard skips in `apero_processing`
            - apero_processing will stop if a recipe finds no runs (this is
              only true in `TRIGGER_RUN=True` mode


Caveats
^^^^^^^^^^^^^^

- results may not be optimal - we recommended running all nights together in
  an offline manner (after having all nights) for optimal results, for example:
    - calibrations may be sub-optimal (missing/using wrong night etc)
    - telluric correction may not be using all hot stars
    - templates may be sub-optimal
    - polar recipes cannot be produced online
- A master night must be run before running `apero_trigger.py`
- Adding files for older nights after newer nights could result in unwanted behaviour
  (especially when it comes to calibrations)
- Removing files may result in new calibrations being generated with less calibrations
  than before (apero_processing skip only works with the same number of files)
  and apero will use the most recently reduced calibration
- Once calibrations are finished for a night remove/adding calibration files will not
  re-trigger the calibration sequence (unless --reset is used)
- All obs_dir and files in the --indir will be processed, use --ignore to remove
  certain obs_dirs from the obs_dirs list