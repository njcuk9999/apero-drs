#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-17 10:56

@author: cook
"""
from multiprocessing import Pool, Process, Manager, Event
import numpy as np
import time

from astropy.time import Time
from test_calibdb import Database, CALIB_DB_PATH

# =============================================================================
# Define variables
# =============================================================================
CORES = 10
RUNS = 50
TRIES = 1
PATH = './testdb.db'
TABLE = 'MAIN'
COLUMNS = ['KEY', 'SUPER', 'DIRS', 'FILES', 'ISO', 'UNIX']
CTYPES = [str, int, str, str, str, float]
# max wait time in ms
WAIT_TIME = 1

# =============================================================================
# Define functions
# =============================================================================
class MyDatabaseError(Exception):
    pass


def connect_to_database(idcode, path=None):
    if path is None:
        path = CALIB_DB_PATH
    pargs = [idcode, path]
    print('{0} | DATABASE | Starting database from file {1}'.format(*pargs))
    # create database
    try:
        database = Database(path)
    except Exception as e:
        message = 'DATABASE ERROR {0}->{1}: {2}'
        raise MyDatabaseError(message.format(idcode, type(e), e))

    # add table is required
    if TABLE not in database.tables:
        pargs = [idcode, TABLE]
        print('{0} | DATABASE | Adding table {1}'.format(*pargs))
        try:
            database.add_table(TABLE, COLUMNS, CTYPES)
        except Exception as e:
            message = 'ADD TABLE ERROR {0}->{1}: {2}'
            raise MyDatabaseError(message.format(idcode, type(e), e))
    return database


def sim_code(idcode, return_dict):
    """
    Simulation of a true code
    1. connects to database
    2. randomly chooses to read or write "TRIES" times
    3. prints output to screen

    :param idcode: string, the id of the multiprocess process
    :return:
    """
    # start database
    database = connect_to_database(idcode, PATH)
    # decide whether we are reading or writing
    kind = np.random.choice([0, 1])
    # if we are writing
    if kind == 0:
        # loop around
        for it in range(TRIES):
            # get start time
            start = time.time()
            # make some fake keys
            key = idcode
            super_key = 0
            directory = 'None'
            filename = '{0}_{1}_test.fits'.format(idcode, it)
            iso_time = Time.now().iso
            unix_time = Time.now().unix
            values = [key, super_key, directory, filename, iso_time, unix_time]
            # add some entries
            database.add_row(values, table=TABLE)
            # get end time
            end = time.time()
            # print progress
            pargs = [idcode, it, end - start]
            print('{0} | WRITE | Iteration={1} Time={2:.3e} s'.format(*pargs))
        # get all entries
        entries = database.get(table=TABLE, return_pandas=True)
        # add outputs
        return_dict[idcode] = ['WRITE', len(entries), entries, Time.now().iso]
    # if we are reading
    else:
        entries = []
        # loop around
        for it in range(TRIES):
            # get entires
            start = time.time()
            entries = database.get(table=TABLE, return_pandas=True)
            end = time.time()
            # print number of entries
            pargs = [idcode, it, len(entries), end - start]
            pmsg = ('{0} | READ  | Iteration={1} Number Entries={2} '
                    'Time={3:.3e} s')
            print(pmsg.format(*pargs))
        # add outputs
        return_dict[idcode] = ['READ', len(entries), entries, Time.now().iso]
    # return the output array
    return return_dict


def run():
    # start process manager
    manager = Manager()
    event = manager.Event()
    return_dict = manager.dict()
    # get ids
    ids = list(map(lambda x: 'ID{0:05d}'.format(x), range(RUNS)))
    # list of params for each entry
    params_per_process = []
    # populate params for each sub group
    for it in range(len(ids)):
        args = [ids[it], return_dict]
        params_per_process.append(args)
    # start parallel jobs
    print('Pool started: {0}'.format(Time.now().iso))
    pool = Pool(CORES)
    pool.starmap(sim_code, params_per_process)
    print('Pool ended'.format(Time.now().iso))

    return return_dict


def count(entry):
    df = entry[2]
    countarr = df.groupby('KEY').count()
    firstcol = countarr.columns[0]
    return countarr[firstcol]



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":

    margs = [RUNS, CORES]
    print('Starting {0} RUNS on {1} CORES'.format(*margs))


    rdict = run()

    print('{0} RUNS on {1} CORES'.format(*margs))

    for entry in rdict:
        rentry = rdict[entry]
        msg = '{0} {1:5s} length={2:3d} time={3}'
        print(msg.format(entry, rentry[0], rentry[1], rentry[3]))



# =============================================================================
# End of code
# =============================================================================
