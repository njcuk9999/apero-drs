#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-21 18:13

@author: cook
"""
from astropy.table import Table
import numpy as np
import pandas as pd
from pathlib import Path
import sqlite3
from typing import Any, Union, List


from apero.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.base.drs_db.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time
Time = base.AstropyTime


# =============================================================================
# Define classes
# =============================================================================
class DatabaseException(Exception):
    pass


class DatabaseError(DatabaseException):
    def __init__(self, message: Union[str, None] = None, 
                 errorobj: Any = None, path: Union[str, Path] = None,
                 func_name: Union[str, None] = None):
        """
        Construct the Database Error instance
        
        :param message: str a mesage to pass / print 
        :param errorobj: the error instance (or anything else)
        :param path: str/Path the path of the database
        :param func_name: str, the function name where error occured
        """
        self.message = message
        self.errorobj = errorobj
        self.path = path
        self.func_name = func_name

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self):
        """
        Standard __str__ return (used in raising as Exception)
        :return:
        """
        emsg = 'DatabaseError: {0}'
        if self.path is not None:
            emsg += '\n\t Database path = {1}'
        if self.func_name is not None:
            emsg += '\n\t Function = {2}'
        return emsg.format(self.message, self.path, self.func_name)


class Database:
    # A wrapper for an SQLite database.
    def __init__(self, path: str, verbose: bool = False):
        """
        Create an object for reading and writing to a SQLite database.

        :param path: the location on disk of the database.
                     This may be :memory: to create a temporary in-memory
                     database which will not be saved when the program closes.
        """
        func_name = __NAME__ + 'Database.__init__()'
        # store whether we want to print steps
        self._verbose_ = verbose
        # storage for tables
        self.tables = []
        # storage for database path
        self.path = path
        # try to connect the the SQL3 database
        try:
            self._conn_ = sqlite3.connect(self.path)
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e, path=self.path,
                                func_name=func_name)
        # try to get the SQL3 connection cursor
        try:
            self._cursor_ = self._conn_.cursor()
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e, path=self.path,
                                func_name=func_name)
        # update table list
        self._update_table_list_()

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['_conn_', '_cursor_']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__:
            if key not in exclude:
                state[key] = item
        # return dictionary state
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # set function name
        func_name = __NAME__ + 'Database.__setstate__()'
        # update dict with state
        self.__dict__.update(state)
        # need to reset _conn_ and _cursor_ manually
        # try to connect the the SQL3 database
        try:
            self._conn_ = sqlite3.connect(self.path)
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e, path=self.path,
                                func_name=func_name)
        # try to get the SQL3 connection cursor
        try:
            self._cursor_ = self._conn_.cursor()
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e, path=self.path,
                                func_name=func_name)

    def __str__(self):
        """
        Standard string return
        :return: 
        """
        return 'Database[{0}]'.format(self.path)

    def __repr__(self):
        """
        Standard string representation
        :return: 
        """
        return self.__str__()

    # get / set / execute / add methods
    def execute(self, command: str, return_cursor: bool = False) -> Any:
        """
        Directly execute an SQL command on the database and return
        any results.

        :param command: str, The SQL command to be run.
        :param return_cursor: bool, whether we need the cursor return for
                              further use

        :returns: The outputs of the command, if any, as a list.
        """
        # set function name
        func_name = __NAME__ + '.Database.execute()'
        # print input if verbose
        if self._verbose_:
            print("SQL INPUT: ", command)
        # try to execute SQL command
        try:
            cursor = self._cursor_.execute(command)
            result = self._cursor_.fetchall()
        # catch all errors and pipe to database error
        except Exception as e:
            raise DatabaseError(message=str(e), errorobj=e, path=self.path,
                                func_name=func_name)
        # print output of sql command if verbose
        if self._verbose_:
            print("SQL OUTPUT:", result)
        # return the sql result and cursor if required
        if return_cursor:
            return result, cursor
        # else just return the sql result
        else:
            return result

    def get(self, columns: str = '*', table: Union[None, str] = None,
            condition: Union[None, str] = None,
            sort_by: Union[None, str] = None,
            sort_descending: bool = True,
            max_rows: Union[int, None] = None, return_array: bool = False,
            return_table: bool = False, return_pandas: bool = False
            ) -> Union[tuple, pd.DataFrame, np.ndarray, Table]:
        """
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
        :param return_array: Whether to transform the results into a numpy array.
                        This works well only when the outputs all have the
                        same type, so it is off by default. Takes slightly
                        longer than default return
        :param return_table: Whether to transform the results into astropy
                             table - takes slightly longer than return_array
        :param return_pandas: Whether to transform the results into a pandas
                              table - takes slightly longer than return_array

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
        """
        # set function name
        func_name = __NAME__ + '.Database.get()'
        # infer table name
        table = self._infer_table_(table)
        # construct basic command SELECT {COLUMNS} FROM {TABLE}
        command = "SELECT {} FROM {}".format(columns, table)
        # add WHERE statement if condition is set
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                emsg = 'get condition must be a string (for WHERE)'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)
            command += " WHERE {} ".format(condition)
        # add ORDER BY if sort_by is set
        if sort_by is not None:
            command += " ORDER BY {} ".format(sort_by)
            # sort descending of ascending depending on sort_descending input
            if sort_descending:
                command += "DESC"
            else:
                command += "ASC"
        # if max rows is set use it to set the limit
        if max_rows is not None:
            # make sure max_rows is an integer
            if not isinstance(max_rows, int):
                emsg = 'get max_rows must be an integer (for LIMIT)'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)
            # add LIMIT command
            command += " LIMIT {}".format(max_rows)
        # if a pandas table is requested use the _to_pandas method to
        #  execute the command
        if return_pandas:
            return self._to_pandas(command)
        # else we execute natively
        else:
            result, cursor = self.execute(command, return_cursor=True)
            # if numpy array requested return it as one
            if return_array:
                return np.asarray(result)
            # if astropy table request return it as one (need the cursor for
            #    columns)
            if return_table:
                return self._to_astropy_table(cursor, result)
            # else just return the result as is (a tuple)
            return result

    def set(self, columns: Union[str, List[str]],
            values: Union[str, List[str]], condition: Union[str, None] = None,
            table: Union[str, None] = None, commit: bool = True):
        """
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
        :param table: A str which specifies which table within the database to
                   retrieve data from.  If there is only one table to pick
                   from, this may be left as None to use it automatically.
        :param commit: boolean, if True will commit changes to sql database

        Examples:
            # Sets the mass of a particular row identified by name.
            db.set('mass', 1., 'name="HD 80606 b"')
            # Increments the value of 'counts' for all rows
            db.set('counts', b'counts+1', None)
            # Resets all mass and radius values to null
            db.set(['mass', 'radius'], [b'null', b'null'], None)
        """
        # set function name
        func_name = __NAME__ + '.Database.set()'
        # we expect columns to be a list but if it is a string we can just make
        #   it a one item list
        if isinstance(columns, str):
            columns = [columns]
            if not isinstance(values, list):
                values = [values]
        # infer table name
        table = self._infer_table_(table)
        # storage for set string
        set_str = []
        # make sure columns and values have the same length
        if len(columns) != len(values):
            emsg = 'The column list must be same length as value list'
            raise DatabaseError(emsg, path=self.path, func_name=func_name)
        # loop around the rows
        for it in range(len(columns)):
            # get this rows column/value
            column = columns[it]
            value = values[it]
            # column must be a string
            if not isinstance(column, str):
                emsg = 'The column to set must be a string'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)

            # deal with value being types (decode to string)
            if isinstance(value, bytes):
                sargs = [column, value.decode('utf=8')]
                set_str.append('{0} = {1}'.format(*sargs))
            elif isinstance(value, str):
                set_str.append('{0} = "{1}"'.format(column, value))
            else:
                set_str.append('{0} = {1}'.format(column,  value))
        # construct sql set command
        command = "UPDATE {} SET {}".format(table, ", ".join(set_str))
        # if we have a condition add it now
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                emsg = 'get condition must be a string (for WHERE)'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)
            # add to command
            command += " WHERE {}".format(condition)
        # execute sql command
        self.execute(command)
        # commit changes to the database (if requested)
        if commit:
            self._commit()

    def add_row(self, values: List[object], table: Union[None, str] = None,
                columns: Union[str, List[str]] = "*",
                commit: bool = True):
        """
        Adds a row to the specified tables with the given values.

        :param values: an iterable of the values to fill into the new row.
        :param table: A str which specifies which table within the database
                      to retrieve data from.  If there is only one table to
                      pick from, this may be left as None to use it
                      automatically.
        :param columns: If you only want to initialize some of the columns,
                        you may list them here.  Otherwise, '*' indicates that
                        all columns will be initialized.
        :param commit: boolean, if True will commit changes to sql database
        """
        # set function name
        _ = __NAME__ + '.Database.add_row()'
        # infer table name
        table = self._infer_table_(table)
        # push values into strings
        _values = []
        for value in values:
            # deal with value being types (decode to string)
            if isinstance(value, bytes):
                _values.append(value.decode('utf=8'))
            # if it is not a string already just pipe it to string
            elif not isinstance(value, str):
                _values.append(str(value))
            # it if is
            else:
                _values.append('"{0}"'.format(value))
        # deal with columns being all columns
        if columns == '*':
            columns = ''
        # if not join them (COLUMN1, COLUMN2, COLUMN3)
        else:
            columns = "(" + ", ".join(columns) + ")"
        # construct the command
        cargs = [table, columns, ', '.join(_values)]
        command = "INSERT INTO {}{} VALUES({})".format(*cargs)
        # execute the sql command
        self.execute(command)
        # if commit is request commit changes to SQL database
        if commit:
            self._commit()

    def add_from_pandas(self, df: pd.DataFrame, table: Union[str, None] = None,
                        if_exists: str = 'append', index: bool = False,
                        commit: bool = True):
        """
        Use pandas to add rows to database

        :param df: pandas dataframe, the pandas dataframe to add to the database
        :param table: A str which specifies which table within the database
                      to retrieve data from.  If there is only one table to
                      pick from, this may be left as None to use it
                      automatically.
        :param if_exists: how to behave if the table already exists in database
                          valid responses are 'fail', 'replace' or 'append'
                          * fail: Raise a ValueError.
                          * replace: Drop the table before inserting new values.
                          * append: Insert new values to the existing table.
        :param index: whether to include an index column in database
        :param commit: whether to commit changes to SQL database after adding
                       (or wait to another commit event)
        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database.add_from_pandas()'
        # infer table name
        table = self._infer_table_(table)
        # check if_exists criteria
        if if_exists not in ['fail', 'replace', 'append']:
            emsg = 'if_exists must be either "fail", "replace" or "append"'
            raise DatabaseError(emsg, path=self.path, func_name=func_name)
        # try to add pandas dataframe to table
        try:
            df.to_sql(table, self._conn_, if_exists=if_exists, index=index)
        except Exception as e:
            raise DatabaseError(str(e), path=self.path, errorobj=e,
                                func_name=func_name)
        # commit change to database if requested
        if commit:
            self._commit()

    # table methods
    def add_table(self, name: str, field_names: List[str],
                  field_types: List[Union[str, type]]):
        """
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
        """
        func_name = __NAME__ + '.Database.add_table()'
        # translator between python types and SQL types
        translator = {str: "TEXT", int: "INTEGER", float: "REAL"}
        # storage for fields
        fields = []
        # make sure field_names and field_types are the same size
        if len(field_names) != len(field_types):
            emsg = 'field_names and field_types must be the same length'
            raise DatabaseError(emsg, path=self.path, func_name=func_name)
        # loop around fields
        for it in range(len(field_names)):
            # get this iterations values
            fname, ftype = field_names[it], field_types[it]
            # make sure names are strings
            if not isinstance(fname, str):
                emsg = 'field_names must be strings'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)
            # deal with type
            if isinstance(ftype, type):
                # deal with wrong type
                if ftype not in translator:
                    emsg = 'field_types must be string or [int/float/str]'
                    raise DatabaseError(emsg, path=self.path,
                                        func_name=func_name)
                # set as sql type
                # noinspection PyTypeChecker
                ftype = translator[ftype]
            # else we must have a string --> so break if not
            elif not isinstance(ftype, str):
                emsg = 'field_types must be string or [int/float/str]'
                raise DatabaseError(emsg, path=self.path, func_name=func_name)
            # set type
            fields.append('{0} {1}'.format(fname, ftype))
        # now create sql command
        cargs = [name, ", ".join(fields)]
        command = "CREATE TABLE IF NOT EXISTS {}({});".format(*cargs)
        # execute command
        self.execute(command)
        # update the table list and commit
        self._update_table_list_()

    def delete_table(self, name: str):
        """
        Deletes a table from the database, erasing all contained data
        permenantly!

        :param name: The name of the table to be deleted.
                     See Database.tables for a list of eligible tables.
        """
        func_name = __NAME__ + '.Database.delete_table()'
        # make sure table is a string
        if not isinstance(name, str):
            emsg = 'table "name" must be a string'
            raise DatabaseError(emsg, path=self.path, func_name=func_name)
        # execute a sql drop table
        self.execute("DROP TABLE {}".format(name))
        # update the table list and commit
        self._update_table_list_()

    def rename_table(self, old_name: str, new_name: str):
        """
        Renames a table.

        :param old_name: The name of the table to be deleted. See
                         Database.tables for a list of eligible tables.
        :param new_name: The new name of the table. This must not be already
                         taken or an SQL keyword.
        """
        self.execute("ALTER TABLE {} RENAME TO {}".format(old_name, new_name))
        self._commit()

    # admin methods
    def backup(self):
        """
        Back up the database

        :return:
        """
        # make backup database
        backup_conn = sqlite3.connect(self.path.replace('.db', 'backup.db'))
        # copy main into backup database
        with backup_conn:
            self._conn_.backup(backup_conn)

    def lock(self):
        """
        Lock the database (until unlock or a commit is done)
        :return:
        """
        self.execute('BEGIN EXCLUSIVE;')

    def unlock(self):
        """
        Unlock the database (when a lock was done)
        :return:
        """
        self.execute('COMMIT;')

    # private methods
    def _infer_table_(self, table: Union[None, str]) -> str:
        """
        Infer the table name if table is None (if only one table)

        :param table: str or None - if None tries to infer the table name
                      (only if we have one table)
        :return:
        """
        if table is None:
            if len(self.tables) != 1:
                emsg = ('The are multiple tables in the database. You must '
                        'pick one -- table cannot be None')
                raise DatabaseError(message=emsg, path=self.path)
            return self.tables[0]
        return table

    def _update_table_list_(self):
        """
        Reads the database for tables and updates the class members
        accordingly.
        """
        # Get the new list of tables
        command = 'SELECT name from sqlite_master where type= "table"'
        # execute command
        _tables = self.execute(command)
        # the table names are the first entry in each row so get the table
        #  names from these (and update self.tables)
        self.tables = []
        for _table in _tables:
            self.tables.append(_table[0])

    def _commit(self):
        """
        Commit to the SQL database
        :return:
        """
        # if verbose then print the commit statement
        if self._verbose_:
            print('SQL: COMMIT')
        # commit
        self._conn_.commit()

    def _get_columns(self, cursor=None,
                     table: Union[str, None] = None) -> List[str]:
        """
        Get the columns names for a particular execute command (using cursor)
        :param cursor: return of the self._cursor_.execute command
        :return:
        """
        # deal with no cursor defined (get it)
        if cursor is None:
            table = self._infer_table_(table)
            command = "SELECT {} from {}".format('*', table)
            _, cursor = self.execute(command, return_cursor=True)
        # return a list of columns
        return list(map(lambda x: x[0], cursor.description))

    def _to_astropy_table(self, cursor, result) -> Table:
        """
        Convert result to astropy table

        :param cursor:
        :param result:
        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database._to_astropy_table()'
        # get columns
        columns = self._get_columns(cursor)
        # set up table
        table = Table()
        for it, col in enumerate(columns):
            try:
                table[col] = list(map(lambda x: x[it], result))
            except Exception as e:
                emsg = 'Cannot convert command to astropy table'
                emsg += '\n\t{0}: {1}'.format(type(e), e)
                raise DatabaseError(emsg, path=self.path, errorobj=e,
                                    func_name=func_name)
        # return astropy table
        return table

    def _to_pandas(self, command: str) -> pd.DataFrame:
        """
        Use pandas to get sql command
        :param command:
        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database._to_pandas()'
        # try to read sql using pandas
        try:
            df = pd.read_sql(command, self._conn_)
        except Exception as e:
            emsg = 'Could not read SQL command as pandas table'
            emsg += '\n\tCommand = {0}'.format(command)
            raise DatabaseError(emsg, path=self.path, errorobj=e,
                                func_name=func_name)
        # return dataframe
        return df


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
