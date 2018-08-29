#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
off_listing_RAW_spirou.py [night_directory]

Recipe to display raw frame + cut across orders + statistics

Created on 2016-06-12

@author: fbouchy

Last modified: 2016-06-15
"""
from __future__ import division
import numpy as np
import os, string
from astropy.io import fits


from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'off_listing_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get param dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, mainfitsdir='reduced')

    # check that we have a night_name
    if p['ARG_NIGHT_NAME'] == '':
        # get available night_names
        nightnames = spirouStartup.GetNightDirs(p)

        emsgs = ['Must define night name. Input should be:']
        emsgs.append('\t >> {0} [NIGHT_NAME]'.format(__NAME__))
        emsgs.append(' ')
        emsgs.append('Some available NIGHT_NAMES are as follows:')
        # loop around night names and add to message
        for nightname in nightnames:
            emsgs.append('\t {0}'.format(nightname))
        # log message
        WLOG('error', p['LOG_OPT'], emsgs)


    # ----------------------------------------------------------------------
    # Get all files in raw night_name directory
    # ----------------------------------------------------------------------
    # get all files in DRS_DATA_RAW/ARG_NIGHT_NAME
    files = os.listdir(p['ARG_FILE_DIR'])
    # sort file by name
    files = np.sort(files)

    # ----------------------------------------------------------------------
    # Define storage for file header keys
    # ----------------------------------------------------------------------
    loc = ParamDict()
    loc['FILES'] = []
    loc['EXPTIME_ALL'] = []
    loc['CAS_ALL'] = []
    loc['REF_ALL'] = []
    loc['DATE_ALL'] = []
    loc['UTC_ALL'] = []
    loc['OBSTYPE_ALL'] = []
    loc['OBJNAME_ALL'] = []
    loc['DENS_ALL'] = []

    # ----------------------------------------------------------------------
    # Loop around all files and extract required header keys
    # ----------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Analysing {0} files'.format(len(files)))
    # loop around files and extract properties
    for filename in files:
        # skip any non-fits file files
        if '.fits' not in filename:
            continue
        # construct absolute path for file
        fitsfilename = os.path.join(p['ARG_FILE_DIR'], filename)
        # read file header
        hdr = spirouImage.ReadHeader(p, filepath=fitsfilename)
        # extract properties from header
        fkwargs = dict(return_value=True, dtype=float, required=False)
        gkwargs = dict(return_value=True, dtype=str, required=False)
        date = spirouImage.ReadParam(p, hdr, 'kw_DATE_OBS', **gkwargs)
        utc = spirouImage.ReadParam(p, hdr, 'kw_UTC_OBS', **gkwargs)
        obstype = spirouImage.ReadParam(p, hdr, 'kw_OBSTYPE', **gkwargs)
        objname = spirouImage.ReadParam(p, hdr, 'kw_OBJNAME', **gkwargs)
        # deal with None
        if date is None:
            data = ''
        if utc is None:
            utc = ''
        if obstype is None:
            obstype = ''
        if objname is None:
            objname = ''
        # add to loc
        loc['FILES'].append(filename)
        loc['DATE_ALL'].append(date)
        loc['UTC_ALL'].append(utc)
        loc['OBSTYPE_ALL'].append(obstype)
        loc['OBJNAME_ALL'].append(objname)
    # Make sure we have some files
    if len(loc['FILES']) == 0:
        wmsg = 'No pre-processed (*{0}) files present.'
        WLOG('warning', p['LOG_OPT'], wmsg.format(p['PROCESSED_SUFFIX']))

    # ----------------------------------------------------------------------
    # archive to table
    # ----------------------------------------------------------------------
    if len(loc['FILES']) != 0:
        # construct table filename
        outfile = spirouConfig.Constants.OFF_LISTING_FILE(p)
        # log progress
        WLOG('', p['LOG_OPT'], 'Creating ascii file for listing.')
        # define column names
        columns = ['file', 'type', 'date', 'utc', 'objname']
        # define the format for each column
        formats = [None, None, None, None, None]

        # get the values for each column
        values = [loc['FILES'], loc['OBSTYPE_ALL'], loc['DATE_ALL'],
                  loc['UTC_ALL'], loc['OBJNAME_ALL']]
        # construct astropy table from column names, values and formats
        table = spirouImage.MakeTable(columns, values, formats)
        # save table to file
        # spirouImage.WriteTable(table, outfile, fmt='ascii.rst')

        # log saving of file
        wmsg = 'Listing of directory on file {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(outfile))

        # print out to screen
        WLOG('', '', '')
        WLOG('', '', 'Listing table:')
        WLOG('', '', '')
        spirouImage.PrintTable(table)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================



