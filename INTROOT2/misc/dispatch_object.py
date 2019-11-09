#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-08 at 15:54

@author: cook
"""
from astropy.table import Table
from astropy.time import Time
import sys
import os
import glob
from tqdm import tqdm


# =============================================================================
# Define variables
# =============================================================================
STORED_OBJECTS = ['TOI-442', 'Gl436', 'Gl699', 'Gl15A', 'HD189733',
                  'GJ1002', 'GJ1214', 'Trappist-1']
STORED_OBJECTS = ['TOI-442']
# -----------------------------------------------------------------------------
INPUT_DIR = '/spirou/cfht_nights/cfht_oct1/reduced/'
DESTINATION = '/spirou/sandbox/per_object/'
STAT_FILE = 'counts.dat'

RDEST = 'cpapir@genesis.astro.umontreal.ca:/home/cpapir/www/per_object/'

# =============================================================================
# Define functions
# =============================================================================


# Download data locally and properly set paths when a new object has been
# observed. We assume that the log on GENESIS is up to date. There are
# a number of files and directories that are assumed to be present

# object to be retrieved

def dispatch_object(obj='Gl436'):
    # path on MAESTRIA in the SPIROU account
    if INPUT_DIR.endswith(os.sep):
        path = INPUT_DIR
    else:
        path = INPUT_DIR + os.sep

    # destination path
    destination = os.path.join(DESTINATION, obj)

    # make directory if it doesn't exist
    if os.path.isdir(destination) == False:
        os.mkdir(destination)

    # we remove the all_log.dat to leae place for the new one. Its OK if the
    # file is not present to start with
    os.system('rm -f all_log.dat')
    # get the file from GENESIS
    os.system('wget http://genesis.astro.umontreal.ca/spirou_logs/all_log.dat')

    # reading the log of all observations
    tbl = Table.read('all_log.dat', format='ascii')

    # remove all other objects
    tbl = tbl[tbl['OBJECT'] == obj]

    cmd = 'cp {0}*/Template*{1}*.fits {2}/'
    os.system(cmd.format(path, obj, destination))

    odometers = []
    for it in range(len(tbl)):
        odometer = tbl['FILE'][it].split('.')[0]
        date = tbl['DATE'][it]

        cmd = 'cp {0}/{1}/{2}*.fits {3}/'
        cmd = cmd.format(path, date, odometer, destination)
        print(it, '/', len(tbl), ' ', cmd)
        os.system(cmd)
        # append odometer
        odometers.append(odometer)

    timestamp = Time.now().iso.replace(':', '').replace('-', '')
    timestamp = timestamp.replace(' ', '').split('.')[0]

    tarname = '{0}_{1}.tar'.format(obj, timestamp)
    os.system('tar -cvf ' + tarname + ' ' + obj + '/* ')


    rsync_cmd = 'rsync -av -e "ssh -oport=5822" {0} {1}'
    rsync_cmd = rsync_cmd.format(tarname, RDEST)

    os.system(rsync_cmd)

    return destination, odometers


def analysis(path, odocodes):
    # storage of types
    types = dict()
    # find all files in path
    files = glob.glob(path + '/*.fits')
    # loop around all files
    for filename in tqdm(files):
        # get base name
        basename = os.path.basename(filename)
        # loop around odocodes
        for odocode in odocodes:
            if odocode in filename:
                # get suffix
                suffix = basename.split(odocode)[1]
                # add to count
                if suffix in types:
                    types[suffix] += 1
                else:
                    types[suffix] = 1
                # once found break
                break
    # return the type counts
    return types


def dispatch_objects(objs):
    # storage of columns
    object_dict = dict()
    # loop around objects and add
    for obj in objs:
        # dispatch objects
        path, odocodes = dispatch_object(obj=obj)
        # analysis for table
        types = analysis(path, odocodes)
        # append to object dict
        object_dict[obj] = types
    # tidy up and save to table
    columns = []
    # get columns
    for obj in object_dict:
        for col in (object_dict[obj].keys()):
            if col not in columns:
                columns.append(col)
    # now make table dict
    tabledict = dict()
    tabledict['name'] = list(object_dict.keys())
    # loop around columns and add values
    for col in columns:
        tabledict[col] = []
        # all all objects
        for obj in object_dict:
            if col in object_dict[obj]:
                tabledict[col] = object_dict[obj][col]
            else:
                tabledict[col] = 0
    # convert to table
    outtable = Table()
    for col in tabledict:
        outtable[col] = tabledict[col]
    # construct count table name
    countfilename = os.path.join(DESTINATION, STAT_FILE)
    # write out table
    outtable.write(countfilename, format='ascii.rst', overwrite=True)
    # sync file to server
    rsync_cmd = 'rsync -av -e "ssh -oport=5822" {0} {1}'
    rsync_cmd = rsync_cmd.format(countfilename, RDEST)
    os.system(rsync_cmd)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # get command line arguments
    args = sys.argv
    # deal with no arguments
    if len(args) == 1:
        print('Please specify object argument(s)')
    # deal with 'all' as argument
    elif args[1] == 'all':
        dispatch_objects(STORED_OBJECTS)
    # if one object just do one dispatch
    elif len(args) == 2:
        dispatch_object(sys.argv[1])
    # else assume we have multiple arguments
    else:
        dispatch_objects(sys.argv[1:])




# =============================================================================
# End of code
# =============================================================================
