#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
import sqlite3
import numpy as np


# =============================================================================
# Define variables
# =============================================================================
class Database:
    '''A wrapper for an SQLite database.'''

    def __init__(self, path, verbose=False):
        '''Create an object for reading and writing to a SQLite database.

        args:
            path: the location on disk of the database.  This may be :memory: to create a temporary
                in-memory database which will not be saved when the program closes.
        '''
        self._verbose_ = verbose
        self._conn_ = sqlite3.connect(path)
        self._cursor_ = self._conn_.cursor()
        self.tables = []
        self._updateTableList_()
        return

    def _inferTable_(self, table):
        if table is None:
            assert len(self.tables) == 1, \
                "There are multiple tables in the database, so you must set 'table' to pick one."
            return self.tables[0]
        return table

    def execute(self, command):
        '''Directly execute an SQL command on the database and return any results.

        args:
            command: The SQL command to be run.

        Returns:
            The outputs of the command, if any, as a list.
        '''
        if self._verbose_:
            print("SQL INPUT: ", command)
        self._cursor_.execute(command)
        result = self._cursor_.fetchall()
        if self._verbose_:
            print("SQL OUTPUT:", result)
        return result

    def _updateTableList_(self):
        '''Reads the database for tables and updates the class members accordingly.'''
        # Get the new list of tables
        self.tables = self.execute('SELECT name from sqlite_master where type= "table"')
        self.tables = [i[0] for i in self.tables]
        return

    def addTable(self, name, fieldNames, fieldTypes):
        '''Adds a table to the database file.

        args:
            name: The name of the table to create.  This must not already be in use or a SQL keyword.
            fieldNames: The names of the fields (columns) in the table as a list of str objects.  These can't be SQL keywords.
            fieldTypes: The data types of the fields as a list.  The list can contain either SQL type specifiers or the python int, str, and float types.

        Examples:
            db.addTable('planets', ['name', 'mass', 'radius'], [str, float, "REAL"])  # "REAL" does the same thing as float
        '''
        translator = {str: "TEXT", int: "INTEGER", float: "REAL"}
        fields = []
        for n, t in zip(fieldNames, fieldTypes):
            assert type(n) is str
            if type(t) is type:
                t = translator[t]
            else:
                assert type(t) is str
            fields.append(n + ' ' + t)
        command = "CREATE TABLE {}({});".format(name, ", ".join(fields))
        self.execute(command)
        self._updateTableList_()
        return

    def deleteTable(self, name):
        '''Deletes a table from the database, erasing all contained data permenantly!

        Args:
            name: The name of the table to be deleted.  See Database.tables for a list of eligible tables.
        '''
        self.execute("DROP TABLE {}".format(name))
        self._updateTableList_()
        return

    def renameTable(self, oldName, newName):
        '''Renames a table.
        Args:
            oldName: The name of the table to be deleted.  See Database.tables for a list of eligible tables.
            newName: The new name of the table.  This must not be already taken or an SQL keyword.
        '''
        self.execute("ALTER TABLE {} RENAME TO {}".format(oldName, newName))
        return

    def get(self, columns='*', table=None, condition=None, sortBy=None, sortDescending=True, maxRows=None,
            returnArray=False):
        '''Retrieves data from the database with a variety of options.

        Args:
            columns: a string containing the comma-separated columns to retrieve from the database.  You may also
                apply basic math functions and aggregators to the columns (see examples below).  "*" retrieves
                all available columns.
            table: A str which specifies which table within the database to retrieve data from.  If there is
                only one table to pick from, this may be left as None to use it automatically.
            condition: Filter results using a SQL conditions string -- see examples, and possibly this
                useful tutorial: https://www.sqlitetutorial.net/sqlite-where/.  If None, no results will be
                filtered out.
            sortBy: A str to sort the results by, which may be a column name or simple functions thereof.  If None,
                the results are not sorted.
            sortDescending: Whether to sort the outputs ascending or descending.  This has no effect if sortBy is
                set to None.
            maxRows: The number of rows to truncate the output to.  If this is None, all matching rows are printed.
            returnAray: Whether to transform the results into a numpy array.  This works well only when the outputs
                all have the same type, so it is off by default.

        Returns:
            The requested data (if any) filtered, sorted, and truncated according to the arguments. The format is a
                list of rows containing a tuple of columns, unless returnArray is True, in which case the output is a
                numpy array.

        Examples:
            db.get()                                                  # Returns the entire table (if there is only one)
            db.get("mass / (radius*radius*radius)", sortBy="radius")  # Returns the planet density, sorted descending by radius.
            db.get(sortBy="radius", maxRows=1)                        # Returns the full row of the largest planet.
            db.get(condition="mass > 1 and radius > 1")               # Returns all planets of sufficient mass and radius.
            db.get("name", sortBy="radius", maxRows=5)                # Returns the names of the five largest planets.
        '''
        table = self._inferTable_(table)
        command = "SELECT {} from {}".format(columns, table)
        if condition is not None:
            assert type(condition) is str
            command += " WHERE {} ".format(condition)
        if sortBy is not None:
            command += " ORDER BY {} ".format(sortBy)
            if sortDescending:
                command += "DESC"
            else:
                command += "ASC"
        if maxRows is not None:
            assert type(maxRows) is int
            command += " LIMIT {}".format(maxRows)
        result = self.execute(command)
        if returnArray:
            return np.asarray(result)
        return result

    def addRow(self, values, table=None, columns="*"):
        '''Adds a row to the specified tables with the given values.
        Args:
            values: an iterable of the values to fill into the new row.
            table: A str which specifies which table within the database to retrieve data from.  If there is
                only one table to pick from, this may be left as None to use it automatically.
            columns: If you only want to initialize some of the columns, you may list them here.  Otherwise,
                '*' indicates that all columns will be initialized.
        '''
        table = self._inferTable_(table)
        values = [str(i) if type(i) is not str else '"' + i + '"' for i in values]
        if columns == '*':
            columns = ''
        else:
            columns = "(" + ", ".join(columns) + ")"
        command = "INSERT INTO {}{} VALUES({})".format(table, columns, ', '.join(values))
        self.execute(command)
        return

    def set(self, columns, values, condition, table=None):
        '''Changes the data in existing rows.

        Args:
            columns: The names of the columns to be changed, as a list of strings.  If there is only one
                column to change, it can just be a string.
            values: The values to set the columns to as a list.  This must be the same length as columns,
                and can consist either of a str, float or int.  Alternatively, a bytestring can be given
                to set the value to the result of a SQL statement given by the bytestring.  If there is only
                one value, putting in a list is optional.
            condition: An SQL condition string to identify the rows to be modified.  This may be set to None
                to apply the modification to all rows.
​
        Examples:
            db.set('mass', 1., 'name="HD 80606 b"')               # Sets the mass of a particular row identified by name.
            db.set('counts', b'counts+1', None)                   # Increments the value of 'counts' for all rows
            db.set(['mass', 'radius'], [b'null', b'null'], None)  # Resets all mass and radius values to null
        '''
        if type(columns) is str:
            columns = [columns]
            if type(values) is not list:
                values = [values]
        table = self._inferTable_(table)
        setStr = []
        assert len(columns) == len(values)
        for c, v in zip(columns, values):
            assert type(c) is str, "The column to set must be a string."
            if type(v) is bytes:
                setStr.append(c + " = " + v.decode("utf-8"))
            elif type(v) is str:
                setStr.append(c + ' = "' + v + '"')
            else:
                setStr.append(c + " = " + str(v))
        command = "UPDATE {} SET {}".format(table, ", ".join(setStr))
        if condition is not None:
            command += " WHERE {}".format(condition)
        self.execute(command)
        return

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main code
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
