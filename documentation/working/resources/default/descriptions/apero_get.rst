The apero_get recipe is a quick and efficient way of copying (or linking to) data from the
main data directories of apero.

apero_get allow the user to select a specific file or files based on:

- object name: (using the --objnames argument), this select only files with
  the given object name

- output file type: (using the --outtypes argument), this selects only files
  with the given output (see file definitions, i.e. :ref:`file definitions for SPIROU <spirou_file_def>`)
  (the name column) for the specific values for each file

- data types (using the --dprtypes argument), this similarly to output file type
  relates to the input file type (see pre-processing file definitions, i.e. :ref:`file definitions for SPIROU <spirou_pp_file>`)
  (the HDR[DPRTYPE] column) for the specific values for each file

- fibers - the fibers to use (i.e. for spirou some combination of AB, A, B, C)

The user can also set the output directory where files should be copied to and
whether the copied files are just symlinks or full copies of the data.

.. note:: We recommend running with --test the first time this is used to make
          sure you have the files you want (and check whether all the options worked)
