
MySQL example commands
================================================================================

If using the MySQL database one can make use of direct access to the databases


To accesing mysql (i.e. from bash):

.. code-block:: bash

    mysql -h rali -u spirou -p

Get/Show to database/tables

.. code-block:: MySQL

    SHOW databases;
    USE spirou;
    SHOW tables;

Show columns in a table

.. code-block:: MySQL

    SHOW COLUMNS FROM {table name}


.. note:: `{index table name}` is the correct index database and {object table name}
          is the correct object index database from the `SHOW tables;` command above



Specific example commands:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get count of each object (in raw directory) with counts over 100

.. code-block:: MySQL

    SELECT KW_OBJNAME, COUNT(KW_OBJNAME)
    FROM {index table name}
    WHERE BLOCK_KIND="raw"
    GROUP BY KW_OBJNAME
    HAVING COUNT(KW_OBJNAME) > 100;

Get all raw files for a specific night:

.. code-block:: MySQL

    SELECT ABSPATH, OBS_DIR, FILENAME, KW_OBJNAME
    FROM {index table name}
    WHERE BLOCK_KIND="raw" AND OBS_DIR="2019-06-15";

Count the number of e2dsff entries for GL699

.. code-block:: MySQL

    SELECT COUNT(*)
    FROM {index table name}
    WHERE block_kind="red" and KW_OBJNAME="GL699" and KW_OUTPUT="EXT_E2DS_FF";

Current local object astrometric database

.. code-block:: MySQL

    SELECT OBJNAME, ORIGINAl_NAME, SP_TYPE, TEFF
    FROM {object table name};

Combining the INDEX and OBJECT database to find the number of raw files and adding the temperature and spectral
type for each from the object database

.. code-block:: MySQL

    SELECT m.KW_OBJNAME as name, COUNT(KW_OBJNAME) as counter, c.TEFF, c.SP_TYPE
    FROM {index table name} AS m
    INNER JOIN {object table name} c ON c.OBJNAME = m.KW_OBJNAME
    WHERE m.BLOCK_KIND="raw"
    GROUP BY m.KW_OBJNAME;

Combining the INDEX and OBJECT database to find the number of e2dsff AB files and adding the temperature and spectral
type for each from the object database

.. code-block:: MySQL

    SELECT m.KW_OBJNAME as name, COUNT(KW_OBJNAME) as counter, c.TEFF, c.SP_TYPE
    FROM {index table name} AS m
    INNER JOIN {object table name} AS c ON c.OBJNAME = m.KW_OBJNAME
    WHERE m.BLOCK_KIND="red" AND m.KW_OUTPUT="EXT_E2DS_FF" AND m.KW_FIBER="AB"
    GROUP BY m.KW_OBJNAME;
