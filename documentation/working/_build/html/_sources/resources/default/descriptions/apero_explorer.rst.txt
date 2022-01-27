The apero_explorer recipe is designed as a graphical user interface (GUI) between the user and the
various databases that APERO uses. The script downloads a static copy of the SQL database,
changes are not updated or saved in real time (but can be updated/saved by selecting the
correct menu options).

Tables within the database currently accessible with the explorer are:

- calib: The calibration database
- tellu: The telluric database
- index: The file index database
- log: The logger database
- object: The object astrometric database
- lang: The text and language database

The GUI allows the user to:

- Do File operations:
    - Open a pickle file to replace the current database
    - Import a csv file to replace the current database
    - Save a pickle file of the current database
    - Export a csv file of the current database

- Edit the current database
    - Find and replace a string with another value
    - Filter rows by a certain criteria
    - Add rows and columns

- Table operations
    - refresh the current database (with updates since launching the GUI)
    - Save changes for the current database to the main database
    - Clean strings
    - Remove formatting
    - Get some information of the table formatting

.. note:: No changes will be saved unless you use the "Table>Save to Database" option

.. note:: We do not recommend changing any of the database entries without good reason
          and without talking to the developers
