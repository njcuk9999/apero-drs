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
import os
import shutil

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from . import spirouDB

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


# =============================================================================
# User functions
# =============================================================================
def get_database_tell_mole(p):
    func_name = __NAME__ + '.get_database_tell_mole()'
    # define key
    key = 'TELL_MOLE'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humantime, unixtime = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
    return filenames[sort][-1]


def get_database_tell_conv(p, required=True):
    func_name = __NAME__ + '.get_database_tell_conv()'
    # define key
    key = 'TELL_CONV'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if not required and key not in t_database:
        return [], [], [], []
    elif key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humantime, unixtime = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
    return filenames[sort]


def get_database_sky(p):
    func_name = __NAME__ + '.get_database_sky()'
    # define key
    key = 'SKY'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humantime, unixtime = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # sort by unixtime
    sort = np.argsort(unixtimes)

    # return sorted filenames
    return filenames[sort]


def get_database_tell_map(p, required=True):
    func_name = __NAME__ + '.get_database_tell_map()'
    # define key
    key = 'TELL_MAP'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if not required and key not in t_database:
        return [], [], [], []
    elif key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes, objnames = [], [], [], []
    airmasses, watercols = [], []
    for value in values:
        # get this iterations value from value
        _, filename, humant, unixt, objname, airmass, watercol = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humant)
        unixtimes = np.append(unixtimes, float(unixt))
        objnames = np.append(objnames, objname)
        airmasses = np.append(airmasses, float(airmass))
        watercols = np.append(watercols, float(watercol))

    # sort by unixtime
    sort = np.argsort(unixtimes)

    # return sorted filenames, objnames, airmasses and watercols
    return filenames[sort], objnames[sort], airmasses[sort], watercols[sort]


def get_database_obj_template(p, object_name, required=True):
    func_name = __NAME__ + '.get_database_obj_template()'
    # define key
    key = 'OBJ_TEMP'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if key not in t_database:
        if not required:
            return None
        else:
            # generate error message
            emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
            emsg2 = '   function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
            return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humantime, unixtime, objname = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # check object name matches
        if objname != object_name:
            continue
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # if we have no files return None
    if len(filenames) == 0:
        return None

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
    return filenames[sort][-1]


def get_database_tell_obj(p, required=True):
    func_name = __NAME__ + '.get_database_tell_map()'
    # define key
    key = 'TELL_OBJ'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if not required and key not in t_database:
        return [], [], [], []
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes, objnames = [], [], [], []
    bervs, airmasses, watercols = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humant, unixt, objname, berv, airmass, watercol = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humant)
        unixtimes = np.append(unixtimes, float(unixt))
        objnames = np.append(objnames, objname)
        bervs = np.append(bervs, berv)
        airmasses = np.append(airmasses, float(airmass))
        watercols = np.append(watercols, float(watercol))

    # sort by unixtime
    sort = np.argsort(unixtimes)

    # return sorted filenames, objnames, bervs, airmasses and watercols
    rdata = [filenames[sort], objnames[sort], bervs[sort]]
    rdata += [airmasses[sort], watercols[sort]]
    return rdata


def get_database_tell_recon(p, required=True):
    func_name = __NAME__ + '.get_database_tell_map()'
    # define key
    key = 'TELL_RECON'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if not required and key not in t_database:
        return [], [], [], []
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes, objnames = [], [], [], []
    bervs, airmasses, watercols = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humant, unixt, objname, berv, airmass, watercol = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humant)
        unixtimes = np.append(unixtimes, float(unixt))
        objnames = np.append(objnames, objname)
        bervs = np.append(bervs, berv)
        airmasses = np.append(airmasses, float(airmass))
        watercols = np.append(watercols, float(watercol))

    # sort by unixtime
    sort = np.argsort(unixtimes)

    # return sorted filenames, objnames, bervs, airmasses and watercols
    rdata = [filenames[sort], objnames[sort], bervs[sort]]
    rdata += [airmasses[sort], watercols[sort]]
    return rdata



def get_database_master_wave(p, required=True):
    func_name = __NAME__ + '.get_database_master_wave()'
    # define key
    key = 'MASTER_WAVE'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if not required and key not in t_database:
        return [], [], [], []
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        return 0

    # filter database by key
    values = t_database[key]

    # extract parameters from database values
    filenames, humantimes, unixtimes, objnames = [], [], [], []
    # bervs, airmasses, watercols = [], [], []
    for value in values:
        # get this iterations value from value
        _, filename, humant, unixt = value
        # get absfilename
        absfilename = os.path.join(p['DRS_TELLU_DB'], filename)
        # check filename exists
        if not os.path.exists(absfilename):
            emsg1 = 'Database error: Cannot find file="{0}"'.format(absfilename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humant)
        unixtimes = np.append(unixtimes, float(unixt))

    # sort by unixtime
    sort = np.argsort(unixtimes)

    # return most recent filename
    return filenames[sort][-1]


# TODO: Move to spirouDB?
def put_file(p, inputfile):
    """
    Copies the "inputfile" to the telluric database folder

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_TELLU_DB: string, the directory that the telluric
                              files should be saved to/read from
                log_opt: string, log option, normally the program name
    :param inputfile: string, the input file path and file name

    :return None:
    """
    func_name = __NAME__ + '.put_file()'
    # construct output filename
    outputfile = os.path.join(p['DRS_TELLU_DB'], os.path.split(inputfile)[1])

    # get and check for file lock file
    lock, lock_file = spirouDB.get_check_lock_file(p, 'Calibration')
    # noinspection PyExceptClausesOrder
    try:
        shutil.copyfile(inputfile, outputfile)
        os.chmod(outputfile, 0o0644)
    except IOError:
        # close lock file
        spirouDB.close_lock_file(p, lock, lock_file)
        # log
        emsg1 = 'I/O problem on {0}'.format(outputfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    except OSError:
        # close lock file
        spirouDB.close_lock_file(p, lock, lock_file)
        # log
        emsg1 = 'Unable to chmod on {0}'.format(outputfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, '', [emsg1, emsg2])

    # close lock file
    spirouDB.close_lock_file(p, lock, lock_file)


def update_database_tell_mole(p, filename, hdr=None):
    # define key for telluric convolve file
    key = 'TELL_MOLE'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time]
    line = '\n{0} {1} {2} {3}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_tell_conv(p, filename, hdr=None):
    # define key for telluric convolve file
    key = 'TELL_CONV'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time]
    line = '\n{0} {1} {2} {3}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_sky(p, filename, hdr=None):
    # define key for sky
    key = 'SKY'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time]
    line = '\n{0} {1} {2} {3}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_tell_map(p, filename, objname, airmass, watercol, hdr=None):
    # define key
    key = 'TELL_MAP'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time, objname, airmass, watercol]
    line = '\n{0} {1} {2} {3} {4} {5:.3f} {6:.3f}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_obj_temp(p, filename, object_name, hdr=None):
    # define key for telluric convolve file
    key = 'OBJ_TEMP'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time, object_name]
    line = '\n{0} {1} {2} {3} {4}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_tell_obj(p, filename, objname, berv, airmass, watercol,
                             hdr=None):
    # define key
    key = 'TELL_OBJ'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time, objname, berv, airmass, watercol]
    line = '\n{0} {1} {2} {3} {4} {5:.3f} {6:.3f} {7:.3f}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_tell_recon(p, filename, objname, berv, airmass, watercol,
                               hdr=None):
    # define key
    key = 'TELL_RECON'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time, objname, berv, airmass, watercol]
    line = '\n{0} {1} {2} {3} {4} {5:.3f} {6:.3f} {7:.3f}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')





# =============================================================================
# End of code
# =============================================================================
