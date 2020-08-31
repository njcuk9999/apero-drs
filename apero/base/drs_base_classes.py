#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base classes (Most typed dictionaries) go in here

Created on 2020-08-2020-08-31 16:07

@author: cook
"""
from collections import UserDict
from typing import Any, Union

from apero.base import base
from apero.base import drs_misc
from apero.base import drs_text

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


# =============================================================================
# Define Custom classes
# =============================================================================
# case insensitive dictionary
class CaseInsensitiveDict(UserDict):
    # Custom dictionary with string keys that are case insensitive
    # Note we inherit from UserDict and not dict due to problems with pickle
    #  UserDict allows __setstate__ and __getstate__ to work as expected
    #  not true for dict

    def __init__(self, *arg, **kw):
        """
        Construct the case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set class name
        self.class_name = 'CaseInsensitiveDict'
        # set function name
        _ = display_func(None, '__init__', __NAME__, self.class_name)
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
        # set function name
        _ = display_func(None, '__getitem__', __NAME__, 'CaseInsensitiveDict')
        # make key capitals
        key = drs_text.capitalise_key(key)
        # return from supers dictionary storage
        return super(CaseInsensitiveDict, self).__getitem__(key)

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
        # set function name
        _ = display_func(None, '__setitem__', __NAME__, self.class_name)
        # capitalise string keys
        key = drs_text.capitalise_key(key)
        # then do the normal dictionary setting
        super(CaseInsensitiveDict, self).__setitem__(key, value)

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
        _ = display_func(None, '__contains__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = drs_text.capitalise_key(key)
        # return True if key in keys else return False
        return super(CaseInsensitiveDict, self).__contains__(key)

    def __delitem__(self, key: str):
        """
        Deletes the "key" from CaseInsensitiveDict instance, case insensitive

        :param key: string, the key to delete from ParamDict instance,
                    case insensitive
        :type key: str

        :return None:
        """
        # set function name
        _ = display_func(None, '__delitem__', __NAME__, 'CaseInsensitiveDict')
        # capitalize key first
        key = drs_text.capitalise_key(key)
        # delete key from keys
        super(CaseInsensitiveDict, self).__delitem__(key)

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
        _ = display_func(None, 'get', __NAME__, 'CaseInsensitiveDict')
        # capitalise string keys
        key = drs_text.capitalise_key(key)
        # if we have the key return the value
        if key in self.keys():
            return self.__getitem__(key)
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
        _ = display_func(None, '__capitalise_keys__', __NAME__,
                         'CaseInsensitiveDict')
        # make keys a list
        keys = list(self.keys())
        # loop around key in keys
        for key in keys:
            # check if key is a string
            if type(key) == str:
                # get value
                value = super(CaseInsensitiveDict, self).__getitem__(key)
                # delete old key
                super(CaseInsensitiveDict, self).__delitem__(key)
                # if it is a string set it to upper case
                key = key.upper()
                # set the new key
                super(CaseInsensitiveDict, self).__setitem__(key, value)

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
        _ = display_func(None, '__init__', __NAME__, self.class_name)
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
        _ = display_func(None, '__getitem__', __NAME__, self.class_name)
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
        _ = display_func(None, '__setitem__', __NAME__, self.class_name)
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
        _ = display_func(None, '__init__', __NAME__, self.class_name)
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
        _ = display_func(None, '__getitem__', __NAME__, self.class_name)
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
        _ = display_func(None, '__setitem__', __NAME__, self.class_name)
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
        _ = display_func(None, '__init__', __NAME__, self.class_name)
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
        _ = display_func(None, '__getitem__', __NAME__, self.class_name)
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
        _ = display_func(None, '__setitem__', __NAME__, self.class_name)
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
