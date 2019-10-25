#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = core.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck

# =============================================================================
# Define class
# =============================================================================
class PolarObj:
    def __init__(self, **kwargs):
        self.infile = kwargs.get('infile', None)
        self.fiber = kwargs.get('fiber', 'NOFIBER')
        self.exposure = kwargs.get('exposure', 'NAN')
        self.stoke = kwargs.get('stoke', 'NAN')
        self.sequence = kwargs.get('seqs', 'NAN')
        self.sequencetot = kwargs.get('seqtot', 'NAN')
        self.data = kwargs.get('data', None)
        self.filename = kwargs.get('filename', None)
        self.basename = kwargs.get('basename', None)
        # if infile is set, set data from infile
        if self.infile is not None:
            self.data = self.infile.data
            self.filename = self.infile.filename
            self.basename = self.infile.basename
        # set name
        self.name = self.__gen_key__()

    def __gen_key__(self):
        return '{0}_{1}'.format(self.fiber, self.exposure)

    def __str__(self):
        return 'PolarObj[{0}]'.format(self.name)

    def __repr__(self):
        return 'PolarObj[{0}]'.format(self.name)


# =============================================================================
# Define functions
# =============================================================================
def validate_polar_files(params, infiles, **kwargs):
    # set function name
    func_name = display_func(params, 'validate_polar_files', __NAME__)

    # get parameters from params
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # this is a constant and should not be changed
    min_files = 4
    # ----------------------------------------------------------------------
    # right now we can only do this with two fibers - break if more fibers are
    #   defined
    if len(valid_fibers) != min_files // 2:
        eargs = ['({0})'.format(','.join(valid_fibers)), 'POLAR_VALID_FIBERS',
                 func_name]
        WLOG(params, 'error', TextEntry('00-021-00001', args=eargs))
    # ----------------------------------------------------------------------
    # get the number of infiles
    num_files = len(infiles)
    # ----------------------------------------------------------------------
    # storage dictionary
    pobjects = ParamDict()
    stokes, fibers, basenames = [], [] ,[]
    # loop around files
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # extract polar values and validate file
        pout = valid_polar_file(params, infile)
        stoke, exp, seq, seqtot, fiber, valid = pout
        # skip any invalid files
        if not valid:
            continue
        # ------------------------------------------------------------------
        # log file addition
        wargs = [infile.basename, fiber, stoke, exp, seq, seqtot]
        WLOG(params, '', TextEntry('40-021-00001', args=wargs))
        # ------------------------------------------------------------------
        # get polar object for each
        pobj = PolarObj(infile=infile, fiber=fiber, exposure=exp, stoke=stoke,
                        seq=seq, seqtot=seqtot)
        # get name
        name = pobj.name
        # push into storage dictionary
        pobjects[name] = pobj
        # set source
        pobjects.set_source(name, func_name)
        # append lists (for checks)
        stokes.append(stoke)
        fibers.append(fiber)
        basenames.append(infile.basename)
    # ----------------------------------------------------------------------
    # deal with having no files
    if len(pobjects) == 0:
        eargs = ['\n\t'.join(basenames)]
        WLOG(params, 'error', TextEntry('09-021-00001', args=eargs))
    # deal with having less than minimum number of required files
    if len(pobjects) < 4:
        eargs = [4, '\n\t'.join(basenames)]
        WLOG(params, 'error', TextEntry('09-021-00002', args=eargs))
    # ----------------------------------------------------------------------
    # make sure we do not have multiple stokes parameters
    if len(np.unique(stokes)) != 1:
        eargs = [', '.join(np.unique(stokes))]
        WLOG(params, 'error', TextEntry('09-021-00003', args=eargs))
    # ----------------------------------------------------------------------
    # find number of A and B files
    num_a = np.sum(np.array(fibers) == valid_fibers[0])
    num_b = np.sum(np.array(fibers) == valid_fibers[1])
    # make sure we have 2 or 4 A fibers and 2 or 4 B fibers
    if len(fibers) == min_files * 2:
        # make sure number of A and B files is correct length
        if (num_a == min_files) and (num_b == min_files):
            kind = min_files
        else:
            eargs = [valid_fibers[0], valid_fibers[1], num_a, num_b, min_files]
            WLOG(params, 'error', TextEntry('09-021-00004', args=eargs))
            kind = None
    elif len(fibers) == min_files:
        # make sure number of A and B files is correct length
        if (num_a == min_files // 2) and (num_b == min_files // 2):
            kind = min_files // 2
        else:
            eargs = [valid_fibers[0], valid_fibers[1], num_a, num_b,
                     min_files // 2]
            WLOG(params, 'error', TextEntry('09-021-00004', args=eargs))
            kind = None
    else:
        eargs = [valid_fibers[0], valid_fibers[1],
                ' or '.join([str(min_files * 2), str(min_files)])]
        WLOG(params, 'error', TextEntry('09-021-00005', args=eargs))
        kind = None
    # ----------------------------------------------------------------------
    # set the output parameters
    props = ParamDict()
    props['NEXPOSURES'] = kind
    props['STOKES'] = np.unique(stokes)[0]
    props['MIN_FILES'] = min_files
    props['VALID_FIBERS'] = valid_fibers
    props['VALID_STOKES'] = valid_stokes
    # set sources
    keys = ['STOKES', 'NEXPOSURES', 'MIN_FILES', 'VALID_FIBERS', 'VALID_STOKES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return polar object and properties
    return pobjects, props


def valid_polar_file(params, infile, **kwargs):
    """
    Read and extract parameters from cmmtseq string from header key at
    KW_CMMTSEQ

    for spirou the format is as follows:
       {0} exposure {1}, sequence {2} of {3}
     where {0} is the stokes parameter
     where {1} is the exposure number
     where {2} is the sequence number
     where {3} is the total number of sequences

    :param params: ParamDict, the parameter dictionary
    :param infile: DrsFitsFile, the Drs Fits file to get the header key from

    :type params: ParamDict
    :type infile: DrsFitsFile

    :return:
    """
    # set function name
    func_name = display_func(params, 'read_cmmtseq', __NAME__)
    # assume valid at first
    valid = True
    # get values from parameters
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # ----------------------------------------------------------------------
    # get cmmtseq key
    cmmtseq = infile.get_key('KW_CMMTSEQ')
    # get fiber type
    fiber = infile.get_key('KW_FIBER')
    # ----------------------------------------------------------------------
    # deal with bad file
    if cmmtseq in [None, '', 'None']:
        eargs = [params['KW_CMMTSEQ'][0], infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00004', args=eargs))
        return None, None, None, None, fiber, False
    # ----------------------------------------------------------------------
    # split to string by white spaces
    split = cmmtseq.split()
    # ----------------------------------------------------------------------
    # get stokes parameter (first letter)
    stoke_parameter = split[0]
    # ----------------------------------------------------------------------
    # get exposure number
    exposure = split[2].strip(',')
    try:
        exposure = int(exposure)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00001', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the sequence number
    sequence = split[4]
    try:
        sequence = int(sequence)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00002', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the total number of sequences
    total = split[6]
    try:
        total = int(total)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00003', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with fiber type
    if fiber not in valid_fibers:
        eargs = [fiber, ', '.join(valid_fibers), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00005', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with stokes parameters - check parameter is valid
    if stoke_parameter not in valid_stokes:
        eargs = [stoke_parameter, ', '.join(valid_stokes), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00006', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # return extracted parameters
    if not valid:
        return None, None, None, None, fiber, False
    else:
        return stoke_parameter, exposure, sequence, total, fiber, valid




# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
