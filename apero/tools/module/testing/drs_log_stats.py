#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-13 at 15:30

@author: cook
"""
from __future__ import division
from astropy.table import Table
from astropy.time import Time, TimeDelta
from astropy import units as uu
import numpy as np
import os
import glob
from collections import OrderedDict

from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_log_stats.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpText = drs_text.HelpDict
# define columns from log files
RECIPECOL = 'RECIPE'
STARTCOL = 'STARTED'
PASSEDCOL = 'PASSED_QC'
ENDCOL = 'ENDED'
LOGCOL = 'LOGFILE'
ERRORSTR = '-!|'
WARNINGSTR = '-@|'
ERRORPREFIX, ERRORSUFFIX = 'E[', ']:'
WARNPREFIX, WARNSUFFIX = 'W[', ']:'

# TODO: Move all text to language database

# =============================================================================
# Define class
# =============================================================================
class LogObj:
    def __init__(self, code, line, mdate=None):
        self.code = code
        self.lines = [line]
        self.msg = ''
        self.mdate = mdate
        if self.mdate is None:
            self.mdate = Time('2000-01-01 00:00:00')
        # update the error message with line
        self._update_msg(line)
        # get time
        self.starttime = self._get_time(line)
        self.endtime = self._get_time(line)
        self.midpoint = self.starttime + 0.5 * (self.endtime - self.starttime)

    def addline(self, line):
        self.lines.append(line)
        # update the error message with line
        self._update_msg(line)
        # update end time
        self.endtime = self._get_time(line)
        self.midpoint = self.starttime + 0.5 * (self.endtime - self.starttime)

    def _get_time(self, line):
        date1 = self.mdate
        # get the modification hour
        hour1 = date1.datetime.hour
        # get the log time (from string)
        time2 = line.split('-')[0]
        hour2, min2, sec2 = time2.split(':')
        hour2 = int(hour2)
        # figure out which day our log entry is on
        if hour2 > hour1:
            date2 = Time(self.mdate) - TimeDelta(1 * uu.day)
        else:
            date2 = Time(self.mdate)
        # get the year month and day for entry
        year2, mon2 = date2.datetime.year, date2.datetime.month
        day2 = date2.datetime.day
        # construct the new date
        targs = [year2, mon2, day2, hour2, min2, sec2]
        date2 = Time('{0}-{1}-{2} {3}:{4}:{5}'.format(*targs),
                     format='iso')
        # return date2
        return date2

    def _update_msg(self, line):
        if self.code in line:
            text = line.split('[{0}]:'.format(self.code))[-1]
        else:
            text = line.split('|')[-1]
        self.msg += text

    def __str__(self):
        desc = ''
        desc += '\n{0}'.format('=' * 12)
        desc += '\nCODE: {0}'.format(self.code)
        desc += '\n{0}'.format('=' * 12)
        for line in self.lines:
            desc += '\n{0}'.format(line)
        desc += '\n{0}\n'.format('=' * 12)
        return desc

    def __repr__(self):
        return self.__str__()


# =============================================================================
# Define functions
# =============================================================================
def get_log_files(params, recipe, path, nightname=None):
    # ----------------------------------------------------------------------
    # load night names
    files = glob.glob(os.path.join(path, '*'))
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, 'info', 'Finding night directories for {0}'.format(path))
    # find directories
    nights = []
    # loop around files
    for filepath in files:
        # get basename
        basename = os.path.basename(filepath)
        # deal with having a night name set
        if nightname not in [None, 'None', '']:
            if basename == nightname:
                nights.append(filepath)
        elif os.path.isdir(filepath):
            nights.append(filepath)
    # log how many nights found
    if len(nights) > 0:
        WLOG(params, '', 'Found {0} night directories'.format(len(nights)))
    else:
        WLOG(params, 'error', 'No night directories found.')
    # ----------------------------------------------------------------------
    # locate log files
    logfitsfile = params['DRS_LOG_FITS_NAME']
    # log files
    logfiles, nightnames = [], []
    # loop around nights
    for night in nights:
        # get absolute path
        abspath = os.path.join(night, logfitsfile)
        # see if file exists
        if os.path.exists(abspath):
            logfiles.append(abspath)
            nightnames.append(os.path.basename(night))
    # log how many log files found
    if len(logfiles) > 0:
        WLOG(params, '', 'Found {0} night directories'.format(len(logfiles)))
    else:
        WLOG(params, 'error', 'No night directories found.')
    # return the log files and night names
    return logfiles, nightnames


def make_log_table(params, logfiles, nightnames, recipename, since=None,
                   before=None):
    # log progress
    WLOG(params, '', 'Loading log files')
    # define dict storage
    masterdict = OrderedDict()
    # loop around log files and open them into storage
    for l_it, logfile in enumerate(logfiles):
        # print progress
        WLOG(params, '', '\t - Loading {0}'.format(logfile))
        # open file
        table = Table.read(logfile, format='fits')

        # filter by recipe name if provided
        if recipename is not None:
            logrecipes = np.char.array(np.array(table['RECIPE'], dtype=str))
            logrecipes = logrecipes.replace('.py', '').strip()
            # create recipe mask
            rmask = logrecipes == recipename.replace('.py', '').strip()
            # test if we have any rows left
            if np.sum(rmask) != 0:
                # apply mask to table
                table = table[rmask]
            else:
                # else skip to next log
                continue

        # filter by time "since" and "before"
        # TODO: remove if statement once we always have HTIME
        if 'HTIME' in table:
            # get htimes as astropy time objects
            htimes = Time(table['HTIME'], format='iso')
            # accept all values originally
            hmask = np.ones(htimes, dtype=bool)

            # use masks from since and before
            if since not in ['None', None, '']:
                hmask &= htimes >= since
            if before not in ['None', None, '']:
                hmask &= htimes <= before
            # test if we have any rows left
            if np.sum(hmask) != 0:
                # apply hmask to table
                table = table[hmask]
            else:
                # else skip to next log
                continue

        # add a night column to masterdict
        if 'NIGHT' not in masterdict:
            masterdict['NIGHT'] = [nightnames[l_it]] * len(table)
        else:
            masterdict['NIGHT'] += [nightnames[l_it]] * len(table)
        # now add columsn from table
        for col in table.colnames:
            if col not in masterdict:
                masterdict[col] = list(table[col])
            else:
                masterdict[col] += list(table[col])
    # deal with no files found
    if len(masterdict.keys()) == 0:
        return None

    # once we have the master dict convert to table
    mastertable = Table()
    for col in masterdict:
        mastertable[col] = masterdict[col]

    # return master table
    return mastertable


def save_master(params, mastertable, path, recipename, makemaster):
    if mastertable is not None and makemaster:
        # define master name
        mastername = 'MASTER_LOG.fits'
        # deal with having a recipename
        if recipename is not None:
            # construct recipe master name
            rmname = recipename.replace('.py', '').replace('.', '_').strip()
            # update master name
            mastername = mastername.replace('.fits', '_' + rmname)
        # construct absolute path
        absmtable = os.path.join(path, mastername)
        # log saving of table
        WLOG(params, 'info', 'Saving master log to: {0}'.format(absmtable))
        # save table
        mastertable.write(absmtable, format='fits', overwrite=True)


def search_recipes(params, recipe, recipename):
    # deal with no recipename set
    if recipename in ['None', '', None]:
        return None

    # deal with recipe name
    if not recipename.endswith('.py'):
        recipename += '.py'

    # try to locate recipe in recipes
    recipes = recipe.recipemod.recipes

    # loop around recipes
    for trial_recipe in recipes:
        # try to see if recipe is matched
        if recipename == trial_recipe.name:
            # log that we found recipe
            wargs = [recipename]
            wmsg = 'Found and filtering by recipe="{0}"'
            WLOG(params, '', wmsg.format(*wargs))
            # return recipe
            return recipename

    # log that we did not find recipe
    wargs = [recipename]
    wmsg = 'Did not find recipe="{0}" not filtering by recipe.'
    WLOG(params, 'warning', wmsg.format(*wargs))

    # if we have got to this point return None
    return None


def get_time(params, inputtime, kind='time'):
    # deal with no time given
    if inputtime in [None, 'None', '']:
        return None
    # else try to make astropy Time instance
    try:
        outtime = Time(inputtime, format='iso')
    except Exception as e:
        eargs = [kind, inputtime, type(e), str(e)]
        emsg = 'Time "{0}"="{1}" not understood. \n\t Error {1}: {2}'
        WLOG(params, 'error', emsg.format(*eargs))
        outtime = None
    # return astropy time
    return outtime


def calculate_stats(params, recipe, mastertable):
    # ----------------------------------------------------------------------
    # get unique recipes
    urecipes = np.unique(mastertable[RECIPECOL])
    # ----------------------------------------------------------------------
    # store stats
    started_stats = OrderedDict()
    passed_stats = OrderedDict()
    ended_stats = OrderedDict()
    started_arr, passed_arr, ended_arr = [], [] ,[]
    # ----------------------------------------------------------------------
    # count how many started, passed qc and ended
    for urecipe in urecipes:
        # mask the table
        mask = mastertable[RECIPECOL] == urecipe
        # started
        started = np.sum(mask & mastertable[STARTCOL])
        # passed qc
        passed = np.sum(mask & mastertable[PASSEDCOL])
        # ended
        ended = np.sum(mask & mastertable[ENDCOL])
        # append stats to dict
        started_stats[urecipe] = started
        passed_stats [urecipe] = passed
        ended_stats[urecipe] = ended

        started_arr.append(started)
        passed_arr.append(passed)
        ended_arr.append(ended)
    # ----------------------------------------------------------------------
    # make arrays
    x = np.arange(0, len(urecipes))
    started_arr = np.array(started_arr)
    passed_arr = np.array(passed_arr)
    ended_arr = np.array(ended_arr)
    # ----------------------------------------------------------------------
    # print stats
    for urecipe in urecipes:
        started = started_stats[urecipe]
        passed = passed_stats [urecipe]
        ended = ended_stats[urecipe]
        _print_stats(params, started, passed, ended, urecipe)
    # ----------------------------------------------------------------------
    # plot bar plot
    pkwargs = dict(started=started_arr, passed=passed_arr, ended=ended_arr,
                   urecipes=urecipes)
    recipe.plot('LOGSTATS_BAR', **pkwargs)


def calculate_recipe_stats(params, mastertable, recipename):
    # started
    started = np.sum(mastertable[STARTCOL])
    # passed qc
    passed = np.sum(mastertable[PASSEDCOL])
    # ended
    ended = np.sum(mastertable[ENDCOL])
    # ----------------------------------------------------------------------
    # print stats
    _print_stats(params, started, passed, ended, recipename)
    # ----------------------------------------------------------------------
    # get log files
    logfiles = mastertable[LOGCOL]
    # log that we are getting log files
    WLOG(params, '', 'Obtaining individual log files')
    # for each log file get all log errors and warnings
    errors, warns = [], []
    for logfile in logfiles:
        # deal with log file not existing
        if not os.path.exists(logfile):
            # try to find it
            found, logfile = _find_log_file(params, logfile)
            # if not found report warning
            if not found:
                WLOG(params, 'warning', '\t - No log file: {0}'.format(logfile))
                errors += 'No log file'
                continue
        WLOG(params, '', '\t - Loading: {0}'.format(logfile))
        error, warn = _create_log_objs(params, logfile)
        errors += error
        warns += warn
    # ----------------------------------------------------------------------
    # tabulate the number of errors and warnings found for this recipe
    # ----------------------------------------------------------------------
    errorcount = OrderedDict()
    errormessages = OrderedDict()
    warncount = OrderedDict()
    warnmessages = OrderedDict()
    # ----------------------------------------------------------------------
    # loop around errors
    for error in errors:
        # store counts
        if error.code in errorcount:
            errorcount[error.code] += 1
        else:
            errorcount[error.code] = 1
        # store messages
        if error.code in errormessages:
            errormessages[error.code].append(error.msg)
        else:
            errormessages[error.code] = [error.msg]
    # ----------------------------------------------------------------------
    # loop around warnings
    for warn in warns:
        # store counts
        if warn.code in warncount:
            warncount[warn.code] += 1
        else:
            warncount[warn.code] = 1
        # store messages
        if warn.code in warnmessages:
            warnmessages[warn.code].append(warn.msg)
        else:
            warnmessages[warn.code] = [warn.msg]
    # ----------------------------------------------------------------------
    # push these counts into lists
    # ----------------------------------------------------------------------
    error_codes, error_msgs, error_sample, error_counts = [], [], [], []
    warn_codes, warn_msgs, warn_sample, warn_counts = [], [], [], []
    for error in errorcount:
        error_codes.append(error)
        error_msgs += errormessages[error]
        error_counts.append(errorcount[error])
        error_sample.append(errormessages[error][-1])
    for warn in warncount:
        warn_codes.append(warn)
        warn_msgs += warnmessages[warn]
        warn_counts.append(warncount[warn])
        warn_sample.append(warnmessages[warn][-1])
    # ----------------------------------------------------------------------
    # Error Print out
    # ----------------------------------------------------------------------
    # print unique error messages
    used_errors = dict()
    WLOG(params, '', '')
    WLOG(params, 'info', 'Unique error messages: ')
    # count number of time unique message appear
    for it, error_msg in enumerate(error_msgs):
        if error_msg not in used_errors:
            used_errors[error_msg] = 1
        else:
            used_errors[error_msg] += 1
    # display unique messages
    for it, error_msg in enumerate(used_errors):
        num = used_errors[error_msg]
        WLOG(params, '', '\t{0} N={1}: {2}'.format(it + 1, num, error_msg))
        WLOG(params, '', '')
    # ----------------------------------------------------------------------
    # Warning Print out
    # ----------------------------------------------------------------------
    # print unique warning messages
    used_warnings = dict()
    WLOG(params, '', '')
    WLOG(params, 'info', 'Unique warning messages: ')
    # count number of time unique message appear
    for it, warn_msg in enumerate(warn_msgs):
        if warn_msg not in used_warnings:
            used_warnings[warn_msg] = 1
        else:
            used_warnings[warn_msg] += 1
    # display unique messages
    for it, warn_msg in enumerate(used_warnings):
        num = used_warnings[warn_msg]
        WLOG(params, '', '\t{0} N={1}: {2}'.format(it + 1, num, warn_msg))
        WLOG(params, '', '')
    # ----------------------------------------------------------------------
    # PLOT
    # ----------------------------------------------------------------------
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ioff()

    fig, frames = plt.subplots(nrows=1, ncols=2)
    tooltip1 = hover_bars(fig, frames[0], error_codes, error_counts,
                          error_sample, align='right')
    tooltip2 = hover_bars(fig, frames[1], warn_codes, warn_counts,
                          warn_sample, align='left')

    # set labels
    frames[0].set(xlabel='Error Codes', ylabel='Number of Errors found',
                  title='Errors Found')
    frames[1].set(xlabel='Warning Codes', ylabel='Number of Warnings found',
                  title='Warnings Found')
    frames[1].yaxis.tick_right()
    frames[1].yaxis.set_label_position("right")
    # push into tool tip wrapper (as we have multiple)
    tth = ToolTipHover(tooltip1, tooltip2)
    fig.canvas.mpl_connect("motion_notify_event", tth.hover)

    fig.subplots_adjust(bottom=0.2, right=0.95, left=0.05, top=0.90,
                       hspace=0, wspace=0.1)

    plt.suptitle('Recipe = {0}'.format(recipename))
    plt.show(block=True)
    plt.close()

    # ----------------------------------------------------------------------
    # recipe.plot()


def hover_bars(fig, frame, x, y, texts, align=None):
    # define the text box
    textbox = frame.annotate("", xy=(0.0, 0.0), xytext=(0.0, 0.0),
                             textcoords="offset points",
                             bbox=dict(boxstyle="round", fc="white",
                                       ec="k", lw=2),
                             arrowprops=dict(arrowstyle="->"),
                             va='center', zorder=100)
    # storage for bars
    allbars = []
    # loop around bars
    for it in range(len(y)):
        # append bar plot to bars storage
        bars = frame.bar(x[it], y[it], align='center')
        # need to add these to all bars
        for bar in bars:
            allbars.append(bar)

    # extend the x-axis
    _extend_xticks(frame, x)
    # add the tool tip
    tooltip = ToolTip(fig, frame, allbars, textbox, texts)
    # return the tooltip
    return tooltip


class ToolTip():
    def __init__(self, fig, frame, bars, textbox, bartexts):
        self.fig = fig
        self.frame = frame
        self.bars = bars
        self.textbox = textbox
        self.bartexts = bartexts

    def hover(self, event):
        visible = self.textbox.get_visible()
        if event.inaxes == self.frame:
            for b_it, bar in enumerate(self.bars):
                cont, ind = bar.contains(event)
                if cont:
                    self.activate_text(b_it, bar)
                    self.textbox.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return
        if visible:
            self.textbox.set_visible(False)
            self.fig.canvas.draw_idle()

    def activate_text(self, it, bar):
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_y() + bar.get_height() / 2
        xmin, xmax, ymin, ymax = self.frame.axis()
        centx = 0.5 * (xmax + xmin)
        centy = 0.5 * (ymax + ymin)

        self.textbox.xy = (x, y)

        # get text for this bar
        text = self.bartexts[it]
        if text is not None:
            self.textbox.set_text(text)
            self.textbox.get_bbox_patch().set_alpha(0.75)


class ToolTipHover:
    def __init__(self, *tooltips):
        self.tooltips = tooltips

    def hover(self, event):
        for tooltip in self.tooltips:
            tooltip.hover(event)


def _extend_xticks(frame, values):
    frame.set_xticklabels(values, rotation=90)
    frame.set_xlim(-1, len(values))


# =============================================================================
# Define worker functions
# =============================================================================
def _print_stats(params, started, passed, ended, urecipe):
    WLOG(params, 'info', 'Recipe = {0}'.format(urecipe))
    WLOG(params, '', '\t Started  ={0:4d}'.format(started))

    uargs = [passed, started - passed, 100 * (started - passed) / started]
    msg = '\t passed qc={0:4d}\t failed qc ={1:4d}\t ({2:.2f} %)'
    WLOG(params, '', msg.format(*uargs))

    uargs = [ended, started - ended, 100 * (started - ended) / started]
    msg = '\t finished ={0:4d}\t unfinished={1:4d}\t ({2:.2f} %)'
    WLOG(params, '', msg.format(*uargs))


def _create_log_objs(params, logfile):
    # open log file
    lfile = open(logfile, 'r')
    lines = lfile.readlines()
    lfile.close()

    # get file creation date
    mdate = Time(os.path.getmtime(logfile), format='unix')

    # storage for errors and lines
    errorlines = []
    warnlines = []

    ecode, wcode = None, None

    for line in lines:
        # find if we have an error string
        try:
            errorlines, ecode = _id_logmessage(line, errorlines, ecode,
                                               ERRORSTR, ERRORPREFIX,
                                               ERRORSUFFIX, mdate)
        except Exception as e:
            emsg = 'Skipping Line(E): {0}\n{1}:{2}'
            eargs = [line, type(e), str(e)]
            WLOG(params, 'warning', emsg.format(*eargs))
            continue
        # find if we have a warning string
        try:
            warnlines, wcode = _id_logmessage(line, warnlines, wcode,
                                              WARNINGSTR, WARNPREFIX,
                                              WARNSUFFIX, mdate)
        except Exception as e:
            emsg = 'Skipping Line(W): {0}\n{1}:{2}'
            eargs = [line, type(e), str(e)]
            WLOG(params, 'warning', emsg.format(*eargs))
    # return errors and warnings
    return errorlines, warnlines


def _id_logmessage(line, storage, code, logstr, logprefix, logsuffix,
                   mdate):

    if logstr in line:
        if logsuffix in line and logprefix in line:
            code = line.split(logprefix)[-1].split(logsuffix)[0]
            newcode = True
        else:
            newcode = False

        if newcode:
            if code not in storage:
                storage.append(LogObj(code, line, mdate))
            else:
                storage.append(LogObj(code, line, mdate))
        else:
            storage[-1].addline(line)
    # return the storage and the code (changed or not)
    return storage, code


def _find_log_file(params, logfile):
    # log dir
    logdir = params['DRS_DATA_MSG']
    # get basename of logfile
    basename = os.path.basename(logfile)
    # walk through dirs
    for root, dirs, files in os.walk(logdir):
        for filename in files:
            if basename == filename:
                return True, os.path.join(root, filename)
    # if we have gotten to here we haven't found file
    return False, None


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
