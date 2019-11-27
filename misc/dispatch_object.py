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
import argparse


# =============================================================================
# Define variables
# =============================================================================
STORED_OBJECTS = ['TOI-442', 'Gl436', 'Gl699', 'Gl15A', 'HD189733',
                  'GJ1002', 'GJ1214', 'Trappist-1']
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

def dispatch_object(obj='Gl436', write=True):
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
        if write:
            os.system(cmd)
        # append odometer
        odometers.append(odometer)

    timestamp = Time.now().iso.replace(':', '').replace('-', '')
    timestamp = timestamp.replace(' ', '').split('.')[0]

    tarname = '{0}_{1}.tar'.format(obj, timestamp)
    if write:
        os.system('tar -cvf ' + tarname + ' ' + obj + '/* ')

    rsync_cmd = 'rsync -av -e "ssh -oport=5822" {0} {1}'
    if write:
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


def dispatch_objects(objs, write=True):
    # storage of columns
    object_dict = dict()
    # loop around objects and add
    for obj in objs:
        # log progress
        print('='*50)
        print('Processing object {0}'.format(obj))
        print('=' * 50)
        # dispatch objects
        path, odocodes = dispatch_object(obj=obj, write=write)
        # analysis for table
        types = analysis(path, odocodes)
        # append to object dict
        object_dict[obj] = types
    # tidy up and save to table
    columns = []
    # get columns
    print('=' * 50)
    print('Getting columns')
    print('=' * 50)
    # loop around object_dict
    for obj in object_dict:
        for col in (object_dict[obj].keys()):
            if col not in columns:
                columns.append(col)
    # now make table dict
    print('=' * 50)
    print('Constructing table')
    print('=' * 50)
    tabledict = dict()
    tabledict['name'] = list(object_dict.keys())
    # loop around columns and add values
    for col in columns:
        # new col name
        newcol = col.replace('_', '').replace('pp', '').replace('.fits', '')
        # create new column
        tabledict[newcol] = []
        # all all objects
        for obj in object_dict:
            if col in object_dict[obj]:
                tabledict[newcol].append(object_dict[obj][col])
            else:
                tabledict[newcol].append(0)
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
    parser = argparse.ArgumentParser(description='Create batch object outputs')


    helpmsg = ('object to dispatch (if left blank does the following: '
               '{0}'.format(' '.join(STORED_OBJECTS)))
    parser.add_argument('--objects', dest='objects', type=str,
                        default='all', help=helpmsg, nargs='+')
    parser.add_argument('--write', dest='write', type=bool,
                        default=False, help='Whether to write/copy/tar objs')
    args = parser.parse_args()

    if args.write in [True, 'True', 1, '1']:
        args.write = True
    else:
        args.write = False

    # deal with 'all' as argument
    if 'all' in args.objects:
        dispatch_objects(STORED_OBJECTS, write=args.write)
    # else assume we have multiple arguments
    else:
        dispatch_objects(args.objects)




# =============================================================================
# End of code
# =============================================================================
