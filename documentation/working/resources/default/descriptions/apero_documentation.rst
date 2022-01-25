The apero_documentation recipe allows updatings, compiling and uploading of
this documenation (via Sphinx).

One can do this for all instruments (--instruments=ALL) or for an individual
instrument (however the compile and upload will re-compile/re-upload all
local files).

If the file_definitions.py has been updated one can use the
--filedef argument to update the documentation file definitions.

If the recipes within recipe_definitions.py has been updated one can use the
--recipedef argument to update the documentation and if the sequences within
recipe_definitions.py has been updated one can use the --recipeseq argument
to update the docuementation.

The safest option is to use --filedef --recipedef --recipeseq to update all
automatically created definitions.

One can compile the html and/or latex documents by using --compile and change
between compiling html/latex/both with the --mode option.

Finally one can --upload the changes to the webserver (password will be
required for the rsync)

.. warning:: you must make sure --compile has been done before this otherwise
             you could sync a empty directory and remove all files from the
             webserver


In general one probably runs this command with all arguments.
i.e.

.. code-block::
    apero_documentation.py --filedef --recipedef --recipeseq --compile --upload --mode=html