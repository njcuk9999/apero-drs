#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 08:53

@author: cook

only from:
    - apero.base.base
    - apero.base.drs_base
    - apero.base.drs_db
"""
from typing import Any, Dict, List, Union

from apero.base import base
from apero.core.lang import drs_lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.drs_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define variables
# =============================================================================
# get arguments for this instrument
lkwargs = drs_lang.get_instrument_args()
# get the language lookup instance (for this instrument)
LanguageLookup = drs_lang.LanguageLookup(**lkwargs)
# -----------------------------------------------------------------------------

# =============================================================================
# Define Text functions
# =============================================================================
class Text(str):
    """
    Special text container (so we can store text entry key)
    """

    def __init__(self, *args, **kwargs):
        str.__init__(*args, **kwargs)
        self.tkey = None
        self.tvalue = str(args[0])
        self.targs = None
        self.tkwargs = None
        self.t_short = ''
        self.formatted = False

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

    def __add__(self, other: Union['Text', str]):
        """
        string-like addition (returning a Text instance)

        Equivalent to x + y

        :param other: Text or str, add 'other' (y) to end of self (x)

        :return: combined string (x + y)   (self + other)
        """
        # must merge changes from other if Text instance
        if isinstance(other, Text):
            othertext = other.get_text()
        else:
            othertext = str(other)
        # make new object
        msg = Text(self.get_text() + othertext)
        # set text properties
        msg.set_text_props(self.tkey)
        return msg

    def __radd__(self, other: Union['Text', str]):
        """
        string-like addition (returning a Text instance)

        Equivalent to y + x

        :param other: Text or str, add 'other' (y) to start of self (x)

        :return: combined string (y + x)   (other + self)
        """
        # must merge changes from other if Text instance
        if isinstance(other, Text):
            othertext = other.get_text()
        else:
            othertext = str(other)
        # make new object
        msg = Text(othertext + self.get_text())
        # set text properties
        msg.set_text_props(self.tkey)
        return msg

    def __mul__(self, other: Any) -> Any:
        """
        Do not allow multiplication

        :param other: Any, anything else to multiple by
        :return:
        """
        NotImplemented('Multiply in {0}.Text not implemented'.format(__NAME__))

    def __repr__(self) -> str:
        """
        String representation of Text class

        :return: str, the string representation of the Text class
        """
        if not self.formatted:
            self.get_formatting()
        return str(self.tvalue)

    def __str__(self) -> str:
        """
        String representation of Text class

        :return: str, the string representation of the Text class
        """
        if not self.formatted:
            self.get_formatting()
        return str(self.tvalue)

    def set_text_props(self, key: str,
                       args: Union[List[Any], str, None] = None,
                       kwargs: Union[Dict[str, Any], None] = None):
        """
        Add the text properties to the Text (done so init is like str)

        :param key: str, the key (code id) for the language database
        :param args: if set a list of arguments to pass to the formatter
                     i.e. value.format(*args)
        :param kwargs: if set a dictionary of keyword arguments to pass to the
                       formatter (i.e. value.format(**kwargs)
        :return: None - updates tkey, tvalue, targs, tkwargs
        """
        self.tkey = str(key)
        # deal with arguments
        if args is not None:
            if isinstance(args, list):
                self.targs = list(args)
            else:
                self.targs = [str(args)]
        # deal with kwargs
        if kwargs is not None:
            self.tkwargs = dict(kwargs)

    def get_text(self, report: bool = False,
                 reportlevel: Union[str, None] = None) -> str:
        """
        Return the full text (with reporting if requested) for this Text
        instance - this is returned as a string instance

        if report = True:
            "X[##-###-#####]: msg.format(*self.targs, **self.tkwargs)"
        else:
            "msg.format(*self.targs, **self.tkwargs)"

        :param report: bool, - if true reports the code id of this text entry
                       in format X[##-###-#####] where X is the first
                       character in reportlevel
        :param reportlevel: str, single character describing the reporting
                            i.e. E for Error, W for Warning etc

        :return: string representation of the Text instance
        """
        # ---------------------------------------------------------------------
        # deal with report level character
        if isinstance(reportlevel, str):
            reportlevel = reportlevel[0].upper()
        else:
            reportlevel = self.t_short
        # ---------------------------------------------------------------------
        # make sure tvalue is up-to-date
        self.get_formatting()
        # ---------------------------------------------------------------------
        vargs = [reportlevel, self.tkey, self.tvalue]
        # deal with report
        if report and (self.tkey != self.tvalue):
            valuestr = '{0}[{1}]: {2}'.format(*vargs)
        else:
            valuestr = '{2}'.format(*vargs)
        # ---------------------------------------------------------------------
        return valuestr

    def get_formatting(self, force=False):
        """
        set the formatting (of self.tvalue) based on self.tkwargs and self.targs

        :param force: bool, if True then override the condition that the text
                      is already formated (self.formatted)

        :return: None, updates self.tvalue
        """
        # don't bother if already formatted
        if not force and self.formatted:
            return
        # set that we have formatted (so we don't do it again)
        self.formatted = True
        # ---------------------------------------------------------------------
        # deal with no value
        if self.tvalue is None:
            value = str(self)
        else:
            value = self.tvalue
        # ---------------------------------------------------------------------
        # deal with no args
        if self.targs is None and self.tkwargs is None:
            self.tvalue = value
        elif self.tkwargs is None and self.targs is not None:
            self.tvalue = value.format(*self.targs)
        elif self.targs is None and self.tkwargs is not None:
            self.tvalue = value.format(**self.tkwargs)
        else:
            self.tvalue = value.format(*self.targs, **self.tkwargs)


def textentry(key: str, args: Union[List[Any], str, None] = None,
              kwargs: Union[Dict[str, Any], None] = None) -> Text:
    """
    Get text from a database

    This is the only function that can use langdict and expect it to be
    populated

    :param key: str, the code by which to find the text in the language
                dictionary
    :param args: dict, arguments passed to text.format
    :param kwargs: dict, keyword arguments passed to text.format

    :return: Text class, the text taken from langdict[key] in Text class format
    """
    # set function name
    _ = __NAME__ + '.textentry()'
    # deal with no entries
    value = LanguageLookup.get(key, required=False)
    # deal with no value (use key)
    if value is None:
        message = key
    else:
        message = value
    # deal with args
    if isinstance(args, str):
        args = [args]
    # create Text class for message
    msg_obj = Text(message)
    msg_obj.set_text_props(key, args, kwargs)
    # return msg_obj
    return msg_obj



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
