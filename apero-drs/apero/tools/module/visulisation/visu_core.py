#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-22

@author: cook
"""
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore import drs_lang
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_misc
from apero.core import drs_database
from aperocore.core import drs_log
from apero.instruments.default import instrument as instrument_mod
from apero.utils import drs_recipe
from apero.io import drs_fits
from apero.core import drs_file
from apero.base import base as apero_base
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.visulisation.visu_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get params
PARAMS = load_functions.load_config(select.INSTRUMENTS)
# Get Logging function
WLOG = drs_log.wlog
# get parameter dictionary
ParamDict = param_functions.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
Instrument = instrument_mod.Instrument
# get display func
display_func = drs_misc.display_func
# Get the text types
textentry = drs_lang.textentry
# get tqdm (if required)
tqdm = base.tqdm_module()
# Define reference prefix
REF_PREFIX = 'REF_'
# Define the gaia drs column in database
GAIA_COL = 'GAIADR2ID'

# define the bokeh python file template
PYTEMPLATE = """
from bokeh.io import curdoc
from apero.tools.module.visulisation import visu_plots

func = getattr(visu_plots, '{func}')

kwargs = dict({kwargs})

root = func(**kwargs)

curdoc().add_root(root)
curdoc().title = '{title}'
"""
# Define allowed types
ValidTypes = Union[int, float, str, bool]


# =============================================================================
# Define general functions
# =============================================================================
class BokehPlot:
    def __init__(self, params: ParamDict, func_name: str, path: str,
                 title: str) -> None:
        """Initialize a Bokeh plot script configuration.

        :param params: APERO parameters used by this plot configuration.
        :param func_name: Plotting function to call from the generated script.
        :param path: Destination path for the proxy Python script.
        :param title: Title assigned to the Bokeh document.
        :return: None. Stores the script configuration.
        """
        self.params = params
        self.func = func_name
        self.path = path
        self.title = title

    def create(self, kwargs: Optional[Dict[str, Any]] = None) -> None:
        """
        Write the proxy Python script used to launch the Bokeh plot.

        :param kwargs: Optional keyword values passed to the plotting function.
        :return: None. Writes the generated script to ``self.path``.
        """
        # push into dictionary
        fkwargs = dict()
        fkwargs['func'] = str(self.func)
        fkwargs['title'] = str(self.title)
        fkwargs['kwargs'] = self.add_kwargs(kwargs)
        # write to file
        with open(self.path, 'w') as pyfile:
            pyfile.write(PYTEMPLATE.format(**fkwargs))

    def run(self) -> None:
        """
        Start a Bokeh server for the generated proxy script.

        :return: None. Launches ``bokeh serve --show`` for ``self.path``.
        """
        # run an interactive session
        os.system('bokeh serve --show {0}'.format(self.path))

    def add_kwargs(self, kwargs: Optional[Dict[str, ValidTypes]] = None) -> str:
        """
        Add keyword arguments (int/float/bool/str) in string form - for passing
        to our script

        :param kwargs: list of keyword arguments
        :return:
        """
        # deal with no keyword arguments --> empty string
        if kwargs is None:
            return ''
        # set up return storage
        strargs = []
        # loop around arguments and try to cast into string
        for key in kwargs:
            # get value
            value = kwargs[key]
            # -----------------------------------------------------------------
            # deal with strings
            if isinstance(value, str):
                strargs.append('{0}="{1}"'.format(key, kwargs[key]))
                continue
            # -----------------------------------------------------------------
            # deal with others
            # noinspection PyBroadException
            try:
                strarg = '{0}={1}'.format(key, str(kwargs[key]))
                # test as dictionary entry
                _ = eval('dict({0})'.format(strarg))
                # append to str args
                strargs.append(strarg)
            except Exception as _:
                eargs = [key, str(kwargs[key])]
                # error: Cannot convert keyword {0}={1} to string
                WLOG(self.params, 'error',
                     textentry('09-511-00002', args=eargs))
        # join into string string
        fullstring = ', '.join(strargs)
        # return cleaned string
        return fullstring


def check_arg(func_name: str, kwargs: Dict[str, Any], key: str,
              dtype: Any, required: bool = True) -> Any:
    """Validate and convert one required or optional plotting argument.

    :param func_name: Name used to identify the calling plotting function.
    :param kwargs: Keyword arguments supplied to that function.
    :param key: Argument name to read and convert.
    :param dtype: Callable used to convert the argument value.
    :param required: Whether a missing argument is an error.
    :return: Converted value, or None when an optional value is absent.
    """
    # check key exists
    if key not in kwargs and required:
        eargs = [func_name, key]
        # error: Function: "{0}" requires keyword "{1}"
        WLOG(PARAMS, 'error', textentry('09-511-00005', args=eargs))
    elif key not in kwargs:
        return None
    # try to return value
    try:
        return dtype(kwargs[key])
    except Exception as e:
        eargs = [key, kwargs[key], type(e), str(e)]
        # error: Error with key {0}={1} \n {2}: {3}
        WLOG(PARAMS, 'error', textentry('09-511-00006', args=eargs))


def get_file(block_kind: str,  obs_dir: str, identifier: str,
             output: str, fiber: str, hdu: int, get_data: bool = True
             ) -> Tuple[Union[np.ndarray, None], Union[str, None]]:
    """Load a file's selected HDU and return its absolute filename.

    :param block_kind: APERO file block containing the requested file.
    :param obs_dir: Observation directory recorded in the file index.
    :param identifier: File identifier recorded in the header.
    :param output: Output keyword value used to filter file-index rows.
    :param fiber: Fiber keyword value used to filter file-index rows.
    :param hdu: FITS extension index to load.
    :param get_data: Whether to read the extension data from disk.
    :return: Data array and filename, or ``(None, None)`` if not indexed.
    """

    # get database
    findexdbm = drs_database.FileIndexDatabase(PARAMS, 'VISU')
    findexdbm.load_db()
    # find file in database
    condition = 'BLOCK_KIND="{0}" AND OBS_DIR="{1}" AND KW_IDENTIFIER="{2}"'
    condition += ' AND KW_OUTPUT="{3}" AND KW_FIBER="{4}"'
    condition = condition.format(block_kind, obs_dir, identifier, output,
                                 fiber)
    # query database
    table = findexdbm.get_entries('BLOCK_KIND, OBS_DIR, FILENAME',
                                  condition=condition)
    # deal with no entries
    if table is None or len(table) == 0:
        return None, None
    # use the first entry as the filename
    filename =  drs_file.DrsPath.get_abs_paths(findexdbm.params,
                                               block_kinds=table['BLOCK_KIND'].iloc[0],
                                               obs_dirs=table['OBS_DIR'].iloc[0],
                                               basenames=table['FILENAME'].iloc[0])
    # load file with correct extension
    if get_data:
        data = drs_fits.readfits(PARAMS, filename, ext=hdu)
    else:
        data = None
    # return file
    return np.array(data), filename


def get_header(filename: str) -> drs_fits.Header:
    """Read and return the primary FITS header for a file.

    :param filename: Absolute path to the FITS file.
    :return: Primary header wrapped as an APERO FITS header.
    """
    # load the header of the filename
    return drs_fits.read_header(PARAMS, filename, ext=0)


def get_calib(header: drs_fits.Header, key: str) -> Tuple[np.ndarray, str]:
    """
    Get a calibration file for a speific file and get

    :param header: fits.Header - the header to get the time of calibration
                   from
    :param key: str, the db key for the specific type of calibration

    :return: tuple, 1. the calibration file data (extension 1)
                    2. the calibration file name
    """
    # get database
    calibdbm = drs_database.CalibrationDatabase(PARAMS, 'VISU')
    calibdbm.load_db()
    # get calib file
    cout = calibdbm.get_calib_file(key=key, header=header, nentries=1)
    # extract absolute filename from calibration database
    cfilename = os.path.join(PARAMS['PATH.CALIB'], cout[0])
    # get data
    cdata = drs_fits.readfits(PARAMS, cfilename, ext=1)
    # return the data and the filename
    return cdata, cfilename


def get_obs_dirs() -> List[str]:
    """Return unique observation directories containing raw files.

    :return: Raw observation-directory names, or an empty list when none exist.
    """
    # get database
    findexdbm = drs_database.FileIndexDatabase(PARAMS, 'VISU')
    findexdbm.load_db()
    # return observation directories
    new_obs_dirs = findexdbm.get_unique('OBS_DIR', condition='BLOCK_KIND="raw"')

    if len(new_obs_dirs) == 0:
        return []
    else:
        return list(new_obs_dirs)


def get_identifers(block_kind: str = 'red',
                   obs_dir: Optional[str] = None) -> List[str]:
    """Return unique file identifiers for a block and optional obsdir.

    :param block_kind: APERO file block to search.
    :param obs_dir: Optional observation directory restriction.
    :return: Matching identifiers, or an empty list when none exist.
    """
    # get database
    findexdbm = drs_database.FileIndexDatabase(PARAMS, 'VISU')
    findexdbm.load_db()
    # set up condition
    if obs_dir is None:
        condition = 'BLOCK_KIND="{0}"'.format(block_kind)
    else:
        condition = 'BLOCK_KIND="{0}" AND OBS_DIR="{1}"'
        condition = condition.format(block_kind, obs_dir)

    condition += ' AND KW_IDENTIFIER IS NOT NULL'
    # return identifiers which conform to these filters
    newidentifiers = findexdbm.get_unique('KW_IDENTIFIER', condition=condition)

    if len(newidentifiers) == 0:
        return []
    else:
        return list(newidentifiers)


def get_bokeh_plot_dir(params: ParamDict, pyfile: str) -> str:
    """Create and return the path for one generated Bokeh script.

    :param params: APERO parameters containing the plot root path.
    :param pyfile: Python filename to place in the Bokeh subdirectory.
    :return: Path to the generated plot script.
    """
    # set path to bokeh subdir
    path = os.path.join(params['PATH.PLOT'], 'bokeh')
    # create path if it doesn't exist
    if not os.path.exists(path):
        os.mkdir(path)
    # return path + python filename
    return os.path.join(path, pyfile)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":

    # _bplt = BokehPlot(PARAMS, 'test_plot', _path, 'My test plot')
    # _bplt.create(kwargs=dict(power=3, xlabel='x', ylabel='x^3'))
    # _bplt.run()

    _path = os.path.join(PARAMS['PATH.PLOT'], 'e2ds_plot.py')
    _bplt = BokehPlot(PARAMS, 'e2ds_plot', _path, 'E2DS plot')
    _bplt.create()
    _bplt.run()


# =============================================================================
# End of code
# =============================================================================
