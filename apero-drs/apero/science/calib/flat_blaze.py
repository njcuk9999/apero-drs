#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO flat and blaze calibration functionality

Created on 2019-07-10 at 09:30

@author: cook
"""
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.science.calib import flat_blaze_core
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.science.calib import gen_calib
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the input fits file class
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
blaze_flat_return = Tuple[np.ndarray, np.ndarray, np.ndarray, float]


def calculate_blaze_flat_sinc(params: ParamDict, e2ds_ini: np.ndarray,
                              peak_cut: float, badpercentile: float,
                              order_num: int, fiber: str,
                              sinc_med_size: Optional[int] = None
                              ) -> blaze_flat_return:
    """
    Calculate the blaze function using a sinc function

    :param params: ParamDict, parameter dictionary of constants
    :param e2ds_ini: numpy (1D) array: the extracted flux for this order
    :param peak_cut: float, the threshold expressed as the fraction of the
                     maximum peak, below this threshold the blaze is set to NaN
    :param badpercentile: float, the hot pixel percentile level
    :param order_num: int, the order number we are dealing with
    :param fiber: str, the fiber name we are dealing with
    :param sinc_med_size: int or None, optional, the sinc fit median filter
                          width, overrides params['CAL.FLAT.BLAZE_SINC_MED_SIZE']

    :return: tuple, 1. the updated extracted flux for this order
             2. the flat profile for this order
             3. the blaze fit for this order
             4. the rms for this order
    """
    # get function name
    func_name = __NAME__ + '.calculate_blaze_flat_sinc()'
    # get med filt parameter
    med_size = pcheck(params, 'CAL.FLAT.BLAZE_SINC_MED_SIZE', func=func_name,
                      override=sinc_med_size)
    # delegate numerical work to the profile-independent core module
    args = [e2ds_ini, peak_cut, badpercentile, med_size]
    try:
        with warnings.catch_warnings(record=True) as _:
            outs = flat_blaze_core.calculate_blaze_flat_sinc(*args)
        return outs
    except RuntimeError as e:
        strguess, strlower, strupper, errtype, errmsg = e.args
        eargs = [order_num, fiber, -1, strguess, strlower, strupper,
                errtype, errmsg, func_name]
        raise AperoCodedException(params, '40-015-00009', targs=eargs)


def get_flat(params: ParamDict, recipe: DrsRecipe,
             header: Union[drs_file.Header, None],
             fiber: str, filename: Optional[str] = None, quiet: bool = False,
             database: Optional[drs_database.CalibrationDatabase] = None
             ) -> Tuple[str, float, np.ndarray]:
    """
    Get the flat calibration file from the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param header: fits Header, the fits header associated with the input
                   file (required to get closest in time) can be None if
                   filename is given
    :param fiber: str, the fiber name
    :param filename: str or None, the filename of the flat calibration to
                     load, overrides getting it from calibration database
                     header not require for this
    :param quiet: bool, whether to log/print loading messages
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database
    :return: tuple, 1. the flat file name used, 2. the MJD time of the flat file
             3. numpy (2D) array, the loaded flat file
    """
    # get file definition
    out_flat = drs_file.get_file_definition(params, 'FF_FLAT', block_kind='red')
    # get key
    key = out_flat.get_dbkey()
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load flat file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, recipe.shortname,
                          key, header, filename=filename,
                          userinputkey='FLATFILE', database=calibdbm,
                          fiber=fiber)
    # get properties from calibration file
    flat = cfile.data
    flat_file = cfile.filename
    flat_time = cfile.mjdmid
    # ------------------------------------------------------------------------
    # log which fpref file we are using
    if not quiet:
        WLOG(params, '', textentry('40-015-00006', args=[flat_file]))
    # return the reference image
    return flat_file, flat_time, flat


def get_blaze(params: ParamDict, recipe: DrsRecipe,
              header: Union[drs_file.Header, None],
              fiber: str, filename: Optional[str] = None,
              database: Optional[drs_database.CalibrationDatabase] = None
              ) -> Tuple[str, float, np.ndarray]:
    """
    Get the blaze calibration file from the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param header: fits Header, the fits header associated with the input
                   file (required to get closest in time) can be None if
                   filename is given
    :param fiber: str, the fiber name
    :param filename: str or None, the filename of the blaze calibration to
                     load, overrides getting it from calibration database
                     header not require for this
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database
    :return: tuple, 1. the blaze file name used, 2. the MJD time of the blaze
             file 3. numpy (2D) array, the loaded blaze file
    """
    # get file definition
    out_blaze = drs_file.get_file_definition(params, 'FF_BLAZE',
                                             block_kind='red')
    # get key
    key = out_blaze.get_dbkey()
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load blaze file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, recipe.shortname,
                          key, header, filename=filename,
                          userinputkey='BLAZEFILE', database=calibdbm,
                          fiber=fiber)
    # get properties from calibration file
    blaze = cfile.data
    blaze_file = cfile.filename
    blaze_time = cfile.mjdmid
    # ------------------------------------------------------------------------
    # log which fpref file we are using
    WLOG(params, '', textentry('40-015-00007', args=[blaze_file]))
    # return the reference image
    return blaze_file, blaze_time, blaze


def flux_edge_trace(params: ParamDict, recipe: DrsRecipe,
                    eprops: ParamDict, fiber: str
                    ) -> Tuple[float, List[str]]:
    """
    Calculate the flux at the edges of the trace

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the drs recipe object
    :param eprops: dictionary, the extraction dictionary
    :param fiber: str, the fiber name

    :return: float, the value of the total flux at the edge of the e2dsll
    """
    # get the width of the center of the trace
    mid_size = params['CAL.FLAT.QC_FLUX_EDGE_MIDSIZE']
    # get limit
    flux_edge_limit = params['CAL.FLAT.QC_FLUX_EDGE_LIMIT']
    # get orders to ignore
    ignore_orders = params['CAL.FLAT.QC_FLUX_EDGE_IGNORE']
    # get the number of orders
    norders = eprops['E2DS'].shape[0]
    # delegate numerical work to the profile-independent core module
    args = [eprops['E2DS'], eprops['E2DSLL'], mid_size, ignore_orders,
           flux_edge_limit]
    outs = flat_blaze_core.flux_edge_trace(*args)
    med, flux_edge, max_edge_flux, failed_orders = outs
    # -------------------------------------------------------------------------
    # get the left/right edge flux (for plotting only)
    flux_left, flux_right = med[:, 0], med[:, -1]
    # plot edge plot
    recipe.plot('FLAT_EDGE_ORDERS', med=med, flux_edge=flux_edge,
                flux_left=flux_left, flux_right=flux_right,
                norders=norders, flux_edge_limit=flux_edge_limit, fiber=fiber)
    recipe.plot('SUM_FLAT_EDGE_ORDERS', med=med, flux_edge=flux_edge,
                flux_left=flux_left, flux_right=flux_right,
                norders=norders, flux_edge_limit=flux_edge_limit, fiber=fiber)
    # -------------------------------------------------------------------------
    # convert failed orders to strings
    failed_orders_str = [str(order_num) for order_num in failed_orders]
    # -------------------------------------------------------------------------
    # return max edge flux and list failed orders
    return max_edge_flux, failed_orders_str


# =============================================================================
# Define write and qc functions
# =============================================================================
def flat_blaze_qc(params: ParamDict, recipe: DrsRecipe,
                  eprops: ParamDict, fiber: str
                  ) -> Tuple[List[list], int]:
    """
    Calculate the flat and blaze quality control criteria

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the drs recipe object
    :param eprops: dictionary, the extraction dictionary
    :param fiber: str, the fiber name

    :return: tuple, 1. the qc lists, 2. int 1 if passed 0 if failed
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    # -------------------------------------------------------------------------
    # qc on the edges of the order
    flux_edge, edge_bad_orders = flux_edge_trace(params, recipe, eprops, fiber)
    # get limit
    flux_edge_limit = params['CAl.FLAT.QC_FLUX_EDGE_LIMIT']
    # if flux edge value is above limit we fail QC
    if flux_edge > flux_edge_limit:
        # add failed message to fail message list
        fargs = [fiber, flux_edge, flux_edge_limit]
        ftext = 'Fiber {0}: Edge flux too high ({1} > {2})'
        fail_msg.append(ftext.format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
        # add to qc header lists
    qc_values.append(flux_edge)
    qc_names.append('flux_edge')
    qc_logic.append('flux_edge < {0:.2e}'.format(flux_edge_limit))
    # -------------------------------------------------------------------------
    # report failed orders as QC
    if len(edge_bad_orders) > 0:
        # add failed message to fail message list
        fargs = [fiber, ','.join(edge_bad_orders)]
        ftext = 'Fiber {0}: Flux edge bad orders = {1}'
        fail_msg.append(ftext.format(*fargs))
        qc_pass.append(0)
        qc_values.append(','.join(edge_bad_orders))
    else:
        qc_pass.append(1)
        qc_values.append('None')
    qc_names.append('flux_edge_orders')
    qc_logic.append('len(flux_edge_orders) > 0')
    # --------------------------------------------------------------
    # check that rms values in required orders are below threshold

    # get mask for removing certain values
    remove_orders = params['CAL.FLAT.RMS_SKIP_ORDERS']
    remove_orders = np.array(remove_orders)
    remove_mask = np.isin(np.arange(len(eprops['RMS'])), remove_orders)
    # apply max and calculate the maximum of the rms values
    max_rms = mp.nanmax(eprops['RMS'][~remove_mask])
    # apply the quality control based on the maximum rms
    if max_rms > params['CAL.FLAT.QC_MAX_RMS']:
        # add failed message to fail message list
        fargs = [fiber, max_rms, params['CAL.FLAT.QC_MAX_RMS']]
        fail_msg.append(textentry('40-015-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(max_rms)
    qc_names.append('max_rms')
    qc_logic.append('max_rms < {0:.2f}'.format(params['CAL.FLAT.QC_MAX_RMS']))
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc params
    return qc_params, passed


def flat_blaze_write(params: ParamDict, recipe: DrsRecipe, infile: DrsFitsFile,
                     eprops: ParamDict, fiber: str, rawfiles: List[str],
                     combine: bool, shapeprops: ParamDict, lprops: ParamDict,
                     sprops: ParamDict, qc_params: List[list]
                     ) -> Tuple[DrsFitsFile, DrsFitsFile]:
    """
    Write the flat and blaze calibration files to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param infile: DrsFitsFile, the input fits file class
    :param eprops: ParamDict, the extraction parameter dictionary
    :param fiber: str, the fiber name
    :param rawfiles: list of strings, the raw filenames
    :param combine: bool, if True input files were combined
    :param shapeprops: ParamDict, the shape parameter dictionary
    :param lprops: ParamDict, the localisation parameter dictionary
    :param sprops: ParamDict, the s1d parameter dictionary
    :param qc_params: list of lists, the quality control lists

    :return: tuple, 1. DrsFitsFile, the output blaze fits file class
             2. DrsFitsFile, the output flat fits file class
    """
    # --------------------------------------------------------------
    # Store Blaze in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    blazefile = recipe.outputs['BLAZE_FILE'].newcopy(params=params,
                                                     fiber=fiber)
    # construct the filename from file instance
    blazefile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file
    blazefile.copy_original_keys(infile)
    # add core values (that should be in all headers)
    blazefile.add_core_hkeys(params)
    # add fiber
    blazefile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    blazefile.add_hkey_1d('KW_INFILE1', values=hfiles,
                          dim1name='file')
    # set in files
    blazefile.infiles = list(hfiles)
    # add qc parameters
    blazefile.add_qckeys(qc_params)
    # add the calibration files use
    blazefile = gen_calib.add_calibs_to_header(blazefile, shapeprops)
    # --------------------------------------------------------------
    # add the other calibration files used
    blazefile.add_hkey('KW_CDBORDP', value=lprops['ORDERPFILE'])
    blazefile.add_hkey('KW_CDTORDP', value=lprops['ORDERPTIME'])
    blazefile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    blazefile.add_hkey('KW_CDTLOCO', value=lprops['LOCOTIME'])
    blazefile.add_hkey('KW_CDBSHAPEL', value=sprops['SHAPELFILE'])
    blazefile.add_hkey('KW_CDTSHAPEL', value=sprops['SHAPELTIME'])
    blazefile.add_hkey('KW_CDBSHAPEDX', value=sprops['SHAPEXFILE'])
    blazefile.add_hkey('KW_CDTSHAPEDX', value=sprops['SHAPEXTIME'])
    blazefile.add_hkey('KW_CDBSHAPEDY', value=sprops['SHAPEYFILE'])
    blazefile.add_hkey('KW_CDTSHAPEDY', value=sprops['SHAPEYTIME'])
    # --------------------------------------------------------------
    # add SNR parameters to header
    blazefile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                          dim1name='order')
    # add start and end extraction order used
    blazefile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    blazefile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    blazefile.add_hkey('KW_EXT_RANGE1', value=eprops['CAL.EXT.RANGE1'])
    blazefile.add_hkey('KW_EXT_RANGE2', value=eprops['CAL.EXT.RANGE2'])
    # add cosmic parameters used
    blazefile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    blazefile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    blazefile.add_hkey('KW_COSMIC_THRES',
                       value=eprops['COSMIC_THRESHOLD'])
    # add blaze sinc parameters used
    blazefile.add_hkey('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'])
    blazefile.add_hkey('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'])
    # add saturation parameters used
    blazefile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    blazefile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # --------------------------------------------------------------
    # copy data
    blazefile.data = eprops['BLAZE']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-015-00003', args=[blazefile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=blazefile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    blazefile.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(blazefile)
    # --------------------------------------------------------------
    # Store Flat-field in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    flatfile = recipe.outputs['FLAT_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the filename from file instance
    flatfile.construct_filename(infile=infile)
    # copy header from blaze file
    flatfile.copy_hdict(blazefile)
    # set in files
    flatfile.infiles = list(hfiles)
    # set output key
    flatfile.add_hkey('KW_OUTPUT', value=flatfile.name)
    # copy data
    flatfile.data = eprops['FLAT']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-015-00004', args=[flatfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=blazefile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    flatfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(flatfile)
    # --------------------------------------------------------------
    # Store E2DSLL in file
    # --------------------------------------------------------------
    if params['DEBUG.OUTFILE.E2DSLL_FILE']:
        # get a new copy of the blaze file
        e2dsllfile = recipe.outputs['E2DSLL_FILE'].newcopy(params=params,
                                                           fiber=fiber)
        # construct the filename from file instance
        e2dsllfile.construct_filename(infile=infile)
        # copy header from blaze file
        e2dsllfile.copy_hdict(blazefile)
        # set in files
        e2dsllfile.infiles = list(hfiles)
        # set output key
        e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
        # copy data
        e2dsllfile.data = eprops['E2DSLL']
        # --------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '',
             textentry('40-015-00005', args=[e2dsllfile.filename]))
        # define multi lists
        data_list, name_list = [eprops['E2DSCC']], ['E2DSLL', 'E2DSCC']
        datatype_list = ['image']
        # snapshot of parameters
        if params['GLOBAL.PSNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsllfile)]
            name_list += ['PARAM_TABLE']
            datatype_list += ['table']
        # write image to file
        e2dsllfile.write_multi(data_list=data_list, name_list=name_list,
                               datatype_list=datatype_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(e2dsllfile)
    # return out file
    return blazefile, flatfile


def flat_blaze_summary(recipe: DrsRecipe, params: ParamDict,
                       qc_params: List[list], eprops: ParamDict, fiber: str):
    """
    Produce the flat and blaze summary document

    :param recipe: DrsRecipe, the recipe that called this function
    :param params: ParamDict, parameter dictionary of constants
    :param qc_params: list of lists, the quality control lists
    :param eprops: ParamDict, the extraction parameter dictionary
    :param fiber: str, the fiber name

    :return: None, produces the summary document
    """
    # alias to eprops
    epp = eprops
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS.VERSION'], fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS.DATE'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_START', value=epp['START_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_END', value=epp['END_ORDER'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE1', value=epp['CAL.EXT.RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=epp['CAL.EXT.RANGE2'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=epp['COSMIC'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=epp['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=epp['COSMIC_THRESHOLD'])
    # add blaze sinc parameters used
    recipe.plot.add_stat('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'],
                         fiber=fiber)


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