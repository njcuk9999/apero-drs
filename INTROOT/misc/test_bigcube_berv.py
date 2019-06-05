#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-18 at 10:46

@author: cook
"""
from astropy.io import fits
import numpy as np
import os
import matplotlib.pyplot as plt


# =============================================================================
# Define variables
# =============================================================================
workspace = '/spirou/cfht_nights/mtl/reduced/2018-09-24'
filename = 'BigCube_Gl699.fits'
filestore = '/spirou/cfht_nights/mtl/telluDB/'
OBJNAME = 'Gl699'

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def convert_to_array(headerlist, header_prefix, dtype=float):
    if dtype == float:
        empty = np.nan
    elif dtype == int:
        empty = -1
    elif dtype == str:
        empty = ' ' * 100
    else:
        raise ValueError('Dtype {0} not supported'.format(dtype))

    dictlist = dict(headerlist)

    keys = np.repeat(np.nan, len(headerlist))
    values = np.repeat(empty, len(headerlist))
    for key in dictlist.keys():
        # get the index from the header prefix
        index = int(key.split(header_prefix)[-1])
        # push into correct location in values
        values[index] = dictlist[key]

    # return values
    return values


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':

    print('Loading BigCube file...')
    path = os.path.join(workspace, filename)

    header = fits.getheader(path)

    rawfiles = header['INA*']
    rawbervs = header['INB*']

    # get actual list in correct order
    files = convert_to_array(rawfiles, 'INA', dtype=str)
    bervs = convert_to_array(rawbervs, 'INB', dtype=float)

    # convert files to odocodes
    odocodes = []
    for filename in files:
        try:
            odocodes.append(int(filename.split('o')[0]))
        except Exception as _:
            odocodes.append(-1)
    odocodes = np.array(odocodes, dtype=int)

    # mask odocodes to filter missing columns
    mask = np.array(odocodes) == -1
    odocodes = odocodes[~mask]
    bervs = bervs[~mask]
    files = files[~mask]

    # sort by odocode
    sortmask = np.argsort(odocodes)
    odocodes = odocodes[sortmask]
    bervs = bervs[sortmask]

    # get actual BERVS and MJDATE from headers of files
    fberv, fmjdate, fobjname = [], [], []

    for it, filename in enumerate(files):
        print('Reading file {0} of {1}'.format(it + 1, len(files)))
        fpath = os.path.join(filestore, filename)
        if os.path.exists(fpath):
            fhdr = fits.getheader(fpath)

            if np.isnan(float(fhdr['BERV'])):
                berv = float(fhdr['BERV_EST'])
            else:
                berv = float(fhdr['BERV'])

            fberv.append(berv)
            fmjdate.append(float(fhdr['MJDATE']))
            fobjname.append(str(fhdr['OBJNAME']))
        else:
            fberv.append(np.nan)
            fmjdate.append(np.nan)
            fobjname.append('')
    fberv = np.array(fberv)
    fmjdate = np.array(fmjdate)
    fobjname = np.array(fobjname)

    # filter by objectname
    mask = fobjname == OBJNAME

    odocodes = odocodes[mask]
    bervs = bervs[mask]
    fberv = fberv[mask]
    fmjdate = fmjdate[mask]
    fobjname = fobjname[mask]

    plt.close()
    fig, frames = plt.subplots(ncols=2, nrows=1)

    # plot bervs from big cube header
    frames[0].plot(odocodes, bervs, color='k', marker='o', linestyle='None')
    frames[0].set(xlabel='Obs Number (sorted by odometer code)',
                  ylabel='BERV from BigCube header')

    frames[1].plot(fmjdate, fberv, color='r', marker='o', linestyle='None')
    frames[1].set(xlabel='MJDATE from individual file headers',
                  ylabel='BERV from individual file headers')

    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================
