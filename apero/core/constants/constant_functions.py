"""
Package containing all constants Classes and functionality

DRS Import Rules:

- only from apero.locale

Created on 2019-01-17 at 14:09

@author: cook
"""
import numpy as np
import os
import sys
import traceback
import importlib
import string
import warnings
from astropy import units as uu
from typing import Union

from apero.locale import drs_exceptions
from apero.locale import drs_lang_db

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
    """
    Constant class - drs constants are instances of this

    e.g. stores information to read and check config/constant file constants

    """
    def __init__(self, name, value=None, dtype=None, dtypei=None,
                 options=None, maximum=None, minimum=None, source=None,
                 unit=None, default=None, datatype=None, dataformat=None,
                 group=None, user=False, active=False, description=None,
                 author=None, parent=None):
        """
        Construct the constant instance

        :param name: str, name of the constant
        :param value: str, value of the constant
        :param dtype: str, data type of the constant
        :param dtypei: str, data type of list/dictionary elements
        :param options: list of strings, the allowed values for the constant
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
        :param parent: Const, the parent of this constant (if a constant is
                       related to or comes from another constant)

        :type name: str
        :type value: str
        :type dtype: str
        :type dtypei: str
        :type options: list[str]
        :type source: str
        :type unit: uu.Unit
        :type datatype: str
        :type dataformat: str
        :type group: str
        :type user: bool
        :type active: bool
        :type description:
        :type author:
        :type parent: Const

        :returns: None
        """
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Const.validate()'
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

    def validate(self, test_value=None, quiet=False, source=None):
        """

        :param test_value:
        :param quiet:
        :param source:

        :type test_value:
        :type quiet: bool
        :type source: Union[str, None]

        :return:
        """
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Const.validate()'
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

        true_value, self.source = _validate_value(*vargs, **vkwargs)
        # deal with storing
        if test_value is None:
            self.true_value = true_value
            return True
        else:
            return true_value

    def copy(self, source=None):
        # set function name (cannot break function here)
        func_name = str(__NAME__) + '.Const.copy()'
        # get display text
        textentry = _DisplayText()
        # check that source is valid
        if source is None:
            raise ConfigError(textentry('00-003-00007', args=[func_name]),
                              level='error')
        # return new copy of Const
        return Const(self.name, self.value, self.dtype, self.dtypei,
                     self.options, self.maximum, self.minimum, source=source,
                     unit=self.unit, default=self.default,
                     datatype=self.datatype, dataformat=self.dataformat,
                     group=self.group, user=self.user, active=self.active,
                     description=self.description, author=self.author,
                     parent=self.parent)

    def write_line(self, value=None):
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Const.write_line()'
        # set up line list
        lines = ['']
        # deal with value
        if value is None:
            value = self.value
        # ------------------------------------------------------------------
        # add description
        # -------------------------------------------------------------------
        # check if we have a description defined
        if self.description is not None:
            description = self.description.strip().capitalize()
            # wrap long descriptions by words
            wrapdesc = textwrap(description, 77)
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

    def __init__(self, name, key=None, value=None, dtype=None, comment=None,
                 options=None, maximum=None, minimum=None, source=None,
                 unit=None, default=None, datatype=None, dataformat=None,
                 group=None, author=None, parent=None):
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Keyword.__init__()'
        # Initialize the constant parameters (super)
        Const.__init__(self, name, value, dtype, None, options, maximum,
                       minimum, source, unit, default, datatype, dataformat,
                       group, author, parent)
        # set the header key associated with this keyword (8 characters only)
        self.key = key
        # set the header comment associated with this keyword
        self.comment = comment
        # set the kind (Const or Keyword)
        self.kind = 'Keyword'
        # set the source file of the Keyword
        self.source = source
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

    def set(self, key=None, value=None, dtype=None, comment=None,
            options=None, unit=None, default=None, datatype=None,
            dataformat=None, group=None, author=None, parent=None):
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Keyword.set()'
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

    def validate(self, test_value=None, quiet=False, source=None):
        # set function name (cannot break function here)
        _ = str(__NAME__) + '.Keyword.validate()'
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
        true_value, self.source = _validate_value(*vargs, **vkwargs)
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
        # set function name (cannot break function here)
        func_name = str(__NAME__) + '.Keyword.copy()'
        # get display text
        textentry = _DisplayText()
        # check that source is valid
        if source is None:
            raise ConfigError(textentry('00-003-00008', args=[func_name]),
                              level='error')
        # return new copy of Const
        return Keyword(self.name, self.key, self.value, self.dtype,
                       self.comment, self.options, self.maximum,
                       self.minimum, source=source, unit=self.unit,
                       default=self.default, datatype=self.datatype,
                       dataformat=self.dataformat, group=self.group,
                       author=self.author, parent=self.parent)


class _DisplayText:
    """
    Manually enter wlog TextEntries here -- will be in english only

    This is used for when we cannot have access to the language database
    """

    def __init__(self):
        # set function name (cannot break here --> no access to inputs)
        _ = __NAME__ + '._DisplayText.__init__()'
        # get the entries from module
        self.entries = drs_lang_db.get_entries()

    def __call__(self, key, args=None):
        # set function name (cannot break here --> no access to inputs)
        _ = str(__NAME__) + '._DisplayText.__init__()'
        # return the entry for key with the arguments used for formatting
        if args is not None:
            return self.entries[key].format(*args)
        # else just return the entry
        else:
            return self.entries[key]


# =============================================================================
# Define functions
# =============================================================================
def generate_consts(modulepath):
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.generate_consts()'
    # import module
    mod = import_module(func_name, modulepath)
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


def import_module(func, modulepath, full=False, quiet=False):
    # set function name (cannot break here --> no access to inputs)
    if func is None:
        func_name = str(__NAME__) + '.import_module()'
    else:
        func_name = str(func)
    # get display text
    textentry = _DisplayText()
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
        mod = importlib.import_module(modfile)
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
            raise ConfigError(textentry('00-000-00003', args=eargs),
                              level='error')


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
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '.get_constants_from_file()'
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


def update_file(filename, dictionary):
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.update_file()'
    # get display text
    textentry = _DisplayText()
    # open file
    try:
        # open the file
        f = open(filename, 'r')
        # read the lines
        lines = f.readlines()
        # close the opened file
        f.close()
    except Exception as e:
        eargs = [filename, func_name, type(e), e]
        raise ConfigError(textentry('00-004-00003', args=eargs),
                          level='error')
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
        # open the file
        f = open(filename, 'w')
        # write the lines
        f.writelines(lines)
        # close the opened file
        f.close()
    except Exception as e:
        eargs = [filename, func_name, type(e), e]
        raise ConfigError(textentry('00-004-00004', args=eargs),
                          level='error')


def textwrap(input_string, length):
    """

    Modified version of this: https://stackoverflow.com/a/16430754

    :param input_string:
    :param length:
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '.textwrap()'
    # set up a new empty list of strings
    new_string = []
    # loop around the input string split by new lines
    for s in input_string.split("\n"):
        # if line is empty add an empty line to new_string
        if s == "":
            new_string.append('')
        # set the current line length to zero initially
        wlen = 0
        # storage
        line = []
        # loop around words in string and split at words if length is too long
        #   words are definied by white spaces
        for dor in s.split():
            # if the word + current length is shorter than the wrap length
            #   then append to current line
            if wlen + len(dor) + 1 <= length:
                line.append(dor)
                # update the current line length
                wlen += len(dor) + 1
            # else we have to wrap
            else:
                # add the current line to the output string
                new_string.append(" ".join(line))
                # start a new line with the word that broke the wrap
                line = [dor]
                # set the current line length to the length of the word
                wlen = len(dor)
        # if the length of the line is larger than zero append line
        if len(line) > 0:
            new_string.append(" ".join(line))
    # add a tab to all but first line
    new_string2 = [new_string[0]]
    # loop around lines in new strings (except the first line)
    for it in range(1, len(new_string)):
        new_string2.append('\t' + new_string[it])
    # return the new string with tabs for subsequent lines
    return new_string2


# =============================================================================
# Define private functions
# =============================================================================
def _get_raw_txt(filename, comments, delimiter):
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '._get_raw_txt()'
    # catch warnings from here
    with warnings.catch_warnings(record=True) as _:
        # noinspection PyBroadException
        # try to read the text file using numpy's genfromtxt (faster)
        try:
            raw = np.genfromtxt(filename, comments=comments,
                                delimiter=delimiter, dtype=str).astype(str)
        # if this fails for any read use a slow method (defined below)
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
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '.read_lines()'
    # get display text
    textentry = _DisplayText()
    # manually open file (slow)
    try:
        # open the file
        f = open(filename, 'r')
        # read the lines
        lines = f.readlines()
        # close the opened file
        f.close()
    except Exception as e:
        eargs = [filename, func_name, type(e), e]
        raise ConfigError(textentry('00-004-00003', args=eargs),
                          level='error')
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
                eargs = [l + 1, filename, line, func_name]
                raise ConfigError(textentry('00-003-00022', args=eargs),
                                  level='error')
            raw.append([key, value])
    # check that raw has entries
    if len(raw) == 0:
        eargs = [filename, func_name]
        raise ConfigError(textentry('00-003-00023', args=eargs),
                          level='error')
    # return raw
    return np.array(raw)


def _test_dtype(name, invalue, dtype, source, quiet=False):
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._test_dtype()'
    # get display text
    textentry = _DisplayText()
    # if we don't have a value (i.e. it is None) don't test
    if invalue is None:
        return None
    # check paths (must be strings and must exist)
    if dtype == 'path':
        if type(invalue) is not str:
            if not quiet:
                eargs = [name, type(invalue), invalue, source, func_name]
                raise ConfigError(textentry('00-003-00009', args=eargs),
                                  level='error')
        if not os.path.exists(invalue):
            if not quiet:
                eargs = [name, invalue, func_name]
                raise ConfigError(textentry('00-003-00010', args=eargs),
                                  level='error')
        return str(invalue)
    # deal with casting a string into a list
    if (dtype is list) and (type(invalue) is str):
        if not quiet:
            eargs = [name, invalue, source, func_name]
            raise ConfigError(textentry('00-003-00011', args=eargs),
                              level='error')
    # now try to cast value
    try:
        outvalue = dtype(invalue)
    except Exception as e:
        if not quiet:
            eargs = [name, dtype, invalue, type(invalue), type(e), e,
                     source, func_name]
            raise ConfigError(textentry('00-003-00012', args=eargs),
                              level='error')
        outvalue = invalue
    # return out value
    return outvalue


def _validate_value(name, dtype, value, dtypei, options, maximum, minimum,
                    quiet=False, source=None):
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._validate_value()'
    # get display text
    textentry = _DisplayText()
    # deal with no source
    if source is None:
        source = 'Unknown ({0})'.format(func_name)
    # ---------------------------------------------------------------------
    # check that we only have simple dtype
    if dtype is None:
        if not quiet:
            eargs = [name, source, func_name]
            raise ConfigError(textentry('00-003-00013', args=eargs),
                              level='error')
    if (dtype not in SIMPLE_TYPES) and (dtype != 'path'):
        if not quiet:
            eargs = [name, ', '.join(SIMPLE_STYPES), source, func_name]
            raise ConfigError(textentry('00-003-00014', args=eargs),
                              level='error')
    # ---------------------------------------------------------------------
    # Check value is not None
    if value is None:
        if not quiet:
            eargs = [name, source, func_name]
            raise ConfigError(textentry('00-003-00015', args=eargs),
                              level='error')
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
                raise ConfigError(textentry('00-003-00016', args=eargs),
                                  level='error')
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
                raise ConfigError(textentry('00-003-00017', args=eargs),
                                  level='error')
    # ---------------------------------------------------------------------
    # check limits if not a list or str or bool
    if dtype in [int, float]:
        if maximum is not None:
            if true_value > maximum:
                if not quiet:
                    eargs = [name, maximum, true_value, source, func_name]
                    raise ConfigError(textentry('00-003-00018', args=eargs),
                                      level='error')
        if minimum is not None:
            if true_value < minimum:
                if not quiet:
                    eargs = [name, minimum, true_value, source, func_name]
                    raise ConfigError(textentry('00-003-00019', args=eargs),
                                      level='error')
    # return true value
    return true_value, source


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
    # set function name (cannot break here --> no access to inputs)
    func_name = str(__NAME__) + '._validate_text_file()'
    # get display text
    textentry = _DisplayText()
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
        eargs = [filename, func_name]
        emsg = textentry('00-003-00020', args=eargs)
        invalid = False
        for char in line:
            if char not in VALID_CHARS:
                invalid = True
                emsg += textentry('00-003-00021', args=[char, l + 1])
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
