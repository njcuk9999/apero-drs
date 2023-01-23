The apero_database recipe gives some ways to manage the local SQL/MySQL databases and tables.


The options are:

- kill all database operations (--kill): Rarely the database completely
  freezes the --kill option should free this up if this is not possible use
  the apero_database_kill recipe.

- update object database (--objdb): Use the online google sheet to update the
  local object database

  .. note:: This requires an internet connection

- update (--update) the calibration, telluric, log and index database using the files on
  disk in all the current apero profile data directories (raw/tmp/red/calib/tellu)

- import (--importdb) a csv file into either the calibration, telluric, index, log or object database

  .. note:: Columns must conform with current database definitions

  .. note:: You must also give the --csv argument with the absolute path to the csv file

  .. note:: The language database can also be imported but this is not recommended

  .. note:: use the --join option to decide how to add the database (replace removes current database,
            append adds the csv contents to the end)

- export (--exportdb) a csv file for the calibration, telluric, index, log or object database.

  .. note:: You must also give the --csv argument with the absolute path to the csv file

  .. note:: The language database can also be imported but this is not recommended

- manage all apero tables i.e. delete (--delete) a database using a GUI to select
  which tables (across all APERO profiles)

  .. warning:: Only remove databases you are sure are not being used. This is not
               backed up
