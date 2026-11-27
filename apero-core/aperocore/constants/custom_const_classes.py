#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom constant classes shared by APERO-core users (POGOS, SOSSISSE, ...)

Register these with ``ConstantsDict.addc(name, ..., const_class=CLASS)``.
Every custom class accepts an extra ``exception`` keyword so that the calling
package can raise its own exception type (e.g. SossisseConstantException).

Classes
-------
MathMemoryConst:
    positive finite memory budget in GiB (Booleans rejected)
FileObjectConst:
    an input file (or list of files) that may be local, downloaded from MAST
    or downloaded from the POGOS data server. In yaml this is either a plain
    filename/list (local) or a mapping containing ``filelist`` plus source
    information. Code reading ``params[KEY]`` always receives the plain
    filename (str) or filenames (list) - the source information travels on
    the value as ``value.fileobj`` (see FileName / FileList).

Created on 2026-11-25

@author: cook
"""
import copy as copy_module
import math
from numbers import Real
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from aperocore.constants import constant_functions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.constants.custom_const_classes'

Const = constant_functions.Const


# =============================================================================
# Define exceptions
# =============================================================================
class AperoConstantError(ValueError):
    """Default exception raised by custom constant validation."""


# =============================================================================
# Base class for custom constants
# =============================================================================
class CustomConst(Const):
    """
    Base class for custom constants

    Adds an ``exception`` keyword (the exception class raised on invalid
    values) and a copy method that preserves the subclass and its extra
    attributes.
    """
    class_name = 'CustomConst'

    def __init__(self, name: str, *args: Any,
                 exception: Optional[Type[Exception]] = None,
                 **kwargs: Any) -> None:
        """
        Construct the custom constant

        :param name: str, the constant name
        :param args: positional arguments accepted by Const
        :param exception: exception class raised for invalid values
                          (defaults to AperoConstantError)
        :param kwargs: keyword arguments accepted by Const
        """
        super().__init__(name, *args, **kwargs)
        self.exception = AperoConstantError if exception is None else exception

    def _raise(self, message: str) -> None:
        """Raise the configured exception class with ``message``."""
        raise self.exception(message)

    @property
    def fullname(self) -> str:
        """Return GROUP.NAME (or NAME without a group) for messages."""
        if self.group is None:
            return self.name
        return f'{self.group}.{self.name}'

    def copy(self, source: Optional[str] = None) -> 'CustomConst':
        """
        Copy this constant keeping the subclass and extra attributes

        :param source: replacement provenance, or None to preserve it
        :return: independent constant of the same class
        """
        constant = copy_module.copy(self)
        if source is not None:
            constant.source = source
        # mutable values must not be shared between copies
        if isinstance(self.value, (list, dict)):
            constant.value = copy_module.deepcopy(self.value)
        return constant


# =============================================================================
# Memory constant
# =============================================================================
class MathMemoryConst(CustomConst):
    """Preserve strict positive finite GiB limits through YAML and copies."""
    class_name = 'MathMemoryConst'

    @staticmethod
    def memory(value: object,
               exception: Optional[Type[Exception]] = None,
               name: str = 'GENERAL.MAX_MATH_MEMORY_GB') -> float:
        """
        Validate the original value before any framework dtype conversion.

        :param value: math budget in GiB (1024**3 bytes), not gigabits
        :param exception: exception class to raise (AperoConstantError if
                          not given)
        :param name: constant name used in the error message
        :return: positive finite floating budget
        :raises exception: for Boolean/non-real/invalid limits
        """
        if exception is None:
            exception = AperoConstantError
        emsg = (f'{name} must be a positive finite real number in GiB '
                f'(1024**3 bytes), not a Boolean')
        if isinstance(value, bool) or not isinstance(value, Real):
            raise exception(emsg)
        # Reject huge integer overflow as a configuration error, not a cast.
        try:
            memory = float(value)
        except OverflowError as error:
            raise exception(emsg) from error
        if not math.isfinite(memory) or memory <= 0:
            raise exception(emsg)
        return memory

    def validate(self, test_value: Any = None, quiet: bool = False,
                 source: Optional[str] = None) -> Any:
        """
        Validate stored/candidate limits using the Const convention.

        :param test_value: candidate, or None to validate the stored value
        :param quiet: accepted for Const compatibility
        :param source: accepted for Const compatibility
        :return: True for stored validation, otherwise validated GiB
        """
        value = self.value if test_value is None else test_value
        memory = self.memory(value, self.exception, self.fullname)
        if test_value is None:
            self.true_value = memory
            return True
        return memory


# =============================================================================
# File object constant
# =============================================================================
# allowed sources
FILE_SOURCES = ('local', 'pogos', 'mast')
# keys allowed for every source
#   (product is the kind of file e.g. uncal, rateints, x1dints - for
#    source: mast it is also the MAST file suffix used to find the files)
FILE_BASE_KEYS = ('filelist', 'source', 'always_download', 'product')
# keys allowed per source (in addition to the base keys and extras)
FILE_SOURCE_KEYS = dict(local=(),
                        pogos=('url',),
                        mast=('pid', 'obsnumber', 'match', 'min_size_mb'))
# all source keys (used to order yaml output)
FILE_ALL_SOURCE_KEYS = ('url', 'pid', 'obsnumber', 'match', 'min_size_mb')
# default MAST filters (match the POGOS dataset definitions)
# (no filename substring required - any *_{product}.fits file is used)
MAST_DEFAULT_MATCH = []
MAST_DEFAULT_MIN_SIZE_MB = 1.0


class FileObject:
    """
    Source information for a FileObjectConst value

    :ivar filelist: str, list of str or None, the filename(s) - basenames
                    relative to the constant's directory or absolute paths
    :ivar source: str, one of 'local', 'pogos', 'mast'
    :ivar always_download: bool, if True download even if files exist
    :ivar url: str or None, POGOS data server directory (source=pogos)
    :ivar pid: int or None, JWST program ID (source=mast)
    :ivar obsnumber: int or None, JWST observation number (source=mast)
    :ivar product: str or None, the kind of file e.g. uncal, rateints,
                   x1dints (for source=mast also the MAST file suffix)
    :ivar match: list of str, substrings MAST filenames must all contain
                 (default: none)
    :ivar min_size_mb: float, minimum MAST file size in MB
    :ivar extras: dict, constant specific extra values (e.g. WAVE_FILE type)
    :ivar path_key: str or None, the parameter (relative to the module)
                    giving the directory files are stored in
    :ivar name: str, the full constant name (for messages)
    """

    def __init__(self, filelist: Union[str, List[str], None] = None,
                 source: str = 'local', always_download: bool = False,
                 url: Optional[str] = None, pid: Optional[int] = None,
                 obsnumber: Optional[int] = None,
                 product: Optional[str] = None,
                 match: Optional[List[str]] = None,
                 min_size_mb: Optional[float] = None,
                 extras: Optional[Dict[str, Any]] = None,
                 path_key: Optional[str] = None, name: str = '',
                 explicit: bool = False) -> None:
        self.filelist = filelist
        self.source = source
        self.always_download = always_download
        self.url = url
        self.pid = pid
        self.obsnumber = obsnumber
        self.product = product
        self.match = match
        self.min_size_mb = min_size_mb
        self.extras = dict() if extras is None else dict(extras)
        self.path_key = path_key
        self.name = name
        # explicit = True when the yaml used the mapping form (keep it so)
        self.explicit = explicit

    def __repr__(self) -> str:
        return (f'FileObject[{self.name}](source={self.source}, '
                f'filelist={self.filelist})')

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FileObject):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def copy(self) -> 'FileObject':
        """Return an independent copy."""
        return copy_module.deepcopy(self)

    @property
    def online(self) -> bool:
        """True if the files come from an online source."""
        return self.source in ('pogos', 'mast')

    @property
    def files(self) -> List[str]:
        """The filelist as a list (empty if not set)."""
        if self.filelist is None:
            return []
        if isinstance(self.filelist, str):
            return [] if not self.filelist else [self.filelist]
        return list(self.filelist)

    def get_match(self) -> List[str]:
        """MAST filename substrings (defaults applied)."""
        if self.match is None:
            return list(MAST_DEFAULT_MATCH)
        return list(self.match)

    def get_min_size_mb(self) -> float:
        """MAST minimum size in MB (default applied)."""
        if self.min_size_mb is None:
            return MAST_DEFAULT_MIN_SIZE_MB
        return float(self.min_size_mb)

    def to_dict(self, filelist: Any = 'self') -> Dict[str, Any]:
        """
        Yaml representation (only non-default keys for this source)

        :param filelist: the filelist to write ('self' uses self.filelist)
        :return: dict, ordered filelist, extras, source keys
        """
        if isinstance(filelist, str) and filelist == 'self':
            filelist = self.filelist
        # plain lists/strings (not subclasses) for the yaml writer
        if isinstance(filelist, list):
            filelist = [str(fname) for fname in filelist]
        elif isinstance(filelist, str):
            filelist = str(filelist)
        # nothing obtained yet is written as an empty "filelist:"
        if not filelist:
            filelist = None
        out = dict(filelist=filelist)
        for key, value in self.extras.items():
            out[key] = value
        out['source'] = self.source
        if self.product is not None:
            out['product'] = self.product
        allowed = FILE_SOURCE_KEYS.get(self.source, ())
        for key in FILE_ALL_SOURCE_KEYS:
            if key in allowed and getattr(self, key) is not None:
                out[key] = copy_module.deepcopy(getattr(self, key))
        if self.online:
            out['always_download'] = bool(self.always_download)
        return out


class FileList(list):
    """A list of filenames carrying its FileObject as ``.fileobj``."""

    def __init__(self, values: Any = (),
                 fileobj: Optional[FileObject] = None) -> None:
        super().__init__(values)
        self.fileobj = fileobj

    def copy(self) -> 'FileList':
        fileobj = None if self.fileobj is None else self.fileobj.copy()
        return FileList(list(self), fileobj)

    def __copy__(self) -> 'FileList':
        return FileList(list(self), self.fileobj)

    def __deepcopy__(self, memo: dict) -> 'FileList':
        return self.copy()

    def __reduce__(self) -> Tuple[Any, ...]:
        return FileList, (list(self), self.fileobj)


class FileName(str):
    """A filename string carrying its FileObject as ``.fileobj``."""

    def __new__(cls, value: str,
                fileobj: Optional[FileObject] = None) -> 'FileName':
        instance = super().__new__(cls, value)
        instance.fileobj = fileobj
        return instance

    def copy(self) -> 'FileName':
        fileobj = None if self.fileobj is None else self.fileobj.copy()
        return FileName(str(self), fileobj)

    def __copy__(self) -> 'FileName':
        return FileName(str(self), self.fileobj)

    def __deepcopy__(self, memo: dict) -> 'FileName':
        return self.copy()

    def __reduce__(self) -> Tuple[Any, ...]:
        return FileName, (str(self), self.fileobj)


def get_fileobj(value: Any) -> Optional[FileObject]:
    """Return the FileObject attached to a parameter value (or None)."""
    return getattr(value, 'fileobj', None)


def _get_instance(params: Any, key: str) -> Any:
    """Return the constant instance of a parameter (or None)."""
    if hasattr(params, 'get_instance'):
        try:
            return params.get_instance(key)
        except Exception:
            return None
    return None


def get_file_product(params: Any, key: str,
                     default: Optional[str] = None) -> Optional[str]:
    """
    Get the product (kind of file e.g. x1dints, fits) of a FileObjectConst

    :param params: ParamDict (or SubParamDict) containing ``key``
    :param key: str, the constant key e.g. 'GENERAL.WAVE_FILE'
    :param default: value returned when not set anywhere
    :return: the product of the value, else the constant default product
    """
    if key not in params:
        return default
    fileobj = get_fileobj(params[key])
    if fileobj is not None and fileobj.product is not None:
        return fileobj.product
    # fall back to the constant default product
    instance = _get_instance(params, key)
    if isinstance(instance, FileObjectConst) and instance.product:
        return instance.product
    return default


def set_file_product(params: Any, key: str, product: Optional[str]) -> None:
    """
    Set the product (kind of file) on a FileObjectConst parameter value

    Plain values are converted to FileName/FileList (source=local).

    :param params: ParamDict (or SubParamDict) containing ``key``
    :param key: str, the constant key e.g. 'GENERAL.WAVE_FILE'
    :param product: str, the product e.g. 'x1dints'
    """
    fileobj = _attach_fileobj(params, key)
    if fileobj is not None:
        fileobj.product = product


def _attach_fileobj(params: Any, key: str) -> Optional[FileObject]:
    """Make sure params[key] carries a FileObject (returns it or None)."""
    current = params[key]
    fileobj = get_fileobj(current)
    if fileobj is not None:
        return fileobj
    fileobj = FileObject(filelist=current, name=key)
    if isinstance(current, list):
        params[key] = FileList(current, fileobj)
    elif isinstance(current, str):
        params[key] = FileName(current, fileobj)
    else:
        # nothing to attach the information to
        return None
    return fileobj


def get_file_extra(params: Any, key: str, extra: str,
                   default: Any = None) -> Any:
    """
    Get an extra value (e.g. WAVE_FILE "type") of a FileObjectConst

    :param params: ParamDict (or SubParamDict) containing ``key``
    :param key: str, the constant key e.g. 'GENERAL.WAVE_FILE'
    :param extra: str, the extra name e.g. 'type'
    :param default: value returned when not set
    :return: the extra value
    """
    if key not in params:
        return default
    value = params[key]
    fileobj = get_fileobj(value)
    if fileobj is not None and fileobj.extras.get(extra) is not None:
        return fileobj.extras[extra]
    # fall back to the constant default for this extra
    instance = _get_instance(params, key)
    if isinstance(instance, FileObjectConst) and extra in instance.extras:
        spec_default = instance.extras[extra].get('default')
        if spec_default is not None:
            return spec_default
    return default


def set_file_extra(params: Any, key: str, extra: str, value: Any) -> None:
    """
    Set an extra value on a FileObjectConst parameter value

    Plain values are converted to FileName/FileList (source=local).

    :param params: ParamDict (or SubParamDict) containing ``key``
    :param key: str, the constant key
    :param extra: str, the extra name
    :param value: the value to set
    """
    fileobj = _attach_fileobj(params, key)
    if fileobj is not None:
        fileobj.extras[extra] = value


# example POGOS server directory used in the usage text
EXAMPLE_POGOS_URL = 'http://206.12.93.77/ari/data/pogos/demos/<dir>/'
# usage text added to every FileObjectConst description (yaml comments)
FILE_USAGE = """
How to set {name}. Files are read from (and downloaded into) the
directory given by {path}.

{name} is either a plain filename / list of filenames (local files) or a
mapping with these keys:
  filelist        {filelist_desc}
                  Leave empty for source: mast to use every matching MAST
                  file (it is filled in after downloading).
  source          where the files come from: local (default), mast (the
                  MAST archive) or pogos (the POGOS data server)
  always_download True: download again on every run. False (default):
                  only download when a file in filelist is missing
  url             (source: pogos only) the server directory of the files
  pid             (source: mast only) JWST program ID e.g. 1366
  obsnumber       (source: mast only) observation number e.g. 1
  product         {product_desc}
  match           (source: mast only, optional) list of strings every
                  filename must contain e.g. [nrs1] (default: none)
  min_size_mb     (source: mast only, optional) skip files smaller than
                  this many MB (default: 1){extras_keys}

Use ONE of the five forms below.

[A] LOCAL - you already have the file(s) on disk:
      {name}: {example}
    (equivalent long form)
      {name}:
        filelist: {example}
        source: local{product_yaml}{extras_yaml}

[B] MAST - not downloaded yet (public data; for proprietary data set the
    environment variable MAST_API_TOKEN to your MAST token first):
      {name}:
        filelist:
        source: mast
        pid: 1366
        obsnumber: 1
        product: {product}{extras_yaml}
    pid = JWST program ID, obsnumber = observation number within it,
    product = the MAST file suffix to download.
    Every *_{product}.fits file of the observation is used, except files
    smaller than min_size_mb. Optional keys (add them to this mapping):
      match: [nrs1]     - filenames must contain all of these strings
                          (default: none), e.g. one NIRSpec detector
      min_size_mb: 1    - skip files smaller than this (default 1)
    The files are downloaded by pogos_setup (if requested) or at the
    start of the run, and filelist and always_download are written back.

[C] MAST - already downloaded (what [B] becomes after downloading):
      {name}:
        filelist: {example}
        source: mast
        pid: 1366
        obsnumber: 1
        product: {product}
        always_download: False{extras_yaml}
    Nothing is downloaded while every listed file exists. Missing files
    (or always_download: True) trigger a new download from MAST.

[D] POGOS data server - not downloaded yet:
      {name}:
        filelist: {example}
        source: pogos
        url: {url}{product_yaml}{extras_yaml}
    filelist must name the file(s) on the server; they are downloaded by
    pogos_setup (if requested) or at the start of the run.

[E] POGOS data server - already downloaded:
      {name}:
        filelist: {example}
        source: pogos
        url: {url}{product_yaml}
        always_download: False{extras_yaml}
    Nothing is downloaded while every listed file exists. Missing files
    (or always_download: True) trigger a new download.
"""


class FileObjectConst(CustomConst):
    """
    An input file (or list of files) with an optional online source

    Yaml forms accepted (see FILE_USAGE):
        plain str / list               -> source = local
        mapping with filelist + source -> local, mast or pogos

    validate() returns the plain filename(s) as a FileName (str) or FileList
    (list) with the source information attached as ``.fileobj``.
    """
    class_name = 'FileObjectConst'
    # yaml loaders keep the mapping of this constant together
    yaml_mapping = True

    def __init__(self, name: str, *args: Any,
                 path_key: Optional[str] = None,
                 allow_list: bool = False,
                 product: Optional[str] = None,
                 product_options: Optional[List[str]] = None,
                 extras: Optional[Dict[str, Dict[str, Any]]] = None,
                 example: Optional[str] = None,
                 **kwargs: Any) -> None:
        """
        Construct the file object constant

        :param name: str, constant name
        :param args: positional arguments accepted by Const
        :param path_key: str, parameter key (relative to the module root e.g.
                         'PATHS.CALIBPATH') of the directory files live in
        :param allow_list: bool, for dtype=str allow a list of filenames too
        :param product: str, default product - the kind of file and, for
                        source=mast, the MAST suffix (e.g. 'uncal')
        :param product_options: list of str or None, allowed products
                                (None: any product)
        :param extras: dict, extra keys allowed in the mapping e.g.
                       dict(type=dict(dtype=str, options=[...], default=None,
                                      description='...'))
        :param example: str, example value used in the yaml description
        :param kwargs: keyword arguments accepted by CustomConst
        """
        super().__init__(name, *args, **kwargs)
        self.path_key = path_key
        self.allow_list = allow_list
        self.product = product
        self.product_options = (None if product_options is None
                                else list(product_options))
        self.extras = dict() if extras is None else dict(extras)
        self.example = example
        # module relative name (cdict.set / sub-dicts may change the group)
        self.relname = self.fullname
        # note: the usage text is added by the description property

    # ------------------------------------------------------------------
    # description
    # ------------------------------------------------------------------
    @property
    def description(self) -> str:
        """The description plus the usage text for every file source."""
        return self._full_description(self.__dict__.get('_description'))

    @description.setter
    def description(self, value: Optional[str]) -> None:
        """Store the constant specific part (usage text is added on read)."""
        # strip any usage text so it is never duplicated
        if isinstance(value, str) and 'How to set' in value:
            value = value[:value.index('How to set')].rstrip()
        self.__dict__['_description'] = value

    def _full_description(self, description: Optional[str]) -> str:
        """Append the source usage text to the description."""
        description = '' if description is None else str(description)
        is_list = self.dtype in [list, 'list']
        if self.example is not None:
            example = self.example
        elif is_list:
            example = '[file1.fits, file2.fits]'
        else:
            example = 'file.fits'
        if self.path_key is not None:
            path = self.path_key
        else:
            path = 'its directory constant'
        # extra keys in the key reference
        extras_keys = ''
        for ekey, espec in self.extras.items():
            eopts = espec.get('options', None)
            edesc = espec.get('description', '')
            if eopts is not None:
                edesc += f' [{", ".join(map(str, eopts))}]'
            extras_keys += f'\n  {ekey:15s} {edesc}'
        # what filelist holds for this constant
        if is_list:
            filelist_desc = 'the file name(s) (a list)'
        elif self.allow_list:
            filelist_desc = 'the file name, or a list of file names'
        else:
            filelist_desc = 'the file name (a single file)'
        # extra keys shown inside every yaml example
        extras_yaml = ''
        for ekey, espec in self.extras.items():
            eopts = espec.get('options', None)
            evalue = eopts[0] if eopts else '...'
            extras_yaml += f'\n        {ekey}: {evalue}'
        # product description / yaml line for this constant
        product_desc = ('the kind of file e.g. uncal, rateints, x1dints. '
                        'For source: mast\n                  also the MAST '
                        'file suffix used to find the files')
        if self.product_options is not None:
            product_desc += ('.\n                  One of: '
                             + ', '.join(self.product_options))
        if self.product is not None:
            product_desc += f' (default: {self.product})'
        product_yaml = ''
        if self.product is not None:
            product_yaml = f'\n        product: {self.product}'
        # fill the usage template for this constant
        usage_kwargs = dict(name=self.name, path=path, example=example,
                            product=self.product or 'rateints',
                            product_desc=product_desc,
                            url=EXAMPLE_POGOS_URL,
                            product_yaml=product_yaml,
                            extras_yaml=extras_yaml,
                            extras_keys=extras_keys,
                            filelist_desc=filelist_desc)
        usage = FILE_USAGE.format(**usage_kwargs)
        return description.rstrip() + '\n' + usage

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------
    def _check_filenames(self, filelist: Any, allow_empty: bool) -> Any:
        """Check a filename / list of filenames, returning a plain copy."""
        is_list = self.dtype in [list, 'list']
        if filelist is None:
            return None
        if isinstance(filelist, str):
            if is_list:
                # a single filename for a list constant becomes a list
                filelist = [filelist]
            elif not filelist.strip():
                if allow_empty:
                    return None
                self._raise(f'{self.fullname} must be a filename or '
                            f'a nonempty list of filenames')
            else:
                return str(filelist)
        if isinstance(filelist, (list, tuple)):
            if not is_list and not self.allow_list:
                self._raise(f'{self.fullname} must be a single filename '
                            f'(got a list)')
            filelist = list(filelist)
            if len(filelist) == 0:
                if allow_empty:
                    return None
                self._raise(f'{self.fullname} must be a filename or '
                            f'a nonempty list of filenames')
            for fname in filelist:
                if not isinstance(fname, str) or not fname.strip():
                    self._raise(f'{self.fullname} must be a filename or '
                                f'a nonempty list of filenames '
                                f'(got entry {fname!r})')
            return [str(fname) for fname in filelist]
        self._raise(f'{self.fullname} must be a filename, a list of '
                    f'filenames or a mapping with "filelist" and "source" '
                    f'(got {type(filelist).__name__})')

    def _check_extra(self, ekey: str, evalue: Any) -> Any:
        """Validate an extra key value against its spec."""
        spec = self.extras[ekey]
        if evalue is None:
            return None
        dtype = spec.get('dtype', None)
        if dtype is not None and not isinstance(evalue, dtype):
            self._raise(f'{self.fullname}.{ekey} must be of type '
                        f'{dtype.__name__} (got {evalue!r})')
        options = spec.get('options', None)
        if options is not None and evalue not in options:
            self._raise(f'{self.fullname}.{ekey} must be one of {options} '
                        f'(got {evalue!r})')
        return evalue

    def _check_product(self, product: Any) -> Optional[str]:
        """Validate a product (None uses the constant default)."""
        if product is None:
            product = self.product
        if product is None:
            return None
        product = str(product).strip()
        if (self.product_options is not None
                and product not in self.product_options):
            self._raise(f'{self.fullname}.product must be one of '
                        f'{self.product_options} (got {product!r})')
        return product

    def parse(self, value: Any) -> Optional[FileObject]:
        """
        Convert any accepted yaml value into a FileObject

        :param value: str, list, dict, FileName, FileList or FileObject
        :return: FileObject (or None if value is None)
        """
        if value is None:
            return None
        if isinstance(value, FileObject):
            fileobj = value.copy()
            fileobj.filelist = self._check_filenames(fileobj.filelist,
                                                     allow_empty=fileobj.online)
            return fileobj
        existing = get_fileobj(value)
        if existing is not None:
            fileobj = existing.copy()
            fileobj.filelist = self._check_filenames(
                list(value) if isinstance(value, list) else str(value),
                allow_empty=fileobj.online)
            return fileobj
        if not isinstance(value, dict):
            filelist = self._check_filenames(value, allow_empty=False)
            return FileObject(filelist=filelist, source='local',
                              product=self.product,
                              path_key=self.path_key, name=self.fullname)
        # ----------------------------------------------------------------
        # mapping form
        # accept hyphenated keys (always-download)
        mapping = {str(key).replace('-', '_').lower(): val
                   for key, val in value.items()}
        if 'filelist' not in mapping:
            self._raise(f'{self.fullname} mapping must contain "filelist" '
                        f'(got keys {list(value.keys())})')
        source = mapping.get('source', 'local')
        source = 'local' if source is None else str(source).lower()
        if source not in FILE_SOURCES:
            self._raise(f'{self.fullname}.source must be one of '
                        f'{list(FILE_SOURCES)} (got {source!r})')
        allowed = (set(FILE_BASE_KEYS) | set(FILE_SOURCE_KEYS[source])
                   | set(self.extras.keys()))
        unknown = [key for key in mapping if key not in allowed]
        if len(unknown) > 0:
            self._raise(f'{self.fullname}: keys {unknown} are not valid for '
                        f'source={source}. Allowed keys: {sorted(allowed)}')
        online = source in ('pogos', 'mast')
        filelist = self._check_filenames(mapping.get('filelist'),
                                         allow_empty=online)
        # the kind of file (all sources, MAST suffix for source=mast)
        kwargs = dict(product=self._check_product(
            mapping.get('product', None)))
        # source specific checks
        if source == 'local' and filelist is None:
            self._raise(f'{self.fullname}: filelist must be set when '
                        f'source=local')
        if source == 'pogos':
            if filelist is None:
                self._raise(f'{self.fullname}: filelist must list the file '
                            f'names on the POGOS server when source=pogos')
            if not mapping.get('url'):
                self._raise(f'{self.fullname}: url must be set when '
                            f'source=pogos')
            kwargs['url'] = str(mapping['url'])
        if source == 'mast':
            for key in ['pid', 'obsnumber']:
                if mapping.get(key) is None:
                    self._raise(f'{self.fullname}: {key} must be set when '
                                f'source=mast')
                try:
                    kwargs[key] = int(mapping[key])
                except (TypeError, ValueError):
                    self._raise(f'{self.fullname}.{key} must be an integer '
                                f'(got {mapping[key]!r})')
            if kwargs.get('product') is None:
                self._raise(f'{self.fullname}: product (e.g. uncal, '
                            f'rateints, x1dints) must be set when '
                            f'source=mast')
            match = mapping.get('match', None)
            if isinstance(match, str):
                match = [match]
            if match is not None:
                if (not isinstance(match, list)
                        or not all(isinstance(m, str) for m in match)):
                    self._raise(f'{self.fullname}.match must be a list of '
                                f'strings (got {match!r})')
            kwargs['match'] = match
            min_size = mapping.get('min_size_mb', None)
            if min_size is not None:
                if isinstance(min_size, bool) or not isinstance(min_size,
                                                                Real):
                    self._raise(f'{self.fullname}.min_size_mb must be a '
                                f'number (got {min_size!r})')
                kwargs['min_size_mb'] = float(min_size)
        always = mapping.get('always_download', False)
        if always is None:
            always = False
        if not isinstance(always, bool):
            self._raise(f'{self.fullname}.always_download must be True or '
                        f'False (got {always!r})')
        extras = dict()
        for ekey in self.extras:
            evalue = self._check_extra(ekey, mapping.get(ekey, None))
            if evalue is None:
                evalue = self.extras[ekey].get('default', None)
            extras[ekey] = evalue
        return FileObject(filelist=filelist, source=source,
                          always_download=always, extras=extras,
                          path_key=self.path_key, name=self.fullname,
                          explicit=True, **kwargs)

    def wrap(self, fileobj: Optional[FileObject]) -> Any:
        """
        Convert a FileObject into the value code receives in params

        :param fileobj: FileObject or None
        :return: FileList (list constants or list filelists), FileName
                 (single filename) or None (unresolved single file)
        """
        if fileobj is None:
            return None
        is_list = self.dtype in [list, 'list']
        filelist = fileobj.filelist
        if is_list or isinstance(filelist, list):
            return FileList(fileobj.files, fileobj)
        if filelist is None:
            # unresolved single file (online, not yet downloaded)
            return FileName('', fileobj)
        return FileName(filelist, fileobj)

    def validate(self, test_value: Any = None, quiet: bool = False,
                 source: Optional[str] = None) -> Any:
        """
        Validate a stored/candidate value (str, list or mapping)

        :param test_value: candidate, or None to validate the stored value
        :param quiet: accepted for Const compatibility
        :param source: accepted for Const compatibility
        :return: True for stored validation, otherwise FileName/FileList
                 (local plain values are returned as plain str/list)
        """
        value = self.value if test_value is None else test_value
        fileobj = self.parse(value)
        # plain local values stay plain (identical behaviour to before)
        plain = (fileobj is not None and not fileobj.explicit
                 and get_fileobj(value) is None and not self.extras)
        if plain:
            true_value = fileobj.filelist
            if isinstance(true_value, list):
                true_value = list(true_value)
        else:
            true_value = self.wrap(fileobj)
        if test_value is None:
            self.true_value = true_value
            return True
        return true_value

    # ------------------------------------------------------------------
    # yaml output
    # ------------------------------------------------------------------
    def yaml_value(self, value: Any) -> Any:
        """
        Convert a parameter value back to its yaml form

        :param value: the parameter value (plain, FileName, FileList, dict)
        :return: plain value (local without source info) or mapping
        """
        if value is None:
            return None
        if isinstance(value, dict):
            try:
                fileobj = self.parse(value)
            except Exception:
                return value
        else:
            fileobj = get_fileobj(value)
            if fileobj is None:
                # plain value: local (unless extras need the mapping form)
                if not self.extras:
                    return list(value) if isinstance(value, list) else value
                fileobj = self.parse(value)
            else:
                fileobj = fileobj.copy()
                if isinstance(value, list):
                    fileobj.filelist = [str(v) for v in value]
                else:
                    fileobj.filelist = str(value) if value else None
        if fileobj is None:
            return None
        has_extras = any(val is not None for val in fileobj.extras.values())
        # a non default product needs the mapping form to be kept
        other_product = fileobj.product not in (None, self.product)
        plain_local = (fileobj.source == 'local' and not fileobj.explicit
                       and not has_extras and not other_product)
        if plain_local:
            filelist = fileobj.filelist
            return list(filelist) if isinstance(filelist, list) else filelist
        return fileobj.to_dict()


def is_mapping_const(instance: Any) -> bool:
    """True if a constant's yaml value is a mapping kept as one value."""
    if getattr(instance, 'yaml_mapping', False):
        return True
    return getattr(instance, 'dtype', None) in [dict, 'dict']


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
