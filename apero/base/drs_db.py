#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-21 18:13

@author: cook

# import rules

only from:
    - apero.base.base
    - apero.base.drs_base

"""
import warnings

from astropy.table import Table
from contextlib import closing
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from apero.base import base
from apero.base import drs_base

# try to import mysql
# noinspection PyBroadException
try:
    import mysql.connector as mysql
except Exception as _:
    mysql = None

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
# timeout parameter in seconds
TIMEOUT = 20.0
MAXWAIT = 1000
# unique hash column
UHASH_COL = 'UHASH'


# =============================================================================
# Define classes
# =============================================================================
class DatabaseException(Exception):
    pass


class UniqueEntryException(Exception):
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
        # call super class
        super().__init__(message)

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
        emsg = drs_base.BETEXT['00-002-00028']
        if self.path is not None:
            emsg += drs_base.BETEXT['00-002-00029']
        if self.func_name is not None:
            emsg += drs_base.BETEXT['00-002-00030']
        return emsg.format(self.message, self.path, self.func_name)


class Database:
    """
    Create an object for reading and writing to a database.
    This should be abstracted for use with different database types
    sqlite or MySQL

    :param path: the location on disk of the database.
                 This may be :memory: to create a temporary in-memory
                 database which will not be saved when the program closes.
    """

    def __init__(self, *args, verbose: bool = False, **kwargs):
        # set class name
        self.classname = 'Database'
        # store whether we want to print steps
        self._verbose_ = verbose
        # storage for tables
        self.tables = []
        # storage for database path
        self.path = None
        self.backup_path = None
        # have a main table name
        self.tname = 'MAIN'

    def connection(self, host: Union[str, None] = None,
                   user: Union[str, None] = None,
                   passwd: Union[str, None] = None,
                   dbname: Union[str, None] = None,
                   connect_kind: str = 'None',
                   func: Union[str, None] = None,
                   kind: Union[str, None] = None):
        """
        Connect to the database
        Only use within with statement (so connection is closed afterwards)

        :param host: str, the host name
        :param user: str, the user name
        :param passwd: str, the password
        :param dbname: str, the database name (can be None)

        :return: return the connection
        """
        # we don't use this if connection is not implemented
        _ = host, user, passwd, dbname, connect_kind
        # log that this function must be implemented in child database
        emsg = 'Must implement "Database.connection" in child database class'
        raise NotImplementedError(emsg)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = []
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
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
        _ = __NAME__ + 'Database.__setstate__()'
        # update dict with state
        self.__dict__.update(state)

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

    def cursor(self, conn):
        """
        Attempt to retrieve a database cursor

        :return: The cursor
        """
        return conn.cursor()

    # get / set / execute / add methods
    def execute(self, command: str, fetch: bool) -> Any:
        """
        Directly execute an SQL command on the database and return
        any results.

        :param command: str, The SQL command to be run.
        :param fetch: bool, if True there is a result to fetch

        :returns: The outputs of the command, if any, as a list.
        """
        # set function name
        func_name = __NAME__ + '.Database.execute()'
        # print input if verbose
        if self._verbose_:
            print("SQL INPUT: ", command)
        # get cursor
        conargs = dict(func=func_name, kind='execute:_execute')
        conn = self.connection(**conargs)
        cursor = self.cursor(conn)
        # try to execute SQL command
        try:
            result = self._execute(cursor, command)
            # commit and close
            conn.commit()
            cursor.close()
            conn.close()
        # pass unique exception upwards
        except UniqueEntryException as e:
            # close
            cursor.close()
            conn.close()
            raise UniqueEntryException(str(e))
        # catch all errors and pipe to database error
        except Exception as e:
            # close
            cursor.close()
            conn.close()
            # log error: Error Type: Error message \n\t Command:
            ecode = '00-002-00032'
            emsg = drs_base.BETEXT[ecode]
            eargs = [type(e), str(e), command]
            exception = DatabaseError(message=emsg.format(*eargs),
                                      errorobj=e,
                                      path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # print output of sql command if verbose
        if self._verbose_:
            print("SQL OUTPUT:", result)
        # return the sql result
        return result

    def _execute(self, cursor: sqlite3.Cursor, command: str,
                 fetch: bool = True):
        """
        Dummy function to try to catch database locked errors
        (up to a max wait time)

        :param cursor: sqlite cursor (self.cursor())
        :param command: str, The SQL command to be run.
        :return:
        """
        cursor.execute(command)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        # return result
        return result

    def count(self, table: Union[None, str],
              condition: Union[None, str] = None) -> int:
        """
        Counts the number of rows in table. If condition is set
        counts just these rows

        :param table: A str which specifies which table within the database to
                   retrieve data from.  If there is only one table to pick
                   from, this may be left as None to use it automatically.
        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.

        :return: int, the count
        """
        # set function name
        func_name = __NAME__ + '.Database.get()'
        # infer table name
        table = self._infer_table_(table)
        # construct basic command SELECT {COLUMNS} FROM {TABLE}
        command = "SELECT COUNT(*) FROM {}".format(table)
        # add WHERE statement if condition is set
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                # log error: Get condition must be a string (for WHERE)
                ecode = '00-002-00031'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)

            command += " WHERE {} ".format(condition)
        # execute result
        result = self.execute(command, fetch=True)[0][0]
        # return result
        return int(result)

    def unique(self, column: str, table: Union[None, str],
               condition: Union[None, str] = None) -> np.ndarray:
        """
        Get the unique values for a column (with condition if set)

        :param column: a string containing the comma-separated columns to
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

        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database.get()'
        # infer table name
        table = self._infer_table_(table)
        # construct basic command SELECT {COLUMNS} FROM {TABLE}
        command = "SELECT DISTINCT {0} FROM {1}".format(column, table)
        # add WHERE statement if condition is set
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                # log error: Get condition must be a string (for WHERE)
                ecode = '00-002-00031'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            command += " WHERE {} ".format(condition)
        # execute result
        result = self.execute(command, fetch=True)
        # return unique result
        return np.unique(result)

    def get(self, columns: str, table: Union[None, str],
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
        command = 'SELECT {} FROM {}'.format(columns, table)
        # add WHERE statement if condition is set
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                # log error: Get condition must be a string (for WHERE)
                ecode = '00-002-00031'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
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
                # log error: Get max_rows must be an integer (for LIMIT)
                ecode = '00-002-00033'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # add LIMIT command
            command += " LIMIT {}".format(max_rows)
        # if a pandas table is requested use the _to_pandas method to
        #  execute the command
        if return_pandas:
            return self._to_pandas(command)
        # else we execute natively
        else:
            result = self.execute(command, fetch=True)
            # if numpy array requested return it as one
            if return_array:
                return np.asarray(result)
            # if astropy table request return it as one (need the cursor for
            #    columns)
            if return_table:
                return self._to_astropy_table(result)
            # else just return the result as is (a tuple)
            return result

    def set(self, columns: Union[str, List[str]], table: Union[str, None],
            values: Union[str, List[str]], condition: Union[str, None] = None,
            unique_cols: Union[List[str], None] = None):
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
        :param unique_cols: list of strings or None, if set this is columns that
                            are used to form the unique hash for specifying
                            unique rows

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
        # infer table name
        table = self._infer_table_(table)
        # deal with columns = '*'
        if columns == '*':
            columns = self.colnames('*', table=table)
        # we expect columns to be a list but if it is a string we can just make
        #   it a one item list
        if isinstance(columns, str):
            columns = [columns]
            if not isinstance(values, list):
                values = [values]
        # add the hash column
        if unique_cols is not None:
            columns, values = _hash_col(columns, values, unique_cols)
            # condition based on only on unique_col
            condition = '{0}={1}'.format(columns[-1], values[-1])
        # storage for set string
        set_str = []
        # make sure columns and values have the same length
        if len(columns) != len(values):
            # log error: The column list must be same length as the value list
            ecode = '00-002-00034'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # loop around the rows
        for it in range(len(columns)):
            # get this rows column/value
            column = columns[it]
            value = values[it]
            # column must be a string
            if not isinstance(column, str):
                # log error: The column to set must be a string
                ecode = '00-002-00035'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # deal with value
            set_str.append('{0} = {1}'.format(column, _decode_value(value)))

        # construct sql set command
        command = "UPDATE {} SET {}".format(table, ", ".join(set_str))
        # if we have a condition add it now
        if condition is not None:
            # make sure condition is a string
            if not isinstance(condition, str):
                # log error: Get condition must be a string (for WHERE)
                ecode = '00-002-00031'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # add to command
            command += " WHERE {}".format(condition)
        # execute sql command
        self.execute(command, fetch=False)

    def add_row(self, values: List[object], table: Union[None, str],
                columns: Union[str, List[str]] = "*",
                unique_cols: Union[List[str], None] = None):
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
        :param unique_cols: list of strings or None, if set this is columns that
                            are used to form the unique hash for specifying
                            unique rows

        :return: None
        """
        # set function name
        _ = __NAME__ + '.Database.add_row()'
        # copy values
        values = list(values)
        # infer table name
        table = self._infer_table_(table)
        # add the hash column
        if unique_cols is not None:
            # get the columns
            if columns == '*':
                columns = self.colnames('*', table=table)
            # add to the values
            columns, values = _hash_col(columns, values, unique_cols)
        # push values into strings
        _values = list(map(_decode_value, values))
        # deal with columns being all columns
        if columns == '*':
            columns = ''
        # if not join them (COLUMN1, COLUMN2, COLUMN3)
        elif isinstance(columns, list):
            columns = '(' + ', '.join(columns) + ')'
        else:
            if not columns.startswith('('):
                columns = '(' + columns
            if not columns.endswith(')'):
                columns = columns + ')'
        # construct the command
        cargs = [table, columns, ', '.join(_values)]
        command = "INSERT INTO {}{} VALUES({})".format(*cargs)
        # execute the sql command
        self.execute(command, fetch=False)

    def delete_rows(self, table: Union[None, str],
                    condition: Union[str, None] = None):
        """
        Delete a row from the table

        :param table: A str which specifies which table within the database
                      to retrieve data from.  If there is only one table to
                      pick from, this may be left as None to use it
                      automatically
        :param condition: An SQL condition string to identify the rows to be
                          modified.  This may be set to None to apply the
                          modification to all rows.

        :return: None removes row(s) from table
        """
        # set function name
        _ = __NAME__ + '.Database.add_row()'
        # infer table name
        table = self._infer_table_(table)
        # deal with no condition
        if condition is None:
            return
        # construct the command
        command = "DELETE FROM {} WHERE {}".format(table, condition)
        # execute the sql command
        self.execute(command, fetch=False)

    # table methods
    def add_table(self, name: str, field_names: List[str],
                  field_types: List[Union[str, type]],
                  unique_cols: Optional[List[str]] = None,
                  index_cols: Optional[List[str]] = None):
        """
        Adds a table to the database file.

        :param name: The name of the table to create. This must not already be
                     in use or a SQL keyword.
        :param field_names: The names of the fields (columns) in the table as a
                           list of str objects.  These can't be SQL keywords.
        :param field_types: The data types of the fields as a list. The list
                            can contain either SQL type specifiers or the
                            python int, str, and float types.
        :param unique_cols: list of str, the field_names that should be unique

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
        # deal with index columns
        _ = index_cols
        # make sure field_names and field_types are the same size
        if len(field_names) != len(field_types):
            # log error: field_names and field_types must be the same length
            ecode = '00-002-00036'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # loop around fields
        for it in range(len(field_names)):
            # get this iterations values
            fname, ftype = field_names[it], field_types[it]
            # make sure names are strings
            if not isinstance(fname, str):
                # log error: field_names must be strings
                ecode = '00-002-00037'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # deal with type
            if isinstance(ftype, type):
                # deal with wrong type
                if ftype not in translator:
                    # log error: field_types must be string or [int/float/str]
                    ecode = '00-002-00038'
                    emsg = drs_base.BETEXT[ecode]
                    exception = DatabaseError(emsg, path=self.path,
                                              func_name=func_name)
                    # add code to database message
                    emsg = 'E[0]: {1}'.format(ecode, emsg)
                    # log base error
                    return drs_base.base_error(ecode, emsg, 'error',
                                               exceptionname='DatabaseError',
                                               exception=exception)
                # set as sql type
                # noinspection PyTypeChecker
                ftype = translator[ftype]
            # else we must have a string --> so break if not
            elif not isinstance(ftype, str):
                # log error:field_types must be string or [int/float/str]
                ecode = '00-002-00038'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # set type
            fields.append('{0} {1}'.format(fname, ftype))
        # ---------------------------------------------------------------------
        # unique columns become a 255 hash
        if unique_cols is not None:
            extra_str = ', {0} VARCHAR(64), UNIQUE({0})'.format(UHASH_COL)
        else:
            extra_str = ''
        # ---------------------------------------------------------------------
        # now create sql command
        cargs = [name, ", ".join(fields) + extra_str]
        command = "CREATE TABLE IF NOT EXISTS {}({});".format(*cargs)
        # ---------------------------------------------------------------------
        # execute command
        self.execute(command, fetch=False)
        # update the table list
        self._update_table_list_()

    def add_unique_uhash_col(self, table: Union[str, None]):
        """
        Need a way to update the unique column (uhash) if set -
        this is because pandas removes uniqueness from the column

        :param table: str or None, the table name
        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

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
            # log error: table 'name' must be a string
            ecode = '00-002-00039'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # execute a sql drop table
        self.execute("DROP TABLE {}".format(name), fetch=False)
        # update the table list
        self._update_table_list_()

    def rename_table(self, old_name: str, new_name: str):
        """
        Renames a table.

        :param old_name: The name of the table to be deleted. See
                         Database.tables for a list of eligible tables.
        :param new_name: The new name of the table. This must not be already
                         taken or an SQL keyword.
        """
        # set function name
        _ = __NAME__ + '.Database.rename_table()'
        # execute a change in table name
        self.execute("ALTER TABLE {} RENAME TO {}".format(old_name, new_name),
                     fetch=False)

    def tname_in_db(self) -> bool:
        """
        Test for tname (table name) in the tables of this database

        :return: bool, True if tname (table name) in database, else False
        """
        if self.tname in self.tables:
            return True
        else:
            return False

    # admin methods
    def backup(self):
        """
        Back up the database

        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    def reload_from_backup(self, pconst: Any = None):
        """
        Reload database from back up the database

        :param pconst: PseudoConsts - apero.core.constants.pload() this is
                       required to get the unique columns - if unset assumes
                       there are no unique columns

        :return:
        """
        _ = pconst
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    def lock(self):
        """
        Lock the database (until unlock is done)
        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    def unlock(self):
        """
        Unlock the database (when a lock was done)
        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    # other methods
    def table_info(self,
                   table: Union[str, None]) -> Tuple[List[str], List[str]]:
        """
        Get the table information for a table name

        :param table: str, the name of the Table
        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)
        return [], []

    def colnames(self, columns: str, table: Union[str, None]) -> List[str]:
        """
        Get the column names from table (i.e. deal with * or columns separated
        by commas)

        :param columns: str, comma separate set of column names or *
        :param table: str, the name of the Table

        :return: list of strings, the column names
        """
        # get all columns names
        allcolnames, _ = self.table_info(table)
        # if user wants all columns return them all
        if columns == '*':
            # return the out put columns
            return allcolnames
        else:
            # get user columns
            user_colnames = columns.split(',')
            user_colnames = list(map(lambda x: x.strip(), user_colnames))
            # set up storage of output columns
            out_colnames = []
            # loop around all the columns in table
            for col in allcolnames:
                # if column one of the one user wants add it to return
                if col in user_colnames:
                    out_colnames.append(col)
            # return the out put columns
            return out_colnames

    def coltypes(self, columns: str, table: Union[str, None]) -> List[str]:
        """
        Get the column names from table (i.e. deal with * or columns separated
        by commas)

        :param columns: str, comma separate set of column names or *
        :param table: str, the name of the Table

        :return: list of strings, the column names
        """
        # get all columns names
        allcolnames, allcoltypes = self.table_info(table)
        # if user wants all columns return them all
        if columns == '*':
            # return the out put columns
            return allcolnames
        else:
            # get user columns
            user_colnames = columns.split(',')
            user_colnames = list(map(lambda x: x.strip(), user_colnames))
            # set up storage of output columns
            out_coltypes = []
            # loop around all the columns in table
            for it, col in enumerate(allcolnames):
                # if column one of the one user wants add it to return
                if col in user_colnames:
                    out_coltypes.append(allcoltypes[it])
            # return the out put columns
            return out_coltypes

    # private methods
    def _infer_table_(self, table: Union[None, str]) -> str:
        """
        Infer the table name if table is None (if only one table)

        :param table: str or None - if None tries to infer the table name
                      (only if we have one table)
        :return:
        """
        # set function name
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           '_infer_table_')
        # infer table name from tname
        if self.tname is not None:
            if self.tname in self.tables:
                return str(self.tname)
        # deal with no table
        if table is None:
            if len(self.tables) != 1:
                # log error: pick one -- table cannot be None
                ecode = '00-002-00041'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            return self.tables[0]
        return table

    def _update_table_list_(self):
        """
        Reads the database for tables and updates the class members
        accordingly.
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    def _to_astropy_table(self, result, table=None) -> Table:
        """
        Convert result to astropy table

        :param result:
        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database._to_astropy_table()'
        # get table name
        if table is None:
            table = self.tname
        # get columns
        columns = self.colnames('*', table=table)
        # set up table
        table = Table()
        for it, col in enumerate(columns):
            # noinspection PyBroadException
            try:
                table[col] = list(map(lambda x: x[it], result))
            except Exception as _:
                # log error: Cannot convert command to astropy table
                ecode = '00-002-00042'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
        # return astropy table
        return table

    def add_from_pandas(self, df: pd.DataFrame, table: Union[str, None],
                        if_exists: str = 'append', index: bool = False,
                        unique_cols: Union[List[str], None] = None):
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
        :param unique_cols: list of strings or None, if set this is columns that
                            are used to form the unique hash for specifying
                            unique rows

        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)

    def _to_pandas(self, command: str) -> Any:
        """
        Use pandas to get sql command
        :param command:
        :return:
        """
        emsg = 'Please abstract method with SQLiteDatabase or MySQLDatabase'
        NotImplemented(emsg)


class DatabaseColumns:
    def __init__(self, name_prefix: Optional[str] = None):
        """
        SQL database columns definition

        """
        self.names = []
        self.datatypes = []
        self.dtypes = []
        self.unique_cols = []
        self.index_cols = []
        self.name_prefix = name_prefix
        self.altnames = []
        self.comments = []

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def add(self, name: str, datatype: str, is_unique: bool = False,
            is_index: bool = False, comment: Optional[str] = None):
        """
        Add a column to the database

        :param name: str, the name of the column
        :param datatype: str, the sql data type e.g. FLOAT, REAL, INT, CHAR,
                         VARCHAR, TEXT, BLOB
        :param is_unique: bool, if True this column is flagged as unique
        :param is_index: bool, if True this column is indexed
        :param comment: str (optional), if set this is the comment associated
                        with this column

        :return: None
        """
        self.names.append(name)
        self.datatypes.append(datatype)
        self.dtypes.append(self._dtyper(datatype))
        if is_unique:
            self.unique_cols.append(name)
        if is_index:
            self.index_cols.append(name)
        self.comments.append(comment)
        if self.name_prefix is not None:
            self.altnames.append('{0}{1}'.format(self.name_prefix, name))

    def __add__(self, other: 'DatabaseColumns'):
        """
        Add one Database Column list to another

        :param other: DatabaseColumns instance to be added to self

        :return: None
        """
        new = DatabaseColumns(name_prefix=self.name_prefix)
        # add to names
        new.names = self.names + other.names
        new.datatypes = self.datatypes + other.datatypes
        new.dtypes = self.dtypes + other.dtypes
        new.unique_cols = self.unique_cols + other.unique_cols
        new.index_cols = self.index_cols + other.index_cols
        new.comments = self.comments + other.comments
        new.altnames = self.altnames + other.altnames
        # return the new
        return new

    @staticmethod
    def _dtyper(datatype):
        """
        Translate sql data types into python data types
        """
        if datatype == 'INT':
            return int
        if datatype == 'FLOAT':
            return float
        if datatype in ['TEXT', 'BLOB']:
            return str
        if datatype.startswith('VARCHAR'):
            return str
        # default is to cast to string
        return str


class SQLiteDatabase(Database):
    # A wrapper for an SQLite database.
    def __init__(self, path: str, verbose: bool = False):
        """
        Create an object for reading and writing to a SQLite database.

        :param path: the location on disk of the database.
                     This may be :memory: to create a temporary in-memory
                     database which will not be saved when the program closes.
        """
        # set function name
        func_name = __NAME__ + 'SQLiteDatabase.__init__()'
        # call to super class
        super().__init__(verbose=verbose)
        # storage for database path
        self.host = None
        self.user = None
        self.path = path
        self.backup_path = ''
        self.passwd = None
        self.dbname = None
        self.tname = 'MAIN'
        # update table list
        self._update_table_list_()

    def connection(self, host: Union[str, None] = None,
                   user: Union[str, None] = None,
                   passwd: Union[str, None] = None,
                   dbname: Union[str, None] = None,
                   connect_kind: str = 'sqlite',
                   func: Union[str, None] = None,
                   kind: Union[str, None] = None):
        """
        Connect to the sqlite database
        Only use within with statement (so connection is closed afterwards)

        :param host: str, the host name
        :param user: str, the user name
        :param passwd: str, the password
        :param dbname: str, the database name (can be None)

        :return: return the sqlite connection
        """
        # set function name
        func_name = '{0}.{1}.{2}()'.format(__NAME__, 'SQLiteDatabase',
                                           'connection')
        # deal with no host / user / password / database name
        _ = host, user, passwd, dbname
        # try to connect
        try:
            if connect_kind == 'sqlite':
                return sqlite3.connect(self.path, timeout=TIMEOUT)
        except Exception as e:
            # log error: {0}: {1} \n\t Command: {2} \n\t Function: {3}
            ecode = '00-002-00043'
            emsg = drs_base.BETEXT[ecode]
            eargs = [type(e), str(e), func_name]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                exceptionname='DatabaseError',
                                exception=exception)

    def __str__(self):
        """
        Standard string return
        :return: 
        """
        return 'SQLiteDatabase[{0}]'.format(self.path)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = []
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
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
        func_name = __NAME__ + 'SQLiteDatabase.__setstate__()'
        # update dict with state
        self.__dict__.update(state)
        # update table list
        self._update_table_list_()

    # table methods
    def add_table(self, name: str, field_names: List[str],
                  field_types: List[Union[str, type]],
                  unique_cols: Optional[List[str]] = None,
                  index_cols: Optional[List[str]] = None):
        """
        Adds a table to the database file.

        :param name: The name of the table to create. This must not already be
                     in use or a SQL keyword.
        :param field_names: The names of the fields (columns) in the table as a
                           list of str objects.  These can't be SQL keywords.
        :param field_types: The data types of the fields as a list. The list
                            can contain either SQL type specifiers or the
                            python int, str, and float types.
        :param unique_cols: list of str, the field_names that should be unique

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
        # deal with index columns
        if index_cols is None:
            index_cols = []
        # make sure field_names and field_types are the same size
        if len(field_names) != len(field_types):
            # log error: field_names and field_types must be the same length
            ecode = '00-002-00036'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)

        # loop around fields
        for it in range(len(field_names)):
            # get this iterations values
            fname, ftype = field_names[it], field_types[it]
            # make sure names are strings
            if not isinstance(fname, str):
                # log error: field_names must be strings
                ecode = '00-002-00037'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # deal with type
            if isinstance(ftype, type):
                # deal with wrong type
                if ftype not in translator:
                    # log error: field_types must be string or [int/float/str]
                    ecode = '00-002-00038'
                    emsg = drs_base.BETEXT[ecode]
                    exception = DatabaseError(emsg, path=self.path,
                                              func_name=func_name)
                    # add code to database message
                    emsg = 'E[0]: {1}'.format(ecode, emsg)
                    # log base error
                    return drs_base.base_error(ecode, emsg, 'error',
                                               exceptionname='DatabaseError',
                                               exception=exception)
                # set as sql type
                # noinspection PyTypeChecker
                ftype = translator[ftype]
            # else we must have a string --> so break if not
            elif not isinstance(ftype, str):
                # log error:field_types must be string or [int/float/str]
                ecode = '00-002-00038'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # set type
            fields.append('{0} {1}'.format(fname, ftype))
        # ---------------------------------------------------------------------
        # unique columns become a 255 hash
        if unique_cols is not None:
            # flag we found uhash col
            found_ucol = False
            # loop around fields
            for it, field in enumerate(fields):
                # if we have the UHASH column replace it
                if UHASH_COL in field:
                    fields[it] = field + ' UNIQUE'
                    found_ucol = True
                    break
            # deal with requiring new uhash column
            if not found_ucol:
                fields.append('{0} VARCHAR(64) UNIQUE'.format(UHASH_COL))
        # ---------------------------------------------------------------------
        # deal with indexes - extra commands for sqlite
        extra_commands = []
        for index_col in index_cols:
            if index_col in field_names:
                index_args = [index_col, name]
                index_cmd = 'CREATE INDEX idx_{0} ON {1} ({0});'
                extra_commands += [index_cmd.format(*index_args)]
        # ---------------------------------------------------------------------
        # now create sql command
        cargs = [name, ", ".join(fields)]
        command = "CREATE TABLE IF NOT EXISTS {0}({1});".format(*cargs)
        # ---------------------------------------------------------------------
        # execute command
        self.execute(command, fetch=False)
        # ---------------------------------------------------------------------
        # execute extra commands
        for extra_command in extra_commands:
            self.execute(extra_command, fetch=False)
        # update the table list
        self._update_table_list_()

    def add_unique_uhash_col(self, table: Union[str, None]):
        """
        Need a way to update the unique column (uhash) if set -
        this is because pandas removes uniqueness from the column

        In sqlite there is no command to do this so we have to create a new
        table with the correct types and then copy table across

        :param table: str or None, the table name
        :return:
        """
        # get current column names and column types
        colnames, coltypes = self.table_info(table)
        # deal with not having uhash column - return
        if UHASH_COL not in colnames:
            return
        # 1. create a temporary table to store these
        tmp_name = table + '_tmp'
        self.add_table(tmp_name, colnames, coltypes, unique_cols=[UHASH_COL])
        # 2. move all data from old table to new temporary table
        command = 'INSERT INTO {0} SELECT * FROM {1};'.format(tmp_name, table)
        self.execute(command, fetch=False)
        # 3. drop original table
        command = 'DROP TABLE {0};'.format(table)
        self.execute(command, fetch=False)
        # 4. rename temporary table
        self.rename_table(tmp_name, table)

    def _execute(self, cursor: sqlite3.Cursor, command: str,
                 fetch: bool = True):
        """
        Dummy function to try to catch database UNIQUE(col) error and
        catch locked errors (up to a max wait time)

        :param cursor: sqlite cursor (self.cursor())
        :param command: str, The SQL command to be run.
        :return:
        """
        # start a counter
        time_count = 0
        # while counter is less than maximum wait time
        while time_count < MAXWAIT:
            try:
                cursor.execute(command)
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    return None
            # catch operational error
            except sqlite3.OperationalError as e:
                # catch the operational error: database is locked
                if 'database is locked' in str(e):
                    time_count += 1
                    # sleep 1 second before trying to execute command against
                    time.sleep(1)
                else:
                    raise e
            # deal with unique error on INSERT
            except sqlite3.IntegrityError as e:
                # look for word 'unique' in exception
                if 'unique' in str(e).lower():
                    raise UniqueEntryException(str(e))
                # else raise exception
                else:
                    raise sqlite3.IntegrityError(str(e))

        # if we get to this point raise operational error
        emsg = 'database locked for > {0} s'.format(MAXWAIT)
        raise sqlite3.OperationalError(emsg)

    def add_from_pandas(self, df: pd.DataFrame, table: Union[str, None],
                        if_exists: str = 'append', index: bool = False,
                        unique_cols: Union[List[str], None] = None):
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
        :param unique_cols: list of strings or None, if set this is columns that
                            are used to form the unique hash for specifying
                            unique rows

        :return:
        """
        # set function name
        func_name = __NAME__ + '.SQLiteDatabase.add_from_pandas()'
        # infer table name
        table = self._infer_table_(table)
        # need to add uhash column
        if unique_cols is not None:
            df = _hash_df(df, unique_cols)
        # check if_exists criteria
        if if_exists not in ['fail', 'replace', 'append']:
            # log error: Pandas.to_sql
            ecode = '00-002-00047'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # try to add pandas dataframe to table
        try:
            conargs = dict(func=func_name, kind='_TO_SQL:SQLiteDatabase')
            with closing(self.connection(**conargs)) as tmpconn:
                df.to_sql(table, tmpconn, if_exists=if_exists, index=index)
                tmpconn.close()
            # pandas removes uniqueness of columns - need to readd this
            #   constraint if unique_cols is not None
            if unique_cols is not None:
                self.add_unique_uhash_col(table)

        except Exception as e:
            # log error: Pandas.to_sql
            ecode = '00-002-00047'
            emsg = drs_base.BETEXT[ecode]
            eargs = [type(e), str(e), func_name]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)

    def _to_pandas(self, command: str) -> pd.DataFrame:
        """
        Use pandas to get sql command
        :param command:
        :return:
        """
        # set function name
        func_name = __NAME__ + '.SQLiteDatabase._to_pandas()'
        # try to read sql using pandas
        # noinspection PyBroadException
        try:
            conargs = dict(func=func_name, kind='_READ_SQL:sqlite3')
            with closing(self.connection(**conargs)) as tmpconn:
                df = pd.read_sql(command, tmpconn)
                tmpconn.close()
        except Exception as _:
            # log error: Could not read SQL command as pandas table
            ecode = '00-002-00048'
            emsg = drs_base.BETEXT[ecode]
            eargs = [command, func_name]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # return dataframe
        return df

    def table_info(self,
                   table: Union[str, None]) -> Tuple[List[str], List[str]]:
        """
        Get the table information for a table name

        :param table: str, the name of the Table
        :return:
        """
        func_name = __NAME__ + '.Database.colnames()'
        # infer the table name if None
        table = self._infer_table_(table)
        # set up command
        command = "PRAGMA table_info({})".format(table)
        # get cursor
        conargs = dict(func=func_name, kind='_execute:colnames')
        conn = self.connection(**conargs)
        cursor = self.cursor(conn)
        # try to execute SQL command
        try:
            # try to execute SQL command
            result = self._execute(cursor, command, fetch=True)
            # get columns
            colnames = list(map(lambda x: x[1], result))
            coltypes = list(map(lambda x: x[2], result))
            # commit and close
            conn.commit()
            cursor.close()
            conn.close()
        # catch all errors and pipe to database error
        except Exception as e:
            # close connection
            cursor.close()
            conn.close()
            # log error: {0}: {1} \n\t Command: {2} \n\t Function: {3}
            ecode = '00-002-00040'
            emsg = drs_base.BETEXT[ecode]
            eargs = [type(e), str(e)]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # return a list of columns
        return colnames, coltypes

    # admin methods
    def backup(self):
        """
        Back up the database

        :return:
        """
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname, 'backup')
        # construct backup path
        backup_path = str(self.path).replace('.db', 'backup.db')
        # remove old backup
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
        except Exception as _:
            pass
        # make backup database
        conargs = dict(func=func_name, kind='backup')
        with closing(self.connection(**conargs)) as conn:
            with closing(sqlite3.connect(backup_path)) as backup_conn:
                # copy main into backup database
                conn.backup(backup_conn)
                # close connections
                backup_conn.close()
                conn.close()

    def reload_from_backup(self, pconst: Any = None):
        """
        Reload database from back up the database

        :param pconst: PseudoConsts - apero.core.constants.pload() this is
                       required to get the unique columns - if unset assumes
                       there are no unique columns

        :return:
        """
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname, 'backup')
        # don't use pconst here
        _ = pconst
        # construct backup path
        backup_path = str(self.path).replace('.db', 'backup.db')
        # make backup database
        conargs = dict(func=func_name, kind='backup')
        with closing(self.connection(**conargs)) as conn:
            with closing(sqlite3.connect(backup_path)) as backup_conn:
                # copy main into backup database
                backup_conn.backup(conn)
                # close connections
                backup_conn.close()
                conn.close()

    def lock(self):
        """
        Lock the database (until unlock is done)
        :return:
        """
        self.execute('BEGIN EXCLUSIVE;', fetch=False)

    def unlock(self):
        """
        Unlock the database (when a lock was done)
        :return:
        """
        self.execute('COMMIT;', fetch=False)

    def _update_table_list_(self):
        """
        Reads the database for tables and updates the class members
        accordingly.
        """
        # Get the new list of tables
        command = 'SELECT name from sqlite_master where type= "table"'
        # execute command
        _tables = self.execute(command, fetch=True)
        # the table names are the first entry in each row so get the table
        #  names from these (and update self.tables)
        self.tables = []
        for _table in _tables:
            # append table name
            self.tables.append(_table[0])


class MySQLDatabase(Database):
    # A wrapper for a MySQL database.
    def __init__(self, path: str, host: str, user: str, passwd: str,
                 database: str, tablename: str, verbose: bool = False,
                 absolute_table_name: bool = False):
        """
        Create an object for reading and writing to a SQLite database.

        :param path: str, the path (only used for backups - so not required
                     unless using the backup method)
        :param host: str, the mysql host name (user@host)
        :param user: str, the mysql user name (user@host)
        :param passwd: str, the password for user@host mysql connection
        :param database: str, the database to connect to
        :param tablename: str, the table name
        :param verbose: bool, whether to verbosely print out database
                        functionality
        :param absolute_table_name: bool, if True does not change the tablename
                                    used when you need to specific a specific
                                    table
        """
        # set class name
        self.classname = 'MySQLDatabase'
        # set function name
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           '__init__()')
        # set path
        aperohome = os.path.join(os.path.expanduser('~'), '.apero')
        if not os.path.exists(aperohome):
            os.makedirs(aperohome)
        # path is in the home directory (for backups)
        self.path = os.path.join(aperohome, '{0}_at_{1}'.format(user, host))
        # deal with mysql not being imported
        if mysql is None:
            # log error: Cannot import mysql connector
            ecode = '00-002-00044'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            drs_base.base_error(ecode, emsg, 'error',
                                exceptionname='DatabaseError',
                                exception=exception)
        # call to super class
        super().__init__(verbose=verbose)
        # storage for database path
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = database
        # deal with setting table name (we only have one per manager hence
        #   why this is set)
        if absolute_table_name:
            self.tname = tablename
        else:
            self.tname = _proxy_table(tablename)
        # re-set path after call to super
        self.path = '{0}@{1}'.format(self.user, self.host)
        self.backup_path = str(path) + '.mysql.backup'
        # deal with database for sql
        self.add_database()
        # update table list
        self._update_table_list_()

    def connection(self, host: Union[str, None] = None,
                   user: Union[str, None] = None,
                   passwd: Union[str, None] = None,
                   dbname: Union[str, None] = None,
                   connect_kind: str = 'mysql.connect',
                   func: Union[str, None] = None,
                   kind: Union[str, None] = None):
        """
        Connect to the mysql database
        Only use within with statement (so connection is closed afterwards)

        :param host: str, the host name
        :param user: str, the user name
        :param passwd: str, the password
        :param dbname: str, the database name (can be None)

        :return: return the mysql connection
        """

        # set function name
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           'connection')
        # deal with no host / user / password / database name
        if host is None:
            host = self.host
        if user is None:
            user = self.user
        if passwd is None:
            passwd = self.passwd
        # deal with database name
        if dbname == 'NULL':
            dbname = None
        elif dbname is None:
            dbname = self.dbname
        # time
        start = time.time()
        # delay processes
        count = 0
        error = None
        while count <= 20:
            # try to connect
            try:
                if connect_kind == 'mysql.connect':
                    conn = _mysql_connect(host, user, passwd, dbname)
                    return conn

                else:
                    conn = _mysql_sqlalchemy_connect(host, user, passwd, dbname)
                    return conn

            except Exception as e:
                # deal with warnings going to errors
                if base.WARN_TO_ERROR:
                    raise e
                error = e
                time.sleep(5 + np.random.uniform()*1)
                count += 1

        # if we get to this point log an error
        # log error: {0}: {1} \n\t Command: {2} \n\t Function: {3}
        ecode = '00-002-00045'
        emsg = drs_base.BETEXT[ecode]
        if self.tname is None:
            tname = 'NONE'
        else:
            tname = self.tname
        # extra error info
        connkind = ('CONNECT: {0} || MySQL {1}@{2}:{3}.{4} || {5}:{6} '
                    '|| Tries {7}')
        connkind = connkind.format(connect_kind, host, user, dbname, tname,
                                   func, kind, count)
        eargs = [type(error), str(error), connkind, func_name]
        exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                  func_name=func_name)
        # add code to database message
        emsg = 'E[0]: {1}'.format(ecode, emsg)
        drs_base.base_error(ecode, emsg, 'error', args=eargs,
                            exceptionname='DatabaseError',
                            exception=exception)

    def __str__(self):
        """
        Standard string return
        :return:
        """
        return 'MySQLDatabase[{0}]'.format(self.path)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = []
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
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
        # update table list
        self._update_table_list_()

    # get / set / execute / add methods
    def execute(self, command: str, fetch: bool) -> Any:
        """
        Directly execute an SQL command on the database and return
        any results.

        :param command: str, The SQL command to be run.
        :param fetch: bool, if True there is a result to fetch

        :returns: The outputs of the command, if any, as a list.
        """
        # set function name
        func_name = __NAME__ + '.Database.execute()'
        # print input if verbose
        if self._verbose_:
            print("SQL INPUT: ", command)
        # get cursor
        conargs = dict(func=func_name, kind='execute:_execute')
        with closing(self.connection(**conargs)) as conn:
            with closing(self.cursor(conn)) as cursor:
                # try to execute SQL command
                try:
                    result = self._execute(cursor, command, fetch=fetch)
                    # commit and close
                    conn.commit()
                    cursor.close()
                    conn.close()
                # pass unique exception upwards
                except UniqueEntryException as e:
                    # close
                    cursor.close()
                    conn.close()
                    raise UniqueEntryException(str(e))
                # catch all errors and pipe to database error
                except Exception as e:
                    # close
                    cursor.close()
                    conn.close()
                    # log error: Error Type: Error message \n\t Command:
                    ecode = '00-002-00032'
                    emsg = drs_base.BETEXT[ecode]
                    eargs = [type(e), str(e), command]
                    exception = DatabaseError(message=emsg.format(*eargs),
                                              errorobj=e,
                                              path=self.path,
                                              func_name=func_name)
                    # add code to database message
                    emsg = 'E[0]: {1}'.format(ecode, emsg)
                    # log base error
                    return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                               exceptionname='DatabaseError',
                                               exception=exception)

        # print output of sql command if verbose
        if self._verbose_:
            print("SQL OUTPUT:", result)
        # return the sql result
        return result

    def _execute(self, cursor: mysql.connection.MySQLCursor, command: str,
                 fetch: bool = True):
        """
        Dummy function to try to catch database locked errors
        (up to a max wait time)

        :param cursor: sqlite cursor (self.cursor())
        :param command: str, The SQL command to be run.
        :return:
        """
        cursor = _mysql_exectue(cursor, command)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        # return result
        return result

    def add_database(self):
        """
        Check for 'database' in the MySQL Database construct and if not add
        'database' to MySQL

        :return: None, either adds database or does nothing
        """
        # set function name
        func_name = '{0}.{1}.{2}'.format(__NAME__, self.classname,
                                         'add_database')
        # ---------------------------------------------------------------------
        # get the cursor
        conargs = dict(func=func_name, kind='SHOW')
        with closing(self.connection(dbname='NULL', **conargs)) as tmpconn:
            with closing(tmpconn.cursor()) as cursor:
                # Get the new list of tables
                command = 'SHOW DATABASES'
                # execute command
                try:
                    cursor = _mysql_exectue(cursor, command)
                    _databases = cursor.fetchall()
                except Exception as e:
                    # close
                    cursor.close()
                    tmpconn.close()
                    # log error
                    ecode = '00-002-00050'
                    emsg = drs_base.BETEXT[ecode]
                    eargs = [self.dbname, type(e), str(e)]
                    exception = DatabaseError(emsg,
                                              path=self.path,
                                              func_name=func_name)
                    # log base error
                    drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                        exceptionname='DatabaseError',
                                        exception=exception)

                # the table names are the first entry in each row so get the
                #  table names from these (and update self.tables)
                databases = []
                for _database in _databases:
                    # append table name
                    databases.append(_database[0])
                # close
                cursor.close()
                tmpconn.close()
        # ---------------------------------------------------------------------
        # check for database in databases (and add it if not there)
        if self.dbname not in databases:
            conargs = dict(func=func_name, kind='CREATE')
            with closing(self.connection(dbname='NULL', **conargs)) as tmpconn:
                with closing(tmpconn.cursor()) as cursor:
                    try:
                        command = 'CREATE DATABASE {0}'.format(self.dbname)
                        cursor = _mysql_exectue(cursor, command)
                        # close
                        cursor.close()
                        tmpconn.close()
                    except Exception as e:
                        # close
                        cursor.close()
                        tmpconn.close()
                        # log error
                        ecode = '00-002-00050'
                        emsg = drs_base.BETEXT[ecode]
                        eargs = [self.dbname, type(e), str(e)]
                        exception = DatabaseError(emsg.format(*eargs),
                                                  path=self.path,
                                                  func_name=func_name)
                        # log base error
                        drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                            exceptionname='DatabaseError',
                                            exception=exception)

    def cursor(self, conn):
        """
        Attempt to retrieve a database cursor and reconnect on failure

        :return: The cursor
        """
        return conn.cursor()

    def _execute(self, cursor: Any, command: str,
                 fetch: bool = True):
        """
        Dummy function to try to catch database UNIQUE(col) error

        :param cursor: mysql cursor (self.cursor())
        :param command: str, The SQL command to be run.
        :return:
        """
        # while counter is less than maximum wait time
        try:
            cursor = _mysql_exectue(cursor, command)
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                return None
        # deal with unique error on INSERT
        except mysql.IntegrityError as e:
            # look for word 'unique' in exception
            if 'duplicate' in str(e).lower():
                raise UniqueEntryException(str(e))
            # else raise exception
            else:
                raise mysql.IntegrityError(str(e))

    # table methods
    def add_table(self, name: str, field_names: List[str],
                  field_types: List[Union[str, type]],
                  unique_cols: Optional[List[str]] = None,
                  index_cols: Optional[List[str]] = None):
        """
        Adds a table to the database file.

        :param name: The name of the table to create. This must not already be
                     in use or a SQL keyword.
        :param field_names: The names of the fields (columns) in the table as a
                           list of str objects.  These can't be SQL keywords.
        :param field_types: The data types of the fields as a list. The list
                            can contain either SQL type specifiers or the
                            python int, str, and float types.
        :param unique_cols: list of str, the field_names that should be unique

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
        # deal with index columns
        if index_cols is None:
            index_cols = []
        # make sure field_names and field_types are the same size
        if len(field_names) != len(field_types):
            # log error: field_names and field_types must be the same length
            ecode = '00-002-00036'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)

        # loop around fields
        for it in range(len(field_names)):
            # get this iterations values
            fname, ftype = field_names[it], field_types[it]
            # make sure names are strings
            if not isinstance(fname, str):
                # log error: field_names must be strings
                ecode = '00-002-00037'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # deal with type
            if isinstance(ftype, type):
                # deal with wrong type
                if ftype not in translator:
                    # log error: field_types must be string or [int/float/str]
                    ecode = '00-002-00038'
                    emsg = drs_base.BETEXT[ecode]
                    exception = DatabaseError(emsg, path=self.path,
                                              func_name=func_name)
                    # add code to database message
                    emsg = 'E[0]: {1}'.format(ecode, emsg)
                    # log base error
                    return drs_base.base_error(ecode, emsg, 'error',
                                               exceptionname='DatabaseError',
                                               exception=exception)
                # set as sql type
                # noinspection PyTypeChecker
                ftype = translator[ftype]
            # else we must have a string --> so break if not
            elif not isinstance(ftype, str):
                # log error:field_types must be string or [int/float/str]
                ecode = '00-002-00038'
                emsg = drs_base.BETEXT[ecode]
                exception = DatabaseError(emsg, path=self.path,
                                          func_name=func_name)
                # add code to database message
                emsg = 'E[0]: {1}'.format(ecode, emsg)
                # log base error
                return drs_base.base_error(ecode, emsg, 'error',
                                           exceptionname='DatabaseError',
                                           exception=exception)
            # set type
            fields.append('{0} {1}'.format(fname, ftype))
        # ---------------------------------------------------------------------
        # unique columns become a 255 hash
        if unique_cols is not None:
            extra_str = ', {0} VARCHAR(64), UNIQUE({0})'.format(UHASH_COL)
        else:
            extra_str = ''
        # ---------------------------------------------------------------------
        # deal with indexes
        for index_col in index_cols:
            if index_col in field_names:
                extra_str += ', INDEX ({0})'.format(index_col)
        # ---------------------------------------------------------------------
        # now create sql command
        cargs = [name, ", ".join(fields) + extra_str]
        command = "CREATE TABLE IF NOT EXISTS {}({});".format(*cargs)
        # ---------------------------------------------------------------------
        # execute command
        self.execute(command, fetch=False)
        # update the table list
        self._update_table_list_()

    def add_unique_uhash_col(self, table: Union[str, None]):
        """
        Need a way to update the unique column (uhash) if set -
        this is because pandas removes uniqueness from the column

        :param table: str or None, the table name
        :return:
        """
        # infer table name
        table = self._infer_table_(table)
        # need to make sure UHASH is a VARCHAR(64)
        command = 'ALTER TABLE {0} MODIFY COLUMN {1} VARCHAR(64);'
        command = command.format(table, UHASH_COL)
        self.execute(command, fetch=False)
        # now create sql command
        command = "ALTER TABLE {0} ADD UNIQUE ({1});"
        command = command.format(table, UHASH_COL)
        # execute command
        self.execute(command, fetch=False)

    def add_from_pandas(self, df: pd.DataFrame, table: Union[str, None],
                        if_exists: str = 'append', index: bool = False,
                        unique_cols: Union[List[str], None] = None):
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
        :param unique_cols: list of strings or None, if set this is columns that
                            are used to form the unique hash for specifying
                            unique rows

        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database.add_from_pandas()'
        # infer table name
        table = self._infer_table_(table)
        # need to add uhash column
        if unique_cols is not None:
            df = _hash_df(df, unique_cols)
        # check if_exists criteria
        if if_exists not in ['fail', 'replace', 'append']:
            # log error: Pandas.to_sql
            ecode = '00-002-00047'
            emsg = drs_base.BETEXT[ecode]
            exception = DatabaseError(emsg, path=self.path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error',
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # try to add pandas dataframe to table
        try:
            conargs = dict(func=func_name, kind='TO_SQL:SQLALCHEMY')
            with closing(self.connection(connect_kind='sqlalchemy', **conargs)) as dconn:
                df.to_sql(table, dconn, if_exists=if_exists, index=index)
                dconn.close()
                # pandas removes uniqueness of columns - need to readd this
                #   constraint if unique_cols is not None
                if unique_cols is not None:
                    self.add_unique_uhash_col(table)

        except Exception as e:
            # log error: Pandas.to_sql
            ecode = '00-002-00047'
            emsg = drs_base.BETEXT[ecode]
            eargs = [type(e), str(e), func_name]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)

    def _to_pandas(self, command: str) -> pd.DataFrame:
        """
        Use pandas to get sql command
        :param command:
        :return:
        """
        # set function name
        func_name = __NAME__ + '.Database._to_pandas()'
        # try to read sql using pandas
        # noinspection PyBroadException
        try:
            with closing(self.connection(connect_kind='sqlalchemy')) as dconn:
                df = _read_sql(command, dconn)
                dconn.close()
        except Exception as _:
            # log error: Could not read SQL command as pandas table
            ecode = '00-002-00048'
            emsg = drs_base.BETEXT[ecode]
            eargs = [command, func_name]
            exception = DatabaseError(emsg.format(*eargs), path=self.path,
                                      func_name=func_name)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # return dataframe
        return df

    def _update_table_list_(self):
        """
        Reads the database for tables and updates the class members
        accordingly.
        """
        # Get the new list of tables
        command = 'SHOW TABLES'
        # execute command
        _tables = self.execute(command, fetch=True)
        # the table names are the first entry in each row so get the table
        #  names from these (and update self.tables)
        self.tables = []
        for _table in _tables:
            # append table name
            self.tables.append(_table[0])

    # other methods
    def table_info(self,
                   table: Union[str, None]) -> Tuple[List[str], List[str]]:
        """
        Get the table information for a table name

        :param table: str, the name of the Table
        :return:
        """
        func_name = __NAME__ + '.Database.colnames()'
        # infer the table name if None
        table = self._infer_table_(table)
        # set up command
        command = "SHOW columns FROM {}".format(table)
        # get cursor
        conargs = dict(func=func_name, kind='_execute:table_info')
        with closing(self.connection(**conargs)) as conn:
            with closing(conn.cursor()) as cursor:
                # try to execute SQL command
                try:
                    # try to execute SQL command
                    result = self._execute(cursor, command, fetch=True)
                    # get columns
                    colnames = list(map(lambda x: x[0], result))
                    coltypes = list(map(lambda x: x[1], result))
                    # commit and close
                    conn.commit()
                    cursor.close()
                    conn.close()
                # catch all errors and pipe to database error
                except Exception as e:
                    # close connection
                    cursor.close()
                    conn.close()
                    # log error: {0}: {1} \n\t Command: {2} \n\t Function: {3}
                    ecode = '00-002-00040'
                    emsg = drs_base.BETEXT[ecode]
                    eargs = [type(e), str(e)]
                    exception = DatabaseError(emsg.format(*eargs),
                                              path=self.path,
                                              func_name=func_name)
                    # add code to database message
                    emsg = 'E[0]: {1}'.format(ecode, emsg)
                    # log base error
                    return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                               exceptionname='DatabaseError',
                                               exception=exception)
        # return a list of columns
        return colnames, coltypes

    # admin methods
    def backup(self):
        """
        Back up the database

        :return:
        """
        # construct backup path
        if self.backup_path is None:
            return
        # -------------------------------------------------------------------
        # remove old backup
        try:
            if os.path.exists(self.backup_path):
                os.remove(self.backup_path)
        except Exception as _:
            pass
        # -------------------------------------------------------------------
        # get all rows as a pandas data frame
        df = self.get('*', table=self.tname, return_pandas=True)
        # -------------------------------------------------------------------
        # save to csv file
        df.to_csv(self.backup_path)

    def reload_from_backup(self, pconst: Any = None):
        """
        Reload database from back up the database

        :param pconst: PseudoConsts - apero.core.constants.pload() this is
                       required to get the unique columns - if unset assumes
                       there are no unique columns

        :return:
        """
        # construct backup path
        if self.backup_path is None:
            return
        # get unique columns
        if pconst is None:
            ucols = None
        elif 'INDEX' in self.tname:
            _, _, ucols = pconst.INDEX_DB_COLUMNS()
        elif 'OBJECT' in self.tname:
            _, _, ucols = pconst.OBJECT_DB_COLUMNS()
        else:
            ucols = None
        # load csv file into pandas table
        df = pd.read_csv(self.backup_path)
        # add pandas table to database
        self.add_from_pandas(df, self.tname, if_exists='replace',
                             unique_cols=ucols)


# =============================================================================
# Define functions
# =============================================================================
def database_wrapper(kind: str, path: Union[Path, str, None],
                     verbose: bool = False) -> Database:
    """
    Database wrapper - takes the database parameter yaml file
    Either uses MySQL or SQLite3

    :param kind: str, the kind of database (CALIB/TELLU/INDEX/LANG/OBJECT)
    :param path: str or Path, for SQLite3 this is the path to the database file
                 for MySQL this is just user@host
    :param verbose: bool - if True the database prints out debug messages
                    verbosely

    :return: Database instance (either SQLiteDatabase or MySQLDatabase)
    """
    # set function name
    func_name = __NAME__ + '.database_wrapper()'
    # get database parameters
    dparams = base.DPARAMS
    # make sure kind is upper case
    kind = kind.upper()
    # if we are using mysql database
    if dparams['USE_MYSQL']:
        # get mysql params
        sparams = dparams['MYSQL']
        # create table name
        if kind == 'NONE':
            tablename = None
            abs_tname = True
        else:
            tablename = '{0}_{1}'.format(kind, sparams[kind]['PROFILE'])
            abs_tname = False
        # return the MySQLDatabase instance
        return MySQLDatabase(path=path,
                             host=sparams['HOST'],
                             user=sparams['USER'],
                             passwd=sparams['PASSWD'],
                             database=sparams['DATABASE'],
                             tablename=tablename,
                             verbose=verbose, absolute_table_name=abs_tname)
    # else default to sqlite3
    else:
        sparams = dparams['SQLITE3']
        # get the path
        if kind not in sparams:
            # log error: Database kind '{0}' is invalid
            ecode = '00-002-00049'
            emsg = drs_base.BETEXT[ecode]
            eargs = [kind]
            exception = DatabaseError(emsg.format(*eargs), path=path,
                                      func_name=func_name)
            # add code to database message
            emsg = 'E[0]: {1}'.format(ecode, emsg)
            # log base error
            return drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                       exceptionname='DatabaseError',
                                       exception=exception)
        # return the SQLiteDatabase instance
        return SQLiteDatabase(path, verbose)


def _decode_value(value: Any) -> str:
    """
    Convert to string that can go into sql

    :param value: Any value to convert to string

    :return: str, the decoded string value
    """
    # Convert None to NULL
    if isinstance(value, str):
        if value.upper() == 'NONE':
            return 'NULL'
        if value.upper() == '"NULL"' or value.upper() == "'NULL'":
            return 'NULL'
        if value.upper() == 'NULL':
            return 'NULL'
    # deal with value being types (decode to string)
    if isinstance(value, bytes):
        return value.decode('utf=8')
    # deal with value being None
    elif value is None:
        return 'NULL'
    # deal with nan
    elif isinstance(value, float) and np.isnan(value):
        return 'NULL'
    # deal with inf
    elif isinstance(value, float) and np.isinf(value):
        if np.isneginf(value):
            return 'NULL'
        else:
            return 'NULL'
    # if it is not a string already just pipe it to string
    elif not isinstance(value, str):
        return str(value)
    # else push it in as a string
    else:
        # need to remove speechmarks at this point
        if '\'' in value:
            value = value.replace('\'', '')
        if '\"' in value:
            value = value.replace('\"', '')
        # return formatted value
        return '"{0}"'.format(value)


def _encode_value(value: str, dtype: Type) -> Union[str, None, float]:
    """
    Convert an sql string into a python variable

    :param value: str, the sql value

    :return: str, None or float - depending on the sql string 'value'
    """
    # return None
    if dtype is None and value == 'NULL':
        return None
    # return not a number
    if dtype is float and value == 'NULL':
        return np.nan
    # else return value
    return value


def _proxy_table(tablename: str) -> str:
    """
    Define a tablename that avoid conflicts with SQL KEYWORDS

    :param tablename: table name to change
    :return:
    """
    if tablename.endswith('_DB'):
        return tablename
    else:
        return tablename + '_DB'


def _hash_df(df: pd.DataFrame, unique_cols: List[str]) -> pd.DataFrame:
    """
    Produce a hash for a data frame (if hash column not present)

    :param df: pandas dataframe (to be added to the database)
    :param unique_cols: list of strings, the unique columns to add

    :return: the update dataframe (only if hash column was not found)
    """
    # check if hash column present
    if UHASH_COL in df:
        return df
    # get column names from pandas table
    columns = list(np.array(df.columns).astype(str))
    # store hash strings
    hash_strings = []
    # loop around all rows
    for row in range(len(df)):
        # get values for this row
        values = list(df.iloc[row].values)
        # generate hash string for this row
        hash_string = _hash_col(columns, values, unique_cols,
                                return_string=True)
        # append to storage
        hash_strings.append(hash_string)
    # push column into dataframe
    df[UHASH_COL] = hash_strings
    # return dataframe
    return df


def _hash_col(columns: List[str], values: List[Any],
              unique_cols: List[str], return_string: bool = False
              ) -> Union[str, Tuple[List[str], List[Any]]]:
    """
    Generate a hash from a list of unique columns

    :param columns: list of column names
    :param values: list of values (without the hash column)
    :param unique_cols: list of column names to construct the hash

    :return: either a str (if return_string is True) or a tuple, the
             updated columns and values
    """

    # store the positions in values of unique columns
    hash_value = ''
    used_cols = []
    # loop around unique columns
    for unique_col in unique_cols:
        # they may be lists
        cols = unique_col.split(',')
        # loop around these
        for col in cols:
            # don't add the column twice
            if col in used_cols:
                continue
            # find the col in columns
            if col in columns:
                # get the position in columns where the value is
                pos = np.where(np.array(columns) == col)[0][0]
                # generate the hash value
                hash_value += str(values[pos])
                # add column to used columns
                used_cols.append(col)

    # generate hash from string combination of values
    hash_string = drs_base.generate_hash(hash_value, 32)

    # if return string return hash
    if return_string:
        return hash_string
    # add to the values
    values.append('"{0}"'.format(hash_string))
    # only add to columns if not already there
    if UHASH_COL not in columns:
        columns.append(UHASH_COL)
    # return the hash string and column
    return columns, values


# =============================================================================
# Define base databases
# =============================================================================
class BaseDatabaseManager:
    def __init__(self, check: bool = True):
        """
        Constructor of the Base Database Manager class

        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
        # save class name
        self.classname = 'DatabaseManager'
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__init__')
        # set instrument name
        self.instrument = base.IPARAMS['INSTRUMENT']
        # set name
        self.name = None
        self.kind = None
        self.dbtype = None
        # set parameters
        self.dbhost = None
        self.dbuser = None
        self.dbpath = None
        self.dbname = None
        self.dbreset = None
        # set empty database
        self.database = None
        # check is not used in base class
        _ = check
        # set path
        self.path = None

    def __str__(self):
        """
        Return the string representation of the class
        :return:
        """
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__str__')
        # return string representation
        return '{0}[{1}]'.format(self.classname, self.path)

    def __repr__(self):
        """
        Return the string representation of the class
        :return:
        """
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__repr__')
        # return string representation
        return self.__str__()

    def set_path(self, path: Union[Path, str], check: bool = True):
        # set function
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__init__')
        # deal with no instrument (i.e. no database)
        if self.instrument == 'None':
            return
        # load database settings
        self.database_settings()
        # ---------------------------------------------------------------------
        # deal with path for SQLITE3
        # ---------------------------------------------------------------------
        if self.dbtype == 'SQLITE3':
            # check that path exists
            if not path.exists() and check:
                # log error: Directory {0} does not exist (database = {1})
                eargs = [path, self.name, func_name]
                emsg = ('Path {0} does not exist for database {1} '
                        '\n\t Function = {2}')
                raise DatabaseException(emsg.format(*eargs))
            # set path
            self.path = path
        # ---------------------------------------------------------------------
        # deal with path for MySQL (only for printing)
        # ---------------------------------------------------------------------
        elif self.dbtype == 'MYSQL':
            self.path = '{0}@{1}'.format(self.dbuser, self.dbhost)
        else:
            emsg = 'Database type "{0}" invalid'
            raise DatabaseException(emsg.format(self.dbtype))

    def load_db(self, check: bool = False):

        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, 'load_db')
        # if we already have database do nothing
        if (self.database is not None) and (not check):
            return
        # load database
        self.database = database_wrapper(self.kind, self.path)

    def database_settings(self):
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                   'database_settings')
        # load database yaml file
        ddict = base.DPARAMS
        # get correct sub-dictionary
        if ddict['USE_MYSQL']:
            sdict = ddict['MYSQL']
            self.dbtype = 'MYSQL'
            self.dbhost = sdict['HOST']
            self.dbuser = sdict['USER']
            self.dbname = sdict['DATABASE']
        else:
            self.dbtype = 'SQLITE3'


class LanguageDatabase(BaseDatabaseManager):
    def __init__(self, check: bool = True):
        """
        Constructor of the Language Database class

        :param check: bool, if True makes sure database file exists (otherwise
                      assumes it is)

        :return: None
        """
        # call super class
        super().__init__(check)
        # save class name
        self.classname = 'LanguageDatabaseManager'
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__init__')
        # set instrument name
        self.instrument = base.IPARAMS.get('INSTRUMENT', 'None')
        # set name
        self.name = 'language'
        self.kind = 'LANG'
        # define columns
        self.columns = DatabaseColumns()
        # add key columns
        self.columns.add(name='KEYNAME', datatype='VARCHAR(50)', is_index=True)
        self.columns.add(name='KIND', datatype='VARCHAR(10)')
        self.columns.add(name='KEYDESC', datatype='TEXT')
        self.columns.add(name='ARGUMENTS', datatype='TEXT')
        # add language columns
        for lang in base.LANGUAGES:
            self.columns.add(name=lang, datatype='TEXT')
        # other paths
        self.databasefile = ''
        self.resetfile = ''
        self.instruement_resetfile = ''
        self.path_definitions()
        # set path
        self.set_path(self.databasefile, check=check)

    def path_definitions(self):
        # set function
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           'path_definitions')
        # get the package name
        package = base.__PACKAGE__
        # get the relative path for the database
        lang_path = base.LANG_DEFAULT_PATH
        # get the absolute path for the language database
        abs_lang_path = drs_base.base_func(drs_base.base_get_relative_folder,
                                           func_name, package, lang_path)
        abs_lang_path = Path(abs_lang_path)
        # set absolute path
        self.databasefile = abs_lang_path.joinpath(base.LANG_DB_FILE)
        self.resetfile = abs_lang_path.joinpath(base.LANG_DB_RESET)
        instrument_reset = base.LANG_DB_RESET_INST.format(self.instrument)
        self.instruement_resetfile = abs_lang_path.joinpath(instrument_reset)

    def get_entry(self, columns: str, key: str):
        # set function
        _ = '{0}.{1}.{2}()'.format(__NAME__, self.classname, '__init__')
        # deal with no instrument set
        if self.instrument == 'None':
            return None
        # deal with having the possibility of more than one column
        colnames = self.database.colnames(columns, table=self.database.tname)
        # set up kwargs from database query
        sql = dict()
        # set up sql kwargs
        sql['sort_by'] = None
        sql['sort_descending'] = True
        # condition for key
        sql['condition'] = 'KEYNAME = "{0}"'.format(key)
        # return only 1 row
        sql['max_rows'] = 1
        # do sql query
        entries = self.database.get(columns, table=self.database.tname, **sql)
        # return filename
        if len(entries) == 1:
            if len(colnames) == 1:
                return entries[0][0]
            else:
                return entries[0]
        else:
            return None

    def add_entry(self, key: str, kind: str, comment: str,
                  arguments: Union[str, None] = None,
                  textdict: Union[Dict[str, str], None] = None):
        """
        Add a language entry

        :param key: str, the key name for the language entry
        :param kind: str, the language entry tag (HELP, TEXT, ERROR, WARNING,
                     INFO, ALL, GRAPH, DEBUG)
        :param comment: a description of this key (in english)
        :param arguments: None or argument
        :param textdict:

        :return:
        """
        # set function
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           'add_entry')
        # deal with bad key
        cond1 = drs_base.base_func(drs_base.base_null_text, func_name, key,
                                   ['None', 'NULL', ''])
        if cond1:
            return
        # check kind
        if kind not in ['HELP', 'TEXT', 'ERROR', 'WARNING', 'INFO', 'ALL',
                        'GRAPH', 'DEBUG']:
            emsg = ('Kind = {0} not valid for Language database\n\t'
                    'Function = {1}')
            raise DatabaseException(emsg.format(kind, func_name))
        # check arguments
        if arguments is None:
            arguments = 'NULL'
        # ---------------------------------------------------------------------
        # construct values
        values = [key, kind, comment, arguments]
        # ---------------------------------------------------------------------
        # add languages
        if textdict is not None:
            for language in base.LANGUAGES:
                if language in textdict:
                    # get text for this language
                    dbtext = str(textdict[language])
                    # replace all " with ' (to avoid conflicts)
                    dbtext = dbtext.replace('"', "'")
                    # if text is null --> NULL
                    cond2 = drs_base.base_func(drs_base.base_null_text,
                                               func_name, dbtext,
                                               ['None', 'NULL', ''])
                    if cond2:
                        values += ['NULL']
                    else:
                        values += ['{0}'.format(dbtext)]
                else:
                    values += ['NULL']
        else:
            values += ['NULL'] * len(base.LANGUAGES)
        # ---------------------------------------------------------------------
        # get unique keys
        ukeys = self.database.unique('KEYNAME', table=self.database.tname)
        # if we have the key update the row
        if key in ukeys:
            # set condition
            condition = 'KEYNAME="{0}"'.format(key)
            # update row in database
            self.database.set('*', values=values, condition=condition,
                              table=self.database.tname)
        # if we don't have the key add a new row
        else:
            self.database.add_row(values, table=self.database.tname)

    def get_dict(self, language: str) -> dict:
        """
        Get a dictionary representation of the database (only use if never
        writing to the database in a run)

        :param language: str, the language to use
        :return:
        """
        # set function
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           'get_dict')
        # get all rows
        df = self.database.get('*', table=self.database.tname,
                               return_pandas=True)
        # set up storage
        storage = dict()
        # loop around dataframe rows
        for row in range(len(df)):
            # get data for row
            rowdata = df.iloc[row]
            # get text
            if language not in rowdata:
                rowtext = rowdata[base.DEFAULT_LANG]

            else:
                cond1 = drs_base.base_func(drs_base.base_null_text,
                                           func_name, rowdata[language],
                                           ['None', 'NULL', ''])
                if cond1:
                    rowtext = rowdata[base.DEFAULT_LANG]
                else:
                    rowtext = rowdata[language]
            # if we still have a null entry do not add this row to storage
            cond2 = drs_base.base_func(drs_base.base_null_text, func_name,
                                       rowtext, ['None', 'NULL', ''])
            if cond2:
                continue
            # encode rowtext with escape chars
            rowtext = rowtext.replace(r'\n', '\n')
            rowtext = rowtext.replace(r'\t', '\t')
            # push to storage
            storage[rowdata['KEYNAME']] = rowtext
        # return dictionary storage
        return storage


# =============================================================================
# Function with annoying warning that need suppressing
#    when we use base.WARN_TO_ERROR
# =============================================================================
def _ignore_warnings():
    if base.WARN_TO_ERROR:
        warnings.filterwarnings('ignore')


def _unignore_warnings():
    if base.WARN_TO_ERROR:
        warnings.filterwarnings('error')


def _mysql_connect(host, user, passwd, dbname):
    with warnings.catch_warnings():
        _ignore_warnings()
        conn = mysql.connect(host=host, user=user, passwd=passwd,
                             database=dbname,
                             connection_timeout=3600)
    _unignore_warnings()
    return conn


def _mysql_sqlalchemy_connect(host, user, passwd, dbname):
    with warnings.catch_warnings():
        _ignore_warnings()
        import sqlalchemy
        dpath = 'mysql+mysqlconnector://{0}:{1}@{2}/{3}'
        dargs = [user, passwd, host, dbname]
        db = sqlalchemy.create_engine(dpath.format(*dargs),
                                      pool_pre_ping=True)
        conn = db.connect()
    _unignore_warnings()
    return conn


def _mysql_exectue(cursor, command):
    with warnings.catch_warnings():
        _ignore_warnings()
        cursor.execute(command)
    _unignore_warnings()
    return cursor


def _read_sql(command, dconn):
    with warnings.catch_warnings():
        _ignore_warnings()
        df = pd.read_sql(command, con=dconn)
    _unignore_warnings()
    return df


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
