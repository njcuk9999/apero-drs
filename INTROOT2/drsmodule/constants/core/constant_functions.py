"""
Package containing all constants Classes and functionality

DRS Import Rules:

- only from drsmodule.locale

Created on 2019-01-17 at 14:09

@author: cook
"""
import numpy as np
import os
import importlib
import string
import warnings

from drsmodule.locale import drs_text
from drsmodule.locale import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'constant_functions.py'
# Define simple types allowed for constants
SIMPLE_TYPES = [int, float, str, bool, list]
SIMPLE_STYPES = ['int', 'float', 'str', 'bool', 'list']
# define valid characters
VALID_CHARS = list(string.ascii_letters) + list(string.digits)
VALID_CHARS += list(string.punctuation) + list(string.whitespace)
# get the Drs Exceptions
DRSError = drs_exceptions.DrsError
DRSWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning
# get the logger
BLOG = drs_exceptions.basiclogger


# =============================================================================
# Define classes
# =============================================================================
class Const:
    def __init__(self, name, value=None, dtype=None, dtypei=None,
                 options=None, maximum=None, minimum=None, source=None):
        self.name = name
        self.value = value
        self.dtype = dtype
        self.dtypei = dtypei
        self.options = options
        self.maximum, self.minimum = maximum, minimum
        self.kind = 'Const'
        self.source = source

    def validate(self, test_value=None, quiet=False, source=None):
        # deal with no test value (use value set at module level)
        if test_value is None:
            value = self.value
        else:
            value = test_value
        # get true value (and test test_value)
        true_value = _validate_value(self.name, self.dtype, value,
                                     self.dtypei, self.options,
                                     self.maximum, self.minimum,
                                     quiet=quiet, source=source)
        # deal with storing
        if test_value is None:
            self.true_value = true_value
            return True
        else:
            return true_value

    def copy(self, source=None):
        # check that source is valid
        if source is None:
            emsg1 = 'Must define new source when copying a Constant'
            emsg2 = ('\tSyntax: Constant.copy(source)\twhere "source" is a '
                     'string')
            raise ConfigError([emsg1, emsg2], level='error')
        # return new copy of Const
        return Const(self.name, self.value, self.dtype, self.dtypei,
                     self.options, self.maximum, self.minimum, source=source)


class Keyword(Const):
    def __init__(self, name, key=None, value=None, dtype=None, comment=None,
                 options=None, maximum=None, minimum=None, source=None):
        Const.__init__(self, name, value, dtype, options, maximum, minimum,
                       source=source)
        self.key = key
        self.comment = comment
        self.kind = 'Keyword'
        self.source = source

    def set(self, key=None, value=None, dtype=None, comment=None,
            options=None):
        if key is not None:
            self.key = key
        if value is not None:
            self.value = value
        if dtype is not None:
            self.dtype = dtype
        if comment is not None:
            self.comment = comment
        if options is not None:
            self.options = options


    def validate(self, test_value=None, quiet=False, source=None):
        # deal with no test value (use value set at module level)
        if test_value is None:
            value = self.value
        else:
            value = test_value
        # get true value (and test test_value)
        true_value = _validate_value(self.name, self.dtype, value,
                                     self.dtypei, self.options,
                                     self.maximum, self.minimum,
                                     quiet=quiet, source=source)
        # deal with no comment
        if self.comment is None:
            self.comment = ''
        # need a key
        if self.key is None:
            emsg = 'Keyword "{0}" must have a key'
            raise ConfigError(emsg.format(self.name), level='error')
        # construct true value as keyword store
        true_value = [self.key, true_value, self.comment]
        # deal with storing
        if test_value is None:
            self.true_value = true_value
            return True
        else:
            return true_value

    def copy(self, source=None):
        # check that source is valid
        if source is None:
            emsg1 = 'Must define new source when copying a Keyword'
            emsg2 = ('\tSyntax: Constant.copy(source)\twhere "source" is a '
                     'string')
            raise ConfigError([emsg1, emsg2], level='error')
        # return new copy of Const
        return Keyword(self.name, self.key, self.value, self.dtype,
                       self.comment, self.options, self.maximum,
                       self.minimum, source=source)


# =============================================================================
# Define functions
# =============================================================================
def generate_consts(module):
    # import module
    mod = importlib.import_module(module)
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


def get_constants_from_file(filename):
    """
    read config file and convert to key, value pairs
        comments have a '#' at the start
        format of variables:   key = value

    If file cannot be read will generate an IOError

    :param filename: string, the filename (+ absolute path) of file to open

    :return keys: list of strings, upper case strings for each variable
    :return values: list of strings, value of each key
    """
    # first try to reformat text file to avoid weird characters
    #   (like mac smart quotes)
    _validate_text_file(filename)
    # read raw config file as strings
    raw = _get_raw_txt(filename, comments='#', delimiter='=')
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


# =============================================================================
# Define private functions
# =============================================================================
def _get_raw_txt(filename, comments, delimiter):
    with warnings.catch_warnings(record=True) as _:
        # noinspection PyBroadException
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        except Exception:
            raw = _read_lines(filename, comments=comments, delimiter=delimiter)
    # return the raw lines
    return raw


def _read_lines(filename, comments='#', delimiter=' '):
    """

    :param filename:
    :param comments:
    :param delimiter:
    :return:
    """

    func_name = __NAME__ + '.read_lines()'
    # manually open file (slow)
    try:
        # open the file
        f = open(filename, 'r')
        # read the lines
        lines = f.readlines()
        # close the opened file
        f.close()
    except Exception as e:
        emsg = ('\n\t\t {0}: File "{1}" cannot be read by {2}. '
                '\n\t\t Error was: {3}')
        raise ConfigError(emsg.format(type(e), filename, func_name, e))
    # valid lines
    raw = []
    # loop around lines
    for l, line in enumerate(lines):
        # remove line endings and blanks at start and end
        line = line.replace('\n', '').strip()
        # do not include blank lines
        if len(line) == 0:
            continue
        # do not include commented lines
        elif line[0] == comments:
            continue
        else:
            # append to raw
            try:
                key, value = line.split(delimiter)
            except ValueError as _:
                emsg = ['Wrong format for line {0} in file {1}'
                        ''.format(l + 1, filename, line),
                        'Lines must be "key" = "value"',
                        'Where "key" and "value" are a valid python ',
                        'strings and contains no equal signs']
                raise ConfigError(emsg)

            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        raise ConfigError("No valid lines found in {0}".format(filename))
    # return raw
    return np.array(raw)


def _test_dtype(name, invalue, dtype, quiet=False):

    # if we don't have a value (i.e. it is None) don't test
    if invalue is None:
        return None

    # check paths (must be strings and must exist)
    if dtype == 'path':
        if type(invalue) is not str:
            eargs = [name, type(invalue), invalue]
            emsg1 = 'Parameter "{0}" must be a string.'
            emsg2 = '\tType: "{1}"\tValue: "{2}"'.format(*eargs)
            if not quiet:
                raise ConfigError([emsg1.format(*eargs), emsg2], level='error')
        if not os.path.exists(invalue):
            emsg = 'Key {0}: Path does not exist "{1}"'
            eargs = [name, invalue]
            if not quiet:
                raise ConfigError(emsg.format(*eargs), level='error')

        return str(invalue)

    # deal with casting a string into a list
    if (dtype is list) and (type(invalue) is str):
        emsg = 'Parameter "{0}" should be a list not a string.'
        if not quiet:
            raise ConfigError(emsg.format(name), level='error')
    # now try to cast value
    try:
        outvalue = dtype(invalue)
    except Exception as e:
        eargs = [name, dtype, invalue]
        emsg1 = ('Parameter "{0}" dtype is incorrect. '
                 'Expected "{1}" value="{2}"')
        emsg2 = '\tError was "{0}": "{1}"'.format(type(e), e)
        if not quiet:
            raise ConfigError([emsg1.format(*eargs), emsg2], level='error')
        outvalue = invalue
    # return out value
    return outvalue


def _validate_value(name, dtype, value, dtypei, options, maximum, minimum,
                    quiet=False, source=None):

    func_name = __NAME__ + '._validate_value()'
    # deal with no source
    if source is None:
        source = 'Unknown ({0})'.format(func_name)
    # ---------------------------------------------------------------------
    # check that we only have simple dtype
    if dtype is None:
        emsg1 = 'Parameter "{0}" dtype not set'
        emsg2 = '\tConfig File = "{0}"'.format(source)
        if not quiet:
            raise ConfigError([emsg1.format(name), emsg2], level='error')
    if (dtype not in SIMPLE_TYPES) and (dtype != 'path'):
        emsg1 = ('Parameter "{0}" dtype is incorrect. Must be'
                 ' one of the following:'.format(name))
        emsg2 = '\t' + ', '.join(SIMPLE_STYPES)
        emsg3 = '\tConfig File = "{0}"'.format(source)
        if not quiet:
            raise ConfigError([emsg1, emsg2, emsg3])
    # ---------------------------------------------------------------------
    # Check value is not None
    if value is None:
        emsg1 = 'Parameter "{0}" value is not set.'.format(name)
        emsg2 = '\tConfig File = "{0}"'.format(source)
        if not quiet:
            raise ConfigError([emsg1, emsg2], level='error')

    # ---------------------------------------------------------------------
    # check bools
    if dtype is bool:

        if type(value) is str:
            if value.lower() in ['1', '0', 'true', 'false']:
                value = bool(value)

        if value not in [True, 1, False, 0]:
            emsg1 = 'Parameter "{0}" must be True or False [1 or 0]'
            emsg2 = '\tCurrent value: "{0}"'.format(value)
            emsg3 = '\tConfig File = "{0}"'.format(source)
            if not quiet:
                raise ConfigError([emsg1.format(name), emsg2, emsg3],
                                  level='error')

    # ---------------------------------------------------------------------
    # Check if dtype is correct
    true_value = _test_dtype(name, value, dtype, quiet=quiet)
    # ---------------------------------------------------------------------
    # check dtypei if list
    if dtype == list:
        if dtypei is not None:
            newvalues = []
            for value in true_value:
                newvalues.append(_test_dtype(name, value, dtypei))
            true_value = newvalues
    # ---------------------------------------------------------------------
    # check options if not a list
    if dtype in [str, int, float] and options is not None:
        if true_value not in options:
            emsg1 = 'Parameter "{0}" value is incorrect.'
            stroptions = ['"{0}"'.format(opt) for opt in options]
            emsg2 = '\tOptions are: {0}'.format(', '.join(stroptions))
            emsg3 = '\tCurrent value: "{0}"'.format(true_value)
            emsg4 = '\tConfig File = "{0}"'.format(source)
            if not quiet:
                raise ConfigError([emsg1.format(name), emsg2, emsg3, emsg4],
                                  level='error')
    # ---------------------------------------------------------------------
    # check limits if not a list or str or bool
    if dtype in [int, float]:
        if maximum is not None:
            if true_value > maximum:
                emsg1 = ('Parameter "{0}" too large'
                         ''.format(name))
                emsg2 = '\tValue must be less than {0}'.format(maximum)
                emsg3 = '\tConfig File = "{0}"'.format(source)
                if not quiet:
                    raise ConfigError([emsg1.format(name), emsg2, emsg3],
                                      level='error')
        if minimum is not None:
            if true_value < minimum:
                emsg1 = ('Parameter "{0}" too large'.format(name))
                emsg2 = '\tValue must be less than {0}'.format(maximum)
                emsg3 = '\tConfig File = "{0}"'.format(source)
                if not quiet:
                    raise ConfigError([emsg1, emsg2, emsg3], level='error')
    # return true value
    return true_value


def _validate_text_file(filename, comments='#'):
    """
    Validation on any text file, makes sure all non commented lines have
    valid characters (i.e. are either letters, digits, punctuation or
    whitespaces as defined by string.ascii_letters, string.digits,
    string.punctuation and string.whitespace.

    A ConfigException is raised if invalid character(s) found

    :param filename: string, name and location of the text file to open
    :param comments: char (string), the character that defines a comment line
    :return None:
    """
    func_name = __NAME__ + '.validate_text_file()'
    # open text file
    f = open(filename, 'r')
    # get lines
    lines = f.readlines()
    # close text file
    f.close()
    # loop around each line in text file
    for l, line in enumerate(lines):
        # ignore blank lines
        if len(line.strip()) == 0:
            continue
        # ignore comment lines (don't care about characters in comments)
        if line.strip()[0] == comments:
            continue
        # loop through each character in line and check if it is a valid
        # character
        emsg = ' Invalid character(s) found in file={0}'.format(filename)
        invalid = False
        for char in line:
            if char not in VALID_CHARS:
                invalid = True
                emsg += '\n\t\tLine {1} character={0}'.format(char, l + 1)
        emsg += '\n\n\tfunction = {0}'.format(func_name)
        # only raise an error if invalid is True (if we found bad characters)
        if invalid:
            raise ConfigError(emsg, level='error')


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
