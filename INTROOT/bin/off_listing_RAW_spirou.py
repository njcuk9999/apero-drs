#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
off_listing_RAW_spirou.py [night_directory]

Recipe to display raw frame + cut across orders + statistics

Created on 2017-12-06 at 14:50

@author: cook

Last modified: 2017-12-11 at 15:23

Up-to-date with cal_BADPIX_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os, string
from astropy.io import fits


from SpirouDRS import spirouCDB
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
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p)

    fitsdir=os.path.join(p['DRS_DATA_RAW'],p['ARG_NIGHT_NAME'])
    files = os.listdir(fitsdir)
    files.sort()

#    outfile='listing_'+p['ARG_NIGHT_NAME']+'.txt'
    outfile=p['DRS_DATA_MSG']+'listing_'+os.path.split(p['ARG_NIGHT_NAME'])[-1]+'.txt'
    p = open(outfile, 'w')
    line = 'file\ttype\tdate\tutc\texptime\tcas\tref\tdens\tobjname'
    p.write(line + '\n')
    line = '----\t----\t----\t---\t-------\t---\t---\t----\t------'
    p.write(line + '\n')

    cpt=0

    for filename in files:

        if filename.find('_pp.fits') > 0:
            header = fits.getheader(os.path.join(fitsdir,filename),ext=0)
            exptime=header['EXPTIME']
            cas=header['SBCCAS_P']
            ref=header['SBCREF_P']
            date=header['DATE-OBS']
            utc=header['UTC-OBS']
            obstype=header['OBSTYPE']
            objname=header['OBJNAME']
            dens=header['SBCDEN_P']

            line = filename + '\t' + obstype + '\t' + date + \
           '\t' + utc + '\t' + '%.1f ' %(exptime) + '\t' + cas + '\t' + ref + \
           '\t' + '%.2f' %(dens) + '\t' + objname
            print(line)
            p.write(line+'\n')
            cpt = cpt + 1

    if cpt==0:
        print('No *_pp.fits files')

    p.close()
    print('Listing of directory on file ' + outfile)

    # return a copy of locally defined variables in the memory
#    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
#    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================



