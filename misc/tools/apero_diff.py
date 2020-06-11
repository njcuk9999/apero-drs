#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code to compare to reductions of APERO

Created on 2020-05-21

@author: cook
"""
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.table import Table

# =============================================================================
# Define variables
# =============================================================================
# workspace for comparison (above reduced/calibDB/telluDB etc)
WORKSPACE1 = '/scratch3/rali/spirou/md_20200603/'
WORKSPACE2 = '/scratch3/LAM/lam_june1/'
# define directories to compare
directories = ['calibDB']
# define fit file suffixes
FITS_SUFFIXES = ['.fits']
# define the percentiles to check
PERCENTILES = [2.5, 16, 50, 84, 97.5]
# define output file
OUTFILE = 'diff-master.fits'
# threshold
THRESHOLD1 = 1.0e-5
THRESHOLD2 = 1.0e-6


# =============================================================================
# Define functions
# =============================================================================
class Comparison:
    def __init__(self, filename1, filename2=None, directory=None):
        # set the directory
        self.directory = directory
        # check that paths exist (formality)
        if not filename1.exists():
            print('File1: {0} not found'.format(filename1))
            self.file1 = None
        else:
            self.file1 = filename1
        # check that paths exist (formality)
        if filename2 is None:
            self.file2 = None
        if not filename2.exists():
            print('File2: {0} not found'.format(filename2))
            self.file2 = None
        else:
            self.file2 = filename2
        # initize stats dictionary
        self.stats = dict()

    def read_files(self):
        # get suffix
        suffix = self.file1.suffix
        # ------------------------------------------------------------------
        if suffix in FITS_SUFFIXES:
            data1, header1, kind1 = read_fits(self.file1)
            data2, header2, kind2 = read_fits(self.file2)
        else:
            data1, header1, kind1 = read_other(self.file1)
            data2, header2, kind2 = read_other(self.file2)
        # ------------------------------------------------------------------
        # deal with kind
        if kind1 != kind2:
            print('WARNING: incompatible kinds: file1 kind={0} file2 kind={1}'
                  ''.format(kind1, kind2))
            kind = None
        else:
            kind = str(kind1)
        # ------------------------------------------------------------------
        # return data
        return data1, data2, header1, header2, kind

    def statistics(self):
        # ------------------------------------------------------------------
        # save file info to stats
        self.stats['DIR'] = str(self.directory)
        # deal with file 1
        if self.file1 is not None:
            self.stats['FILE1'] = str(self.file1.name)
            self.stats['PATH1'] = str(self.file1.parent)
        else:
            self.stats['FILE1'] = 'None'
            self.stats['PATH1'] = 'None'
        # deal with file 2
        if self.file2 is not None:
            self.stats['FILE2'] = str(self.file2.name)
            self.stats['PATH2'] = str(self.file2.parent)
        else:
            self.stats['FILE2'] = 'None'
            self.stats['PATH2'] = 'None'
        # ------------------------------------------------------------------
        # get data
        data1, data2, hdr1, hdr2, kind = self.read_files()
        # get shape
        self.get_shape(data1, kind, 1)
        self.get_shape(data2, kind, 2)
        # get numerical stats
        self.get_numerical(data1, kind, 1)
        self.get_numerical(data2, kind, 2)
        # get diff stats
        self.get_diff_stats(data1, data2, kind)
        # compare headers
        self.get_diff_headers(hdr1, hdr2)
        # ------------------------------------------------------------------
        # clean up variables
        del data1, data2, hdr1, hdr2

    def get_shape(self, data, kind, it=1):
        # set up key
        key = 'SHAPE{0}'.format(it)
        # deal with different kinds
        if kind is None:
            self.stats[key] = 'None'
        elif kind == 'fits-image':
            self.stats[key] = 'x'.join(np.array(data.shape, dtype=str))
        elif kind == 'fits-table':
            shargs = [len(data.colnames), len(data)]
            self.stats[key] = 'NCOLS={0} NROWS{1}'.format(*shargs)
        elif kind == 'other':
            self.stats[key] = 'LINES={0}'.format(len(data))
        else:
            self.stats[key] = 'None'

    def get_numerical(self, data, kind, it=1):
        # set up keys
        indexkey = 'INDEX_{0}'.format(it)
        minkey = 'MIN_{0}'.format(it)
        maxkey = 'MAX_{0}'.format(it)
        stdkey = 'STD_{0}'.format(it)
        meankey = 'MEAN_{0}'.format(it)
        medkey = 'MEDIAN_{0}'.format(it)
        nnankey = 'NUM_NAN_{0}'.format(it)
        ntotkey = 'N_TOT_{0}'.format(it)
        # add percentile keys
        pkeys = []
        for percentile in PERCENTILES:
            # can't have decimals
            strp = str(percentile).replace('.', '_')
            # add percentile key
            pkeys.append('P{0}_{1}'.format(strp, it))
        # ------------------------------------------------------------------
        # access data - for fits image we take the whole image
        if kind == 'fits-image':
            values, index = np.array(data), None
        # access data - for table we need to find a column of numbers
        elif kind == 'fits-table':
            values, index = find_numerical_col(data)
        # else values is None
        else:
            values, index = None, None
        # ------------------------------------------------------------------
        # populate values
        if values is not None:
            self.stats[indexkey] = str(index)
            self.stats[minkey] = np.nanmin(values)
            self.stats[maxkey] = np.nanmax(values)
            self.stats[stdkey] = np.nanstd(values)
            self.stats[meankey] = np.nanmean(values)
            self.stats[medkey] = np.nanmedian(values)
            self.stats[nnankey] = np.sum(np.isnan(values))
            # deal with number of total pixels
            if index is not None:
                self.stats[ntotkey] = len(values)
            else:
                self.stats[ntotkey] = np.product(values.shape)
            # deal with percentiles
            for p_it, percentile in enumerate(PERCENTILES):
                pkey = pkeys[p_it]
                self.stats[pkey] = np.nanpercentile(values, percentile)
        # ------------------------------------------------------------------
        # else fill in the None values
        else:
            self.stats[indexkey] = 'None'
            self.stats[minkey] = np.nan
            self.stats[maxkey] = np.nan
            self.stats[stdkey] = np.nan
            self.stats[meankey] = np.nan
            self.stats[medkey] = np.nan
            self.stats[nnankey] = np.nan
            self.stats[ntotkey] = np.nan
            # deal with percentiles
            for p_it, percentile in enumerate(PERCENTILES):
                pkey = pkeys[p_it]
                self.stats[pkey] = np.nan
        # ------------------------------------------------------------------
        # clean values
        del values

    def get_diff_stats(self, data1, data2, kind):
        # set up keys
        n95key = 'NORM95'
        rmsdkey = 'RMS_DEV_NORM95'
        maxdkey = 'MAX_DEV_NORM95'
        frackey = 'FRAC_IDENTICAL'
        rt1 = 'RMS_THRES_1'
        rt2 = 'RMS_THRES_2'
        mt1 = 'MAX_THRES_1'
        mt2 = 'MAX_THRES_2'
        # ------------------------------------------------------------------
        # access data - for fits image we take the whole image
        if kind == 'fits-image':
            values1, index1 = np.array(data1), None
            values2, index2 = np.array(data2), None
        # access data - for table we need to find a column of numbers
        elif kind == 'fits-table':
            values1, index1 = find_numerical_col(data1)
            values2, index2 = find_numerical_col(data2)
        # else values is None
        else:
            values1, index1 = None, None
            values2, index2 = None, None
        # ------------------------------------------------------------------
        # populate values
        if (values1 is not None) and (values2 is not None):
            # calculate norm95 and diff image
            norm95 = np.nanpercentile((values1 + values2)/2, 95)
            diff_image = values1 - values2
            # calculate stats
            rmsd = np.nanstd(diff_image) / norm95
            maxd = np.nanmax(np.abs(diff_image)) / norm95
            # populate states
            self.stats[n95key] = norm95
            self.stats[rmsdkey] = rmsd
            self.stats[maxdkey] = maxd
            self.stats[frackey] = np.mean(values1 == values2)
            self.stats[rt1] = float(rmsd < THRESHOLD1)
            self.stats[rt2] = float(rmsd < THRESHOLD2)
            self.stats[mt1] = float(maxd < THRESHOLD1)
            self.stats[mt2] = float(maxd < THRESHOLD2)
        # ------------------------------------------------------------------
        # else fill in the None values
        else:
            self.stats[n95key] = np.nan
            self.stats[rmsdkey] = np.nan
            self.stats[maxdkey] = np.nan
            self.stats[frackey] = np.nan
            self.stats[rt1] = np.nan
            self.stats[rt2] = np.nan
            self.stats[mt1] = np.nan
            self.stats[mt2] = np.nan

    def get_diff_headers(self, header1, header2):

        # define keys
        hdrckey = 'HEADER_COUNT'
        hdrmkey = 'HEADER_MISSING'
        hdrdkey = 'HEADER_DIFFERENT'
        # check data type of headers
        cond1 = isinstance(header1, fits.Header)
        cond2 = isinstance(header2, fits.Header)
        # if both header1 and header2 are astropy.headers
        if cond1 and cond2:
            # start counter for not found
            count = 0
            missing = []
            different = []
            # loop through header 1 keys
            for key in list(header1.keys()):
                # look for key in header 2
                if key not in list(header2.keys()):
                    # add to the count and add to missing keys
                    count += 1
                    missing.append(key)
                else:
                    # add to value
                    value1 = header1[key]
                    value2 = header2[key]
                    # if value
                    if value1 != value2:
                        count += 1
                        different.append(key)
            # now just check we didn't miss any keys in header2
            for key in list(header2.keys()):
                # skip keys in header1
                if key in list(header1.keys()):
                    continue
                # add key to count and missing keys
                count += 1
                missing.append(key)
            # now add to stats
            self.stats[hdrckey] = count
            self.stats[hdrmkey] = ', '.join(missing)
            self.stats[hdrdkey] = ', '.join(different)
        # else set them to None
        else:
            self.stats[hdrckey] = np.nan
            self.stats[hdrmkey] = ''
            self.stats[hdrdkey] = ''


def read_fits(filename):
    """
    read a fits file (after finding out type)
    """
    # deal with filename being unset
    if filename is None:
        return None, None, None

    # load data 1
    try:
        hdulist = fits.open(filename)
        # deal with no hdus present
        if len(hdulist) == 0:
            print('WARNING: Fits file empty: {0}'.format(filename))
            return None, None, None
        elif len(hdulist) == 1:
            if isinstance(hdulist[0], fits.hdu.image.PrimaryHDU):
                return hdulist[0].data, hdulist[0].header, 'fits-image'
        else:
            # deal with table (ext=1 for data and header)
            if hdulist[0].data is None:
                if isinstance(hdulist[1], fits.hdu.table.BinTableHDU):
                    try:
                        data = Table.read(filename)
                        header = hdulist[1].header
                        return data, header, 'fits-table'
                    except Exception as e:
                        print('WARNING: Fits table broken: {0}'
                              ''.format(filename))
                        return None, None, None
                else:
                    return hdulist[1].data, hdulist[1].header, 'fits-image'
            else:
                return hdulist[0].data, hdulist[0].header, 'fits-image'
    except Exception as e:
        print('WARNING: cannot read fits file: {0}'.format(filename))
        return None, None, None


def read_other(filename):
    """
    If not a fits file assume we can read with as text file
    :return:
    """
    # deal with filename being unset
    if filename is None:
        return None, None, None
    # try to read lines of text file
    try:
        with open(filename, 'r') as file1:
            data = file1.readlines()
        return data, None, 'other'
    except Exception as e:
        print('WARNING: cannot read other file: {0}'.format(filename))
        return None, None, None


def find_numerical_col(table):
    # only for astropy.table.Table instances
    if isinstance(table, Table):
        # loop through columns
        for col in table.colnames:
            # if values are a float use this column
            if isinstance(table[col][0], float):
                return np.array(table[col]), col
    # in all other cases return None, None
    return None, None


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get workspaces
    path1 = Path(WORKSPACE1)
    path2 = Path(WORKSPACE2)
    # loop around directories
    for directory in directories:
        # ------------------------------------------------------------------
        # storage dictionary
        comparisons = []
        # ------------------------------------------------------------------
        # get the full directory path
        directory1 = path1.joinpath(directory)
        directory2 = path2.joinpath(directory)
        # get the list of all files
        all_files1 = np.sort(list(directory1.glob('*')))
        all_files2 = np.sort(list(directory2.glob('*')))
        # index file base names
        names1 = list(map(lambda x: x.name, all_files1))
        names2 = list(map(lambda x: x.name, all_files2))
        # ------------------------------------------------------------------
        # loop around files and match files
        for f_it, basename1 in enumerate(names1):
            # print progress
            fargs = [f_it + 1, len(names1), basename1]
            print('Matching file {0} of {1} ({2})'.format(*fargs))
            # deal with not finding the same file
            if basename1 not in names2:
                # construct with empty path2
                comp = Comparison(all_files1[f_it], None, directory=directory)
                # append to list
                comparisons.append(comp)
            # else add both files
            else:
                # construct with both paths
                comp = Comparison(all_files1[f_it], all_files2[f_it],
                                  directory=directory)
                # append to list
                comparisons.append(comp)
        # ------------------------------------------------------------------
        # storage dictionary (for outputs)
        table_dict = dict()
        # loop around and get stats
        for c_it, comp in enumerate(comparisons):
            # print progress
            cargs = [c_it + 1, len(comparisons), comp.file1.name]
            print('Processing {0}/{1} ({2})'.format(*cargs))
            # compile the statistics
            comp.statistics()
            # propagate stats to output dictionary
            for key in list(comp.stats.keys()):
                if key not in table_dict:
                    # add to table dict
                    table_dict[key] = [comp.stats[key]]
                else:
                    table_dict[key].append(comp.stats[key])
        # ------------------------------------------------------------------
        # now push table dict into a table
        table = Table()
        for key in list(table_dict.keys()):
            table[key] = np.array(table_dict[key])
        # save table
        table.write(OUTFILE, overwrite=True)


# =============================================================================
# End of code
# =============================================================================
