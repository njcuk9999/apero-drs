"""
Package containing all constants Classes and functionality

DRS Import Rules:

- only from apero.lang

Created on 2019-01-17 at 14:09

@author: cook
"""
from astropy import units as uu
import numpy as np
import os
from pathlib import Path
import sys
import traceback
from typing import Any, List, Tuple, Union

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_exceptions
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero import lang

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'constant_functions.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# get the Drs Exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get the text entry
textentry = lang.textentry
# get simple types
SIMPLE_TYPES = base.SIMPLE_TYPES
SIMPLE_STYPES = base.SIMPLE_STYPES
VALID_CHARS = base.VALID_CHARS
# get display function
display_func = drs_misc.display_func


# =============================================================================
# Define classes
# =============================================================================
class Const:
    """
    Constant class - drs constants are instances of this

    e.g. stores information to read and check config/constant file constants

    """
    # set class name
    class_name = 'Const'

    def __init__(self, name: str, value: Any = None,
                 dtype: Union[None, str, type] = None,
                 dtypei: Union[None, str, type] = None,
                 options: List = None,
                 maximum: Union[int, float, None] = None,
                 minimum: Union[int, float, None] = None,
                 source: Union[str, None] = None,
                 unit: Union[uu.Unit] = None, default: Any = None,
                 datatype: Union[type, None] = None,
                 dataformat: Union[str, None] = None,
                 group: Union[str, None] = None, user: bool = False,
                 active: bool = False, description: Union[str, None] = None,
                 author: Union[str, List[str], None] = None,
                 parent: Union[str, None] = None):
        """
        Construct the constant instance

        :param name: str, name of the constant
        :param value: object, value of the constant
        :param dtype: type, data type of the constant
        :param dtypei: type, data type of list/dictionary elements
        :param options: list of objects, the allowed values for the constant
        :param maximum: the maximum value allowed for the constant
        :param minimum: the minimum value allowed for the constant
        :param source: str, the source file of the constant
        :param unit: astropy unit, the units of the constant
        :param default: default value of the constant
        :param datatype: str, an additional datatype i.e. used to pass to
                         another function e.g. a time having data type "MJD"
        :param dataformat: str, an additional data format i.e. used to pass to
                           another function e.g. a time having data format float
        :param group: str, the group this constant belongs to
        :param user: bool, whether the constant is a user constant
        :param active: bool, whether the constant is active in constant files
                       (for user config file generation)
        :param description: str, the description for this constant
        :param author: str, the author of this constant (i.e. who to contact)
        :param parent: str, the parent of this constant (if a constant is
                       related to or comes from another constant)

        :returns: None (constructor)
        """
        # set function name
        func_name = display_func(None, '__init__', __NAME__, self.class_name)
        # set the name of the constant
        self.name = name
        # set the value of the constant
        self.value = value
        # set the data type of the constant
        self.dtype = dtype
        # set the data type of list/dictionary elements
        self.dtypei = dtypei
        # set the allowed values for the constant
        self.options = options
        # set the minimum and maximum values of the constant
        self.maximum, self.minimum = maximum, minimum
        # set the kind (Const or Keyword)
        self.kind = 'Const'
        # set the source file of the constant
        if source is None:
            eargs = [self.class_name, self.name]
            raise DrsCodedException('00-003-00034', level='error',
                                    targs=eargs, func_name=func_name)
        else:
            self.source = source
        # set the units of the constant (astropy units)
        self.unit = unit
        # set the default value of the constant
        self.default = default
        # set an additional datatype i.e. used to pass to another function
        #    e.g. a time having data type "MJD"
        self.datatype = datatype
        # set an additional data format i.e. used to pass to another function
        #    e.g. a time having data format float
        self.dataformat = dataformat
        # set the group this constant belongs to
        self.group = group
        # set whether the constant is a user constant
        self.user = user
        # set whether the constant is active in constant files (for users)
        self.active = active
        # set the description for this constant
        self.description = description
        # set the author of this constant (i.e. who to contact)
        self.author = author
        # set the parent of this constant (if a constant is related to or
        #   comes from another constant)
        self.parent = parent
        # set true value
        self.true_value = None

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

    def __str__(self) -> str:
        """
        Return string represenation of Const class
        :return:
        """
        return 'Const[{0}]'.format(self.name)

    def validate(self, test_value: Any = None, quiet: bool = False,
                 source: Union[str, None] = None) -> Union[bool, Any]:
        """
        Validate a value either from definition (when `test_value` is None)
        or test a new value for this constant instance (`test_value` set).
        Updates `self.true_value`

        :param test_value: object, if set test this value against the defined
                           parameters of this constant instance.
                           If not set uses the value (self.value) and tests
                           this value
        :param quiet: bool, if True logs statements when constant passes or
                      fails, if False may only log in debug mode
        :param source: string, the source code/recipe of the constant (only
                       important if `test_value` is set

        :type test_value: object
        :type quiet: bool
        :type source: Union[str, None]
        :return: If `test_value` was set returns value in correct datatype
                 else if unset returns True if value is valid. If not valid
                 exception is raised.
        :rtype: Union[bool, object]
        :raises DrsCodedError: if value is not valid
        """
        # set function name
        _ = display_func(None, 'validate', __NAME__, self.class_name)
        # deal with no test value (use value set at module level)
        if test_value is None:
            value = self.value
        else:
            value = test_value
        # deal with no source
        if source is None:
            source = self.source
        # skip validation if value is None
        if value is None:
            self.true_value = None
            return True
        # get true value (and test test_value)
        vargs = [self.name, self.dtype, value, self.dtypei, self.options,
                 self.maximum, self.minimum, ]
        vkwargs = dict(quiet=quiet, source=source)

        true_value, source = _validate_value(*vargs, **vkwargs)
        # deal with storing
        if test_value is None:
            self.true_value = true_value
            return True
        else:
            return true_value

    def copy(self, source: Union[str, None] = None) -> 'Const':
        """
        Shallow copy of constant instance

        :param source: str, the code/recipe in which constant instance was
                       copied (required for use)

        :type source: str
        :return: Const, a shallow copy of the constant
        :rtype: Const
        :raises DrsCodedException: if source is None
        """
        # set function name
        func_name = display_func(None, 'copy', __NAME__, self.class_name)
        # check that source is valid
        if source is None:
            raise DrsCodedException('00-003-00007', 'error', targs=[func_name],
                                    func_name=func_name)

        # return new copy of Const
        return Const(self.name, self.value, self.dtype, self.dtypei,
                     self.options, self.maximum, self.minimum, source=source,
                     unit=self.unit, default=self.default,
                     datatype=self.datatype, dataformat=self.dataformat,
                     group=self.group, user=self.user, active=self.active,
                     description=self.description, author=self.author,
                     parent=self.parent)

    def write_line(self, value: Any = None) -> List[str]:
        """
        Creates the lines required for a config/constant file for this constant

        i.e.
        ```
        # {DESCRIPTION}
        # dtype={DTYPE} default={DEFAULT}
        {NAME} = {VALUE}
        ```

        :param value: object, the value to add as the `value` in a
                      config/constant file.

        :return: A list of strings (lines) to add to config/constant file for
                 this constant

        :rtype: list[str]
        """
        # set function name
        _ = display_func(None, 'write_line', __NAME__, self.class_name)
        # set up line list
        lines = ['']
        # deal with value
        if value is None:
            value = self.value
        # ------------------------------------------------------------------
        # add description
        # -------------------------------------------------------------------
        # check if we have a description defined
        if not drs_text.null_text(self.description, ['', 'None']):
            description = self.description.strip().capitalize()
            # wrap long descriptions by words
            wrapdesc = drs_text.textwrap(description, 77)
            # loop around wrapped lines and add as comments
            for wline in wrapdesc:
                # add wrapped line to
                lines.append('# {0}'.format(wline))
        # if we don't have descriptions add a default one
        else:
            lines.append('# {0} [DESCRIPTION NEEDED]'.format(self.name))
        # -------------------------------------------------------------------
        # add default set up values
        # -------------------------------------------------------------------
        dline = '#\t'
        # add data type
        if self.dtype is not None:
            if self.dtype in [str, 'str']:
                dline += 'dtype=string '
            elif self.dtype in [int, 'int']:
                dline += 'dtype=int '
            elif self.dtype in [float, 'float']:
                dline += 'dtype=float '
            elif self.dtype in [bool, 'bool']:
                dline += 'dtype=bool '
            elif self.dtype == 'path':
                dline += 'dtype=file-path '
        # add maximum / minimum constraints (if present)
        if self.minimum is not None:
            dline += 'min={0} '.format(self.minimum)
        if self.maximum is not None:
            dline += 'max={0} '.format(self.maximum)
        # add default
        if self.dtype != 'path':
            dline += 'default={0} '.format(value)
        # append line to lines
        lines.append(dline.strip())
        # -------------------------------------------------------------------
        # add options if present
        # -------------------------------------------------------------------
        if self.options is not None:
            # make sure options are strings
            stroptions = list(map(lambda x: '{0}'.format(x), self.options))
            # add options string
            oline = '#\toptions = {0}'.format(', '.join(stroptions))
            # append line to lines
            lines.append(oline.strip())

        # ------------------------------------------------------------------
        # construct line to add (for user changing)
        # -------------------------------------------------------------------
        # construct line
        aline = '{0} = {1}'.format(self.name, value)
        # if not active add as comment
        if not self.active:
            aline = '# ' + aline
        # add to lines
        lines.append(aline)
        # return lines
        return lines


class Keyword(Const):
    """
    Keyword class - drs keywords are instances of this

    e.g. stores information for writing to the header:

        key  value // comment

    """
    # set class name
    class_name = 'Keyword'

    def __init__(self, name: str, key: Union[str, None] = None,
                 value: Any = None, dtype: Union[None, str, type] = None,
                 comment: Union[str, None] = None,
                 options: List = None,
                 maximum: Union[int, float, None] = None,
                 minimum: Union[int, float, None] = None,
                 source: Union[str, None] = None,
                 unit: Union[uu.Unit] = None, default: Any = None,
                 datatype: Union[type, None] = None,
                 dataformat: Union[str, None] = None,
                 group: Union[str, None] = None,
                 author: Union[str, List[str], None] = None,
                 parent: Union[str, None] = None,
                 combine_method: Union[str, None] = None):
        """
        Construct the keyword instance

        :param name: str, name of the keyword
        :param key: str, the FITS HEADER key for the keyword
        :param value: str, the FITS HEADER value for the keyword
        :param dtype: str, the data type for the keyword value
        :param comment: str, the FITS HEADER comment for the keyword
        :param options: list of objects, the allowed values for the keyword
        :param maximum: the maximum value allowed for the keyword value
        :param minimum: the minimum value allowed for the keyword value
        :param source: str, the source file of the keyword
        :param unit: astropy unit, the units of the keyword value
        :param default: default value of the keyword value
        :param datatype: str, an additional datatype i.e. used to pass to
                         another function e.g. a time having data type "MJD"
        :param dataformat: str, an additional data format i.e. used to pass to
                           another function e.g. a time having data format float
        :param group: str, the group this constant belongs to
        :param author: str, the author of this constant (i.e. who to contact)
        :param parent: Const, the parent of this constant (if a constant is
                       related to or comes from another constant)

        :type name: str
        :type key: str
        :type value: object
        :type dtype: Union[str, type]
        :type comment: str
        :type options: list[object]
        :type maximum: object
        :type minimum: object
        :type source: str
        :type unit: uu.Unit
        :type default: object
        :type datatype: str
        :type dataformat: str
        :type group: str
        :type author: str
        :type parent: Union[Const,Keyword]
        :param combine_method: str, the method used to combine this keyword
                               when combining two or more files

        :returns: None (constructor)
        """
        # set function name
        func_name = display_func(None, '__init__', __NAME__, self.class_name)
        # set the name
        self.name = name
        # set the source file of the Keyword
        if source is None:
            eargs = [self.class_name, self.name]
            raise DrsCodedException('00-003-00034', level='error',
                                    targs=eargs, func_name=func_name)
        else:
            self.source = source
        # Initialize the constant parameters (super)
        Const.__init__(self, name, value, dtype, None, options, maximum,
                       minimum, source, unit, default, datatype, dataformat,
                       group, user=False, active=False, description='',
                       author=author, parent=parent)
        # set the header key associated with this keyword (8 characters only)
        self.key = key
        # set the header comment associated with this keyword
        self.comment = comment
        # set the kind (Const or Keyword)
        self.kind = 'Keyword'
        # set the units of the Keyword (for use when reading and converting)
        self.unit = unit
        # set the default value of this constant
        self.default = default
        # set an additional datatype i.e. used to pass to another function
        #    e.g. a time having data type "MJD"
        self.datatype = datatype
        # set an additional data format i.e. used to pass to another function
        #    e.g. a time having data format float
        self.dataformat = dataformat
        # set the group this keyword belongs to
        self.group = group
        # set the author of this keyword (i.e. who to contact)
        self.author = author
        # set the parent of this keyword (if a constant/keyword is related to
        #   or comes from another constant/keyword)
        self.parent = parent
        # set the combine method
        self.combine_method = combine_method

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

    def __str__(self) -> str:
        """
        Return string represenation of Const class
        :return:
        """
        return 'Const[{0}]'.format(self.name)

    def set(self, key: str = None, value: Any = None,
            dtype: Union[None, str, type] = None,
            comment: Union[str, None] = None,
            options: List = None,
            maximum: Union[int, float, None] = None,
            minimum: Union[int, float, None] = None,
            source: Union[str, None] = None,
            unit: Union[uu.Unit] = None, default: Any = None,
            datatype: Union[type, None] = None,
            dataformat: Union[str, None] = None,
            group: Union[str, None] = None,
            author: Union[str, List[str], None] = None,
            parent: Union[str, None] = None,
            combine_method: Union[str, None] = None):
        """
        Set attributes of the Keyword instance

        :param key: str, the FITS HEADER key for the keyword
        :param value: str, the FITS HEADER value for the keyword
        :param dtype: str, the data type for the keyword value
        :param comment: str, the FITS HEADER comment for the keyword
        :param options: list of objects, the allowed values for the keyword
        :param maximum: the maximum value allowed for the keyword value
        :param minimum: the minimum value allowed for the keyword value
        :param source: str, the source file of the keyword
        :param unit: astropy unit, the units of the keyword value
        :param default: default value of the keyword value
        :param datatype: str, an additional datatype i.e. used to pass to
                         another function e.g. a time having data type "MJD"
        :param dataformat: str, an additional data format i.e. used to pass to
                           another function e.g. a time having data format float
        :param group: str, the group this constant belongs to
        :param author: str, the author of this constant (i.e. who to contact)
        :param parent: Const, the parent of this constant (if a constant is
                       related to or comes from another constant)
        :param combine_method: str, the method used to combine this keyword
                               when combining two or more files

        :type key: str
        :type value: object
        :type dtype: object
        :type comment: str
        :type options: list[object]
        :type maximum: object
        :type minimum: object
        :type source: str
        :type unit: uu.Unit
        :type default: object
        :type datatype: str
        :type dataformat: str
        :type group: str
        :type author: str
        :type parent: Union[Const,Keyword]
        :type combine_method: str

        :returns: None
        """
        # set function name
        _ = display_func(None, 'set', __NAME__, self.class_name)
        # set the header key associated with this keyword
        if key is not None:
            self.key = key
        # set the header value associated with this keyword
        if value is not None:
            self.value = value
        # set the data type associated with this keyword
        if dtype is not None:
            self.dtype = dtype
        # set the header comment associated with this keyword
        if comment is not None:
            self.comment = comment
        # set the allowed values for tis keyword
        if options is not None:
            self.options = options
        # set the units for this keyword
        if unit is not None:
            self.unit = unit
        # set the maximum value for this keyword
        if maximum is not None:
            self.maximum = maximum
        # set the minimum value for this keyword
        if minimum is not None:
            self.minimum = minimum
        # set the default value for this keyword
        if default is not None:
            self.default = default
        # set an additional datatype i.e. used to pass to another function
        #    e.g. a time having data type "MJD"
        if datatype is not None:
            self.datatype = datatype
        # set an additional data format i.e. used to pass to another function
        #    e.g. a time having data format float
        if dataformat is not None:
            self.dataformat = dataformat
        # set the source for this keyword
        if source is not None:
            self.source = source
        # set the group this constant belongs to
        if group is not None:
            self.group = group
        # set the author of this constant (i.e. who to contact)
        if author is not None:
            self.author = author
        # set the parent of this constant (if a constant is related to or
        #   comes from another constant)
        if parent is not None:
            self.parent = parent
        # set the combine method for this keyword
        if combine_method is not None:
            self.combine_method = combine_method

    def validate(self, test_value: Any = None, quiet: bool = False,
                 source: Union[str, None] = None) -> Union[bool, Any]:
        """
        Validate a value either from definition (when `test_value` is None)
        or test a new value for this keyword instance (`test_value` set).
        Updates `self.true_value`

        `true_value` is a keyword store i.e.:

        `[key, value, comment]`

        for use in FITS HEADERS

        :param test_value: object, if set test this value against the defined
                           parameters of this keyword instance.
                           If not set uses the value (self.value) and tests
                           this value
        :param quiet: bool, if True logs statements when keyword passes or
                      fails, if False may only log in debug mode
        :param source: string, the source code/recipe of the keyword (only
                       important if `test_value` is set

        :type test_value: object
        :type quiet: bool
        :type source: Union[str, None]
        :return: If `test_value` was set returns keyword store
                 else if unset returns True if value is valid. If not valid
                 exception is raised.
        :rtype: Union[bool, object]
        :raises DrsCodedException: if value is not valid
        """
        # set function name
        func_name = display_func(None, 'validate', __NAME__, self.class_name)
        # deal with no test value (use value set at module level)
        if test_value is None:
            value = self.value
        else:
            value = test_value
        # deal with no source
        if source is None:
            source = self.source
        # get true value (and test test_value)
        vargs = [self.name, self.dtype, value, self.dtypei, self.options,
                 self.maximum, self.minimum, ]
        vkwargs = dict(quiet=quiet, source=source)
        true_value, source = _validate_value(*vargs, **vkwargs)
        # deal with no comment
        if self.comment is None:
            self.comment = ''
        # need a key
        if self.key is None:
            raise DrsCodedException('00-003-00035', 'error', targs=[self.name],
                                    func_name=func_name)

        # construct true value as keyword store
        true_value = [self.key, true_value, self.comment]
        # deal with storing
        if test_value is None:
            self.true_value = true_value
            return True
        else:
            return true_value

    def copy(self, source: Union[str, None] = None) -> 'Keyword':
        """
        Shallow copy of keyword instance

        :param source: str, the code/recipe in which keyword instance was
                       copied (required for use)

        :type source: str
        :return: Keyword, a shallow copy of the keyword
        :rtype: Keyword
        :raises DrsCodedException: if source is None
        """
        # set function name
        func_name = display_func(None, 'copy', __NAME__, self.class_name)
        # check that source is valid
        if source is None:
            raise DrsCodedException('00-003-00008', 'error', targs=[func_name],
                                    func_name=func_name)
        # return new copy of Const
        return Keyword(self.name, self.key, self.value, self.dtype,
                       self.comment, self.options, self.maximum,
                       self.minimum, source=source, unit=self.unit,
                       default=self.default, datatype=self.datatype,
                       dataformat=self.dataformat, group=self.group,
                       author=self.author, parent=self.parent,
                       combine_method=self.combine_method)


class CKCaseINSDict(base_class.CaseInsensitiveDict):
    def __init__(self, *arg, **kw):
        """
        Construct the Const/Keyword elements case insensitive dictionary class
        :param arg: arguments passed to dict
        :param kw: keyword arguments passed to dict
        """
        # set class name
        self.class_name = 'CKCaseINSDict'
        # set function name
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # super from dict
        super(CKCaseINSDict, self).__init__(*arg, **kw)

    def __getitem__(self, key: str) -> Union[None, Const, Keyword]:
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
        return super(CKCaseINSDict, self).__getitem__(key)

    def __setitem__(self, key: str, value: Union[None, Const, Keyword]):
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
        super(CKCaseINSDict, self).__setitem__(key, value)

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


# =============================================================================
# Define complex type returns
# =============================================================================
GenConsts = Tuple[List[str], Union[List[Const], List[Keyword]]]


# =============================================================================
# Define functions
# =============================================================================
def generate_consts(modulepath: str) -> GenConsts:
    """
    Get all Const and Keyword instances from a module - basically load
    constants from a python file

    :param modulepath: str, the module name and location

    :type modulepath: str

    :return: the keys (Const/Keyword names) and their respective instances
    :rtype: tuple[list[str], list[Const, Keyword]]
    :raises DrsCodedException: if module name is not valid
    """
    # set function name
    func_name = display_func(None, 'generate_consts', __NAME__)
    # get the import module class
    module = import_module(func_name, modulepath)
    # get the correct module for this class
    mod = module.get()
    # get keys and values
    keys, values = list(mod.__dict__.keys()), list(mod.__dict__.values())
    # storage for all values
    all_list, new_keys, new_values = [], [], []
    # loop around keys
    for it in range(len(keys)):
        # get this iterations values
        key, value = keys[it], values[it]
        # skip any that do not have a "kind" attribute
        if not hasattr(value, "kind"):
            continue
        # check the value of "kind"
        if value.kind not in ['Const', 'Keyword']:
            continue
        # now append to list
        new_keys.append(key)
        new_values.append(value)
    # return
    return new_keys, new_values


def import_module(func: str, modulepath: str, full: bool = False,
                  quiet: bool = False) -> base_class.ImportModule:
    """
    Import a module given a module path

    :param func: str, the function where import_module was called
    :param modulepath: str, the
    :param full: bool, if True, assumes modulepath is the full path
    :param quiet: bool, if True raises a ValueError instead of a
                  DrsCodedException

    :type func: str
    :type modulepath: str
    :type full: bool
    :type quiet: bool

    :raises: DrsCodedException - if module path is not valid (and quiet=False)
    :raises: ValueError - if module path is not valid (and quiet=True)

    :return: the imported module instance
    """
    # set function name (cannot break here --> no access to inputs)
    if func is None:
        # set function name
        func_name = display_func(None, 'import_module', __NAME__)
    else:
        func_name = str(func)
    # deal with getting module
    if full:
        modfile = modulepath
        moddir = ''
    else:
        # get module name and directory
        modfile = os.path.basename(modulepath).replace('.py', '')
        moddir = os.path.dirname(modulepath)
    # import module
    try:
        if modfile in sys.modules:
            del sys.modules[modfile]
        if not full:
            sys.path.insert(0, moddir)
        # get name for import module class
        name = modfile.split('.')[-1]
        # construct class and get module
        mod = base_class.ImportModule(name, modfile)
        mod.get()
        # remove mod directory from sys.path (if not full)
        if not full:
            sys.path.remove(moddir)
        # return
        return mod
    except Exception as e:
        string_trackback = traceback.format_exc()
        # report error
        eargs = [modfile, moddir, func_name, type(e), e, str(string_trackback)]
        # deal with quiet return vs normal return
        if quiet:
            raise ValueError(textentry('00-000-00003', args=eargs))
        else:
            raise DrsCodedException('00-000-00003', 'error', targs=eargs,
                                    func_name=func_name)


def get_constants_from_file(filename: str) -> Tuple[List[str], List[str]]:
    """
    Read config file and convert to key, value pairs
        comments have a '#' at the start
        format of variables:   key = value

    :param filename: string, the filename (+ absolute path) of file to open

    :type: str

    :return keys: list of strings, upper case strings for each variable
    :return values: list of strings, value of each key

    :raises DrsCodedException: if there is a profile read constants from file
    """
    # set function name (cannot break here --> no access to inputs)
    _ = display_func(None, 'get_constants_from_file', __NAME__)
    # first try to reformat text file to avoid weird characters
    #   (like mac smart quotes)
    _validate_text_file(filename)
    # read raw config file as strings
    raw = drs_text.load_text_file(filename, comments='#', delimiter='=')
    # check that we have lines in config file
    if len(raw) == 0:
        return [], []
    elif len(raw.shape) == 1:
        single = True
    else:
        single = False
    # check that we have opened config file correctly
    try:
        # check how many rows we have
        lraw = raw.shape[0]
    except TypeError:
        return [], []
    # loop around each variable (key and value pairs)
    if single:
        key = raw[0].strip().strip("'").strip('"')
        value = raw[1].strip().strip("'").strip('"')
        keys = [key]
        values = [value]
    else:
        keys, values = [], []
        for row in range(lraw):
            # remove whitespaces and quotation marks from start/end
            key = raw[row, 0].strip().strip("'").strip('"')
            value = raw[row, 1].strip().strip("'").strip('"')
            # add key.upper() to keys
            keys.append(key.upper())
            # add value to values
            values.append(value)
    # return keys and values
    return keys, values


def update_file(filename: str, dictionary: dict):
    """
    Updates a config/constants file with key/value pairs in the `dictionary`
    If key not found in config/constants file does not add key/value to file

    :param filename: str, the config/constants file (absolute path)
    :param dictionary: dict, the dictionary containing the key/value pairs
                       to update in the config/constants file

    :type filename: str
    :type dictionary: dict
    :return: None
    :raises DrsCodedException: if we cannot read filename
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.update_file()'
    # open file
    try:
        # read the lines
        with open(filename, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        eargs = [filename, func_name, type(e), e]
        raise DrsCodedException('00-004-00003', 'error', targs=eargs,
                                func_name=func_name)
    # convert lines to char array
    clines = np.char.array(lines).strip()
    # loop through keys in dictionary
    for key in dictionary:
        # get value
        value = dictionary[key]
        # create replacement string
        rstring = '{0} = {1}\n'.format(key, value)
        # find any line that starts with
        mask = clines.startswith(key + ' = ')
        # if we have this entry update it
        if np.sum(mask) > 0:
            # get line numbers
            linenumbers = np.where(mask)[0]
            # loop around line numbers and replace
            for linenumber in linenumbers:
                lines[linenumber] = rstring
    # open file
    try:
        # write the lines
        with open(filename, 'w') as f:
            f.writelines(lines)
    except Exception as e:
        eargs = [filename, func_name, type(e), e]
        raise DrsCodedException('00-004-00004', 'error', targs=eargs,
                                func_name=func_name)


# =============================================================================
# Define private functions
# =============================================================================
def _test_dtype(name: str, invalue: Any, dtype: Union[str, type],
                source: str, quiet: bool = False) -> Any:
    """
    Test the data type of a variable `invalue`

    :param name: str, the name of the variable to test
    :param invalue: str, the value of the variable to test
    :param dtype: str, the data type to test of the
    :param source: str, the source of the variable
    :param quiet: bool, if True raises exceptions if there is an error

    :type name: str
    :type invalue: object
    :type dtype: Union[str, type]
    :type source: str
    :type quiet: bool

    :return: returns the value in the input dtype (if valid) if invalid
             returns input value (unless quiet=True then exception raised)
    :rtype: Any
    :raises DrsCodedException: if quiet=True and type invalid
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._test_dtype()'
    # if we don't have a value (i.e. it is None) don't test
    if invalue is None:
        return None
    # check paths (must be strings and must exist)
    if dtype == 'path':
        if not isinstance(invalue, str):
            if not quiet:
                eargs = [name, type(invalue), invalue, source, func_name]
                raise DrsCodedException('00-003-00009', 'error', targs=eargs,
                                        func_name=func_name)
        if not os.path.exists(invalue):
            if not quiet:
                eargs = [name, invalue, func_name]
                raise DrsCodedException('00-003-00010', 'error', targs=eargs,
                                        func_name=func_name)
        return str(invalue)
    # deal with casting a string into a list
    if (dtype is list) and isinstance(invalue, str):
        if not quiet:
            eargs = [name, invalue, source, func_name]
            raise DrsCodedException('00-003-00011', 'error', targs=eargs,
                                    func_name=func_name)
    # now try to cast value
    try:
        outvalue = dtype(invalue)
    except Exception as e:
        if not quiet:
            eargs = [name, dtype, invalue, type(invalue), type(e), e,
                     source, func_name]
            raise DrsCodedException('00-003-00012', 'error', targs=eargs,
                                    func_name='error')
        outvalue = invalue
    # return out value
    return outvalue


def _validate_value(name: str, dtype: Union[str, type, None],
                    value: Any, dtypei: Union[str, type, None],
                    options: list, maximum: Union[int, float, None],
                    minimum: Union[int, float, None], quiet: bool = False,
                    source: Union[None, str] = None) -> Tuple[Any, str]:
    """
    Checks whether a variable `value` is valid based on the specifications given

    :param name: str, the name of the variable
    :param dtype: str, the required data type of the variable
    :param value: object, the value of the variable
    :param dtypei: type, the required data type of
    :param options: list of objects, the allowed values for the keyword
    :param maximum: the maximum value allowed for the keyword value
    :param minimum: the minimum value allowed for the keyword value
    :param quiet: bool, if True raises exceptions if there is an error
    :param source: str, the source file of the keyword

    :type name: str
    :type dtype: Union[str, type]
    :type dtypei: Union[str, type]
    :type value: object
    :type options: list[object]
    :type quiet: bool
    :type source: str

    :return: returns the value in the input dtype and the source of that
             value
    :rtype: tuple[object, str]
    :raises DrsCodedException: if quiet=True and type invalid
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._validate_value()'
    # deal with no source
    if source is None:
        source = 'Unknown ({0})'.format(func_name)
    # ---------------------------------------------------------------------
    # check that we only have simple dtype
    if dtype is None:
        if not quiet:
            eargs = [name, source, func_name]
            raise DrsCodedException('00-003-00013', 'error', targs=eargs,
                                    func_name=func_name)
    if (dtype not in SIMPLE_TYPES) and (dtype != 'path'):
        if not quiet:
            eargs = [name, ', '.join(SIMPLE_STYPES), source, func_name]
            raise DrsCodedException('00-003-00014', 'error', targs=eargs,
                                    func_name=func_name)
    # ---------------------------------------------------------------------
    # Check value is not None
    if value is None:
        if not quiet:
            eargs = [name, source, func_name]
            raise DrsCodedException('00-003-00015', 'error', targs=eargs,
                                    func_name=func_name)
    # ---------------------------------------------------------------------
    # check bools
    if dtype is bool:
        if isinstance(value, str):
            if value.lower() in ['1', 'true']:
                value = True
            elif value.lower() in ['0', 'false']:
                value = False
        if value not in [True, 1, False, 0]:
            if not quiet:
                eargs = [name, value, source, func_name]
                raise DrsCodedException('00-003-00016', 'error', targs=eargs,
                                        func_name=func_name)
    # ---------------------------------------------------------------------
    # Check if dtype is correct
    true_value = _test_dtype(name, value, dtype, source, quiet=quiet)
    # ---------------------------------------------------------------------
    # check dtypei if list
    if dtype == list:
        if dtypei is not None:
            newvalues = []
            for value in true_value:
                newvalues.append(_test_dtype(name, value, dtypei, source))
            true_value = newvalues
    # ---------------------------------------------------------------------
    # check options if not a list
    if dtype in [str, int, float] and options is not None:
        if true_value not in options:
            if not quiet:
                stroptions = ['"{0}"'.format(opt) for opt in options]
                eargs = [name, ', '.join(stroptions), true_value, source,
                         func_name]
                raise DrsCodedException('00-003-00017', 'error', targs=eargs,
                                        func_name=func_name)
    # ---------------------------------------------------------------------
    # check limits if not a list or str or bool
    if dtype in [int, float]:
        if maximum is not None:
            if true_value > maximum:
                if not quiet:
                    eargs = [name, maximum, true_value, source, func_name]
                    raise DrsCodedException('00-003-00018', 'error',
                                            targs=eargs, func_name=func_name)
        if minimum is not None:
            if true_value < minimum:
                if not quiet:
                    eargs = [name, minimum, true_value, source, func_name]
                    raise DrsCodedException('00-003-00019', 'error',
                                            targs=eargs, func_name=func_name)
    # return true value
    return true_value, source


def _validate_text_file(filename: Union[str, Path],
                        comments: str = '#'):
    """
    Validation on any text file, makes sure all non commented lines have
    valid characters (i.e. are either letters, digits, punctuation or
    whitespaces as defined by string.ascii_letters, string.digits,
    string.punctuation and string.whitespace.

    A ConfigException is raised if invalid character(s) found

    :param filename: string, name and location of the text file to open
    :param comments: char (string), the character that defines a comment line

    :type filename: str
    :type comments: str

    :return None:
    :raises DrsCodedException: If text file is invalid
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._validate_text_file()'
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # loop around each line in text file
    for l_it, line in enumerate(lines):
        # ignore blank lines
        if len(line.strip()) == 0:
            continue
        # ignore comment lines (don't care about characters in comments)
        if line.strip()[0] == comments:
            continue
        # loop through each character in line and check if it is a valid
        # character
        eargs = [filename, func_name]
        emsg = textentry('00-003-00020', args=eargs)
        invalid = False
        for char in line:
            if char not in VALID_CHARS:
                invalid = True
                emsg += textentry('00-003-00021', args=[char, l_it + 1])
        # only raise an error if invalid is True (if we found bad characters)
        if invalid:
            raise DrsCodedException('00-003-00020', 'error', message=emsg,
                                    func_name=func_name)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
