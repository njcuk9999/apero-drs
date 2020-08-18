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

# =============================================================================
# Define variables
# =============================================================================


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

    def __init__(self, path, verbose=False):
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
