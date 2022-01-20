The apero stats file is usually run during or after a apero_processing run.

There are three modes:

- timing mode: (using --mode=timing)
- quality control mode: (using --mode=qc)
- error mode: (using --mode=error)

If the `--plog` argument is used (with the absolute path to a apero log file group)
then only the stats for that apero_processing run are used


1.1 Timing mode
^^^^^^^^^^^^^^^^^^^^^^

This mode takes all the :term:`recipe-runs` in the logger database (at this point in time) and measures
various timing stats for each recipe.

.. warning:: timing mode has to read and sort all log entries. This can take
             quite some time to get the stats of a full run of data

The stats are printed per recipe (named by the :term:`shortname`) and are as
follows:

- Mean time: the mean time for recipes of this shortname +/- the standard deviation
- Median time: the median time for recipes of this shortname +/- the standard deviation
- The range in times (minimum and maximum) for recipes of this shortname
- The number of runs (`Nruns`) of this recipe attempted
- The total time recipes of this shortname were running (end of last recipe run minus start of first recipe run)
   .. note:: The total time is only correct if all recipes of this shortname were run without interruption with no
             other recipe runs between - this is the standard apero_processing approach but may not be true if
             analysing multiple log entries

- The total cpu time the recipe of this shortname were running (the duration) note if all recipes of this shortname
  ran in a single block this should be the time taken if done on a single core
- efficiency `(total cpu time)/(total time)`, perfect efficiency would give a value equal to the number of cores used
  (however a perfect efficiency is impossible)

  .. note:: If `Nruns` is less than the number of cores the total cpu time and total time should be the same and the
            efficiency should tend towards (or be exactly 1).


As well as the stats, after all stats have printed a histogram of each recipe with over 10 recipe-runs is plotted.
This shows this distribution of timings for each shortname.


1.2 Quality control mode
^^^^^^^^^^^^^^^^^^^^^^

This mode takes all the :term:`recipe-runs` in the logger database and prints statistics on the quality control
recorded in each recipe (if present).

.. warning:: quality control mode has to read and sort all log entries. This can take
             quite some time to get the stats of a full run of data

The stats are printed per recipe (named by the :term:`shortname`) and are as
follows:

- The number passed compared to the number that finished in total
- The number failed compared to the number that finished in total
- The Mean/Median/Max/Min and criteria of failure for each quality control
- The number that were still "running" when this report was made (should be zero if not apero_processing is running)
- The number that ended successfully (i.e. did not encouter an error or exception - handled or otherwise)

As well as this for each shortname that has quality control a plot is produced. This plot should show N+1 panels,
where N is the number of quality control criteria. The top panel shows the global pass/fail/ended statistics
(taking into account all quality control criteria). The other panels show (if numeric) a value of the quality control
criteria measured for each recipe run with that shortname as a function of observation date
(from header key :term:`KW_MID_OBS_TIME`). These values should be in blue and in red (as a dashed line) compared to
a logic threshold (i.e. points above or below, depending on the criteria fail or pass).

This process is repeated for each shortname and graphs and or stats are shown if quality control criteria are available
and numeric.


1.3 Error mode
^^^^^^^^^^^^^^^^^^^^^^

The error mode takes all errors