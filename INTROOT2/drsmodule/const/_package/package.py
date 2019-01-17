"""
Package containing all constants Classes and functionality

Created on 2019-01-17 at 14:09

@author: cook
"""
import importlib


# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'package.py'
# Define simple types allowed for constants
SIMPLE_TYPES = [int, float, str, bool, list]
SIMPLE_STYPES = ['int', 'float', 'str', 'bool', 'list']

# =============================================================================
# Define Custom classes
# =============================================================================
class ConfigException(Exception):
    """Raised when config file is incorrect"""
    pass


class ConfigError(ConfigException):
    """
    Custom Config Error for passing to the log
    """

    def __init__(self, message=None, level=None):
        """
        Constructor for ConfigError sets message to self.message and level to
        self.level

        if key is not None defined self.message reads "key [key] must be
        defined in config file (located at [config_file]

        if config_file is None then deafult config file is used in its place

        :param message: list or string, the message to print in the error
        :param level: string, level (for logging) must be key in TRIG key above
                      default = all, error, warning, info or graph
        """
        # deal with message
        if message is None:
            self.message = 'Config Error'
        elif type(message) == str:
            self.message = message
        else:
            self.message = list(message)
        # set logging level
        if level is None:
            self.level = 'error'
        else:
            self.level = level
        # deal with a list message (for printing)
        if type(self.message) == list:
            amessage = ''
            for mess in message:
                amessage += '\n\t\t{0}'.format(mess)
            message = amessage
        # set args to message (for printing)
        argmessage = 'level={0}: {1}'
        self.args = (argmessage.format(self.level, message),)

    # overwrite string repr message with args[0]
    def __repr__(self):
        """
        String representation of ConfigError

        :return message: string, the message assigned in constructor
        """
        return self.args[0]

    # overwrite print message with args[0]
    def __str__(self):
        """
        String printing of ConfigError

        :return message: string, the message assigned in constructor
        """
        return self.args[0]


# =============================================================================
# Define classes
# =============================================================================
class Const:
    def __init__(self, name, value=None, dtype=None, dtypei=None,
                 options=None, maximum=None, minimum=None):
        self.name = name
        self.value = value
        self.dtype = dtype
        self.dtypei = dtypei
        self.options = options
        self.maximum, self.minimum = maximum, minimum
        self.kind = 'Const'
        self.true_value = None

    def validate(self):
        self.true_value = _validate(self.name, self.dtype, self.value,
                                    self.dtypei, self.options,  self.maximum,
                                    self.minimum)


class Keyword(Const):
    def __init__(self, name, key=None, value=None, dtype=None, comment=None,
                 options=None, maximum=None, minimum=None):
        Const.__init__(self, name, value, dtype, options, maximum, minimum)
        self.key = key
        self.comment = comment
        self.kind = 'Keyword'

    def set(self, key=None, value=None, dtype=None, comment=None, options=None):
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

    def validate(self):
        self.true_value = _validate(self.name, self.dtype, self.value,
                                    self.dtypei, self.options,  self.maximum,
                                    self.minimum)
        # deal with no comment
        if self.comment is None:
            self.comment = ''
        # need a key
        if self.key is None:
            emsg = 'DevError: Keyword "{0}" must have a key'
            ConfigError(emsg.format(self.name), level='error')
        # construct true value as keyword store
        self.true_value = [self.key, self.true_value, self.comment]


# =============================================================================
# Define functions
# =============================================================================
def generate_all_consts(module):
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


def _test_dtype(name, invalue, dtype):

    # deal with casting a string into a list
    if (dtype is list) and (type(invalue) is str):
        emsg = 'DevError: Parameter "{0}" should be a list not a string.'
        ConfigError(emsg.format(name), level='error')
    # now try to cast value
    try:
        outvalue = dtype(invalue)
    except Exception as e:
        eargs = [name, dtype, invalue]
        emsg1 = ('DevError: Parameter "{0}" dtype is incorrect. '
                 'Expected "{1}" value="{2}"')
        emsg2 = '\tError was "{0}": "{1}"'.format(type(e), e)
        ConfigError([emsg1.format(*eargs), emsg2], level='error')
    # return out value
    return outvalue


def _validate(name, dtype, value, dtypei, options, maximum, minimum):
    # ---------------------------------------------------------------------
    # check that we only have simple dtype
    if dtype is None:
        emsg = 'DevError: Parameter "{0}" dtype not set'
        ConfigError(emsg.format(name), level='error')
    if dtype not in SIMPLE_TYPES:
        emsg1 = ('DevError: Parameter "{0}" dtype is incorrect. Must be'
                 ' one of the following:'.format(name))
        emsg2 = '\t' + ', '.join(SIMPLE_STYPES)
        ConfigError(emsg1, emsg2)
    # ---------------------------------------------------------------------
    # Check value is not None
    if value is None:
        emsg = 'DevError: Parameter "{0}" value is not set.'.format(name)
        ConfigError(emsg, level='error')

    # ---------------------------------------------------------------------
    # check bools
    if dtype is bool:
        if value not in [True, 1, False, 0]:
            emsg1 = 'DevError: Parameter "{0}" must be True or False [1 or 0]'
            emsg2 = '\tCurrent value: "{0}"'.format(value)
            ConfigError([emsg1, emsg2], level='error')
    # ---------------------------------------------------------------------
    # Check if dtype is correct
    true_value = _test_dtype(name, value, dtype)
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
            emsg1 = 'DevError: Parameter "{0}" value is incorrect.'
            emsg2 = '\tOptions are: {0}'.format(','.join(options))
            emsg3 = '\tCurrent value: {0}'.format(true_value)
            ConfigError([emsg1.format(name), emsg2, emsg3], level='error')
    # ---------------------------------------------------------------------
    # check limits if not a list or str or bool
    if dtype in [int, float]:
        if maximum is not None:
            if true_value > maximum:
                emsg1 = ('DevError: Parameter "{0}" too large'
                         ''.format(name))
                emsg2 = '\tValue must be less than {0}'.format(maximum)
                ConfigError([emsg1.format(name), emsg2], level='error')
        if minimum is not None:
            if true_value < minimum:
                emsg1 = ('DevError: Parameter "{0}" too large'.format(name))
                emsg2 = '\tValue must be less than {0}'.format(maximum)
                ConfigError([emsg1, emsg2], level='error')
    # return true value
    return true_value

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
