apero_langdb is used to view, update or reload the language database.

The view option (--find) loads a GUI that provides a search of all
message codes in APERO.

Message codes have the form XX-XXX-XXXXX  where each X is a digit.

One can search a code and find all python files which have that message code
and locate some other information about that message code.

The update option (--update or --upgrade) takes the current database.xsl file
and writes various csv files and update the local language database.

Similarly the reload optoin (--reload) just updates the local language database
(with the current csv files) this option is useful if updating APEROs version.