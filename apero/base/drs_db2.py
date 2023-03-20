#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2023-03-14 at 11:27

@author: cook
"""
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import sqlalchemy
from astropy.table import Table as AstropyTable
from sqlalchemy_utils import database_exists, create_database

from apero.base import base
from apero.base import drs_db
from apero.base import drs_base

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
# -----------------------------------------------------------------------------
# unique hash column
UHASH_COL = 'UHASH'
# ReturnType of the update dictionary
UpdateDict = Union[List[Dict[str, Any]], Dict[str, Any]]


# =============================================================================
# Define functions
# =============================================================================
class AperoDatabaseException(Exception):
    """
    Database exception
    """
    pass


class AperoDatabaseError(AperoDatabaseException):
    def __init__(self, message: Union[str, None] = None,
                 errorobj: Any = None, url: str = None,
                 func_name: Union[str, None] = None):
        """
        Construct the Database Error instance

        :param message: str a mesage to pass / print
        :param errorobj: the error instance (or anything else)
        :param url: str, the database URL
        :param func_name: str, the function name where error occured
        """
        self.message = message
        self.errorobj = errorobj
        self.url = url
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
        if self.url is not None:
            emsg += drs_base.BETEXT['00-002-00029']
        if self.func_name is not None:
            emsg += drs_base.BETEXT['00-002-00030']
        return emsg.format(self.message, self.url, self.func_name)


class AperoDatabase:
    def __init__(self, url, verbose: bool = False,
                 tablename: Optional[str] = None):
        """

        """
        # set the class name
        self.classname = 'AperoDatabase'
        # store the uri used
        self.url = url
        # store verboseness
        self.verbose = verbose
        # define the engine to use
        self.engine = sqlalchemy.create_engine(url, echo=verbose)
        # define the table name
        self.tablename = tablename

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['engine']
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
        # re-create engine after pickle
        self.engine = sqlalchemy.create_engine(self.url, echo=self.verbose)

    def __str__(self):
        """
        Standard string return
        :return:
        """
        return 'Database[{0}]'.format(self.url)

    def __repr__(self):
        """
        Standard string representation
        :return:
        """
        return self.__str__()

    def add_database(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def add_table(self, tablename: str,
                  columns: List[sqlalchemy.Column],
                  indexes: List[sqlalchemy.Index] = None,
                  uniques: List[sqlalchemy.UniqueConstraint] = None):
        """
        Add a table to the database

        :param tablename: str, the name of the table
        :param columns: list of sqlalchemy.Column instances
        :param indexes: Optional, list of sqlalchemy.Index instances
        :param uniques: Optional, list of sqlalchemy.UniqueConstraint instances

        :return:
        """
        # ----------------------------------------------------------------------
        # get a list of unique columns
        unique_cols = self._unique_cols(columns=columns)
        # deal with adding the hash columns
        if len(unique_cols) > 0:
            # create a hash column
            hash_col = sqlalchemy.Column(UHASH_COL, sqlalchemy.String(64),
                                         unique=True)
            # add the hash columns to columns
            columns.append(hash_col)
        # ----------------------------------------------------------------------
        # check to see if table name exists in database
        inspector = sqlalchemy.inspect(self.engine)
        # remove current table if adding a table
        if inspector.has_table(tablename):
            self.delete_table(tablename)
        # define the meta data
        metadata = sqlalchemy.MetaData()
        # create the table
        _ = sqlalchemy.Table(tablename, metadata, *columns, *indexes)
        # create table
        metadata.create_all(self.engine)

    def count(self, tablename: Optional[str] = None,
              condition: Optional[str] = None) -> int:
        """
        Counts the number of rows in table. If condition is set
        counts just these rows

        :param tablename: A str which specifies which table within the
                   database to retrieve data from.  If there is only one
                   table to pick from, this may be left as None to use it
                   automatically.
        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.

        :return: int, the count
        """
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # Create a session
        sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        # ---------------------------------------------------------------------
        with sessionmaker() as session:
            # set up query
            query = session.query(sqlalchemy.func.count())
            # add the table to select from
            query = query.select_from(sqltable)
            # if we have a condition filter by it
            if condition is not None:
                query = query.filter(sqlalchemy.text(condition))
            # get the count
            count = query.scalar()
        # ---------------------------------------------------------------------
        # return the count
        return count

    def unique(self, column: str, tablename: Optional[str] = None,
               condition: Optional[str] = None) -> np.ndarray:
        """
        Get the unique values for a column (with condition if set)

        :param column: a string containing the comma-separated columns to
             retrieve from the database.  You may also apply basic
             math functions and aggregators to the columns
             ( see examples below).
             "*" retrieves all available columns.
        :param tablename: A str which specifies which table within the database to
                   retrieve data from.  If there is only one table to pick
                   from, this may be left as None to use it automatically.
        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.

        :return:
        """
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # add the table to select from
        query = sqltable.select().with_only_columns(getattr(sqltable.c, column))
        # deal with where condition
        if condition is not None:
            query = query.where(sqlalchemy.text(condition))
        # make sure we only get unique values
        query = query.distinct()
        # get the unique values
        with self.engine.begin() as conn:
            result = conn.execute(query).fetchall()
        # flatten result
        items = [item for sublist in result for item in sublist]
        # remove None from items
        items = [item for item in items if item is not None]
        # return unique result
        return np.array(list(set(items)))

    def get(self, columns: str, tablename: Optional[str] = None,
            condition: Optional[str] = None,
            sort_by: Optional[Union[List[str], str]] = None,
            sort_descending: bool = True, max_rows: Optional[int] = None,
            return_array: bool = False, return_table: bool = False,
            return_pandas: bool = False, groupby: Optional[str] = None
            ) -> Union[tuple, pd.DataFrame, np.ndarray, AstropyTable]:
        """
        Retrieves data from the database with a variety of options.

        :param columns: a string containing the comma-separated columns to
                     retrieve from the database.  You may also apply basic
                     math functions and aggregators to the columns
                     ( see examples below).
                     "*" retrieves all available columns.
        :param tablename: A str which specifies which table within the
                          database to retrieve data from.  If there is only
                          one table to pick from, this may be left as None to
                          use it automatically.
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
        :param groupby: str or None, if set sets the group by sql criteria

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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # create a query statement
        if columns == '*':
            query = sqltable.select()
        else:
            sqlcols = [getattr(sqltable.c, col) for col in columns.split(',')]
            query = sqltable.select().with_only_columns(*sqlcols)
        # ---------------------------------------------------------------------
        # add condition
        if condition is not None:
            query = query.where(sqlalchemy.text(condition))
        # ---------------------------------------------------------------------
        # deal with descending
        if sort_descending:
            ordering = sqlalchemy.desc
        else:
            ordering = sqlalchemy.asc
        # ---------------------------------------------------------------------
        # deal with sort by
        if sort_by is not None:
            if isinstance(sort_by, list):
                for column in sort_by:
                    query = query.order_by(ordering(column))
            else:
                query = query.order_by(ordering(sort_by))
        # ---------------------------------------------------------------------
        # deal with max rows
        if max_rows is not None:
            query = query.limit(max_rows)
        # ---------------------------------------------------------------------
        # add the group by statement
        if groupby is not None:
            query = query.group_by(groupby)
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as conn:
            result = conn.execute(query)
            # get the results as a list
            if return_pandas:
                rows = pd.DataFrame(result.fetchall(), columns=result.keys())
            elif return_table:
                rows = pd.DataFrame(result.fetchall(), columns=result.keys())
                rows = AstropyTable.from_pandas(rows)
            elif return_array:
                rows = np.array(result.fetchall())
            else:
                rows = result.fetchall()
        # ---------------------------------------------------------------------
        return rows

    def set(self, columns: Optional[Union[str, List[str]]] = None,
            values: Optional[Union[str, List[str]]] = None,
            tablename: Optional[str] = None, condition: Optional[str] = None,
            update_dict: Optional[UpdateDict] = None):
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
        :param tablename: A str which specifies which table within the
                          database to retrieve data from.  If there is only
                          one table to pick from, this may be left as None
                          to use it automatically.
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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # ---------------------------------------------------------------------
        # get a list of the unique columns
        unique_cols = self._unique_cols(tablename)
        # ---------------------------------------------------------------------
        # create an update query statement
        update_query = sqlalchemy.update(sqltable)
        # ---------------------------------------------------------------------
        # create a dictionary of the columns and values
        if columns is None:
            columns = list(update_dict.keys())
        if columns == '*':
            columns = [col.name for col in sqltable.columns]
        # ---------------------------------------------------------------------
        # add the hash column
        if len(unique_cols) > 0:
            columns, values = drs_db._hash_col(columns, values, unique_cols)
            # condition based on only on unique_col
            condition = '{0}={1}'.format(columns[-1], values[-1])
        # ---------------------------------------------------------------------
        # make the update dictionary
        if update_dict is None and values is not None:
            update_dict = {col: val for col, val in zip(columns, values)}
        # ---------------------------------------------------------------------
        # add condition
        if condition is not None:
            update_query = update_query.where(sqlalchemy.text(condition))
        # ---------------------------------------------------------------------
        # add values to update
        update_query.values(update_dict)
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as conn:
            conn.execute(update_query)

    def add_row(self, values: Optional[List[object]] = None,
                tablename: Optional[str] = None,
                columns: Union[str, List[str]] = "*",
                insert_dict: Optional[UpdateDict] = None):
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
        :param tablename: A str which specifies which table within the
                          database to retrieve data from.  If there is only
                          one table to pick from, this may be left as None to
                          use it automatically.
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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # ---------------------------------------------------------------------
        # get a list of the unique columns
        unique_cols = self._unique_cols(tablename)
        # ---------------------------------------------------------------------
        # create an update query statement
        insert_query = sqlalchemy.insert(sqltable)
        # ---------------------------------------------------------------------
        # create a dictionary of the columns and values
        if columns is None:
            columns = list(insert_dict.keys())
        if columns == '*':
            columns = [col.name for col in sqltable.columns]
        # ---------------------------------------------------------------------
        # make the update dictionary
        if insert_dict is None and values is not None:
            insert_dict = {col: val for col, val in zip(columns, values)}
        # ---------------------------------------------------------------------
        # add the hash column
        if len(unique_cols) > 0:
            columns, values = drs_db._hash_col(columns, values, unique_cols)
            # update update_dict
            if insert_dict is not None:
                insert_dict[columns[-1]] = values[-1]
        # ---------------------------------------------------------------------
        # add values to update
        insert_query = insert_query.values(insert_dict)
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as conn:
            conn.execute(insert_query)

    def delete_rows(self, tablename: Optional[str] = None,
                    condition: Optional[str] = None):
        """
        Delete a row from the table

        :param tablename: A str which specifies which table within the database
                          to retrieve data from.  If there is only one table to
                          pick from, this may be left as None to use it
                          automatically
        :param condition: An SQL condition string to identify the rows to be
                          modified.  This may be set to None to apply the
                          modification to all rows.

        :return: None removes row(s) from table
        """
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # ---------------------------------------------------------------------
        # set up a delete query
        delete_query = sqlalchemy.delete(sqltable)
        # ---------------------------------------------------------------------
        # add condition
        if condition is not None:
            delete_query = delete_query.where(sqlalchemy.text(condition))
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as conn:
            conn.execute(delete_query)

    def delete_table(self, tablename: str):
        """
        Deletes a table from the database, erasing all contained data
        permenantly!

        :param tablename: The name of the table to be deleted.
                          See Database.tables for a list of eligible tables.
        """
        func_name = __NAME__ + '.Database.delete_table()'
        # make sure table is a string
        if not isinstance(tablename, str):
            # log error: table 'name' must be a string
            ecode = '00-002-00039'
            emsg = drs_base.BETEXT[ecode]
            eargs = [self.url, tablename, func_name]
            # log base error
            raise drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                      exceptionname='DatabaseError',
                                      exception=func_name)
        # ---------------------------------------------------------------------
        # check to see if table name exists in database
        inspector = sqlalchemy.inspect(self.engine)
        # cannot delete if table does not exist
        if not inspector.has_table(tablename):
            return
        # ---------------------------------------------------------------------
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as _:
            sqltable.drop(self.engine)

    def rename_table(self, old_name: str, new_name: str):
        """
        Renames a table.

        :param old_name: The name of the table to be deleted. See
                         Database.tables for a list of eligible tables.
        :param new_name: The new name of the table. This must not be already
                         taken or an SQL keyword.
        """
        # ---------------------------------------------------------------------
        # define command
        # TODO: Question: Does this work with all SQL dialects?
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        command = 'ALTER TABLE {} RENAME TO {}'.format(old_name, new_name)
        # ---------------------------------------------------------------------
        # execute the query
        with self.engine.begin() as conn:
            conn.execute(sqlalchemy.text(command))
        # ---------------------------------------------------------------------
        # if old_name is the current tablename then change it the new_name
        if old_name == self.tablename:
            self.tablename = new_name

    def colnames(self, columns: str,
                 tablename: Optional[str] = None) -> List[str]:
        """
        Get the column names from table (i.e. deal with * or columns separated
        by commas)

        :param columns: str, comma separate set of column names or *
        :param tablename: str, the name of the Table

        :return: list of strings, the column names
        """
        # define the meta data
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine)
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata)
        # ---------------------------------------------------------------------
        # create a dictionary of the columns and values
        if columns == '*':
            columns = [col.name for col in sqltable.columns]
        else:
            columns.split(',')
        # ---------------------------------------------------------------------
        return columns

    def add_from_pandas(self, df: pd.DataFrame, tablename: Optional[str] = None,
                        if_exists: str = 'append', index: bool = False,
                        unique_cols: Optional[List[str]] = None):
        """
        Use pandas to add rows to database

        :param df: pandas dataframe, the pandas dataframe to add to the database
        :param tablename: A str which specifies which table within the database
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
        # ---------------------------------------------------------------------
        # deal with empty unique column list
        if unique_cols is not None and len(unique_cols) == 0:
            unique_cols = None
        # need to add uhash column
        if unique_cols is not None:
            df = drs_db._hash_df(df, unique_cols)
        # ---------------------------------------------------------------------
        # try to add pandas dataframe to table
        with self.engine.begin() as conn:
            try:
                df.to_sql(tablename, conn, if_exists=if_exists, index=index)
                # pandas removes uniqueness of columns - need to readd this
                #   constraint if unique_cols is not None
                if unique_cols is not None and len(unique_cols) > 0:
                    self._add_unique_uhash_col(tablename)
            except Exception as e:
                # log error: Pandas.to_sql
                ecode = '00-002-00047'
                emsg = drs_base.BETEXT[ecode]
                eargs = [type(e), str(e), func_name, self.url, tablename,
                         func_name]
                # log base error
                raise drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                          exceptionname='AperoDatabaseError',
                                          exception=AperoDatabaseError)

    def backup(self):
        # TODO: Can we add this?
        emsg = 'The backup method is not implemented'
        NotImplemented(emsg)

    def reload_from_backup(self):
        # TODO: Can we add this?
        emsg = 'The reload_from_backup method is not implemented'
        NotImplemented(emsg)

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------
    def _infer_table_(self, tablename: Optional[str] = None) -> str:
        """
        Infer the table from the database

        :param tablename: str, the name of the table

        :return: sqlalchemy.Table
        """
        # set function name
        func_name = '{0}.{1}.{2}()'.format(__NAME__, self.classname,
                                           '_infer_table_')
        # ---------------------------------------------------------------------
        # use an inspector to get a list of table names
        inspector = sqlalchemy.inspect(self.engine)
        # get the table names
        table_names = inspector.get_table_names()
        # ---------------------------------------------------------------------
        # if we have a tablename set the return this
        if self.tablename is not None:
            if self.tablename in table_names:
                return self.tablename
        # if the argument tablename is a string return this
        if isinstance(tablename, str):
            if tablename in table_names:
                return tablename
        # ---------------------------------------------------------------------
        if len(table_names) != 1:
            # log error: pick one -- table cannot be None
            ecode = '00-002-00041'
            emsg = drs_base.BETEXT[ecode]
            # get string list of tables
            strtables = ''
            for _table in table_names:
                strtables += '\n\t\t- ' + _table
            # add error args
            eargs = [self.url, strtables, func_name]
            # log base error
            raise drs_base.base_error(ecode, emsg, 'error', args=eargs,
                                      exceptionname='AperoDatabaseError',
                                      exception=AperoDatabaseError)
        return table_names[0]

    def _add_unique_uhash_col(self, tablename: Optional[str] = None):
        """
        Add a unique hash column to the table

        :param tablename: str, the name of the table
        """
        # TODO: Test if this actually works
        # ---------------------------------------------------------------------
        # get the table
        table = self._infer_table_(tablename)
        # ---------------------------------------------------------------------
        # add a unique hash column
        with self.engine.begin() as conn:
            # need to make sure UHASH is a VARCHAR(64)
            command = 'ALTER TABLE {0} MODIFY COLUMN {1} VARCHAR(64);'
            command = command.format(table, UHASH_COL)
            # run the modify column command
            conn.execute(command)
            # now create sql command to make the column unique
            command = "ALTER TABLE {0} ADD UNIQUE ({1});"
            command = command.format(table, UHASH_COL)
            # run the modify column command
            conn.execute(command)

    def _unique_cols(self, tablename: Optional[str] = None,
                     columns: Optional[List[sqlalchemy.Column]] = None
                     ) -> List[str]:
        """
        Get the unique columns from the table

        :return: list of strings
        """
        # ---------------------------------------------------------------------
        # deal with having columns
        if columns is not None:
            # find all unique columns
            unique_cols = []
            for _col in columns:
                if _col.unique:
                    unique_cols.append(_col.name)
            # return a list of unique columns
            return unique_cols
        # ---------------------------------------------------------------------
        # define an inspector
        inspector = sqlalchemy.inspect(self.engine)
        # find all unique columns
        unique_cols = set()
        for _entry in inspector.get_unique_constraints(tablename):
            for _col in _entry['column_names']:
                unique_cols.add(_col)
        # return a list of unique columns
        return list(unique_cols)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    _db_uri = 'mysql+pymysql://spirou:Covid19!@rali:3306/test'

    _database = AperoDatabase(_db_uri)

    _database.add_database()

    _columns = [sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column('name', sqlalchemy.String(128), unique=True),
                sqlalchemy.Column('age', sqlalchemy.Integer)]
    _indexes = [sqlalchemy.Index('idx_users_name_age', 'name', 'age')]
    _uniques = [sqlalchemy.UniqueConstraint('name', name='uix_name')]

    _database.delete_table('users')
    _database.delete_table('users2')
    _database.add_table('users', _columns, _indexes)

    _database.tablename = 'users'

    _database.add_row(insert_dict=[{'id': 1, 'name': 'test1', 'age': 11},
                                   {'id': 2, 'name': 'test2', 'age': 22},
                                   {'id': 3, 'name': 'test3', 'age': 33}])

    _database.add_row(insert_dict={'id': 4, 'name': 'test4', 'age': 44})

    _rows = _database.get(columns='id,name,age')

    # create a pandas dataframe
    df = pd.DataFrame()
    # add id, name, age columns and add test values
    df['id'] = [101, 102, 103, 104]
    df['name'] = ['test101', 'test102', 'test103', 'test104']
    df['age'] = [110, 220, 330, 440]

    # test the add from pandas functionality
    _database.add_from_pandas(df, 'users', if_exists='append', index=False)



# =============================================================================
# End of code
# =============================================================================
