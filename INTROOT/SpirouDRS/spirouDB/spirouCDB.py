#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou calibration database module

Created on 2017-10-13 at 13:54

@author: cook

Import rules: Only from spirouConfig and spirouCore

"""
from __future__ import division
import numpy as np
import filecmp
from astropy.io import fits
import os
import shutil
import time

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS.spirouCore import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouDB.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# get Config Error
ConfigError = spirouConfig.ConfigError
# Get plotting functions
sPlt = spirouCore.sPlt

# TODO: update using generic database functions
# TODO:    located in spirouDB
# TODO:   (similar to spirouTDB)
# =============================================================================
# User functions
# =============================================================================
def update_datebase(p, keys, filenames, hdrs, timekey=None):
    """
    Updates (or creates) the calibDB with an entry or entries in the form:

        {key} {arg_night_name} {filename} {human_time} {unix_time}

    where arg_night_name comes from p["arg_night_name']
    where "human_time" and "unix_time" come from the filename headers (hdrs)
        using HEADER_KEY = timekey (or "ACQTIME1" if timekey=None)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                log_opt: string, log option, normally the program name
                kw_ACQTIME_KEY: list, the keyword store for acquisition time
                                (string timestamp)
                            [name, value, comment] = [string, object, string]
                kw_ACQTIME_KEY_UNIX: list, the keyword store fore acquisition
                                     time (float unixtime)
    :param keys: string or list of strings, keys to add to the calibDB
    :param filenames: string or list of strings, filenames to add to the
                      calibDB, if keys is a list must be a list of same length
                      as "keys"
    :param hdrs: dictionary or list of dictionaries, header dictionary/
                 dictionaries to find 'timekey' in - the acquisition time,
                 if keys is a list must be a list of same length  as "keys"
    :param timekey: string, key to find acquisition time in header "hdr" if
                    None defaults to the program default ('ACQTIME1')

    :return None:
    """
    funcname = __NAME__ + '.update_database()'
    # deal with time key
    if timekey is None:
        kwacqkey = 'kw_ACQTIME_KEY'
    else:
        kwacqkey = timekey
    # key acqtime_key from parameter dictionary
    if kwacqkey not in p:
        emsg = ('Key {0} not defined in ParamDict (or SpirouKeywords.py)'
                ' - function = {1}')
        WLOG('error', p['LOG_OPT'], emsg.format(kwacqkey, funcname))
        acqtime_key = None
    else:
        acqtime_key = p[kwacqkey][0]

    # deal with single entry
    if type(keys) != list:
        keys = [keys]
        filenames = [filenames]
        hdrs = [hdrs]
    # deal with unequal length filenames/hdrs/keys being entered
    if len(filenames) != len(keys) or len(hdrs) != len(keys):
        emsg = ('"filenames" and "hdrs" must be the same length as "keys"'
                ' - function = {0}')
        WLOG('error', p['LOG_OPT'], emsg.format(funcname))

    # get and check the lock file (Any errors must close and remove lock file
    #     after this point)
    lock, lock_file = get_check_lock_file(p)
    # construct lines for each key in keys
    lines = []
    for k_it in range(len(keys)):
        # get iteration
        key, filename, hdr = keys[k_it], filenames[k_it], hdrs[k_it]

        # get ACQT time from header or
        t, t_fmt = None, None
        if acqtime_key in hdr:
            # get the header time
            header_time = hdr[acqtime_key]
            # get the header format for dates
            header_fmt = spirouConfig.Constants.DATE_FMT_HEADER(p)
            # get the calib DB format for dates
            calibdb_fmt = spirouConfig.Constants.DATE_FMT_CALIBDB()
            # get the unix time from header time (header time assumes GMT/UTC)
            t = spirouMath.stringtime2unixtime(header_time, header_fmt)
            # get the formatted string time for calib DB (GMT/UTC)
            t_fmt = spirouMath.unixtime2stringtime(t, calibdb_fmt)
        else:
            emsg = 'File {0} has no HEADER keyword {1} - function = {2}'
            eargs = [hdr['@@@hname'], acqtime_key, funcname]
            lock.close()
            os.remove(lock_file)
            WLOG('error', p['LOG_OPT'], emsg.format(*eargs))

        # construct database line entry
        lineargs = [key, p['ARG_NIGHT_NAME'], filename, t_fmt, t]
        line = '\n{0} {1} {2} {3} {4}'.format(*lineargs)
        # add line to lines list
        lines.append(line)
    # write lines to master
    write_files_to_master(p, lines, keys, lock, lock_file)
    # finally close the lock file and remove it for next access
    lock.close()
    os.remove(lock_file)


def get_acquisition_time(p, header=None, kind='human', filename=None):
    """
    Get the acquision time from the header file, if there is not header file
    use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                log_opt: string, log option, normally the program name
                kw_ACQTIME_KEY: list, the keyword store for acquisition time
                                (string timestamp)
                            [name, value, comment] = [string, object, string]
    :param header: dictionary or None, the header dictionary created by
                   spirouFITS.ReadImage, if header is None code tries to get
                   header from p['ARG_FILE_NAMES'][0]
    :param kind: string, 'human' for 'YYYY-mm-dd-HH-MM-SS.ss'
    :param filename: string or None, location of the file if header is None

    :return acqtime: string, the human or unix time from header file
    """
    func_name = __NAME__ + '.get_acquisition_time()'

    acqtime = None

    # deal with kinds
    if kind == 'human':
        kwakey = 'kw_ACQTIME_KEY'
    else:
        WLOG('error', p['LOG_OPT'], 'Kind not supported')
        kwakey = None

    # key acqtime_key from parameter dictionary
    if kwakey not in p and kind == 'human':
        emsg = ('Error "{0}" not defined in keyword config files'
                ' - function = {1}')
        WLOG('error', p['LOG_OPT'], emsg.format(kwakey, func_name))
        acqtime_key = None
    else:
        acqtime_key = p[kwakey][0]

    # if we don't have header get it (using 'fitsfilename')
    if header is None:
        # deal with no filename
        if filename is None:
            if os.path.exists(p['ARG_FILE_NAMES'][0]):
                rfile = p['ARG_FILE_NAMES'][0]
            else:
                rfile = os.path.join(p['ARG_FILE_DIR'], p['ARG_FILE_NAMES'][0])

            if not os.path.exists(rfile):
                emsg1 = '"header" and "filename" not defined in {0}'
                emsg2 = '   AND "arg_file_names" not defined in ParamDict'
                eargs = func_name
                WLOG('error', p['LOG_OPT'], [emsg1.format(eargs), emsg2])
        # else we have a filename defined
        else:
            rfile = filename
            # if rawfile does not exist make error
            if not os.path.exists(rfile):
                emsg = ('"header" not defined in {0} and "filename" '
                        'path not found.')
                WLOG('error', p['LOG_OPT'], emsg.format(func_name))
        # get file
        header = fits.getheader(rfile, ext=0)

    # get max_time from file
    if acqtime_key not in header:
        eargs = [acqtime_key, p['ARG_FILE_NAMES'][0], func_name]
        WLOG('error', p['LOG_OPT'], ('Key {0} not in HEADER file of {1}'
                                     ' for function {2}'.format(*eargs)))
    # else get acqtime from header key
    else:
        acqtime = header[acqtime_key]

    return acqtime


def get_database(p, max_time=None, update=False):
    """
    Gets all entries from calibDB where unix time <= max_time. If update is
    False then will first search for and use 'calibDB' in p (if it exists)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                log_opt: string, log option, normally the program name
    :param max_time: str, maximum time allowed for all calibDB entries
                     format = (YYYY-MM-DD HH:MM:SS.MS)
    :param update: bool, if False looks for "calibDB' in p, and if found does
                   not load new database

    :return c_database: dictionary, the calibDB database in form:
                    c_database[key] = [dirname, filename]
        lines in calibDB must be in form:
            {key} {dirname} {filename} {human_time} {unix_time}

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                max_time_human: string, maximum time from "max_time"
                max_time_unix: float, maximum time from "max_time"

    """
    func_name = __NAME__ + '.get_database()'
    # if we already have calib database don't load it
    if 'calibDB' in p and not update:
        return p['CALIBDB'], p

    if max_time is None:
        max_time = get_acquisition_time(p)
    # add max_time to p
    p['MAX_TIME_HUMAN'] = max_time
    p.set_source('MAX_TIME_HUMAN', func_name)
    # check that max_time is a valid unix time (i.e. a float)
    try:
        # get the header format for dates
        header_fmt = spirouConfig.Constants.DATE_FMT_HEADER(p)
        # get the unix time from header time (assume max_time is in GMT/UTC)
        max_time = spirouMath.stringtime2unixtime(max_time, header_fmt)
    except ValueError:
        emsg = 'max_time {0} is not a valid float - function {1}'
        WLOG('error', p['LOG_OPT'], emsg.format(max_time, func_name))
    # add max_time to p
    p['MAX_TIME_UNIX'] = max_time
    p.set_source('MAX_TIME_UNIX', func_name)
    # get and check the lock file
    lock, lock_file = get_check_lock_file(p)
    # try to open the master file
    lines = read_master_file(p, lock, lock_file)
    # store all lines that have unix time <= max_time
    keys, dirnames, filenames, utimes = [], [], [], []
    for l_it, line in enumerate(lines):
        # ignore blank lines or lines starting with '#'
        if len(line) == 0:
            continue
        if line == '\n':
            continue
        if line.strip()[0] == '#':
            continue
        # get elements from database
        try:
            key, dirname, filename, t_fmt, t = line.split()
            t = float(t)
        # will crash if we don't have 5 variables --> thus log and exit
        except ValueError:
            # Must close and remove lock file before exiting
            lock.close()
            os.remove(lock_file)
            emsg1 = 'Incorrectly formatted line in calibDB - function = {0}'
            lineedit = line.replace('\n', '')
            emsg2 = '   Line {0}: "{1}"'.format(l_it + 1, lineedit)
            WLOG('error', p['LOG_OPT'], [emsg1.format(func_name), emsg2])
            key, dirname, filename, t_fmt, t = None, None, None, None, None

        # Make sure unix time and t_fmt agree
        calibdb_fmt = spirouConfig.Constants.DATE_FMT_CALIBDB()
        # get unix time (assume t_fmt is in GMT/UTC)
        t_fmt_unix = spirouMath.stringtime2unixtime(t_fmt, calibdb_fmt)
        # get human time in UTC/GMT
        t_human = spirouMath.unixtime2stringtime(t, calibdb_fmt)
        if t_fmt_unix != t:
            lock.close()
            os.remove(lock_file)
            emsg1 = 'Times do not match in calibDB'
            emsg2 = '\tHuman time = {0}'.format(t_fmt)
            emsg3 = '\tUnix time = {0}'.format(t_human)
            emsg4 = ' - function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3, emsg4])
        # t must be a float here --> exception
        try:
            t = float(t)
        except ValueError:
            # Must close and remove lock file before exiting
            lock.close()
            os.remove(lock_file)
            emsg1 = 'unix time="{0}" is not a valid float'.format(t)
            emsg2 = '    for key {0}="{1}"'.format(key, line)
            emsg3 = '    function = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        # append all database elements to lists
        utimes.append(t)
        keys.append(key)
        dirnames.append(dirname)
        filenames.append(filename)
    # convert to numpy arrays
    utimes = np.array(utimes)
    keys = np.array(keys)
    dirnames = np.array(dirnames)
    filenames = np.array(filenames)
    # Need to check if lists are empty after loop
    # Must close and remove lock file before exiting
    if len(keys) == 0:
        lock.close()
        os.remove(lock_file)
        # log and exit
        calibdb_file = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        emsg1 = 'There are no entries in calibDB'
        emsg2 = '   Please check CalibDB file at {0}'.format(calibdb_file)
        emsg3 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
    # Finally we only want to keep one calibDB file for each key
    #     This depends on 'calib_db_match'
    #     If calib_db_match = 'older' - select the newest file that is older
    #                                   than max_time
    #     If calib_db_match = 'closest' - select the file that is closest to
    #                                     max_time (newer OR older)
    try:
        c_database = choose_keys(p, utimes, keys, dirnames, filenames)
    except ConfigError as e:
        lock.close()
        os.remove(lock_file)
        # log error in standard way
        WLOG(e.level, p['LOG_OPT'], e.msg)
        c_database = None

    # Must close and remove lock file before continuing
    lock.close()
    os.remove(lock_file)
    # return calibDB dictionary
    return c_database, p


def choose_keys(p, utimes, keys, dirnames, filenames):
    """
    Choose the keys in the calibration database based on 'calib_db_match'
    if 'calib_db_match' == older, then choose the most recent of each key that
    is closest but older than the time in p['MAX_TIME_UNIX']
    if 'calib_db_match' == closest, then choose the most recent of each key
    that is closest (older or newer) than the time in p['MAX_TIME_UNIX']

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                max_time_unix: float, the unix time to use as the time of
                               reference
                CALIB_DB_MATCH: string, either "closest" or "older"
                                whether to use the "closest" time
                                ("closest") or the closest time that is
                                older ("older") than "max_time_unix"
                max_time_human: string, the time stampe to use as the time
                                of reference
    :param utimes: list of floats, the unix times for each key in keys
    :param keys: list of strings, the keys in calibDB
    :param dirnames: list of strings, the directory names for each key in keys
    :param filenames: list of strings, the filenames for each key in keys

    :return c_database: dict, the calibration database, with keys equal to the
                        unique keys in "keys" and values equal to:
                        [dirname, filename] for each unique key matching the
                        time criteria
    """
    func_name = __NAME__ + '.choose_keys()'
    # set up database
    c_database = ParamDict()
    # get match
    match = p['CALIB_DB_MATCH']
    # log calibDB match method
    wmsg = 'CalibDB loaded with method "{0}"'
    WLOG('', p['LOG_OPT'], wmsg.format(match))
    # get max time unix and human
    maxtime_u = p['MAX_TIME_UNIX']
    maxtime_h = p['MAX_TIME_HUMAN']
    # display max time
    wmsg = '\tMax time used = {0} ({1})'
    WLOG('', p['LOG_OPT'], wmsg.format(maxtime_h, maxtime_u))
    # get unique keys
    ukeys = np.unique(keys)
    # loop around unique keys
    for ukey in ukeys:
        # gather all keys with ukey
        kmask = keys == ukey
        # if we only want older ones test this else keep all
        if match == 'older':
            older = utimes <= maxtime_u
        else:
            older = np.ones(len(keys), dtype=bool)
        # combine masks
        cmask = older & kmask
        # if we only have one key continue (use this one)
        if np.sum(cmask) == 1:
            closest_time = utimes[cmask][0]
        # if we have none then cause error
        elif match == 'older' and np.sum(cmask) == 0:
            calibdb_file = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
            emsg1 = ('There are no entries for key="{0}" in calibDB file with '
                     'time < {1}'.format(ukey, maxtime_h))
            emsg2 = '   Please check CalibDB file at {0}'.format(calibdb_file)
            emsg3 = '   function = {0}'.format(func_name)
            raise ConfigError([emsg1, emsg2, emsg3], level='error')
        elif np.sum(cmask) == 0:
            calibdb_file = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
            emsg1 = ('There is an undefined error with key="{0}" in '
                     'calibDB file'.format(ukey))
            emsg2 = '   Please check CalibDB file at {0}'.format(calibdb_file)
            emsg3 = '   function = {0}'.format(func_name)
            raise ConfigError([emsg1, emsg2, emsg3], level='error')
        # else we need to choose the one closest to max_time
        else:
            tpos = np.argmin(abs(utimes[cmask] - maxtime_u))
            closest_time = utimes[cmask][tpos]
        # find where in original array utimes = closest_time
        pos = np.where((utimes == closest_time) & cmask)[0][-1]
        # add to c_database
        humantime = spirouMath.unixtime2stringtime(utimes[pos])
        c_database[ukey] = [dirnames[pos], filenames[pos], humantime,
                            utimes[pos]]
        # set the source of each entry
        c_database.set_source(ukey, func_name)
    # return c_database
    return c_database


def put_file(p, inputfile):
    """
    Copies the "inputfile" to the calibration database folder

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
                log_opt: string, log option, normally the program name
    :param inputfile: string, the input file path and file name

    :return None:
    """
    func_name = __NAME__ + '.put_file()'
    # construct output filename
    outputfile = os.path.join(p['DRS_CALIB_DB'], os.path.split(inputfile)[1])

    try:
        shutil.copyfile(inputfile, outputfile)
        os.chmod(outputfile, 0o0644)
    except IOError:
        emsg1 = 'I/O problem on {0}'.format(outputfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    except OSError:
        emsg1 = 'Unable to chmod on {0}'.format(outputfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('', p['LOG_OPT'], [emsg1, emsg2])


def copy_files(p, header=None):
    """
    Copy the files from calibDB to the reduced folder
       p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME']
    based on the latest calibDB files from header, if there is not header file
    use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
                log_opt: string, log option, normally the program name
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return None:
    """
    func_name = __NAME__ + '.copy_files()'
    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = get_acquisition_time(p, header)
        # get calibDB
        c_database, p = get_database(p, acqtime)
    else:
        c_database = p['CALIBDB']

    # construct reduced directory path
    reduced_dir = p['REDUCED_DIR']
    calib_dir = p['DRS_CALIB_DB']

    # loop around the files in Calib database
    for row in range(len(c_database)):
        # Get the key for this entry
        key = list(c_database.values())[row][0]
        # Get the file name for this row
        filename = list(c_database.values())[row][1]
        # Construct the old and new locations of this file from filename
        newloc = os.path.join(reduced_dir, filename)
        oldloc = os.path.join(calib_dir, filename)
        # if the file exists in the new location
        if os.path.exists(newloc):
            # check if it is the same
            if filecmp.cmp(newloc, oldloc):
                wmsg = 'Cal. file: {0} already exists - not copied'
                WLOG('', p['LOG_OPT'], wmsg.format(filename))
            # if it isn't then copy over it
            else:
                # Make sure old path exists
                if not os.path.exists(oldloc):
                    emsg1 = ('Error file {0} define in calibDB (key={1}) '
                             'does not exist').format(oldloc, key)
                    emsg2 = '    function = {0}'.format(func_name)
                    WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
                # try to copy --> if not raise an error and log it
                try:
                    shutil.copyfile(oldloc, newloc)
                    wmsg = 'Cal. file: {0} copied in dir {1}'
                    WLOG('', p['LOG_OPT'], wmsg.format(filename, reduced_dir))
                except IOError:
                    emsg1 = ('I/O problem on input file from calibDB: {0}'
                             '').format(oldloc)
                    emsg2 = ('   or problem on writing to outfile file: {0}'
                             '').format(newloc)
                    emsg3 = '    function = {0}'.format(func_name)
                    WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
        # else if the file doesn't exist
        else:
            # try to copy --> if not raise an error and log it
            try:
                shutil.copyfile(oldloc, newloc)
                wmsg = 'Calib file: {0} copied in dir {1}'
                WLOG('', p['LOG_OPT'], wmsg.format(filename, reduced_dir))
            except IOError:
                emsg1 = 'I/O problem on {0} or {1}'.format(oldloc, newloc)
                emsg2 = '   function = {0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])


def get_file_name(p, key, hdr=None, filename=None, required=True):
    """
    Get the filename for "key" in the calibration database (for use when
    the calibration database is not needed for more than one use and does
    not exist already (i.e. called via spirouDB.GetCalibDatabase() )

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                calibDB: dictionary, the calibration database dictionary
                max_time_human: string, maximum time from "max_time"
                log_opt: string, log option, normally the program name
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
    :param key: string, the key to look for in the calibration database
    :param hdr: dict or None, the header dictionary to use to get the
                acquisition time, if hdr is None code tries to get
                header from p['ARG_FILE_NAMES'][0]
    :param filename: string or None, if defined this is the filename returned
                     (means calibration database is not used)
    :param required: bool, if True code generates log exit else raises a
                     ConfigError (to be caught)

    :return read_file: string, the filename in calibration database for
                       "key" (selected via unix_time in calibDB)
    """
    func_name = __NAME__ + '.get_file_name()'
    # get calibDB
    if 'calibDB' not in p:
        # get acquisition time
        acqtime = get_acquisition_time(p, hdr)
        # get calibDB
        c_database, p = get_database(p, acqtime)
    else:
        c_database = p['CALIBDB']

    # Check that "KEY" is in calib database and assign value if it is
    if filename is not None:
        read_file = filename
    else:
        if key in c_database:
            rawfilename = c_database[key][1]
        else:
            emsg1 = ('Calibration database has no valid "{0}" entry '
                     'for time<{1}').format(key, p['MAX_TIME_HUMAN'])
            emsg2 = '   function = {0}'.format(func_name)
            if required:
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
            else:
                raise ConfigError(level='error', message=emsg1)
            rawfilename = ''
        # construct filename
        read_file = os.path.join(p['REDUCED_DIR'], rawfilename)
    # read file and return
    return read_file


# =============================================================================
# Worker functions
# =============================================================================
def get_check_lock_file(p):
    """
    Creates a lock_file if it doesn't exist, if it does waits for it to not
    exist - acts to stop calibDB being open multiple times at once

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                CALIB_MAX_WAIT: float, the maximum wait time (in seconds)
                                for calibration database file to be in
                                use (locked) after which an error is raised

    :return lock: file, the opened lock_file (using open(lockfile, 'w'))
    :return lockfile: string, the opened lock file name
    """
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    lock_file = spirouConfig.Constants.CALIBDB_LOCKFILE(p)
    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG('warning', p['LOG_OPT'], 'CalibDB locked. Waiting...')
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) or wait_time > p['CALIB_MAX_WAIT']:
        time.sleep(1)
        wait_time += 1
    if wait_time > p['CALIB_MAX_WAIT']:
        emsg1 = ('CalibDB can not be accessed (file locked and max wait time '
                 'exceeded.')
        emsg2 = ('Please make sure CalibDB is not being used and '
                 'manually delete {0}').format(lock_file)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # open the lock file
    lock = open(lock_file, 'w')
    # return lock file and name
    return lock, lock_file


def write_files_to_master(p, lines, keys, lock, lock_file):
    """
    writes database entries to master file

    master file is defined as 'DRS_CALIB_DB'/'IC_CALIBDB_FILENAME' and
    variables are taken from p

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
    :param lines: list of strings, entries to add to the master file
    :param keys: list of strings, the keys that are to be added to master file
    :param lock: file, the lock file (for closing if error occurs)
    :param lock_file: string, the lock file name (for deleting once an error
                      occurs)
    :return:
    """
    func_name = __NAME__ + '.write_files_to_master()'
    # construct master filename
    masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
    # try to
    try:
        f = open(masterfile, 'a')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        emsg1 = 'I/O Error on file: {0}'.format(masterfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    else:
        # write database line entry to file
        f.writelines(lines)
        f.close()
        wmsg = 'Updating Calib Data Base with {0}'
        WLOG('info', p['LOG_OPT'], wmsg.format(', '.join(keys)))
        try:
            os.chmod(masterfile, 0o666)
        except OSError:
            pass


def read_master_file(p, lock, lock_file):
    """
    Read the calibration database master file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
    :param lock: file, the lock file
    :param lock_file: string, the lock file location and filename

    :return lines: list of strings, the lines in calibration database
                   master file (defined at:
                      spirouConfig.Constants.CALIBDB_MASTERFILE)
    """
    func_name = __NAME__ + '.read_master_file()'

    # construct master filename
    masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
    # try to
    try:
        f = open(masterfile, 'r')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        emsg1 = 'CalibDB master file: {0} can not be found!'.format(masterfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    else:
        # write database line entry to file
        lines = list(f.readlines())
        f.close()
        return lines


# =============================================================================
# End of code
# =============================================================================
