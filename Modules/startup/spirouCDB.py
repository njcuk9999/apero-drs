#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-13 at 13:54

@author: cook



Version 0.0.0
"""
import numpy as np
import sys
import os
import shutil
import datetime
import time

from startup import log


# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
DATE_FMT = "%Y-%m-%d-%H:%M:%S.%f"
# -----------------------------------------------------------------------------

# =============================================================================
# Usable functions
# =============================================================================
def update_datebase(p, keys, filenames, hdrs, timekey=None):
    """
    Updates (or creates) the calibDB with an entry or entries in the form:

        {key} {arg_night_name} {filename} {human_time} {unix_time}

    where arg_night_name comes from p["arg_night_name']
    where "human_time" and "unix_time" come from the filename headers (hdrs)
        using HEADER_KEY = timekey (or "ACQTIME1" if timekey=None)


    :param p: dictionary, parameter dictionary

    :param keys: string or list of strings, keys to add to the calibDB

    :param filenames: string or list of strings, filenames to add to the
                      calibDB, if keys is a list must be a list of same length
                      as "keys"

    :param hdrs: dictionary or list of dictionaries, header dictionary/
                 dictionaries to find 'timekey' in - the acquisition time,
                 if keys is a list must be a list of same length  as "keys"

    :param timekey: string, key to find acquisition time in header "hdr" if
                    None defaults to the program default ('ACQTIME1')

    :return:
    """
    if 'ACQTIME_KEY' not in p:
        WLOG('error', p['log_opt'], ('Error ACQTIME_KEY not defined in'
                                     ' config files'))

    # deal with single entry
    if type(keys) != list:
        keys = [keys]
        filenames = [filenames]
        hdrs = [hdrs]
    # deal with unequal length filenames/hdrs/keys being entered
    if len(filenames) != len(keys) or len(hdrs) != len(keys):
        emsg = ('"filenames" and "hdrs" must be lists as "keys" is a'
                'list and must be the same length as "keys"')
        WLOG('error', p['log_opt'], emsg)

    # get and check the lock file
    lock, lock_file = get_check_lock_file(p)
    # construct lines for each key in keys
    lines = []
    for k_it in range(len(keys)):
        # get iteration
        key, filename, hdr = keys[k_it], filenames[k_it], hdrs[k_it]

        # get ACQT time from header or
        if p['ACQTIME_KEY'] in hdr:
            t = time2unixtime(hdr[p['ACQTIME_KEY']])
            t_fmt = time.strftime('%D/%H:%M:%S', time.gmtime(t))
        else:
            emsg = 'File {0} has no Header keyword {1}'
            WLOG('error', p['log_opt'], emsg.format(hdr['@@@hname'],
                                                    p['ACQTIME_KEY']))

        # construct database line entry
        lineargs = [key, p['arg_night_name'], filename, t_fmt, t]
        line = '{0} {1} {2} {3} {4}\n'.format(*lineargs)
        # add line to lines list
        lines.append(line)
    # write lines to master
    write_files_to_master(p, lines, keys, lock, lock_file)
    # finally close the lock file and remove it for next access
    lock.close()
    os.remove(lock_file)


def get_database(p, max_time):
    """
    Gets all entries from calibDB where unix time <= max_time

    :param p: dictionary, parameter dictionary
    :param max_time: str, maximum time allowed for all calibDB entries
                     format = (YYYY-MM-DD HH:MM:SS.MS)

    :return c_database: dictionary, the calibDB database in form:

                    c_database[key] = [dirname, filename]

        lines in calibDB must be in form:

            {key} {dirname} {filename} {human_time} {unix_time}
    """
    # check that max_time is a valid unix time (i.e. a float)
    try:
        max_time = time2unixtime(max_time)
    except ValueError:
        WLOG('error', p['log_opt'], ('max_time {0} is not a valid float.'
                                     '').format(max_time))


    # get and check the lock file
    lock, lock_file = get_check_lock_file(p)
    # try to open the master file
    lines = read_master_file(p, lock, lock_file)
    # store all lines that have unix time <= max_time
    keys, dirnames, filenames, utimes = [], [], [], []
    for l_it, line in enumerate(lines):
        # get elements from database
        try:
            key, dirname, filename, t_fmt, t = line.split()
        # will crash if we don't have 5 variables --> thus log and exit
        except ValueError:
            # Must close and remove lock file before exiting
            lock.close()
            os.remove(lock_file)
            WLOG('error', p['log_opt'], ('Incorrectly formatted line in '
                                         'calibDB (Line {0} = {1})'
                                         '').format(l_it+1, line))
        # only keep those entries earlier or equal to "max_time"
        # note t must be a float here --> exception
        try:
            if float(t) <= max_time:
                # append unix time, key, directory name and filename
                utimes.append(t)
                keys.append(key)
                dirnames.append(dirname)
                filenames.append(filename)
        except ValueError:
            # Must close and remove lock file before exiting
            lock.close()
            os.remove(lock_file)
            WLOG('error', p['log_opt'], ('unix time {0} is not a valid float.'
                                         '').format(t))


    # Need to check if lists are empty after loop
    if len(keys) == 0:
        # Must close and remove lock file before exiting
        lock.close()
        os.remove(lock_file)
        # log and exit
        WLOG('error', p['log_opt'], ('There are no entries in calibDB with '
                                     'time <= {0}').format(max_time))
    # Finally we only want to keep the most recent key of each time so
    #     write all keys (in sorted unix time order) to a dictionary
    #     all keys currently in dictionary will be overwritten thus keeping
    #     newest key only
    c_database = dict()
    for it in np.argsort(utimes):
        c_database[keys[it]] = [dirnames[it], filenames[it]]
    # Must close and remove lock file before continuing
    lock.close()
    os.remove(lock_file)
    # return calibDB dictionary
    return c_database


def put_file(p, inputfile):
    """
    Copies the "inputfile" to the calibDB folder

    :param p: dictionary, parameter dictionary
    :param inputfile: string, the input file path and file name
    :return:
    """
    # construct output filename
    outputfile = os.path.join(p['DRS_CALIB_DB'], os.path.split(inputfile)[1])

    try:
        shutil.copyfile(inputfile, outputfile)
        os.chmod(outputfile, 0o0644)
    except IOError:
        WLOG('error', p['log_opt'], 'I/O problem on {0}'.format(outputfile))
    except OSError:
        WLOG('', p['log_opt'], 'Unable to chmod on {0}'.format(outputfile))



# =============================================================================
# Worker functions
# =============================================================================
def get_check_lock_file(p):
    """
    Creates a lock_file if it doesn't exist, if it does waits for it to not
    exist - acts to stop calibDB being open multiple times at once

    :param p: dictionary, parameter dictionary
    :return:
    """
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    lock_file = os.path.join(p['DRS_CALIB_DB'], 'lock_calibDB')
    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG('warning', p['log_opt'], 'CalibDB locked. Waiting...')
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) or wait_time > p['CALIB_MAX_WAIT']:
        time.sleep(1)
        wait_time += 1
    if wait_time > p['CALIB_MAX_WAIT']:
        emsg = ('CalibDB can not be accessed (file locked and max wait time '
                'exceeded. Please make sure CalibDB is not being used and '
                'manually delete {0}').format(lock_file)
        WLOG('error', p['log_opt'], emsg)
    # open the lock file
    lock = open(lock_file, 'w')
    # return lock file and name
    return lock, lock_file


def write_files_to_master(p, lines, keys, lock, lock_file):
    """
    writes database entries to master file

    master file is defined as 'DRS_CALIB_DB'/'IC_CALIBDB_FILENAME' and
    variables are taken from p

    :param p: dictionary, parameter dictionary
    :param lines: list of strings, entries to add to the master file
    :param keys: list of strings, the keys that are to be added to master file
    :param lock: file, the lock file (for closing if error occurs)
    :param lock_file: string, the lock file name (for deleting once an error
                      occurs)
    :return:
    """
    # construct master filename
    masterfile = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    # try to
    try:
        f = open(masterfile, 'a')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        WLOG('error', p['log_opt'], 'I/O Error on file: {0}'.format(masterfile))
    else:
        # write database line entry to file
        f.writelines(lines)
        f.close()
        WLOG('info', p['log_opt'], ('Updating Calib Data Base '
                                    'with {0}').format(', '.join(keys)))
        try:
            os.chmod(masterfile, 0o666)
        except OSError:
            pass


def read_master_file(p, lock, lock_file):
    # construct master filename
    masterfile = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    # try to
    try:
        f = open(masterfile, 'r')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        WLOG('error', p['log_opt'],
             'CalibDB master file: {0} can not be found!'.format(masterfile))


    else:
        # write database line entry to file
        lines = list(f.readlines())
        f.close()
        return lines




def time2unixtime(t):
    return time.mktime(datetime.datetime.strptime(t, DATE_FMT).timetuple())

# =============================================================================
# End of code
# =============================================================================
