#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-15 14:27
@author: ncook
Version 0.0.1
"""
import os
import numpy as np


# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/cook/runs1/'
SEED_FILE = WORKSPACE + 'fp_hc1_list.txt'
TRANSLATION_FILE = WORKSPACE + 'messy2tidy.dat'

OUTNAME = 'full_run2.run'

RAW_PATH = '/spirou/cfht_nights/common/raw/'
TMP_PATH = '/spirou/cfht_nights/common/tmp/'
OUT_PATH = '/spirou/cfht_nights/cfht/reduced_1/'

FP_RAWFILE_EXT = 'a.fits'
HC_RAWFILE_EXT = 'c.fits'
FP_PPFILE_EXT = 'a_pp.fits'
HC_PPFILE_EXT = 'c_pp.fits'


FORCE_PP = False
FORCE_E2DS = False
FORCE_HC = False
FORCE_WAVE = True
# -----------------------------------------------------------------------------

ERRORS = []
RUNSTRING = []
RUNCOUNT = 0

# =============================================================================
# Define functions
# =============================================================================
def read_seed_file_list(seedfile):

    # open file
    f = open(seedfile, 'r')
    lines = f.readlines()
    f.close()
    # storage for valid lines
    runs = dict()
    # loop around lines and extract info
    for line in lines:
        # see if this is an FP line
        if (FP_PPFILE_EXT in line) or (HC_PPFILE_EXT in line):
            name = 'run{0:04d}'.format(int(line.split()[0]))
            if name in runs:
                runs[name].append(line.split())
            else:
                runs[name] = [line.split()]
        # else skip
        else:
            continue
    # return runs
    return runs


def read_translation_file(filename):
    # open file
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    # get translation
    before, after = [], []
    for line in lines:
        before_it, after_it = line.split()
        before.append(before_it)
        after.append(after_it)

    return before, after


def translate_seed_list(runs, trans1, trans2):
    newrun = dict()
    # loop around runs
    for runname in runs.keys():
        # loop around lines in run
        for line in runs[runname]:
            # get nightname and files
            night_name = line[1]
            files = line[2:]
            # outputs for this run
            newfiles = []
            new_night_name = None
            # loop around files to try to find them in translation
            for filename in files:
                # get new absolute path
                newabspath = get_translation_path(line, filename, trans1, trans2)

                if newabspath is None:
                    continue
                # get new night name
                newnightname = os.path.dirname(newabspath)
                newfilename = os.path.basename(newabspath)
                # check that night name is consistent
                if new_night_name is not None:
                    if newnightname != new_night_name:
                        margs = [newabspath, newnightname, new_night_name]
                        message = ('Error run files in different directory '
                                   'for file {0} ({1} and {2})'
                                   ''.format(*margs))
                        print(message)
                        continue
                else:
                    new_night_name = str(newnightname)
                # update newfiles
                newfiles.append(newfilename)

            # do no append if night name missing
            if new_night_name is None:
                continue
            # append to new list
            if runname in newrun:
                newrun[runname].append([new_night_name] + newfiles)
            else:
                newrun[runname] = [[new_night_name] + newfiles]
    # return new run
    return newrun


def get_translation_path(line, filename, t1, t2):

    nightname = line[1]

    filename = filename.replace('_pp.fits', '.fits')

    # loop around translations
    for it in range(len(t1)):
        # if we have an AT5 file then
        if nightname.startswith('AT5'):
            # get the unique dir name
            directory = nightname.split('/')[2]
            # if directory and filename in translation line we have
            #   found the translation
            if directory in t1[it] and filename in t1[it]:
                return t2[it]
        else:
            # if not just look for the file name
            if filename in t1[it]:
                return t2[it]
    # if we reach this point we do not have this file
    message = ('Error cannot translate file={0}'
               ''.format(os.path.join(nightname, filename)))
    print(message)

    global ERRORS
    emsg = 'INPUT FILE NOT FOUND: {0}'.format(os.path.join(nightname, filename))
    ERRORS.append(emsg)

    return None


def remove_raw_path(runs):

    for runname in runs.keys():

        for it in range(len(runs[runname])):
            runs[runname][it][0] = runs[runname][it][0].replace(RAW_PATH, '')
    return runs


def look_for_files(runs):

    gotraw, gotpp, gote2ds, gotwave = dict(), dict(), dict(), dict()

    for runname in runs.keys():
        gotraw[runname] = [[]] * len(runs[runname])
        gotpp[runname] = [[]] * len(runs[runname])
        gote2ds[runname] = [[]] * len(runs[runname])
        gotwave[runname] = [[]] * len(runs[runname])

        for it in range(len(runs[runname])):
            # get night name and filenames
            night_name = runs[runname][it][0]
            files = runs[runname][it][1:]

            gotraw[runname][it] = [night_name]
            gotpp[runname][it] = [night_name]
            gote2ds[runname][it] = [night_name]
            gotwave[runname][it] = [night_name]

            for filename in files:
                # construct filename
                rawfile = filename
                ppfile = filename.replace('.fits', '_pp.fits')
                e2dsfileAB = filename.replace('.fits', '_pp_e2ds_AB.fits')
                e2dsfileC = filename.replace('.fits', '_pp_e2ds_C.fits')
                wavefileAB = filename.replace('.fits', '_pp_wave_ea_AB.fits')
                wavefileC = filename.replace('.fits', '_pp_wave_ea_C.fits')

                # construct paths
                rawpath = os.path.join(RAW_PATH, night_name, rawfile)
                pppath = os.path.join(TMP_PATH, night_name, ppfile)
                e2dspathAB = os.path.join(OUT_PATH, night_name, e2dsfileAB)
                e2dspathC = os.path.join(OUT_PATH, night_name, e2dsfileC)
                wavepathAB = os.path.join(OUT_PATH, night_name, wavefileAB)
                wavepathC = os.path.join(OUT_PATH, night_name, wavefileC)
                # look for raw file
                if os.path.exists(rawpath):
                    gotraw[runname][it].append(True)
                else:
                    gotraw[runname][it].append(False)
                # look for pp file
                if os.path.exists(pppath):
                    gotpp[runname][it].append(True)
                else:
                    gotpp[runname][it].append(False)
                # look for e2ds file
                if os.path.exists(e2dspathAB) and os.path.exists(e2dspathC):
                    gote2ds[runname][it].append(True)
                else:
                    gote2ds[runname][it].append(False)
                # look for wave file
                if os.path.exists(wavepathAB) and os.path.exists(wavepathC):
                    gotwave[runname][it].append(True)
                else:
                    gotwave[runname][it].append(False)

    return gotraw, gotpp, gote2ds, gotwave


def deal_with_raw_files(runs, got):
    global ERRORS
    for runname in runs.keys():
        for rit in range(len(runs[runname])):
            # get files
            nightname = runs[runname][rit][0]
            files = runs[runname][rit][1:]
            gotfiles = got[runname][rit][1:]

            for fit in range(len(files)):
                if not gotfiles[fit]:
                    eargs = [os.path.join(nightname, files[fit])]
                    emsg = 'RAW FILE NOT FOUND: {0}'.format(*eargs)
                    ERRORS.append(emsg)

def deal_with_pp_files(runs, got):
    global RUNSTRING
    global RUNCOUNT
    recipe = 'cal_preprocess_spirou'
    for runname in runs.keys():
        for rit in range(len(runs[runname])):
            # get files
            nightname = runs[runname][rit][0]
            files = runs[runname][rit][1:]
            gotfiles = got[runname][rit][1:]

            for fit in range(len(files)):
                runstring = 'run{0:04d}'.format(int(RUNCOUNT))
                args1 = [runstring, recipe, nightname]
                string1 = "{0} = ['{1}', '{2}',".format(*args1)
                if not gotfiles[fit] or FORCE_PP:
                    rstring = string1 + " '{0}']\n".format(files[fit])
                    RUNSTRING.append(rstring)
                    RUNCOUNT += 1

def deal_with_e2ds_files(runs, got):
    global RUNSTRING
    global RUNCOUNT
    recipe = 'cal_extract_RAW_spirou'
    for runname in runs.keys():
        for rit in range(len(runs[runname])):
            # get files
            nightname = runs[runname][rit][0]
            files = runs[runname][rit][1:]
            gotfiles = got[runname][rit][1:]

            for fit in range(len(files)):
                if not gotfiles[fit] or FORCE_E2DS:
                    runstring = 'run{0:04d}'.format(int(RUNCOUNT))
                    args1 = [runstring, recipe, nightname]
                    string1 = "{0} = ['{1}', '{2}',".format(*args1)
                    ppfile = files[fit].replace('.fits', '_pp.fits')
                    rstring = string1 + " '{0}']\n".format(ppfile)
                    RUNSTRING.append(rstring)
                    RUNCOUNT += 1


def deal_with_hc_files(runs, got):
    global RUNSTRING
    global RUNCOUNT

    recipe = 'cal_HC_E2DS_EA_spirou'
    for runname in runs.keys():
        for rit in range(len(runs[runname])):
            # get files
            nightname = runs[runname][rit][0]
            files = runs[runname][rit][1:]
            gotfiles = got[runname][rit][1:]
            # make sure all files are valid
            valid = True
            for fit in range(len(files)):
                valid &= HC_RAWFILE_EXT in files[fit]
            # skip if not all hc files
            if not valid:
                continue

            # add to run string
            runstring = 'run{0:04d}'.format(int(RUNCOUNT))
            args1 = [runstring, recipe, nightname]
            string1 = "{0} = ['{1}', '{2}',".format(*args1)

            liststring1, liststring2 = [], []
            for fit in range(len(files)):
                if not gotfiles[fit] or FORCE_WAVE:
                    outfileAB = files[fit].replace('.fits', '_pp_e2ds_AB.fits')
                    outfileC = files[fit].replace('.fits', '_pp_e2ds_C.fits')
                    liststring1.append("'{0}'".format(outfileAB))
                    liststring2.append("'{0}'".format(outfileC))

            rstring = string1 + ', '.join(liststring1) + "]\n"
            RUNSTRING.append(rstring)
            RUNCOUNT += 1

            # add to run string
            runstring = 'run{0:04d}'.format(int(RUNCOUNT))
            args1 = [runstring, recipe, nightname]
            string1 = "{0} = ['{1}', '{2}',".format(*args1)
            rstring = string1 + ', '.join(liststring2) + "]\n"
            RUNSTRING.append(rstring)
            RUNCOUNT += 1


def deal_with_wave_files(runs, got):
    global RUNSTRING
    global RUNCOUNT
    recipe = 'cal_WAVE_E2DS_EA_spirou'
    for runname in runs.keys():

        # get files (1 fp file + all hc files)
        nightname = runs[runname][0][0]
        gotfiles = got[runname][0][1:]
        try:
            fpfiles = runs[runname][0][1:]
            hcfiles = runs[runname][1][1:]
            files = [fpfiles[0]] + hcfiles
        except:
            print('\tError with run {0}'.format(runname))
            continue

        if not (not gotfiles[0] or FORCE_WAVE):
            continue

        runstring = 'run{0:04d}'.format(int(RUNCOUNT))
        args1 = [runstring, recipe, nightname]
        string1 = "{0} = ['{1}', '{2}',".format(*args1)

        liststring1, liststring2 = [], []
        for fit in range(len(files)):
            outfileAB = files[fit].replace('.fits', '_pp_AB.fits')
            outfileC = files[fit].replace('.fits', '_pp_C.fits')
            liststring1.append("'{0}'".format(outfileAB))
            liststring2.append("'{0}'".format(outfileC))

        rstring = string1 + ', '.join(liststring1) + "]\n"
        RUNSTRING.append(rstring)
        RUNCOUNT += 1

        runstring = 'run{0:04d}'.format(int(RUNCOUNT))
        args1 = [runstring, recipe, nightname]
        string1 = "{0} = ['{1}', '{2}',".format(*args1)
        rstring = string1 + ', '.join(liststring2) + "]\n"
        RUNSTRING.append(rstring)
        RUNCOUNT += 1


def write_to_file(filename, liststring):
    f = open(filename, 'w')
    f.writelines(liststring)
    f.close()



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Read seed file list
    print('Reading SEED file list...')
    rawruns = read_seed_file_list(SEED_FILE)
    # read translation file
    print('Reading Translator file...')
    trans_before, trans_after = read_translation_file(TRANSLATION_FILE)
    # Translate these into mtl file system
    print('Translating SEED file list...')
    mtlruns = translate_seed_list(rawruns, trans_before, trans_after)
    # remove the raw path from the night names
    print('Removing RAW path from night names...')
    mtlruns = remove_raw_path(mtlruns)
    # look for the files (raw/pp/reduced)
    print('Looking for RAW/PP/OUT files...')
    gotruns = look_for_files(mtlruns)
    # deal with raw files
    print('Dealing with RAW files...')
    deal_with_raw_files(mtlruns, gotruns[0])
    # deal with pp files
    print('Dealing with PP files...')
    deal_with_pp_files(mtlruns, gotruns[1])
    # deal with e2ds files
    print('Dealing with E2DS files...')
    deal_with_e2ds_files(mtlruns, gotruns[2])
    # deal with hc files
    print('Dealing with HC files...')
    deal_with_hc_files(mtlruns, gotruns[3])
    # deal with wave files
    print('Dealing with WAVE files...')
    deal_with_wave_files(mtlruns, gotruns[3])
    # writing to file
    print('Writing to file {0}'.format(OUTNAME))
    write_to_file(OUTNAME, RUNSTRING)


# =============================================================================
# End of code
# =============================================================================