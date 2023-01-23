The apero_listing recipe re-builds the index database.
It has various ways of doing this:

 - :term:`observation-directory` (using the --obs_dir argument) to select one observation-directory
 - :term:`block_kind` (using the --block_kind argument) to select either "raw", "tmp" or "red" data directory
 - excluding observation directories: these directories will be ignored
   (multiple observation-directories should be comma separated)
 - including observation directories: these directories will be included and everything else ignored
   (multiple observation-directories should be comma separated)
