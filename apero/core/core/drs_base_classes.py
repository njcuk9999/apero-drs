#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base classes (Most typed dictionaries) go in here

Created on 2020-08-2020-08-31 16:07

@author: cook

import rules

only from
- apero.base.*
- apero.lang.*
- apero.core.core.drs_misc
- apero.core.core.drs_text
- apero.core.core.drs_exceptions
"""
from collections import UserDict
import importlib
import pandas as pd
from pandasql import sqldf
from typing import Any, List, Optional, Union

from apero.base import base
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core.core import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display function
display_func = drs_misc.display_func
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException


# =============================================================================
# Define Custom classes
# =============================================================================
# case insensitive dictionary
class CaseInsensitiveDict(UserDict):
    # Custom dictionary with string keys that are case insensitive
    # Note we inherit from UserDict and not dict due to problems with pickle
    #  UserDict allows __setstate__ and __getstate__ to work as expected
    #  not true for dict
    # set class name
    class_name = 'CaseInsensitiveDict'

    def __init__(self, *arg, **kw):
        """
        Construct the case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # super from dict
        super(CaseInsensitiveDict, self).__init__(*arg, **kw)
        # force keys to be capitals (internally)
        self.__capitalise_keys__()

    def __getitem__(self, key: str) -> object:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: object, the value stored at position "key"
        """
        # make key capitals
        key = drs_text.capitalise_key(key)
        # return from supers dictionary storage
        # return super(CaseInsensitiveDict, self).__getitem__(key)
        return self.data[key]

    def __setitem__(self, key: str, value: Any):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter

        :type key: str
        :type value: object

        :return: None
        """
        # capitalise string keys
        key = drs_text.capitalise_key(key)
        # then do the normal dictionary setting
        # super(CaseInsensitiveDict, self).__setitem__(key, value)
        self.data[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Method to find whether CaseInsensitiveDict instance has key="key"
        used with the "in" operator
        if key exists in CaseInsensitiveDict True is returned else False
        is returned

        :param key: string, "key" to look for in CaseInsensitiveDict instance
        :type key: str

        :return bool: True if CaseInsensitiveDict instance has a key "key",
        else False
        :rtype: bool
        """
        # set function name
        # _ = display_func('__contains__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = drs_text.capitalise_key(key)
        # return True if key in keys else return False
        # return super(CaseInsensitiveDict, self).__contains__(key)
        return key in self.data.keys()

    def __delitem__(self, key: str):
        """
        Deletes the "key" from CaseInsensitiveDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive
        :type key: str

        :return None:
        """
        # set function name
        # _ = display_func('__delitem__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = drs_text.capitalise_key(key)
        # delete key from keys
        # super(CaseInsensitiveDict, self).__delitem__(key)
        del self.data[key]

    def get(self, key: str, default: Union[None, object] = None):
        """
        Overrides the dictionary get function
        If "key" is in CaseInsensitiveDict instance then returns this value,
        else returns "default" (if default returned source is set to None)
        key is case insensitive

        :param key: string, the key to search for in ParamDict instance
                    case insensitive
        :param default: object or None, if key not in ParamDict instance this
                        object is returned

        :type key: str
        :type default: Union[None, object]

        :return value: if key in ParamDict instance this value is returned else
                       the default value is returned (None if undefined)
        """
        # set function name
        # _ = display_func('get', __NAME__, 'CaseInsensitiveDict')
        # capitalise string keys
        key = drs_text.capitalise_key(key)
        # if we have the key return the value
        if key in self.keys():
            # return self.__getitem__(key)
            return self.data[key]
        # else return the default key (None if not defined)
        else:
            return default

    def __capitalise_keys__(self):
        """
        Capitalizes all keys in ParamDict (used to make ParamDict case
        insensitive), only if keys entered are strings

        :return None:
        """
        # set function name
        # _ = display_func('__capitalise_keys__', __NAME__,
        #                  'CaseInsensitiveDict')
        # make keys a list
        keys = list(self.keys())
        # loop around key in keys
        for key in keys:
            # check if key is a string
            if type(key) == str:
                # get value
                # value = super(CaseInsensitiveDict, self).__getitem__(key)
                value = self.data[key]
                # delete old key
                # super(CaseInsensitiveDict, self).__delitem__(key)
                del self.data[key]
                # if it is a string set it to upper case
                key = key.upper()
                # set the new key
                # super(CaseInsensitiveDict, self).__setitem__(key, value)
                self.data[key] = value

    def __str__(self):
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return '{0}[UserDict]'.format(self.class_name)

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return self.__str__()


class StrCaseINSDict(CaseInsensitiveDict):
    # Case insensitive dictionary only containing strings
    def __init__(self, *arg, **kw):
        """
        Construct the string elements case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set class name
        self.class_name = 'StrCaseINSDict'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # super from dict
        super(StrCaseINSDict, self).__init__(*arg, **kw)

    def __getitem__(self, key: str) -> Union[None, str]:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: list, the value stored at position "key"
        """
        # set function name
        # _ = display_func('__getitem__', __NAME__, self.class_name)
        # return from supers dictionary storage
        # noinspection PyTypeChecker
        return list(super(StrCaseINSDict, self).__getitem__(key))

    def __setitem__(self, key: str, value: Union[None, str]):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: str, the object to set (as in dictionary) for the
                      parameter

        :type key: str
        :type value: list

        :return: None
        """
        # set function name
        # _ = display_func('__setitem__', __NAME__, self.class_name)
        # then do the normal dictionary setting
        super(StrCaseINSDict, self).__setitem__(key, list(value))

    def __str__(self):
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return '{0}[CaseInsensitiveDict]'.format(self.class_name)

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return self.__str__()


class ListCaseINSDict(CaseInsensitiveDict):
    def __init__(self, *arg, **kw):
        """
        Construct the list elements case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set class name
        self.class_name = 'ListCaseINSDict'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # super from dict
        super(ListCaseINSDict, self).__init__(*arg, **kw)

    def __getitem__(self, key: str) -> list:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: list, the value stored at position "key"
        """
        # set function name
        # _ = display_func('__getitem__', __NAME__, self.class_name)
        # return from supers dictionary storage
        # noinspection PyTypeChecker
        return list(super(ListCaseINSDict, self).__getitem__(key))

    def __setitem__(self, key: str, value: list):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter

        :type key: str
        :type value: list

        :return: None
        """
        # set function name
        # _ = display_func('__setitem__', __NAME__, self.class_name)
        # then do the normal dictionary setting
        super(ListCaseINSDict, self).__setitem__(key, list(value))

    def __str__(self):
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return '{0}[CaseInsensitiveDict]'.format(self.class_name)

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return self.__str__()


class ListDict(UserDict):
    def __init__(self, *arg, **kw):
        """
        Construct the list elements dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set class name
        self.class_name = 'ListDict'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # super from dict
        super(ListDict, self).__init__(*arg, **kw)

    def __getitem__(self, key: str) -> list:
        """
        Method used to get the value of an item using "key"
        used as x.__getitem__(y) <==> x[y]
        where key is case insensitive

        :param key: string, the key for the value returned (case insensitive)

        :type key: str

        :return value: object, the value stored at position "key"
        """
        # set function name
        # _ = display_func('__getitem__', __NAME__, self.class_name)
        # return from supers dictionary storage
        return list(super(ListDict, self).__getitem__(key))

    def __setitem__(self, key: str, value: list):
        """
        Sets an item wrapper for self[key] = value
        :param key: string, the key to set for the parameter
        :param value: object, the object to set (as in dictionary) for the
                      parameter

        :type key: str
        :type value: object

        :return: None
        """
        # set function name
        # _ = display_func('__setitem__', __NAME__, self.class_name)
        # then do the normal dictionary setting
        super(ListDict, self).__setitem__(key, value)

    def __str__(self):
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return '{0}[UserDict]'.format(self.class_name)

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return: str, the string representation
        """
        return self.__str__()


class ImportModule:
    # set class name
    class_name = 'ImportModule'


    def __init__(self, name: str, path: str, mod: Any = None):
        """
        Constructor of the import module class - this is how we can keep
        a module open (and not re-import it) but also pickle it when required

        :param name: str, the name of the module to be imported
        :param path: str, the path to the module
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # set the name of the module to be imported
        self.name = name
        # set the path to the module to be imported
        self.path = path
        # ---------------------------------------------------------------------
        # deal with mod
        if mod is not None:
            # set whether module has be imported
            self.modset = True
            # set storage for the module
            self.mod = mod
        else:
            # set whether module has be imported
            self.modset = False
            # set storage for the module
            self.mod = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        # _ = display_func('__getstate__', __NAME__, self.class_name)
        # what to exclude from state
        exclude = ['mod']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
            if key not in exclude:
                state[key] = item
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle

        :return:
        """
        # set function name
        # _ = display_func('__setstate__', __NAME__, self.class_name)
        # update dict with state
        self.__dict__.update(state)
        # now re-get module (if module is set)
        if self.modset:
            self.get()

    def __repr__(self) -> str:
        """
        String representation of import module class
        :return:
        """
        return 'ImportMod[{0}]'.format(self.name)

    def __str__(self) -> str:
        """
        String representation of import module class
        :return:
        """
        return self.__repr__()

    def get(self, force: bool = False) -> Any:
        """
        Import the module using importlib.import_module
        :return:
        """
        # set function name
        func_name = display_func('get', __NAME__, self.class_name)
        # if we already have the module set then just return it
        if self.modset and not force:
            return self.mod
        else:
            # try to import the module
            try:
                # import the module
                self.mod = importlib.import_module(self.path)
                # remember that we have imported the module
                self.modset = True
                # return module
                return self.mod
            except Exception as e:
                # forget if we have ever imported the module
                self.modset = False
                try:
                    import traceback
                    string_traceback = traceback.format_exc()
                except Exception as _:
                    string_traceback = ''
                # set exception arguments
                eargs = [self.name, self.path, func_name, type(e), str(e),
                         string_traceback]
                # raise an exception
                raise DrsCodedException('00-000-00003', level='error',
                                        targs=eargs, func_name=func_name)

    def copy(self) -> 'ImportModule':
        """
        Copy the import module class
        :return:
        """
        module = ImportModule(self.name, self.path)
        # check if module is set
        if self.modset:
            module.mod = self.mod
        # return import module instances
        return module


class PandasLikeDatabase:
    def __init__(self, data: pd.DataFrame):
        """
        Construct a database just using a pandas dataframe stored in the memory

        can be used instead of a database (when we have a static database
        loading from a dataframe is more efficient and avoids extra reads of
        the database)

        :param data: pandas.DataFrame, the pandas dataframe - usually taken
                     from a call to a database
        """
        self.namespace = dict(data=data)
        self.tablename = 'data'

    def execute(self, command: str) -> pd.DataFrame:
        """
        How we run an sql query on a pandas database

        Note the table has to be in self.namespace

        i.e. "SELECT * FROM data" requires self.namespace['data'] = self.data

        :param command: str, the sql command to run
        :return:
        """
        return sqldf(command, self.namespace)

    def count(self, condition: str = None) -> int:
        """
        Proxy for the drs_database.database count method

        :param condition: Filter results using a SQL conditions string
                       -- see examples, and possibly this
                       useful tutorial:
                           https://www.sqlitetutorial.net/sqlite-where/.
                       If None, no results will be filtered out.

        :return: int, the count
        """
        # construct basic command SELECT COUNT(*) FROM {TABLE}
        command = "SELECT COUNT(*) FROM {}".format(self.tablename)
        # deal with condition
        if condition is not None:
            command += " WHERE {} ".format(condition)
        # run command
        df = self.execute(command)
        # return result
        return int(df.iloc[0])

    def get_index_entries(self, columns: str,
                          condition: Optional[str] = None):
        """
        Proxy for index database get_entries method

        Currently only supports a columns and condition argument

        :param columns: str, the columns to return ('*' for all)
        :param condition: str or None, if set the SQL query to add
        :return:
        """
        # construct basic command SELECT {COLUMNS} FROM {TABLE}
        command = 'SELECT {0} FROM {1}'.format(columns, self.tablename)
        # deal with condition
        if condition is not None:
            command += " WHERE {} ".format(condition)
        # run command
        df = self.execute(command)
        # return the data frame
        return df

    def colnames(self, columns: str = '*') -> List[str]:
        """
        Return the list of column names

        Proxy for database.colnames

        :return: List of strings (the column names)
        """
        cnames = list(self.namespace['data'].columns)
        # if user requested all columns, return all columns
        if columns == '*':
            return cnames
        # deal with specifying columns (return just columns in database
        #   that match "columns"
        else:
            requested_columns = columns.split(',')
            # loop around requested columns and search for them in all columns
            outcolumns = []
            for rcol in requested_columns:
                if rcol.strip() in cnames:
                    outcolumns.append(rcol.strip())
            # return the output columns
            return outcolumns


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
