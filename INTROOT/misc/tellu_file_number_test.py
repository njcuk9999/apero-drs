#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-11 at 10:29

@author: cook
"""
import numpy as np
from astropy.io import fits
from astropy.table import Table
import os
import glob

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE0 = '/spirou/cfht_nights/common/tmp/'
WORKSPACE1 = '/spirou/cfht_nights/cfht_Jan19/reduced_2/'
WORKSPACE2 = '/spirou/cfht_nights/cfht_Jan19/telluDB_2/'
WORKSPACE3 = '/spirou/drs/spirou_py3/INTROOT/SpirouDRS/data/constants/'

WHITELIST_FILE = os.path.join(WORKSPACE3, 'tellu_whitelist.txt')
MASTERTELLU_FILE = os.path.join(WORKSPACE2, 'master_tellu_SPIROU.txt')
TELLU_KEY = 'TELL_MAP'
BIGCUBE_FILE = 'BigCube_*'
INDEX_FILENAME = 'index.fits'
DRS_OUTS = ['OBJ_FP', 'OBJ_DARK']
DRS_IDS = ['EXT_E2DS_AB']


# =============================================================================
# Define functions
# =============================================================================
def load_db(filename, key):
    print('Loading database = {0}'.format(filename))
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    out_lines = []
    for line in lines:
        if key not in line:
            continue
        else:
            out_lines.append(line.split())
    return out_lines


def get_index_files(path):
    index_files = []
    index_tables = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == INDEX_FILENAME:
                absfilename = os.path.join(root, filename)
                print('Loading index = {0}'.format(absfilename))
                index_files.append(absfilename)
                index_tables.append(Table.read(absfilename))
    return index_files, index_tables


def stripstr(x):
    return x.strip()


def find_pp_files(object_name, index_files, index_tables):
    out_files = []
    for it in range(len(index_tables)):
        itable = index_tables[it]
        idir = os.path.dirname(index_files[it])
        objnames = np.array(list(map(stripstr, list(itable['OBJNAME']))))
        dprtypes = np.array(list(map(stripstr, list(itable['DPRTYPE']))))
        for row in range(len(itable)):
            cond1 = (objnames[row] == object_name)
            cond2 = (dprtypes[row] in DRS_OUTS)
            if cond1 and cond2:
                out_files.append(os.path.join(idir, itable['FILENAME'][row]))
    return out_files


def find_e2ds_files(object_name, index_files, index_tables):
    out_files = []
    for it in range(len(index_tables)):
        itable = index_tables[it]
        idir = os.path.dirname(index_files[it])
        objnames = np.array(list(map(stripstr, list(itable['OBJNAME']))))
        dprtypes = np.array(list(map(stripstr, list(itable['DRS_EOUT']))))
        drsoutid = np.array(list(map(stripstr, list(itable['DRSOUTID']))))

        for row in range(len(itable)):
            cond1 = (objnames[row] == object_name)
            cond2 = (dprtypes[row] in DRS_OUTS)
            cond3 = (drsoutid[row] in DRS_IDS)
            if cond1 and cond2 and cond3:
                out_files.append(os.path.join(idir, itable['FILENAME'][row]))
    return out_files


def find_matching(object_name, database):
    matching_files = []
    for entry in database:
        if entry[4].strip() == object_name.strip():
            if entry[1].strip() not in matching_files:
                matching_files.append(entry[1].strip())
    return matching_files


def compare_pp_e2ds_files(pfiles, efiles):

    # get base name files
    bfiles = list(map(lambda x: os.path.basename(x).split('_pp')[0], pfiles))
    befiles = list(map(lambda x: os.path.basename(x).split('_pp')[0], efiles))

    # storage for not found (index)
    not_found_index = []
    found_index = []
    # all efiles should be in pfiles
    for it in range(len(pfiles)):
        if bfiles[it] not in befiles:
            not_found_index.append(pfiles[it])
        else:
            found_index.append(pfiles[it])

    # storage for not found (disk)
    not_found_disk = []
    found_disk = []
    # all efiles should be on disk
    for it in range(len(pfiles)):
        if not os.path.exists(pfiles[it]):
            not_found_disk.append(pfiles[it])
        else:
            found_disk.append(pfiles[it])

    return not_found_index, found_index, not_found_disk, found_disk

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':

    # load up BigCubes filenames
    bigcubes_files = glob.glob(os.path.join(WORKSPACE1, '*', BIGCUBE_FILE))

    # sort by base filename
    basefilenames = list(map(lambda x: os.path.basename(x), bigcubes_files))
    sortmask = np.argsort(np.array(basefilenames))
    bigcubes_files = np.array(bigcubes_files)[sortmask]
    basefilenames = np.array(basefilenames)[sortmask]

    # load white list file
    wlist = np.loadtxt(WHITELIST_FILE, dtype=str)

    # load up the master tellu file
    mastertellu = load_db(MASTERTELLU_FILE, 'TELL_MAP')

    # load up all index files
    ifiles1, itables1 = get_index_files(WORKSPACE0)
    ifiles2, itables2 = get_index_files(WORKSPACE1)

    # storage for numbers
    storage = dict()
    filestorage1, filestorage2, filestorage3 = dict(), dict(), dict()
    filestorage_nfi, filestorage_nfd = dict(), dict()
    filestorage_fi, filestorage_fd = dict(), dict()
    totals = dict(PP=0, E2DS=0, TELLUDB=0, BIGCUBE=0)
    # loop around big cubes
    for objname in wlist:

        # construct bigcube filename
        bigcube_filename = 'BigCube_{0}.fits'.format(objname)

        # find in list
        pos = (bigcube_filename == np.array(basefilenames))

        if np.sum(pos) > 0:
            # read header
            header = fits.getheader(bigcubes_files[pos][0])
            # get object name
            objname_hdr = header['OBJECT'].strip()
            # get fits table
            bigtable = Table.read(bigcubes_files[pos][0])
            # check objname in header
            if objname_hdr.strip() != objname:
                oargs = [objname, objname_hdr]
                print('Error for object {0}, header obj={1}'.format(*oargs))
        else:
            bigtable = Table()

        # find all pp files
        pp_files = find_pp_files(objname, ifiles1, itables1)

        # find all E2DS_AB files
        e2ds_files = find_e2ds_files(objname, ifiles2, itables2)

        # find those in pp and not in e2ds
        eout = compare_pp_e2ds_files(pp_files, e2ds_files)
        e2ds_nfi, e2ds_fi, e2ds_nfd, e2ds_fd = eout

        # find all objects in master tellu that match
        matching_filenames = find_matching(objname, mastertellu)
        # add to totals
        totals['PP'] += len(pp_files)
        totals['BIGCUBE'] += len(bigtable)
        totals['TELLUDB'] += len(matching_filenames)
        totals['E2DS'] += len(e2ds_files)
        # store in file and print
        pargs = [objname, len(pp_files), len(e2ds_files),
                 len(matching_filenames), len(bigtable)]
        print('{0:15s}: in PP={1:3d} in E2DS={2:3d} in telluDB={3:3d} '
              'in BigCube={4:3d}'.format(*pargs))
        storage[objname] = pargs[1:]
        filestorage1[objname] = pp_files
        filestorage2[objname] = e2ds_files

        filestorage_nfi[objname] = e2ds_nfi
        filestorage_fi[objname] = e2ds_fi
        filestorage_nfd[objname] = e2ds_nfd
        filestorage_fd[objname] = e2ds_fd

        if len(bigtable) > 0:
            filestorage3[objname] = list(bigtable['Filename'])
        else:
            filestorage3[objname] = []

# =============================================================================
# End of code
# =============================================================================
