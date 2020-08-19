#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 15:15

@author: cook
"""
from astropy.table import Table
import numpy as np
import pandas as pd
import sqlite3
import sys
from astropy.time import Time

# =============================================================================
# Define variables
# =============================================================================
__NOW__ = Time.now()


# =============================================================================
# Define classes
# =============================================================================
class DatabaseException(Exception):
    pass


class DatabaseError(DatabaseException):
    def __init__(self, message=None, errorobj=None):
        self.message = message
        self.errorobj = errorobj

    def __str__(self):
        return 'DatabaseError: {0}'.format(self.message)


class Database:
    '''A wrapper for an SQLite database.'''

    def __init__(self, path: str, verbose=False):
        '''
        Create an object for reading and writing to a SQLite database.

        :param path: the location on disk of the database.
                     This may be :memory: to create a temporary in-memory
                     database which will not be saved when the program closes.
        '''
        # store whether we want to print steps
        self._verbose_ = verbose
        # try to connect the the SQL3 database
        try:
            self._conn_ = sqlite3.connect(path)
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e)
        # try to get the SQL3 connection cursor
        try:
            self._cursor_ = self._conn_.cursor()
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e)
        # storage for tables
        self.tables = []
        # storage for database path
        self.path = path
        # update table list
        self._update_table_list_()

    def _infer_table_(self, table):
        if table is None:
            if len(self.tables) != 1:
                emsg = ('The are multiple tables in the database. You must '
                        'pick one -- table cannot be None')
                raise DatabaseError(message=emsg)
            return self.tables[0]
        return table

    def _commit(self):
        if self._verbose_:
            print('SQL: COMMIT')
        self._conn_.commit()

    def execute(self, command, return_cursor=False):
        '''
        Directly execute an SQL command on the database and return
        any results.

        :param command: The SQL command to be run.

        Returns:
            The outputs of the command, if any, as a list.
        '''
        if self._verbose_:
            print("SQL INPUT: ", command)
        cursor = self._cursor_.execute(command)
        result = self._cursor_.fetchall()
        if self._verbose_:
            print("SQL OUTPUT:", result)
        if return_cursor:
            return result, cursor
        else:
            return result

    def _update_table_list_(self):
        '''
        Reads the database for tables and updates the class members
        accordingly.
        '''
        # Get the new list of tables
        command = 'SELECT name from sqlite_master where type= "table"'
        self.tables = self.execute(command)
        self.tables = [i[0] for i in self.tables]
        self._commit()
        return

    def add_table(self, name, field_names, field_types):
        '''
        Adds a table to the database file.

        :param name: The name of the table to create. This must not already be
                     in use or a SQL keyword.
        :param field_names: The names of the fields (columns) in the table as a
                           list of str objects.  These can't be SQL keywords.
        :param field_types: The data types of the fields as a list. The list
                            can contain either SQL type specifiers or the
                            python int, str, and float types.

        Examples:
            # "REAL" does the same thing as float
            db.addTable('planets', ['name', 'mass', 'radius'],
                        [str, float, "REAL"])
        '''
        translator = {str: "TEXT", int: "INTEGER", float: "REAL"}
        fields = []
        for n, t in zip(field_names, field_types):
            assert type(n) is str
            if type(t) is type:
                t = translator[t]
            else:
                assert type(t) is str
            fields.append(n + ' ' + t)
        cargs = [name, ", ".join(fields)]
        command = "CREATE TABLE IF NOT EXISTS {}({});".format(*cargs)
        self.execute(command)
        self._update_table_list_()
        self._commit()
        return

    def delete_table(self, name):
        '''
        Deletes a table from the database, erasing all contained data
        permenantly!

        :param name: The name of the table to be deleted.
                     See Database.tables for a list of eligible tables.
        '''
        self.execute("DROP TABLE {}".format(name))
        self._update_table_list_()
        self._commit()
        return

    def rename_table(self, oldName, newName):
        '''Renames a table.


        :param oldName: The name of the table to be deleted. See Database.tables
                        for a list of eligible tables.
        :param newName: The new name of the table.  This must not be already
                        taken or an SQL keyword.
        '''
        self.execute("ALTER TABLE {} RENAME TO {}".format(oldName, newName))
        self._commit()
        return

    def get(self, columns='*', table=None, condition=None, sort_by=None,
            sort_descending=True, max_rows=None, return_array=False,
            return_table=False, return_pandas=False):
        '''
        Retrieves data from the database with a variety of options.

        :param columns: a string containing the comma-separated columns to
                     retrieve from the database.  You may also apply basic
                     math functions and aggregators to the columns
                     ( see examples below).
                     "*" retrieves all available columns.
        :param table: A str which specifies which table within the database to
                   retrieve data from.  If there is only one table to pick
                   from, this may be left as None to use it automatically.
        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.
        :param sort_by: A str to sort the results by, which may be a column name
                    or simple functions thereof.  If None, the results are not
                    sorted.
        :param sort_descending: Whether to sort the outputs ascending or
                               descending.  This has no effect if sortBy is
                               set to None.
        :param max_rows: The number of rows to truncate the output to.
                        If this is None, all matching rows are returned.
        :param returnAray: Whether to transform the results into a numpy array.
                        This works well only when the outputs all have the
                        same type, so it is off by default.

        :returns:
            The requested data (if any) filtered, sorted, and truncated
            according to the arguments. The format is a list of rows containing
            a tuple of columns, unless returnArray is True, in which case the
            output is a numpy array.

        Examples:
            # Returns the entire table (if there is only one)
            db.get()
            # Returns the planet density, sorted descending by radius.
            db.get("mass / (radius*radius*radius)", sortBy="radius")
            # Returns the full row of the largest planet.
            db.get(sortBy="radius", maxRows=1)
            # Returns all planets of sufficient mass and radius.
            db.get(condition="mass > 1 and radius > 1")
            # Returns the names of the five largest planets.
            db.get("name", sortBy="radius", maxRows=5)
        '''
        table = self._infer_table_(table)
        command = "SELECT {} from {}".format(columns, table)
        if condition is not None:
            assert type(condition) is str
            command += " WHERE {} ".format(condition)
        if sort_by is not None:
            command += " ORDER BY {} ".format(sort_by)
            if sort_descending:
                command += "DESC"
            else:
                command += "ASC"
        if max_rows is not None:
            assert type(max_rows) is int
            command += " LIMIT {}".format(max_rows)

        if return_pandas:
            return self._to_pandas(command)
        else:
            result, cursor = self.execute(command, return_cursor=True)
            if return_array:
                return np.asarray(result)
            if return_table:
                return self._to_table(cursor, result)
            return result

    def add_row(self, values, table=None, columns="*", commit=True):
        '''
        Adds a row to the specified tables with the given values.

        :param values: an iterable of the values to fill into the new row.
        :param table: A str which specifies which table within the database
                      to retrieve data from.  If there is only one table to
                      pick from, this may be left as None to use it
                      automatically.
        :param columns: If you only want to initialize some of the columns,
                        you may list them here.  Otherwise, '*' indicates that
                        all columns will be initialized.
        '''
        table = self._infer_table_(table)

        _values = []
        for i in values:
            if not isinstance(i, str):
                _values.append(str(i))
            else:
                _values.append('"{0}"'.format(i))

        if columns == '*':
            columns = ''
        else:
            columns = "(" + ", ".join(columns) + ")"
        cargs = [table, columns, ', '.join(_values)]
        command = "INSERT INTO {}{} VALUES({})".format(*cargs)
        self.execute(command)
        if commit:
            self._commit()

    def add_from_pandas(self, df, table, if_exists='append', index=False,
                        commit=True):
        """
        Use pandas to add rows to database

        :param df:
        :param table:
        :param if_exists:
        :param index:
        :return:
        """
        table = self._infer_table_(table)
        # add pandas dataframe to table
        df.to_sql(table, self._conn_, if_exists=if_exists, index=index)
        # commit change to database if requested
        if commit:
            self._commit()

    def set(self, columns, values, condition, table=None):
        '''
        Changes the data in existing rows.

        :param columns: The names of the columns to be changed, as a list of
                        strings.  If there is only one column to change, it
                        can just be a string.
        :param values: The values to set the columns to as a list. This must be
                       the same length as columns, and can consist either of a
                       str, float or int.  Alternatively, a bytestring can be
                       given to set the value to the result of a SQL statement
                       given by the bytestring.  If there is only one value,
                       putting in a list is optional.
        :param condition: An SQL condition string to identify the rows to be
                          modified.  This may be set to None to apply the
                          modification to all rows.

        Examples:
            # Sets the mass of a particular row identified by name.
            db.set('mass', 1., 'name="HD 80606 b"')
            # Increments the value of 'counts' for all rows
            db.set('counts', b'counts+1', None)
            # Resets all mass and radius values to null
            db.set(['mass', 'radius'], [b'null', b'null'], None)
        '''
        if type(columns) is str:
            columns = [columns]
            if type(values) is not list:
                values = [values]
        table = self._infer_table_(table)
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
        self._commit()
        return

    def backup(self):
        # make backup database
        backup_conn = sqlite3.connect(self.path.replace('.db', 'backup.db'))
        # copy main into backup database
        with backup_conn:
            self._conn_.backup(backup_conn)

    def lock(self):
        self.execute('BEGIN EXCLUSIVE;')

    def unlock(self):
        self.execute('COMMIT;')

    def _get_columns(self, cursor=None, table=None):
        """
        Get the columns names for a particular execute command (using cursor)
        :param cursor: return of the self._cursor_.execute command
        :return:
        """
        if cursor is None:
            table = self._infer_table_(table)
            command = "SELECT {} from {}".format('*', table)
            _, cursor = self.execute(command, return_cursor=True)

        return list(map(lambda x: x[0], cursor.description))

    def _to_table(self, cursor, result):
        # get columns
        columns = self._get_columns(cursor)
        # set up table
        table = Table()
        for it, col in enumerate(columns):
            table[col] = list(map(lambda x: x[it], result))

    def _to_pandas(self, command):
        """
        Use pandas to get sql command
        :param command:
        :return:
        """
        return pd.read_sql(command, self._conn_)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
