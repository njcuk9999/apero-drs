#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-09-2020-09-04 15:03

@author: cook
"""
from astropy.io import fits
from astropy.time import Time
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
from pytz import timezone


# =============================================================================
# Define variables
# =============================================================================
CALIBDB_PATH = '/scratch3/rali/spirou/data_0_6_131_test/calibDB/'
REDUCED_PATH = '/scratch3/rali/spirou/data_0_6_131_test/reduced/'

# CALIBDB_PATH = '/net/GSP/big_spirou/FULL_REDUCTION_CALIBDB_06129/MINIDATA_06129_older/calibDB/'
# REDUCED_PATH = '/net/GSP/big_spirou/FULL_REDUCTION_CALIBDB_06129/MINIDATA_06129_older/reduced/'

# CALIBDB_PATH = '/net/nas10c/GSP/spirou/MINIDATA_06129_closest/calibDB/'
# REDUCEDPATH = '/net/nas10c/GSP/spirou/MINIDATA_06129_closest/reduced/'

TEXT_PREFIX = '2'
TEXT_SUFFIX = 'o_pp_e2dsff_AB.fits'
CALIB_CACHE = dict()
hawaiitime = timezone('US/Hawaii')

# Type an object name here to filter (ALL CAPITALS PLEASE)
OBJNAME = None
OBJNAME = 'Gl699'

# =============================================================================
# Define classes
# =============================================================================
class DrsFile:
    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.basename(filename)
        self.odocode = self.basename.split(TEXT_SUFFIX)[0]
        self.time = None
        self.objname = None
        self.dark = None
        self.badpix = None
        self.back = None
        self.ordp = None
        self.loc = None
        self.shapel = None
        self.shapex = None
        self.shapey = None
        self.flat = None
        self.blaze = None
        self.therm = None
        self.wave = None

    def load(self, calibs=True):
        # get header
        print('Loading {0}'.format(self.filename))
        hdr = fits.getheader(self.filename)
        # get keys
        self.gettime(hdr)

        if 'DRSOBJN' in hdr:
            self.objname = str(hdr['DRSOBJN']).upper()
        # get calibrations
        if calibs:
            self.dark = self.getcalib('CDBDARK', hdr)
            self.badpix = self.getcalib('CDBBAD', hdr)
            self.back = self.getcalib('CDBBACK', hdr)
            self.ordp = self.getcalib('CDBORDP', hdr)
            self.loc = self.getcalib('CDBLOCO', hdr)
            self.shapel = self.getcalib('CDBSHAPL', hdr)
            self.shapex = self.getcalib('CDBSHAPX', hdr)
            self.shapey = self.getcalib('CDBSHAPY', hdr)
            self.flat = self.getcalib('CDBFLAT', hdr)
            self.blaze = self.getcalib('CDBBLAZE', hdr)
            self.therm = self.getcalib('CDBTHERM', hdr)
            self.wave = self.getcalib('CDBWAVE', hdr)
        # now delete header
        del hdr

    def gettime(self, hdr):
        # get time
        if 'MJDMID' in hdr:
            self.time = Time(hdr['MJDMID'], format='mjd')


    def getcalib(self, key, hdr):
        # step 1: get basename from hdr
        if key in hdr:
            basename = str(hdr[key])
            filename = os.path.join(CALIBDB_PATH, basename)

            if filename == self.filename:
                return None

            if filename in CALIB_CACHE:
                return CALIB_CACHE[filename]
            else:
                if not os.path.exists(filename):
                    CALIB_CACHE[filename] = None
                    return None
                else:
                    calib = DrsFile(filename)
                    calib.load(calibs=False)
                    CALIB_CACHE[filename] = calib
                    return calib
        else:
            return None


def plot_point(frame, it, time1, time2, **kwargs):
    # deal with no time info
    if time1 is None:
        return
    if time2 is None:
        return
    # get time diff in hours
    tdiff = time2.mjd
    # plot
    frame.plot([tdiff], [it], **kwargs)
    frame.plot([tdiff, time1.mjd], [it, it], color='0.5')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":

    # construct glob query
    gquery = os.path.join(REDUCED_PATH, '*', TEXT_PREFIX + '*' + TEXT_SUFFIX)

    # first job find all OBJ_FP and OBJ_DARK e2ds files
    extract_files = glob.glob(gquery)

    # storage of object
    extract_objs = []
    extract_times = []
    # now go through these files and load them (and their calibrations)
    for extract_file in extract_files:
        # construct this instance
        extract_obj = DrsFile(extract_file)
        # load instance
        extract_obj.load()
        # deal with object name filter
        if OBJNAME is not None:
            if isinstance(OBJNAME, str):
                if extract_obj.objname.upper() != OBJNAME.upper():
                    continue
        # push into extract objs
        extract_objs.append(extract_obj)
        extract_times.append(extract_obj.time.mjd)
    # sort by time
    sortmask = np.argsort(extract_times)
    extract_objs = np.array(extract_objs)[sortmask]

    # now plot these points
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)
    # get y axis value
    ypos = np.arange(len(extract_objs)).astype(int)
    ynames = []
    # loop around extraction objects
    for it, eobj in enumerate(extract_objs):
        # plotting
        print('Plotting observation {0}/{1}'.format(it + 1, len(extract_objs)))
        # plot the extract point
        frame.plot([eobj.time.mjd], [ypos[it]], marker='*', color='r',
                   ms=10)
        # plot the dark point
        # plot_point(frame, it, eobj.time, eobj.dark.time, marker='x',
        #            mec='k', mfc='None', label='dark', ls='None')
        # plot the badpix
        plot_point(frame, it, eobj.time, eobj.badpix.time, marker='+',
                   mec='k', mfc='None', label='badpix', ls='None')
        # plot the back
        plot_point(frame, it, eobj.time, eobj.back.time, marker='v',
                   mec='k', mfc='None', label='back', ls='None')
        # plot the ordp
        plot_point(frame, it, eobj.time, eobj.ordp.time, marker='s',
                   mec='b', mfc='None', label='ordp', ls='None')
        # plot the loc
        plot_point(frame, it, eobj.time, eobj.loc.time, marker='^',
                   mec='b', mfc='None', label='loc', ls='None')
        # plot the shapel
        plot_point(frame, it, eobj.time, eobj.shapel.time, marker='o',
                   mec='orange', mfc='None', label='shapel', ls='None')
        # # plot the shapex
        # plot_point(frame, it, eobj.time, eobj.shapex.time, marker='>',
        #            mec='orange', mfc='None', label='shapex', ls='None')
        # # plot the shapey
        # plot_point(frame, it, eobj.time, eobj.shapey.time, marker='<',
        #            mec='orange', mfc='None', label='shapey', ls='None')
        # plot the flat
        plot_point(frame, it, eobj.time, eobj.flat.time, marker='d',
                   mec='purple', mfc='None', label='flat', ls='None')
        # plot the blaze
        plot_point(frame, it, eobj.time, eobj.blaze.time, marker='p',
                   mec='purple', mfc='None', label='blaze', ls='None')
        # plot the therm
        plot_point(frame, it, eobj.time, eobj.therm.time, marker='h',
                   mec='g', mfc='None', label='therm', ls='None')
        # plot the wave
        plot_point(frame, it, eobj.time, eobj.wave.time, marker='.',
                   mec='g', mfc='None', label='wave', ls='None')
        # append
        ynames.append(eobj.odocode)

    # need to sort out legend
    hh, ll = frame.get_legend_handles_labels()
    handles, labels = [], []
    for it, label in enumerate(ll):
        if label not in labels:
            handles.append(hh[it])
            labels.append(ll[it])
    # add legend
    frame.legend(handles, labels, loc=0)

    # change ylabels
    frame.set_yticks(ypos)
    frame.set_yticklabels(ynames)
    # set labels
    frame.set(xlabel='MJDMID',
              ylabel='Odometer code')

    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================
