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
import os
from collections import OrderedDict

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
__args__ = ['night_name']
__required__ = [True]
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
    p = spirouStartup.LoadArguments(p, night_name)

    # check that we have a night_name
    if p['ARG_NIGHT_NAME'] == '':
        # get available night_names
        nightnames = spirouStartup.GetNightDirs(p)

        emsgs = ['Must define night name. Input should be:',
                 '\t >> {0} [NIGHT_NAME] '.format(__NAME__),
                 'Some available NIGHT_NAMES are as follows:']
        # loop around night names and add to message
        for nightname in nightnames:
            emsgs.append('\t {0}'.format(nightname))
        # log message
        WLOG(p, 'error', emsgs)

    # ----------------------------------------------------------------------
    # Check if we have an index file
    # ----------------------------------------------------------------------
    # get expected index file name and location
    index_file = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    path = p['ARG_FILE_DIR']
    index_path = os.path.join(path, index_file)
    # get expected columns
    columns = spirouConfig.Constants.RAW_OUTPUT_COLUMNS(p)
    # create storage
    loc = OrderedDict()
    # if file exists then we have some indexed files
    if os.path.exists(index_path):
        rawloc = spirouImage.ReadFitsTable(p, index_path)
        loc['FILENAME'] = list(rawloc['FILENAME'])
        loc['LAST_MODIFIED'] = list(rawloc['LAST_MODIFIED'])
        for col in columns:
            loc[col] = list(rawloc[col])
    # else we have to create this file
    else:
        loc['FILENAME'] = []
        loc['LAST_MODIFIED'] = []
        # loop around columns and add blank list to each
        for col in columns:
            loc[col] = []

    # ----------------------------------------------------------------------
    # Get all files in raw night_name directory
    # ----------------------------------------------------------------------
    # get all files in DRS_DATA_RAW/ARG_NIGHT_NAME
    files = os.listdir(p['ARG_FILE_DIR'])
    # sort file by name
    files = np.sort(files)

    # ----------------------------------------------------------------------
    # Loop around all files and extract required header keys
    # ----------------------------------------------------------------------
    # log progress
    WLOG(p, '', 'Analysing {0} files'.format(len(files)))
    # loop around files and extract properties
    for filename in files:
        # skip any non-fits file files
        if '.fits' not in filename:
            continue
        # skip the index file
        if filename == os.path.basename(index_file):
            continue
        # skip non-preprocessed files
        if p['PROCESSED_SUFFIX'] not in filename:
            continue
        # if already in loc['FILENAME'] then skip
        if filename in loc['FILENAME']:
            continue
        # construct absolute path for file
        fitsfilename = os.path.join(p['ARG_FILE_DIR'], filename)
        # read file header
        hdr = spirouImage.ReadHeader(p, filepath=fitsfilename)
        # add filename
        loc['FILENAME'].append(filename)
        loc['LAST_MODIFIED'].append(os.path.getmtime(fitsfilename))
        # loop around columns and look for key in header
        for col in columns:
            # get value from header
            if col in hdr:
                value = str(hdr[col])
            else:
                value = '--'
            # push into loc
            loc[col].append(value)

    # Make sure we have some files
    if len(loc['FILENAME']) == 0:
        wmsg = 'No pre-processed (*{0}) files present.'
        WLOG(p, 'warning', wmsg.format(p['PROCESSED_SUFFIX']))

    # ----------------------------------------------------------------------
    # archive to table
    # ----------------------------------------------------------------------
    if len(loc['FILENAME']) != 0:
        # construct table filename
        outfile = spirouConfig.Constants.OFF_LISTING_RAW_FILE(p)
        # log progress
        WLOG(p, '', 'Creating ascii file for listing.')
        # get column names
        colnames = ['FILENAME', 'LAST_MODIFIED'] + list(columns)
        # define the format for each column
        formats = [None] * len(colnames)
        # get the values for each column
        values = []
        for col in colnames:
            values.append(loc[col])
        # construct astropy table from column names, values and formats
        table = spirouImage.MakeTable(p, colnames, values, formats)
        # save table to file
        spirouImage.WriteTable(p, table, outfile, fmt='ascii.rst')

        # log saving of file
        wmsg = 'Listing of directory on file {0}'
        WLOG(p, '', wmsg.format(outfile))

        # print out to screen
        WLOG(p, '', '')
        WLOG(p, '', 'Listing table:')
        WLOG(p, '', '')
        spirouImage.PrintTable(p, table)

    # ----------------------------------------------------------------------
    # Update Index
    # ----------------------------------------------------------------------
    spirouStartup.SortSaveOutputs(p, loc, index_path)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
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



