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
kind = 1
# kind = 2

WORKSPACE_RAW = '/spirou/cfht_nights/common/raw/'
WORKSPACE0 = '/spirou/cfht_nights/common/tmp/'
WORKSPACE1 = '/spirou/cfht_nights/cfht_Jan19/reduced_{0}/'.format(kind)
WORKSPACE2 = '/spirou/cfht_nights/cfht_Jan19/telluDB_{0}/'.format(kind)
WORKSPACE3 = '/spirou/drs/spirou_py3/INTROOT/SpirouDRS/data/constants/'

WHITELIST_FILE = os.path.join(WORKSPACE3, 'tellu_whitelist.txt')
MASTERTELLU_FILE = os.path.join(WORKSPACE2, 'master_tellu_SPIROU.txt')
TELLU_KEY1 = 'TELL_OBJ'
TELLU_KEY2 = 'TELL_MAP'
BIGCUBE_FILE = 'BigCube_*'
INDEX_FILENAME = 'index.fits'
DRS_OUTS = ['OBJ_FP', 'OBJ_DARK']
DRS_IDS = ['EXT_E2DS_AB']
RAW_SUFFIX = 'o.fits'
PP_SUFFIX = 'o_pp.fits'
E2DS_SUFFIX = 'o_pp_e2ds_AB.fits'


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
    print('Loading index files...')
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == INDEX_FILENAME:
                absfilename = os.path.join(root, filename)
                index_files.append(absfilename)
                index_tables.append(Table.read(absfilename))
    return index_files, index_tables


def stripstr(x):
    return x.strip()


def get_raw_files(suffix=''):
    print('Searching all raw files headers, please wait...')

    out_files, out_objs = [], []
    allfiles = glob.glob(os.path.join(WORKSPACE_RAW, '*', '*' + suffix))
    for it in range(len(allfiles)):
        header = fits.getheader(allfiles[it])
        objname_hdr = str(header['OBJNAME'])
        out_files.append(allfiles[it])
        out_objs.append(objname_hdr.strip())
    return np.array(out_files), np.array(out_objs)


def get_pp_files(suffix=''):
    print('Searching all pp files headers, please wait...')

    out_files, out_objs = [], []
    allfiles = glob.glob(os.path.join(WORKSPACE0, '*', '*' + suffix))
    for it in range(len(allfiles)):
        header = fits.getheader(allfiles[it])
        objname_hdr = str(header['OBJNAME'])
        out_files.append(allfiles[it])
        out_objs.append(objname_hdr.strip())
    return np.array(out_files), np.array(out_objs)


def get_e2ds_files(suffix=''):
    print('Searching all e2ds files headers, please wait...')

    out_files, out_objs = [], []
    allfiles = glob.glob(os.path.join(WORKSPACE1, '*', '*' + suffix))
    for it in range(len(allfiles)):
        header = fits.getheader(allfiles[it])
        objname_hdr = str(header['OBJNAME'])
        out_files.append(allfiles[it])
        out_objs.append(objname_hdr.strip())
    return np.array(out_files), np.array(out_objs)


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
    tellu_files1 = load_db(MASTERTELLU_FILE, TELLU_KEY1)
    tellu_files2 = load_db(MASTERTELLU_FILE, TELLU_KEY2)

    # load up raw file objnames
    all_raw_filenames, all_raw_objnames = get_raw_files(suffix=RAW_SUFFIX)
    all_pp_filenames, all_pp_objnames = get_pp_files(suffix=PP_SUFFIX)
    all_e2ds_filenames, all_e2ds_objnames = get_e2ds_files(suffix=E2DS_SUFFIX)

    # load up all index files
    ifiles1, itables1 = get_index_files(WORKSPACE0)
    ifiles2, itables2 = get_index_files(WORKSPACE1)

    # storage for numbers
    storage = dict()

    not_found_disk, found_disk, not_found_index, found_index = [], [], [], []

    totals = dict(RAW=0, PPD=0, PPI=0, E2DSD=0, E2DSI=0, TELLOBJ=0, TELLMAP=0,
                  BIGCUBE=0)
    # loop around big cubes
    for objname in wlist:

        # construct bigcube filename
        bigcube_filename = 'BigCube_{0}.fits'.format(objname)

        # find in list
        if len(basefilenames) == 0:
            pos = [0]
        else:
            pos = (bigcube_filename == np.array(basefilenames))

        if np.nansum(pos) > 0:
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

        # find all raw files
        rawmask = all_raw_objnames == objname.strip()
        raw_files = all_raw_filenames[rawmask]

        ppmask = all_pp_objnames == objname.strip()
        pp_disk_files = all_pp_filenames[ppmask]

        e2dsmask = all_e2ds_objnames == objname.strip()
        e2ds_disk_files = all_e2ds_filenames[e2dsmask]

        # find all pp files
        pp_files = find_pp_files(objname, ifiles1, itables1)

        # find all E2DS_AB files
        e2ds_files = find_e2ds_files(objname, ifiles2, itables2)

        # find those in pp and not in e2ds
        eout = compare_pp_e2ds_files(pp_files, e2ds_files)
        e2ds_nfi, e2ds_fi, e2ds_nfd, e2ds_fd = eout

        # find all objects in master tellu that match
        matching_filenames1 = find_matching(objname, tellu_files1)
        matching_filenames2 = find_matching(objname, tellu_files2)
        # add to totals
        totals['RAW'] += len(raw_files)
        totals['PPD'] += len(pp_disk_files)
        totals['PPI'] += len(pp_files)
        totals['BIGCUBE'] += len(bigtable)
        totals['TELLOBJ'] += len(matching_filenames1)
        totals['TELLMAP'] += len(matching_filenames2)
        totals['E2DSI'] += len(e2ds_files)
        totals['E2DSD'] += len(e2ds_disk_files)
        # store in file and print
        pargs = [objname, len(raw_files), len(pp_disk_files), len(pp_files),
                 len(e2ds_disk_files), len(e2ds_files),
                 len(matching_filenames1), len(matching_filenames2),
                 len(bigtable)]
        print('{0:15s}: raw={1:3d} PPD={2:3d} PPI={3:3d} E2DSD={4:3d} '
              'E2DSI={5:3d} TELLMAP={7:3d} TELLOBJ={6:3d} BigCube={8:3d}'
              ''.format(*pargs))
        storage[objname] = pargs[1:]

        not_found_disk += e2ds_nfd
        not_found_index += e2ds_nfi
        found_disk += e2ds_fd
        found_index += e2ds_fi

    totals['tt'] = 'totals'
    print('{tt:15s}: raw={RAW:3d} PPD={PPD:3d} PPI={PPI:3d} E2DSD={E2DSD:3d} '
          'E2DSI={E2DSI:3d} TELLMAP={TELLMAP:3d} TELLOBJ={TELLOBJ:3d} '
          'BigCube={BIGCUBE:3d}'.format(**totals))

# =============================================================================
# End of code
# =============================================================================
