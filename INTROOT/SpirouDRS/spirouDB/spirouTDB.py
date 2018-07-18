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
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
    return filenames[sort][-1]


# TODO: Figure out how we use this with no wave file
# TODO: Currently just returns most recent
def get_database_tell_conv(p):
    func_name = __NAME__ + '.get_database_tell_conv()'
    # define key
    key = 'TELL_CONV'
    # get the telluric database (all lines)
    t_database = spirouDB.get_database(p, dbkind='Telluric')
    # check for key in database
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
    return filenames[sort][-1]


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
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
        return [],[], [], []
    if key not in t_database:
        # generate error message
        emsg1 = 'Telluric database has no valid "{0}" entry '.format(key)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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



# TODO: Might require OBJNAME to select file (not most recent)
def get_database_tell_template(p, required=True):
    func_name = __NAME__ + '.get_database_tell_template()'
    # define key
    key = 'TELL_TEMP'
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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
            WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
        # add to array
        filenames = np.append(filenames, absfilename)
        humantimes = np.append(humantimes, humantime)
        unixtimes = np.append(unixtimes, float(unixtime))

    # for tell_mole we only want to use the most recent key (if more than one)
    # sort by unixtime
    sort = np.argsort(unixtimes)

    # only returning most recent filename
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


def update_database_tell_map(p, filename, objname, airmass, watercol,
                             hdr=None):
    # define key
    key = 'TELL_MAP'
    # get h_time and u_time
    h_time, u_time = spirouDB.get_times_from_header(p, hdr)
    # set up line
    args = [key, filename, h_time, u_time, objname, airmass, watercol]
    line = '\n{0} {1} {2} {3} {4} {5} {6}'.format(*args)
    # push into list
    keys = [key]
    lines = [line]
    # update database
    spirouDB.update_datebase(p, keys, lines, dbkind='Telluric')


def update_database_tell_temp(p, filename, hdr=None):

    # define key for telluric convolve file
    key = 'TELL_TEMP'
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


# =============================================================================
# End of code
# =============================================================================
