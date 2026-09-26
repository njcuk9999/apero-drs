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
import hashlib
import importlib
import importlib.util
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aperocore.base import base
from aperocore.drs_lang import drs_lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.drs_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define variables
# =============================================================================
# Language compile is expensive (default_text.py alone is ~13k lines of
#   langlist.create/item.value['ENG'] = ... statements that execute at
#   module import). The compiled result is a plain dict of str -> str
#   keyed by code (e.g. '40-001-00017') that only changes when the
#   language table .py files change. Cache the compiled mode='value'
#   dict under __pycache__ next to this module, keyed on a hash of the
#   language module file paths + mtimes + selected language. On a warm
#   cache this skips importing the table modules entirely.
_LANG_CACHE_VERSION = 1


def _lang_cache_path(cache_key: str) -> Path:
    """
    Location of the compiled-language-values pickle cache. Stored under
    the module's __pycache__ so it lives with the installed package and
    is naturally scoped per Python version.

    :param cache_key: str, hash-derived cache identifier
    :return: pathlib.Path to the cache file
    """
    cache_dir = Path(__file__).resolve().parent / '__pycache__'
    return cache_dir / f'lang_values_v{_LANG_CACHE_VERSION}_{cache_key}.pkl'


def _lang_cache_key(module_names: List[str], language: str) -> Optional[str]:
    """
    Compute a stable cache key from the language module file paths and
    their mtimes plus the selected language. Returns None if any module
    cannot be located (in which case we fall back to the slow path).

    :param module_names: list of str, module names to import for language
                         tables (from install.yaml DRS_LANG_MODULES)
    :param language: str, selected language code (e.g. 'ENG')
    :return: str hex digest, or None if a module file could not be found
    """
    hasher = hashlib.blake2b(digest_size=16)
    hasher.update(language.encode('utf-8'))
    for module_name in module_names:
        try:
            spec = importlib.util.find_spec(module_name)
        except Exception:
            return None
        if spec is None or spec.origin is None:
            return None
        try:
            mtime_ns = os.stat(spec.origin).st_mtime_ns
        except OSError:
            return None
        hasher.update(module_name.encode('utf-8'))
        hasher.update(spec.origin.encode('utf-8'))
        hasher.update(str(mtime_ns).encode('utf-8'))
    return hasher.hexdigest()


def _try_load_lang_cache() -> Optional[str]:
    """
    Attempt to populate drs_lang.LANG_VALUES from the on-disk cache.

    :return: str, the selected language code if the cache was used;
             None if the cache was missing/stale (caller should fall
             through to the full compile path).
    """
    iparams = base.load_install_yaml(required=False)
    module_names = iparams['DRS_LANG_MODULES']
    language = iparams['GLOBAL.LANGUAGE']
    if not module_names or language is None:
        return None
    cache_key = _lang_cache_key(module_names, language)
    if cache_key is None:
        return None
    cache_path = _lang_cache_path(cache_key)
    if not cache_path.exists():
        return None
    try:
        with cache_path.open('rb') as fhandle:
            cached_values = pickle.load(fhandle)
    except Exception:
        # unreadable cache — treat as a miss and let the compile path
        # rewrite it on success
        return None
    if not isinstance(cached_values, dict):
        return None
    drs_lang.LANG_VALUES.update(cached_values)
    return language


def _save_lang_cache(language: str) -> None:
    """
    Persist the freshly-compiled drs_lang.LANG_VALUES dict alongside a
    hash of the source modules so the next process can skip the compile.

    :param language: str, the language code that was compiled
    :return: None
    """
    iparams = base.load_install_yaml(required=False)
    module_names = iparams['DRS_LANG_MODULES']
    cache_key = _lang_cache_key(module_names, language)
    if cache_key is None:
        return
    cache_path = _lang_cache_path(cache_key)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # write via a temp file so partial writes never leave a corrupt
        # cache in place
        tmp_path = cache_path.with_suffix(cache_path.suffix + '.tmp')
        with tmp_path.open('wb') as fhandle:
            pickle.dump(dict(drs_lang.LANG_VALUES), fhandle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp_path, cache_path)
    except Exception:
        # a failed cache write must never break language lookup
        pass


# Try the pickle cache first; on a hit LANG_VALUES is already populated
# and we can build a no-op LanguageLookup (empty lang_insts short-circuits
# the compile inside its __init__). Any unexpected failure inside the
# cache path must fall through to the original compile path so language
# lookup can never be broken by a bad cache file / stat error.
try:
    _cached_language = _try_load_lang_cache()
except Exception:
    _cached_language = None
if _cached_language is not None:
    LanguageLookup = drs_lang.LanguageLookup(lang_insts=[],
                                             langauge=_cached_language)
else:
    # cold path: import every language table module and compile as before
    lkwargs = drs_lang.get_instrument_args()
    LanguageLookup = drs_lang.LanguageLookup(**lkwargs)
    _save_lang_cache(lkwargs['langauge'])
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
        if self.tkey in [None, 'None', '']:
            valuestr = '{2}'.format(*vargs)
        elif report and (self.tkey != self.tvalue):
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
              kwargs: Union[Dict[str, Any], None] = None,
              message: Union[str, None] = None) -> Text:
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
    if message is not None:
        if args is not None:
            value = message.format(*args)
        elif kwargs is not None:
            value = message.format(**kwargs)
        else:
            value = message
    # deal with no value (use key)
    if value is None:
        message = str(key)
        key = None
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
