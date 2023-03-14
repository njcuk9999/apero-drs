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

UpdateDict = Union[List[Dict[str, Any]], Dict[str, Any]]

# =============================================================================
# Define functions
# =============================================================================
class Database:
    def __init__(self, url, verbose: bool = False,
                 tablename: Optional[str] = None):
        """

        """
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
        self.engine = sqlalchemy.create_engine(self.url, echo=self.verbose )

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

    def add_table(self, name: str,
                  columns: List[sqlalchemy.Column],
                  indexes: List[sqlalchemy.Index] = None):
        # define the meta data
        metadata = sqlalchemy.MetaData()
        # create the table
        _ = sqlalchemy.Table(name, metadata, *columns, *indexes)
        # create table
        metadata.create_all(self.engine)

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
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata, autoload=True,
                                    autoload_with=self.engine)
        # create a query statement
        if columns == '*':
            query = sqlalchemy.select([sqltable])
        else:
            sqlcols = [getattr(sqltable.c, col) for col in columns.split(',')]
            query = sqlalchemy.select(sqlcols)
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
        # execute the query
        with self.engine.begin() as conn:
            result = conn.execute(query)
            # get the results
            rows = result.fetchall()
        # ---------------------------------------------------------------------
        return rows

    def set(self, columns: Optional[Union[str, List[str]]] = None,
            values: Optional[Union[str, List[str]]] = None,
            tablename: Optional[str] = None, condition: Optional[str] = None,
            unique_cols: Optional[List[str]] = None,
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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata, autoload=True,
                                    autoload_with=self.engine)
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
        if unique_cols is not None:
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
                unique_cols: Optional[List[str]] = None,
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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata, autoload=True,
                                    autoload_with=self.engine)
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
        # add the hash column
        if unique_cols is not None:
            columns, values = drs_db._hash_col(columns, values, unique_cols)
            # update update_dict
            if insert_dict is not None:
                insert_dict[columns[-1]] = values[-1]
        # ---------------------------------------------------------------------
        # make the update dictionary
        if insert_dict is None and values is not None:
            insert_dict = {col: val for col, val in zip(columns, values)}
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

        :param table: A str which specifies which table within the database
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
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata, autoload=True,
                                    autoload_with=self.engine)
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

        :param name: The name of the table to be deleted.
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
        # define the meta data
        metadata = sqlalchemy.MetaData()
        # get the table name
        if tablename is None:
            tablename = self.tablename
        # create a table to fill
        sqltable = sqlalchemy.Table(tablename, metadata, autoload=True,
                                    autoload_with=self.engine)
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
        # define the meta data
        metadata = sqlalchemy.MetaData(bind=self.engine)
        # create a table to fill
        oldtable = sqlalchemy.Table(old_name, metadata, autoload=True)
        # copy the parameters of old_table to create a new table
        newtable = sqlalchemy.Table(new_name, metadata, *oldtable.columns,
                                    extend_existing=True)

        metadata.create_all(bind=self.engine, tables=[newtable])
        # execute the query
        with self.engine.begin() as conn:
            conn.execute.execute(newtable.insert().from_select(oldtable.columns,
                                                     oldtable.select()))
        metadata.drop_all(bind=self.engine, tables=[oldtable])


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    db_uri = 'mysql+pymysql://spirou:Covid19!@rali:3306/test'

    database = Database(db_uri)

    database.add_database()

    columns = [sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
               sqlalchemy.Column('name', sqlalchemy.String(128), unique=True),
               sqlalchemy.Column('age', sqlalchemy.Integer)]
    indexes = [sqlalchemy.Index('idx_users_name_age', 'name', 'age')]

    database.delete_table('users')
    database.add_table('users', columns, indexes)

    database.tablename = 'users'

    database.add_row(insert_dict=[{'id': 1, 'name': 'test1', 'age': 11},
                                  {'id': 2, 'name': 'test2', 'age': 22},
                                  {'id': 3, 'name': 'test3', 'age': 33}])

    database.add_row(insert_dict={'id': 4, 'name': 'test4', 'age': 44})

    rows = database.get(columns='id,name,age')

    database.rename_table('users', 'users2')



# =============================================================================
# End of code
# =============================================================================
