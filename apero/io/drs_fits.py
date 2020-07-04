#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time, TimeDelta
from astropy import version as av
from astropy import units as uu
import os
import warnings
import traceback

from apero.core import constants
from apero.core.core import drs_log
from apero import lang
from apero.io import drs_table
from apero.io import drs_lock
from apero.io import drs_path


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_fits.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = drs_log.find_param
# Get the text types
TextEntry = lang.drs_text.TextEntry
# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)


# =============================================================================
# Define classes
# =============================================================================
# noinspection PyCompatibility
class Header(fits.Header):
    """
    Wrapper class for fits headers that allows us to add functionality.
    - Stores temporary items with keys starting with '@@@'
       - Only shows up through "[]" and "in" operations
    - Can automatically convert NaN values to strings
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__temp_items = {}

    def __setitem__(self, key, item):
        if key.startswith('@@@'):
            self.__temp_items.__setitem__(self.__get_temp_key(key), item)
        elif key == '':
            pass
        else:
            nan_filtered = self.__nan_check(item)
            super().__setitem__(key, nan_filtered)

    def __getitem__(self, key):
        if key.startswith('@@@'):
            return self.__temp_items.__getitem__(self.__get_temp_key(key))
        else:
            return super().__getitem__(key)

    def __contains__(self, key):
        if key.startswith('@@@'):
            return self.__temp_items.__contains__(self.__get_temp_key(key))
        else:
            return super().__contains__(key)

    def copy(self, strip=False):
        header = Header(super().copy(strip), copy=False)
        header.__temp_items = self.__temp_items.copy()
        return header

    def to_fits_header(self, strip=True, nan_to_string=True):
        header = super().copy(strip=strip)
        if nan_to_string:
            for key in list(header.keys()):
                header[key] = header[key]
        return header

    @staticmethod
    def from_fits_header(fits_header):
        return Header(fits_header, copy=True)

    @staticmethod
    def __get_temp_key(key):
        return key[3:]

    @staticmethod
    def __nan_check(value):
        if isinstance(value, float) and np.isnan(value):
            return 'NaN'
        elif type(value) == tuple:
            return (Header.__nan_check(value[0]),) + value[1:]
        else:
            return value


# =============================================================================
# Define read functions
# =============================================================================
def id_drs_file(params, recipe, drs_file_sets, filename=None, nentries=None,
                required=True, use_input_file=False):

    func_name = __NAME__ + '.id_drs_file()'
    # ----------------------------------------------------------------------
    # deal with list vs no list for drs_file_sets
    if isinstance(drs_file_sets, list):
        pass
    else:
        drs_file_sets = [drs_file_sets]
    # ----------------------------------------------------------------------
    # storage
    found = False
    kinds = []
    names = []
    file_set = None
    # ----------------------------------------------------------------------
    # loop around file set
    for file_set in drs_file_sets:
        # get the names of the file_set
        names.append(file_set.name)
        # ------------------------------------------------------------------
        # check we have entries
        if len(file_set.fileset) == 0:
            continue
        # ------------------------------------------------------------------
        # check we have a recipe set
        if file_set.recipe is None:
            file_set.recipe = recipe
        # ------------------------------------------------------------------
        # check we ahve a file set
        if file_set.filename is None:
            if filename is None:
                WLOG(params, 'error', 'filename is not set')
            else:
                file_set.set_filename(filename)
        # ------------------------------------------------------------------
        # get the associated files with this generic drs file
        fileset = list(file_set.fileset)
        # ------------------------------------------------------------------
        # loop around files
        for drs_file in fileset:
            # --------------------------------------------------------------
            # debug
            dargs = [str(drs_file)]
            WLOG(params, 'debug', TextEntry('90-010-00001', args=dargs))
            # --------------------------------------------------------------
            # copy info from given_drs_file into drs_file
            file_in = drs_file.copyother(file_set, recipe=recipe)
            # --------------------------------------------------------------
            # load the header for this kind
            try:
                # need to read the file header for this specific drs file
                file_in.read_header(log=False)
                # copy in hdict from file_set
                # - this is the only way to get keys added from file that is
                #   read above
                if file_set.hdict is not None:
                    for key in file_set.hdict:
                        file_in.header[key] = file_set.hdict[key]

            # if exception occurs continue to next file
            #    (this is not the correct file)
            except Exception as _:
                continue
            except SystemExit as _:
                continue
            # --------------------------------------------------------------
            # check this file is valid
            cond, _ = file_in.check_file()
            # --------------------------------------------------------------
            # if True we have found our file
            if cond:
                # ----------------------------------------------------------
                found = True
                # ----------------------------------------------------------
                # load the data for this kind
                cond1 = file_set.data is not None
                cond2 = file_set.header is not None
                # use the data if flagged and if possible (cond1 & cond2)
                if use_input_file and cond1 and cond2:
                    # shallow copy data
                    file_in.data = file_set.data
                    # copy over header
                    file_in.header = file_set.header
                else:
                    file_in.read_data()
                # ----------------------------------------------------------
                # append to list
                kinds.append(file_in)
                # ----------------------------------------------------------
                # if we only want one entry break here
                if nentries == 1:
                    break
    # ----------------------------------------------------------------------
    # deal with no files found
    if len(kinds) == 0 and required:
        # get header keys for info purposes
        keys = ['KW_CCAS', 'KW_CREF', 'KW_OBSTYPE', 'KW_TARGET_TYPE',
                'KW_OBJNAME']
        argstr = ''
        for key in keys:
            if file_set is not None and file_set.header is not None:
                value = file_set.get_key(key)
            else:
                value = None
            argstr += '\t{0}: {1}\n'.format(key, value)

        eargs = [' '.join(names), file_set.filename, argstr, func_name]
        WLOG(params, 'error', TextEntry('00-010-00001', args=eargs))
    # ----------------------------------------------------------------------
    # return found and the drs_file instance
    if len(kinds) == 0:
        return found, kinds
    elif nentries == None:
        return found, kinds
    elif nentries == 1:
        return found, kinds[0]
    else:
        return found, kinds[:nentries]


# =============================================================================
# Define read functions
# =============================================================================
def readfits(params, filename, getdata=True, gethdr=False, fmt='fits-image',
             ext=0, func=None, log=True):
    """
    The drs fits file read function

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the absolute path to the file
    :param getdata: bool, whether to return data from "ext"
    :param gethdr: bool, whether to return header from "ext"
    :param fmt: str, format of data (either 'fits-image' or 'fits-table'
    :param ext: int, the extension to open
    :param func: str, function name of calling function (input function)

    :type params: ParamDict
    :type filename: str
    :type getdata: bool
    :type gethdr: bool
    :type fmt: str
    :type ext: int
    :type func: str

    :returns: if getdata and gethdr: returns data, header, if getdata return
              data, if gethdr returns header.
              if fmt 'fits-time' returns np.array for data and dictionary for
              header, if fmt 'fits-table' returns astropy.table for data and
              dictionary for header
    """
    if func is None:
        func_name = __NAME__ + '.readfits()'
    else:
        func_name = '{0} and {1}'.format(func, __NAME__ + '.readfits()')
    # define allowed values of 'fmt'
    allowed_formats = ['fits-image', 'fits-table', 'fits-multi']
    # -------------------------------------------------------------------------
    # deal with filename not existing
    if not os.path.exists(filename):
        # check directory exists
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            eargs = [dirname, os.path.basename(filename), func_name]
            WLOG(params, 'error', TextEntry('01-001-00013', args=eargs))
        else:
            eargs = [os.path.basename(filename), dirname, func_name]
            WLOG(params, 'error', TextEntry('01-001-00012', args=eargs))
    # -------------------------------------------------------------------------
    # deal with obtaining data
    if fmt == 'fits-image':
        data, header = _read_fitsimage(params, filename, getdata, gethdr, ext,
                                       log=log)
    elif fmt == 'fits-table':
        data, header = _read_fitstable(params, filename, getdata, gethdr, ext,
                                       log=log)
    elif fmt == 'fits-multi':
        data, header = _read_fitsmulti(params, filename, getdata, gethdr,
                                       log=log)
    else:
        cfmts = ', '.join(allowed_formats)
        eargs = [filename, fmt, cfmts, func_name]
        WLOG(params, 'error', TextEntry('00-008-00019', args=eargs))
        data, header = None, None
    # -------------------------------------------------------------------------
    # deal with return
    if getdata and gethdr:
        return data, header
    elif getdata:
        return data
    elif gethdr:
        return header
    else:
        return None


def read_header(params, filename, ext=0, log=True):
    func_name = __NAME__ + '.read_header()'
    # try to open header
    try:
        header = fits.getheader(filename, ext=ext)
    except Exception as e:
        if log:
            eargs = [os.path.basename(filename), ext, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00010', args=eargs))
            header = None
        else:
            raise e
    # return header
    return header


def _read_fitsmulti(params, filename, getdata, gethdr):
    func_name = __NAME__ + '._read_fitsmulti()'
    # attempt to open hdu of fits file
    try:
        hdulist = fits.open(filename)
    except Exception as e:
        eargs = [filename, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('01-001-00006', args=eargs))
        hdulist = None
    # -------------------------------------------------------------------------
    # get the number of fits files in filename
    try:
        n_ext = len(hdulist)
    except Exception as e:
        WLOG(params, 'warning', TextEntry('10-001-00005', args=[type(e), e]))
        n_ext = None
    # deal with unknown number of extensions
    if n_ext is None:
        data, header = deal_with_bad_header(params, hdulist, filename)
    # -------------------------------------------------------------------------
    # else get the data and header based on how many extnesions there are
    else:
        dataarr, headerarr = [], []
        for it in range(n_ext):
            # append header
            try:
                headerarr.append(hdulist[it].header)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00008', args=eargs))
            # append data
            try:
                if isinstance(hdulist[it].data, fits.BinTableHDU):
                    dataarr.append(Table.read(hdulist[it].data))
                else:
                    dataarr.append(hdulist[it].data)
            except Exception as e:
                eargs = [os.path.basename(filename), it, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('01-001-00007', args=eargs))
        data = list(dataarr)
        header = list(headerarr)
    # -------------------------------------------------------------------------
    # return data and/or header
    if getdata and gethdr:
        return data, header
    elif getdata:
        return data
    else:
        return header


def _read_fitsimage(params, filename, getdata, gethdr, ext=0, log=True):
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = fits.getdata(filename, ext=ext)
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00014', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
                WLOG(params, 'error', emsg)
                data = None
            else:
                raise e
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            header = fits.getheader(filename, ext=ext)
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00015', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
                WLOG(params, 'error', emsg)
                header = None
            else:
                raise e
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


def _read_fitstable(params, filename, getdata, gethdr, ext=0, log=True):
    # -------------------------------------------------------------------------
    # deal with getting data
    if getdata:
        try:
            data = Table.read(filename, format='fits')
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00016', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
                WLOG(params, 'error', emsg)
                data = None
            else:
                raise e
    else:
        data = None
    # -------------------------------------------------------------------------
    # deal with getting header
    if gethdr:
        try:
            header = fits.getheader(filename, ext=ext)
        except Exception as e:
            if log:
                string_trackback = traceback.format_exc()
                emsg = TextEntry('01-001-00017', args=[filename, ext, type(e)])
                emsg += '\n\n' + TextEntry(string_trackback)
                WLOG(params, 'error', emsg)
                header = None
            else:
                raise e
    else:
        header = None
    # -------------------------------------------------------------------------
    # return data and header
    return data, header


# =============================================================================
# Define write functions
# =============================================================================
def writefits(params, filename, data, header, datatype='image', dtype=None,
              func=None):
    # ------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename(filename)
    # start a lock
    lock = drs_lock.Lock(params, lockfile)
    # ------------------------------------------------------------------
    # make locked read function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_write():
        return _write_fits(params, filename, data, header, datatype, dtype,
                           func)
    # ------------------------------------------------------------------
    # try to run locked read function
    try:
        locked_write()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def _write_fits(params, filename, data, header, datatype='image', dtype=None,
                func=None):
    # deal with function name coming from somewhere else
    if func is None:
        func_name = __NAME__ + '.writefits()'
    else:
        func_name = '{0} (via {1})'.format(func, __NAME__ + '.writefits()')
    # ----------------------------------------------------------------------
    # check if file exists and remove it if it does
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            eargs = [os.path.basename(filename), type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00003', args=eargs))
    # ----------------------------------------------------------------------
    # make sure we are dealing with lists of data and headers
    if not isinstance(data, list):
        data = [data]
    if not isinstance(header, list):
        header = [header.to_fits_header()]
    if not isinstance(datatype, list):
        datatype = [datatype]
    if dtype is not None and not isinstance(dtype, list):
        dtype = [dtype]
    # ----------------------------------------------------------------------
    # header must be same length as data
    if len(data) != len(header):
        eargs = [filename, len(data), len(header), func_name]
        WLOG(params, 'error', TextEntry('00-013-00004', args=eargs))
    # datatype must be same length as data
    if len(data) != len(datatype):
        eargs = [filename, len(data), len(datatype), func_name]
        WLOG(params, 'error', TextEntry('00-013-00005', args=eargs))
    # if dtype is not None must be same length as data
    if dtype is not None:
        if len(data) != len(dtype):
            eargs = [filename, len(data), len(dtype), func_name]
            WLOG(params, 'error', TextEntry('00-013-00006', args=eargs))
    # ----------------------------------------------------------------------
    # create the multi HDU list
    # try to create primary HDU first
    if isinstance(header[0], Header):
        header0 = header[0].to_fits_header()
    else:
        header0 = header[0]
    # set up primary HDU (if data[0] == image then put this in the primary)
    #   else if table then primary HDU should be empty
    if datatype[0] == 'image':
        hdu0 = fits.PrimaryHDU(data[0], header=header0)
        start = 1
    else:
        hdu0 = fits.PrimaryHDU()
        start = 0

    if dtype is not None:
        hdu0.scale(type=dtype[0], **SCALEARGS)
    # add all others afterwards
    hdus = [hdu0]
    for it in range(start, len(data)):
        if datatype[it] == 'image':
            fitstype = fits.ImageHDU
        elif datatype[it] == 'table':
            fitstype = fits.BinTableHDU
        else:
            continue
        # add to hdu list
        if isinstance(header[it], Header):
            header_it = header[it].to_fits_header()
        else:
            header_it = header[it]
        hdu_i = fitstype(data[it], header=header_it)
        if dtype is not None and datatype[it] == 'image':
            if dtype[it] is not None:
                hdu_i.scale(type=dtype[it])
        hdus.append(hdu_i)
    # convert to  HDU list
    hdulist = fits.HDUList(hdus)
    # except Exception as e:
    #     eargs = [type(e), e, func_name]
    #     WLOG(params, 'error', TextEntry('01-001-00004', args=eargs))
    #     hdulist = None
    # ---------------------------------------------------------------------
    # write to file
    with warnings.catch_warnings(record=True) as w:
        try:
            hdulist.writeto(filename, overwrite=True)
        except Exception as e:
            eargs = [os.path.basename(filename), type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-001-00005', args=eargs))
    # ---------------------------------------------------------------------
    # ignore truncated comment warning since spirou images have some poorly
    #   formatted header cards
    w1 = []
    for warning in w:
        # Note: cannot change language as we are looking for python error
        #       this is in english and shouldn't be changed
        wmsg = 'Card is too long, comment will be truncated.'
        if wmsg != str(warning.message):
            w1.append(warning)
    # add warnings to the warning logger and log if we have them
    drs_log.warninglogger(params, w1)


def add_header_key(header, keystore, value=None):
    # only used if one cannot use DrsFitsFile
    hkey, hvalue, hcomment = keystore
    # deal with value set
    if value is not None:
        hvalue = value
    # add to header
    header[hkey] = (hvalue, hcomment)
    # return header
    return header


# =============================================================================
# Define search functions
# =============================================================================
def find_files(params, recipe, kind=None, path=None, logic='and', fiber=None,
               return_table=False, night=None, **kwargs):
    """
    Find files using kwargs (using index files located in 'kind' or 'path')

    If path is set will use this path to look for index files

    If kind is set to 'raw' uses DRS_DATA_RAW path, if kind is set to 'tmp'
    uses DRS_DATA_WORKING path, if kind is set to 'red' uses DRS_DATA_REDUC
    else uses params['INPATH']

    The logic defines how kwargs are added.
    kwargs must be in index file (column names) or in params as header keyword
    stores (i.e. KW_DPRTYPE = [HEADER key, HEADER value, HEADER comment]

    i.e.

    find_files(params, kind='tmp', KW_DPRTYPE='FP_FP')
    --> will return all files in the working directory with DPRTYPE = 'FP_FP'

    find_files(params, kind='red', KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK'],
               KW_OUTPUT='EXT_E2DS')
    --> will return all files in reduced directory with:
          DPRTYPE = OBJ_FP or OBJ_DARK   and DRSOUTID

    :param params:
    :param kind:
    :param path:
    :param logic:
    :param kwargs:
    :return:
    """
    func_name = __NAME__ + '.find_files()'
    # ----------------------------------------------------------------------
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get the index file col name
    filecol = params['DRS_INDEX_FILENAME']
    nightcol = params['REPROCESS_NIGHTCOL']
    timecol = 'KW_MID_OBS_TIME'
    # ----------------------------------------------------------------------
    # deal with setting path
    if path is not None:
        path = str(path)
        columns = None
        index_files = None
        index_dir = None
    elif kind == 'raw':
        # get index table (generate if needed)
        indextable, index_dir = find_raw_files(params, recipe)
        # construct index file path for raw
        raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE',
                                'raw_index_file', kwargs, func_name)
        mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
        # set the columns from table
        columns = indextable.colnames
        # set index files
        index_files = [mpath]
    elif kind == 'tmp':
        path = params['DRS_DATA_WORKING']
        columns = pconst.OUTPUT_FILE_HEADER_KEYS()
        index_files = None
        index_dir = None
    elif kind == 'red':
        path = params['DRS_DATA_REDUC']
        columns = pconst.OUTPUT_FILE_HEADER_KEYS()
        index_files = None
        index_dir = None
    else:
        path = params['INPATH']
        columns = None
        index_files = None
        index_dir = None
    # ----------------------------------------------------------------------
    # deal with making sure all kwargs are in columns (if columns defined)
    if columns is not None:
        for kwarg in kwargs:
            # if dkey not in columns report error
            if kwarg not in columns:
                # log and raise error
                eargs = [kwarg, path, func_name]
                WLOG(params, 'error', TextEntry('00-004-00001', args=eargs))
    # ----------------------------------------------------------------------
    # get index files
    if index_files is None:
        index_files = get_index_files(params, path, night=night)
    # ----------------------------------------------------------------------
    # valid files storage
    valid_files = []
    table_list = []
    time_list = []
    # filters added string
    fstring = ''
    # ----------------------------------------------------------------------
    # loop through index files
    for index_file in index_files:
        # read index file
        index = drs_table.read_fits_table(params, index_file)
        # get directory
        if index_dir is None:
            dirname = os.path.dirname(index_file)
        else:
            dirname = index_dir
        # ------------------------------------------------------------------
        # overall masks
        mask = np.ones(len(index), dtype=bool)
        # filters added string
        fstring = ''
        # ------------------------------------------------------------------
        # filter via kwargs
        for kwarg in kwargs:
            # --------------------------------------------------------------
            # if dkey is not found in index file then report error
            if kwarg not in index.colnames:
                # report error
                eargs = [kwarg, index_file, func_name]
                WLOG(params, 'error', TextEntry('00-004-00002', args=eargs))
            # --------------------------------------------------------------
            # deal with list of args
            if isinstance(kwargs[kwarg], list):
                # get new mask
                mask0 = np.zeros_like(mask)
                # loop around kwargs[kwarg] values (has to be logic==or here)
                for value in kwargs[kwarg]:
                    mask0 |= (index[kwarg] == value.strip())
            else:
                mask0 = (index[kwarg] == kwargs[kwarg])
            # --------------------------------------------------------------
            # mask by filter
            if logic == 'or':
                mask |= mask0
            else:
                mask &= mask0
            # --------------------------------------------------------------
            # add to fstring
            fstring += '\n\t{0}=\'{1}\''.format(kwarg, kwargs[kwarg])
        # ------------------------------------------------------------------
        # get files for those that remain
        masked_files = index[filecol][mask]
        if index_dir is None:
            nightnames = np.array(mask).astype(int)
        else:
            nightnames = index[nightcol][mask]
        # ------------------------------------------------------------------
        masked_index = index[mask]
        # new mask for index files
        mask1 = np.zeros(len(masked_files), dtype=bool)
        # check that files exist
        # loop around masked files
        for row, filename in enumerate(masked_files):
            # deal with requiring night name
            if index_dir is None:
                nightname = ''
            else:
                nightname = nightnames[row]
            # --------------------------------------------------------------
            # deal with fiber
            if fiber is not None:
                # two conditions for not having fiber in name
                cond1 = '_{0}.'.format(fiber) not in filename
                cond2 = '_{0}_'.format(fiber) not in filename
                # if both conditions are True then skip
                if cond1 and cond2:
                    continue
            # get time value
            timeval = float(masked_index[timecol][row])
            # construct absolute path
            absfilename = os.path.join(dirname, nightname, filename)
            # check that file exists
            if not os.path.exists(absfilename):
                continue
            # deal with returning index
            mask1[row] = True
            # append to storage
            if absfilename not in valid_files:
                valid_files.append(absfilename)
                time_list.append(timeval)
        # ------------------------------------------------------------------
        # append to table list
        if return_table:
            table_list.append(masked_index[mask1])
    # ----------------------------------------------------------------------
    # log found
    wargs = [len(valid_files), fstring]
    WLOG(params, '', TextEntry('40-004-00004', args=wargs))
    # ----------------------------------------------------------------------
    # define sort mask (sort by time column)
    sortmask = np.argsort(time_list)
    # make sure valid_files is a numpy array
    valid_files = np.array(valid_files)
    # deal with table list
    if return_table:
        indextable = drs_table.vstack_cols(params, table_list)
        return valid_files[sortmask], indextable[sortmask]
    else:
        # return full list
        return valid_files[sortmask]


def get_index_files(params, path=None, required=True, night=None):
    """
    Get index files in path (or sub-directory of path)
        if path is "None" params['INPATH'] is used

    :param params: ParamDict, the parameter dictionary of constants
    :param path: str, the path to check for filetypes (must have index files
                 in this path or sub directories of this path)
                 if path is "None" params['INPATH'] is used
    :param required: bool, if True generates an error when None found
    :param night: str or None, if set filters index files by night

    :type params: ParamDict
    :type path: str
    :type required: bool
    :type night: str

    :return: the absolute paths to all index files under path
    :rtype: list[str]
    """
    func_name = __NAME__ + '.get_index_files()'
    # deal with no path set
    if path is None:
        path = params['INPATH']
    # storage of index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        # skip nights if required
        if night is not None:
            if not root.strip(os.sep).endswith(night):
                continue
        for filename in files:
            if filename == params['DRS_INDEX_FILE']:
                index_files.append(os.path.join(root, filename))
    # log number of index files found
    if len(index_files) > 0:
        WLOG(params, '', TextEntry('40-004-00003', args=[len(index_files)]))
    elif required:
        eargs = [path, func_name]
        WLOG(params, 'error', TextEntry('01-001-00021', args=eargs))
    # return the index files
    return np.sort(index_files)


def find_raw_files(params, recipe, **kwargs):
    func_name = __NAME__ + '.find_raw_files()'
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col',
                         kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    sortcol = pcheck(params, 'REPROCESS_SORTCOL_HDRKEY', 'sortcol', kwargs,
                     func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE',
                            'raw_index_file',
                            kwargs, func_name)
    itable_filecol = pcheck(params, 'DRS_INDEX_FILENAME', 'itable_filecol',
                            kwargs, func_name)
    # get path
    path, rpath = _get_path_and_check(params, 'DRS_DATA_RAW')

    # print progress
    WLOG(params, 'info', TextEntry('40-503-00010'))

    # get files
    gfout = _get_files(params, recipe, path, rpath)
    nightnames, filelist, basenames, mod_times, mkwargs = gfout

    # construct a table
    mastertable = Table()
    mastertable[night_col] = nightnames
    mastertable[itable_filecol] = basenames
    mastertable[absfile_col] = filelist
    mastertable[modified_col] = mod_times
    for kwarg in mkwargs:
        mastertable[kwarg] = mkwargs[kwarg]
    # sort by sortcol
    sortmask = np.argsort(mastertable[sortcol])
    mastertable = mastertable[sortmask]
    # save master table
    mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    mastertable.write(mpath, overwrite=True)
    # return the file list
    return mastertable, rpath


def fix_header(params, recipe, infile=None, header=None, **kwargs):
    """
    Instrument specific header fixes are define in pseudo_const.py for an
    instrument and called here (function in pseudo_const.py is HEADER_FIXES)
    :param params:
    :param infile:
    :return:
    """
    # deal with no header
    if header is None:
        header = infile.header
        hdict = infile.hdict
        has_infile = True
    else:
        has_infile = False
        hdict = Header()

    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # use pseudo constant to apply any header fixes required (specific to
    #   a specific instrument) and update the header
    header, hdict = pconst.HEADER_FIXES(params=params, recipe=recipe,
                                        header=header, hdict=hdict, **kwargs)
    # if the input was an infile return the infile back
    if has_infile:
        # return the updated infile
        infile.header = header
        infile.hdict = hdict
        return infile
    # else return the header (assuming input was a header only)
    else:
        # else return the header
        return header, hdict


# =============================================================================
# Define other functions
# =============================================================================
def combine(params, recipe, infiles, math='average', same_type=True):
    """
    Takes a list of infiles and combines them (infiles must be DrsFitsFiles)
    combines using the math given.

    Allowed math:
        'sum', 'add', '+'
        'average', 'mean'
        'subtract', '-'
        'divide', '/'
        'multiply', 'times', '*'

    Note 'infiles' must be all the same DrsFitsFile type to combine by default,
    use 'same_type=False' to override this option

    Note the header is copied from infiles[0]

    :param params: ParamDict, parameter dictionary of constants
    :param infiles: list of DrsFiles, list of DrsFitsFiles to combine
    :param math: str, the math allowed (see above)
    :param same_type: bool, if True all infiles must have the same DrsFitFile
                      dtype

    :type params: ParamDict
    :type infiles: list[DrsFitsFile]
    :type math: str
    :type same_type: bool

    :return: Returns the combined DrsFitFile (header same as infiles[0])
    :rtype: DrsFitsFile
    """
    func_name = __NAME__ + '.combine()'
    # if we have a string assume we have 1 file and skip combine
    if type(infiles) is str:
        return infiles
    # make sure infiles is a list
    if type(infiles) is not list:
        WLOG(params, 'error', TextEntry('00-001-00020', args=[func_name]))
    # if we have only one file (or none) skip combine
    if len(infiles) == 1:
        return infiles[0]
    elif len(infiles) == 0:
        return infiles
    # check that all infiles are the same DrsFileType
    if same_type:
        for it, infile in enumerate(infiles):
            if infile.name != infiles[0].name:
                eargs = [infiles[0].name, it, infile.name, func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))

    # get output path from params
    outpath = str(params['OUTPATH'])
    # check if outpath is set
    if outpath is None:
        WLOG(params, 'error', TextEntry('01-001-00023', args=[func_name]))
        return None
    # get the absolute path (for combined output)
    if params['NIGHTNAME'] is None:
        outdirectory = ''
    else:
        outdirectory = params['NIGHTNAME']
    # combine outpath and out directory
    abspath = os.path.join(outpath, outdirectory)
    # make new infile using math
    outfile = infiles[0].combine(infiles[1:], math, same_type, path=abspath)
    # update the number of files
    outfile.numfiles = len(infiles)
    # write to disk
    WLOG(params, '', TextEntry('40-001-00025', args=[outfile.filename]))
    outfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return combined infile
    return outfile


def get_mid_obs_time(params, header, out_fmt=None, **kwargs):
    func_name = __NAME__ + '.get_mid_obs_time()'
    # get obs_time
    outkey = params['KW_MID_OBS_TIME'][0]
    # get format from params
    timefmt = params.instances['KW_MID_OBS_TIME'].datatype
    # get data type from params
    timetype = params.instances['KW_MID_OBS_TIME'].dataformat
    # get raw value from header
    rawtime = header[outkey]
    # get time object
    obstime = Time(timetype(rawtime), format=timefmt)
    # set the method for getting mid obs time
    method = 'header'
    dbname = 'header_time'
    # return time in requested format
    if out_fmt is None:
        return obstime, method
    elif out_fmt == 'mjd':
        return float(obstime.mjd), method
    elif out_fmt == 'jd':
        return float(obstime.jd), method
    elif out_fmt == 'iso' or out_fmt == 'human':
        return obstime.iso, method
    elif out_fmt == 'unix':
        return float(obstime.unix), method
    elif out_fmt == 'decimalyear':
        return float(obstime.decimalyear), method
    else:
        kinds = ['None', 'human', 'iso', 'unix', 'mjd', 'jd', 'decimalyear']
        eargs = [dbname, ' or '.join(kinds), out_fmt, func_name]
        WLOG(params, 'error', TextEntry('00-001-00030', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
def deal_with_bad_header(p, hdu, filename):
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param p: ParamDict, the constants file
    :param hdu: astropy.io.fits HDU
    :param filename: string - the filename for logging

    :return data:
    :return header:
    """
    # define condition to pass
    cond = True
    # define iterator
    it = 0
    # define storage
    datastore = []
    headerstore = []
    # loop through HDU's until we cannot open them
    while cond:
        # noinspection PyBroadException
        try:
            datastore.append(hdu[it].data)
            headerstore.append(hdu[it].header)
        except Exception as _:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        dargs = [it - 1, filename]
        WLOG(p, 'warning', TextEntry('10-001-00001', args=dargs))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        WLOG(p, 'error', TextEntry('01-001-00001', args=[filename]))
    # return valid data
    return datastore, headerstore


def check_dtype_for_header(value):
    # if value is a string check if it is a path if it is remove path
    #   and leave base file
    if isinstance(value, str):
        if os.path.isfile(value):
            newvalue = os.path.basename(value)
        elif os.path.isdir(value):
            newvalue = os.path.dirname(value)
        else:
            newvalue = str(value)
    # if value is a bool then we need to true it to a int (1 or 0)
    elif isinstance(value, bool):
        if value:
            newvalue = 1
        else:
            newvalue = 0
    # if value is a float need to check for NaN
    elif isinstance(value, float):
        if np.isnan(value):
            newvalue = 'NaN'
        else:
            newvalue = float(value)
    # if value is a int do nothing
    elif isinstance(value, int):
        newvalue = int(value)
    # else convert to string to be safe
    else:
        newvalue = str(value)
    # return new value
    return newvalue


def _get_path_and_check(params, key):
    # check key in params
    if key not in params:
        WLOG(params, 'error', '{0} not found in params'.format(key))
    # get top level path to search
    rpath = params[key]
    # deal with not having nightname
    if 'NIGHTNAME' not in params:
        path = str(rpath)
    elif params['NIGHTNAME'] not in ['', 'None', None]:
        path = os.path.join(rpath, params['NIGHTNAME'])
    else:
        path = str(rpath)
    # check if path exists
    if not os.path.exists(path):
        WLOG(params, 'error', 'Path {0} does not exist'.format(path))
    else:
        return path, rpath


def _get_files(params, recipe, path, rpath, **kwargs):
    func_name = __NAME__ + '.get_files()'
    # get properties from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col', kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', 'raw_index_file',
                            kwargs, func_name)
    # get the file filter (should be None unless we want specific files)
    filefilter = params.get('FILENAME', None)
    if filefilter is not None:
        filefilter = list(params['FILENAME'])
    # ----------------------------------------------------------------------
    # get the pseudo constant object
    pconst = constants.pload(params['INSTRUMENT'])
    # ----------------------------------------------------------------------
    # get header keys
    headerkeys = pconst.OUTPUT_FILE_HEADER_KEYS()
    # get raw valid files
    raw_valid = pconst.VALID_RAW_FILES()
    # ----------------------------------------------------------------------
    # storage list
    filelist, basenames, nightnames, mod_times = [], [], [], []
    # load raw index
    rawindexfile = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    if os.path.exists(rawindexfile):
        rawindex = drs_table.read_table(params, rawindexfile, fmt='fits')
    else:
        rawindex = None
    # ----------------------------------------------------------------------
    # populate the storage dictionary
    kwargs = dict()
    for key in headerkeys:
        kwargs[key] = []
    # ----------------------------------------------------------------------
    # deal with white/black list for nights
    if 'WNIGHTNAMES' in params and params['WNIGHTNAMES'] is not None:
        wnightnames = params.listp('WNIGHTNAMES', dtype=str)
    else:
        wnightnames = None
    if 'BNIGHTNAMES' in params and params['BNIGHTNAMES'] is not None:
        bnightnames = params.listp('BNIGHTNAMES', dtype=str)
    else:
        bnightnames = None
    # ----------------------------------------------------------------------
    # get files (walk through path)
    for root, dirs, files in os.walk(path):
        # loop around files in this root directory
        for filename in files:
            # --------------------------------------------------------------
            if filefilter is not None:
                if os.path.basename(filename) not in filefilter:
                    continue
            # --------------------------------------------------------------
            # get night name
            ucpath = drs_path.get_uncommon_path(rpath, root)
            if ucpath is None:
                eargs = [path, rpath, func_name]
                WLOG(params, 'error', TextEntry('00-503-00003', args=eargs))
            # --------------------------------------------------------------
            # make sure file is valid
            isvalid = False
            for suffix in raw_valid:
                if filename.endswith(suffix):
                    isvalid = True
            # --------------------------------------------------------------
            # do not scan empty ucpath
            if len(ucpath) == 0:
                continue
            # --------------------------------------------------------------
            # deal with blacklist/whitelist
            if bnightnames not in [None, 'None', '']:
                if ucpath in bnightnames:
                    # TODO: add to language db
                    wmsg = '\t\tBlacklisted: {0}'.format(ucpath)
                    WLOG(params, '', wmsg)
                    continue
            if wnightnames not in [None, 'None', '']:
                if ucpath not in wnightnames:
                    continue
                else:
                    # TODO: add to language db
                    wmsg = '\t\tWhitelisted: {0}'.format(ucpath)
                    WLOG(params, '', wmsg)
            # --------------------------------------------------------------
            # log the night directory
            if ucpath not in nightnames:
                WLOG(params, '', TextEntry('40-503-00003', args=[ucpath]))
            # --------------------------------------------------------------
            # get absolute path
            abspath = os.path.join(root, filename)
            modified = os.path.getmtime(abspath)
            # --------------------------------------------------------------
            # if not valid skip
            if not isvalid:
                continue
            # --------------------------------------------------------------
            # else append to list
            else:
                nightnames.append(ucpath)
                filelist.append(abspath)
                basenames.append(filename)
                mod_times.append(modified)
            # --------------------------------------------------------------
            # see if file in raw index and has correct modified date
            if rawindex is not None:
                # find file
                rowmask = (rawindex[absfile_col] == abspath)
                # find match date
                rowmask &= modified == rawindex[modified_col]
                # only continue if both conditions found
                if np.sum(rowmask) > 0:
                    # locate file
                    row = np.where(rowmask)[0][0]
                    # if both conditions met load from raw fits file
                    for key in headerkeys:
                        kwargs[key].append(rawindex[key][row])
                    # file was found
                    rfound = True
                else:
                    rfound = False
            else:
                rfound = False
            # --------------------------------------------------------------
            # deal with header
            if filename.endswith('.fits') and not rfound:
                # read the header
                header = read_header(params, abspath)
                # fix the headers
                header, _ = fix_header(params, recipe, header=header)
                # loop around header keys
                for key in headerkeys:
                    rkey = params[key][0]
                    if rkey in header:
                        kwargs[key].append(header[rkey])
                    else:
                        kwargs[key].append('')
    # ----------------------------------------------------------------------
    # sort by filename
    sortmask = np.argsort(filelist)
    filelist = np.array(filelist)[sortmask]
    nightnames = np.array(nightnames)[sortmask]
    basenames = np.array(basenames)[sortmask]
    mod_times = np.array(mod_times)[sortmask]
    # need to sort kwargs
    for key in kwargs:
        kwargs[key] = np.array(kwargs[key])[sortmask]
    # ----------------------------------------------------------------------
    # return filelist
    return nightnames, filelist, basenames, mod_times, kwargs


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
