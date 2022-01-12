#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General calibration functions in here only

Created on 2019-06-27 at 10:48

@author: cook
"""
from astropy.io import fits
from astropy.table import Table
import numpy as np
import os
from typing import List, Optional, Tuple, Union
import warnings

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_data
from apero.core.utils import drs_recipe
from apero.io import drs_fits
from apero.io import drs_image
from apero.science.calib import dark
from apero.science.calib import badpix
from apero.science.calib import background


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.gen_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsHeader = drs_fits.Header
# get calibration database
CalibDatabase = drs_database.CalibrationDatabase
# Get Logging function
WLOG = drs_log.wlog
# get time
Time = base.Time
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get display func
display_func = drs_log.display_func


# =============================================================================
# Define classes
# =============================================================================
class CalibFile:
    key: Optional[str]
    fiber: Optional[str]
    filename: Optional[Union[List[str], str]]
    mjdmid: Union[List[float], float]
    data: Optional[Union[List[np.ndarray], np.ndarray]]
    header: Optional[Union[drs_fits.Header, drs_fits.Header]]
    source: str
    mode: str
    length: int
    found: bool
    master: Union[List[bool], bool]
    user: bool

    def __init__(self):
        """
        Construct the calibration file class (mostly just storage and loading
        of the calibration file)
        """
        # the calibration database key
        self.key = None
        # the fiber associated to this calibration
        self.fiber = None
        # the filename of this calibration
        self.filename = None
        # the modified julian date
        self.mjdmid = np.nan
        # the data (if loaded)
        self.data = None
        # the header (if loaded)
        self.header = None
        # the source of the calibration (user input or calibration database)
        self.source = 'None'
        # the select mode of the calibration (None, closest, newer, older)
        self.mode = 'None'
        # the length of the number of files (length = 1 is a single file)
        self.length = 0
        # whether calibration was found
        self.found = False
        # whether calibration is a master
        self.master = False
        # whether the calibration is from a user input override
        self.user = False

    def load_calib_file(self, params: ParamDict, key: str,
                        inheader: Union[drs_fits.Header, None] = None,
                        filename: Union[str, None] = None,
                        get_image: bool = True, get_header: bool = False,
                        fiber: Union[str, None] = None,
                        userinputkey: Union[str, None] = None,
                        database: Union[CalibDatabase, None] = None,
                        return_filename: bool = False,
                        mode: Union[str, None] = None,
                        n_entries: Union[int, str] = 1,
                        required: bool = True, ext: Union[int, None] = None,
                        fmt: str = 'fits',
                        kind: str = 'image'):
        """
        Load one or many calibration files

        :param params: ParamDict, the parameter dictionary of constants
        :param key: str, the key from the calibration database to select a
                    specific calibration with
        :param inheader: fits.Header - the header file (required to match by
                         time) if None does not match by a 'zero point' time)

        :param filename: str or None, if set overrides filename from database
        :param get_image: bool, if True loads image (or images if nentries > 1),
                          if False image is None (or list of Nones if
                          nentries > 1)
        :param get_header: bool, if True loads header (or headers if
                           nentries > 1)
                           if False header is None (or list of Nones if
                           nentries > 1)
        :param fiber: str or None, if set must be the fiber type - all returned
                      calibrations are filtered by this fiber type
        :param userinputkey: str or None, if set checks params['INPUTS'] for
                             this key and sets filename from here - note
                             params['INPUTS'] is where command line arguments
                             are stored
        :param database: drs calibration database instance - set this if
                         calibration database already loaded (if unset will
                         reload the database)
        :param return_filename: bool, if True returns the filename only
        :param mode: str or None, the time mode for getting from sql
                     ('closest'/'newer'/'older')
        :param n_entries: int or str, maximum number of calibration files to
                          return for all entries use '*'
        :param required: bool, whether we require an entry - will raise
                         exception if required=True and no entries found
        :param ext: int, valid extension (unset by default) when kind='image'
        :param fmt: str, astropy.table.Table valid format (when kind='table')
        :param kind: str, either 'image' for fits image or 'table' for table

        :return: None, updates the attributes of the class

        """
        # set function
        _ = display_func('load_calib_file', __NAME__)
        # ---------------------------------------------------------------------
        # set properties from load file
        self.key = key
        self.fiber = fiber
        self.mode = mode
        # get mjdmid key
        mjdmid_key = params['KW_MID_OBS_TIME'][0]
        # ---------------------------------------------------------------------
        # first try to get file from inputs
        fout = drs_data.get_file_from_inputs(params, 'calibration',
                                             userinputkey,
                                             filename,
                                             return_source=True)
        # set filename and source from inputs
        self.filename, self.source = fout[0], str(fout[1])
        # ---------------------------------------------------------------------
        # if filename is defined this is the filename we should return
        if self.filename is not None:
            # set filename, filetime and source
            self.filename = str(self.filename)
            # deal with non found file
            if os.path.exists(self.filename):
                self.found = True
                # we need to get file time
                hdr = drs_fits.read_header(params, self.filename)
                if mjdmid_key in hdr:
                    self.mjdmid = float(hdr[mjdmid_key])
                    self.user = True
            else:
                # warn user that input file was not valid
                # TODO: add to language database
                wmsg = ('Warning user file: {0} not found. '
                        'Using calibration database')
                WLOG(params, 'warning', wmsg.format(self.filename), sublevel=2)
                self.filename = None
            # we are finished - return here
            if return_filename:
                return
        # -------------------------------------------------------------------------
        # else we have to load from database
        if self.filename is None:
            # check if we have the database
            if database is None:
                # construct a new database instance
                database = CalibDatabase(params)
                # load the database
                database.load_db()
            # load filename from database
            fout = database.get_calib_file(key, header=inheader, timemode=mode,
                                           nentries=n_entries,
                                           required=required, fiber=fiber)
            # deal with outputs of get calib file
            self.filename, self.mjdmid, self.master = fout
            self.source = 'calibDB'
        # ---------------------------------------------------------------------
        # deal with filename being a path --> string (unless None)
        if self.filename is not None:
            if isinstance(self.filename, list):
                self.filename = list(map(lambda x: str(x), self.filename))
            else:
                self.filename = str(self.filename)
            # set found
            self.found = True
        # ---------------------------------------------------------------------
        # deal with checking delta time between this observation (header) and
        #  the calibration
        if inheader is not None:
            if isinstance(self.filename, list):
                for it in range(len(filename)):
                    calib_delta_time_check(params, inheader, self.mjdmid[it],
                                           self.filename[it], self.master[it],
                                           self.user, self.key)
            else:
                calib_delta_time_check(params, inheader, self.mjdmid,
                                       self.filename, self.master, self.user,
                                       self.key)
        # ---------------------------------------------------------------------
        # if we are just returning filename return here
        if return_filename:
            return
        # deal with not return filename
        elif self.filename is None and not required:
            return
        # ---------------------------------------------------------------------
        # need to deal with a list of files
        if isinstance(self.filename, list):
            # storage for images and headers
            images, headers = [], []
            # loop around files
            for file_it in self.filename:
                # now read the calibration file
                image, header = drs_data.read_db_file(params, file_it,
                                                      get_image, get_header,
                                                      kind, fmt, ext)
                # append to storage
                images.append(image)
                headers.append(headers)
            # make sure filetimes is a list
            if isinstance(self.mjdmid, float):
                self.mjdmid = [self.mjdmid]
            else:
                self.mjdmid = list(self.mjdmid)
            # set data and header
            self.data = images
            self.header = headers
            self.length = len(images)
            # return
            return
        else:
            # now read the calibration file
            image, header = drs_data.read_db_file(params, self.filename,
                                                  get_image, get_header,
                                                  kind, fmt, ext)
            # make sure file time is float (MJDMID)
            self.mjdmid = float(self.mjdmid)
            # set data and header
            self.data = image
            self.header = header
            self.length = 1
            # return
            return


# =============================================================================
# Define user functions
# =============================================================================
def check_files(params: ParamDict,
                infile: DrsFitsFile) -> Tuple[bool, List[List[str]]]:
    """
    Skip objnames and dprtypes based on whether:

    1. KW_DPRTYPE is None (or user set --dprtype)
    2. KW_OBJNAME is None or Null (or user set --objname)

    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile, the drs fits file instance, this contains
                   the header to look for KW_DPRTYPE and KW_OBJNAME
    :return: tuple, 1. bool, True if DPRTYPE/OBJNAME match skip conditions
                    2. list - first element the DPRTYPE skip conditions, second
                       elemtn the OBJNAME skip conditions
    """
    # get pseudo constants
    pconst = constants.pload()
    # get infile DPRTYPE and OBJNAME
    dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str, required=False)
    objname = infile.get_hkey('KW_OBJNAME', dtype=str, required=False)
    filename = infile.filename
    # deal with unset value
    if dprtype is None:
        dprtype = 'None'
    if objname is None:
        objname = 'None'
    # clean (capitalize and remove white spaces)
    dprtype = drs_text.clean_strings(dprtype)
    objname = pconst.DRS_OBJ_NAME(objname)
    # get inputs
    dprtype_inputs = params['INPUTS']['DPRTYPE'].split(',')
    objname_inputs = params['INPUTS']['OBJNAME'].split(',')
    # clean (capitalize and remove white spaces)
    dprtype_inputs = drs_text.clean_strings(dprtype_inputs)
    objname_inputs = pconst.DRS_OBJ_NAMES(objname_inputs)
    # ----------------------------------------------------------------------
    # log checking file info
    wargs = [dprtype, objname]
    WLOG(params, 'info', textentry('40-016-00032', args=wargs))
    # ----------------------------------------------------------------------
    # storage of outputs
    skip = False
    skip_conditions = [[], [], []]
    # ----------------------------------------------------------------------
    # convert objname_inputs to char array
    objarray = np.char.array(objname_inputs).upper()
    # deal with objname filter
    if 'NONE' in objarray:
        skip = skip or False
    elif 'NULL' in objarray:
        skip = skip or False
    # else check for objname in
    elif objname.upper() in objarray:
        skip = skip or False
    # else we skip
    else:
        skip = skip or True
        skip_conditions[0].append('OBJNAME')
        skip_conditions[2] = [objname, ' or '.join(objname_inputs), filename]
    # ----------------------------------------------------------------------
    # deal with objname filter
    if 'NONE' in dprtype_inputs:
        skip = skip or False
    elif 'NULL' in dprtype_inputs:
        skip = skip or False
    # else check for objname in
    elif dprtype in dprtype_inputs:
        skip = skip or False
    # else we skip
    else:
        skip = skip or True
        skip_conditions[0].append('DPRTYPE')
        skip_conditions[1] = [dprtype, ' or '.join(dprtype_inputs), filename]
    # ----------------------------------------------------------------------
    # return the skip and conditions
    return skip, skip_conditions


def calibrate_ppfile(params: ParamDict, recipe: DrsRecipe,
                     infile: DrsFitsFile,
                     database: Union[CalibDatabase, None] = None,
                     image: Union[np.ndarray, None] = None,
                     header: Union[DrsHeader, fits.Header, None] = None,
                     correctdark: bool = True,
                     flip_image: Union[bool, None] = None,
                     converte: bool = True,
                     resize_image: Union[bool, None] = None,
                     correctbad: bool = True, correctback: bool = True,
                     cleanhotpix: bool = True,
                     n_percentile: Union[float, None] = None,
                     darkfile: Union[str, None] = None,
                     badpixfile: Union[str, None] = None,
                     backfile: Union[str, None] = None
                     ) -> Tuple[ParamDict, np.ndarray]:
    """
    Calibrate a preprocessed file

    The following steps are done (based on configuration)

    1. remove pixels that are out of bounds
    2. correct for dark
    3. flip image
    4. convert ADU/s to electrons
    5. resize
    6. corrected for bad pixels
    7. corrected for background
    8. normalise by a percentile
    9. clean hot pixels
    10. remove pixels that are out of bounds

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe class that called this function
    :param infile: DrsFitsFile, the fits file instance
    :param database: CalibrationDatabase or None, if set passes the calibration
                     database from call instead of reloading it again
    :param image: numpy array or None, if set does not get the image from
                  the "infile" argument but sets it from this
    :param header: Header instance, if set does not get the header from the
                   "infile" argument buts sets it from this
    :param correctdark: bool, if True corrects dark using calibrations
    :param flip_image: bool or None, if True overrides "INPUT_FLIP_IMAGE" and
                       flips the image based on configuration params
    :param converte: bool, if True converts from ADU/s to electrons
    :param resize_image: bool or None, if True overrides "INPUT_RESIZE_IMAGE"
                         and resizes the image based on configruation params
    :param correctbad: bool, if True replaces bad pixels with NaNs
    :param correctback: bool, if True corrects background
    :param cleanhotpix: bool, if True corrects hot pixels
    :param n_percentile: float or None, if set uses this percentile to normalize
                         the image
    :param darkfile: str or None, if set overrides the dark file used from the
                     calibration database
    :param badpixfile: str or None, if set overrides the bad pixel map file used
                       from the calibration database
    :param backfile: str or None, if set overrides the background file used
                     from the calibration database

    :return: Tuple, 1. the calibration properties as a parameter dictionary,
                    2. the calibrated image
    """
    func_name = __NAME__ + '.calibrate_file()'
    # deal with inputs from params
    flip = pcheck(params, 'INPUT_FLIP_IMAGE', func=func_name,
                  override=flip_image)
    resize = pcheck(params, 'INPUT_RESIZE_IMAGE', func=func_name,
                    override=resize_image)
    # get image and header
    if image is None:
        image = infile.get_data(copy=True)
    if header is None:
        header = infile.get_header()
    # -------------------------------------------------------------------------
    # get loco file instance
    darkinst = drs_file.get_file_definition(params, 'DARKM', block_kind='red')
    badinst = drs_file.get_file_definition(params, 'BADPIX', block_kind='red')
    backinst = drs_file.get_file_definition(params, 'BKGRD_MAP',
                                            block_kind='red')
    # get calibration key
    darkkey = darkinst.get_dbkey()
    badkey = badinst.get_dbkey()
    backkey = backinst.get_dbkey()
    # load database
    if database is None:
        calibdbm = CalibDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # -------------------------------------------------------------------------
    # load pconst
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # Get basic image properties
    sigdet = infile.get_hkey('KW_RDNOISE')
    exptime = infile.get_hkey('KW_EXPTIME')
    gain = infile.get_hkey('KW_GAIN')
    dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
    saturate = pconst.SATURATION(params, infile.get_header())
    frmtime = pconst.FRAME_TIME(params, infile.get_header())
    nfiles = infile.numfiles
    # log that we are calibrating a file
    WLOG(params, 'info', textentry('40-014-00038', args=[infile.filename]))

    # ----------------------------------------------------------------------
    # image 0 remove pixels that are out of bounds
    # ----------------------------------------------------------------------
    # Pixel values need to be within reasonable bounds considering the
    # physics of the IR array, and if they are not, we set them to NaN.
    # Upper bound is the saturation/frame time (we express things as slope).
    # A pixel with a value greater than can be recorded by the array is
    # nonphysical. The lower bound is set at -10 * readout noise.
    upperlim = saturate / frmtime
    lowerlim = -10 * (sigdet * gain) / frmtime
    with warnings.catch_warnings(record=True) as _:
        mask = (image > upperlim) | (image < lowerlim)
    image[mask] = np.nan

    # ----------------------------------------------------------------------
    # image 1 is corrected for dark
    # ----------------------------------------------------------------------
    if correctdark:
        # load dark file
        cfile = CalibFile()
        cfile.load_calib_file(params, darkkey, header, filename=darkfile,
                              userinputkey='DARKFILE', database=calibdbm,
                              return_filename=True)
        # get properties from calibration file
        darkfile, darktime = cfile.filename, cfile.mjdmid
        # correct image
        image1 = dark.correction(params, image, nfiles=nfiles,
                                 darkfile=darkfile)
    else:
        image1 = np.array(image)
        darkfile, darktime = 'None', np.nan
    # ----------------------------------------------------------------------
    # flip image
    # ----------------------------------------------------------------------
    if flip:
        image2 = drs_image.flip_image(params, image1)
    else:
        image2 = np.array(image1)
    # ----------------------------------------------------------------------
    # convert ADU/s to electrons
    # ----------------------------------------------------------------------
    if converte:
        image2 = drs_image.convert_to_e(params, image2, gain=gain,
                                        exptime=exptime)
        # convert limits
        upperlim = upperlim * gain * exptime
        lowerlim = lowerlim * gain * exptime

    # ----------------------------------------------------------------------
    # image 2 is resized (if required)
    # ----------------------------------------------------------------------
    if resize:
        # get resize size
        sargs = dict(xlow=params['IMAGE_X_LOW'], xhigh=params['IMAGE_X_HIGH'],
                     ylow=params['IMAGE_Y_LOW'], yhigh=params['IMAGE_Y_HIGH'])
        # resize flat
        image2 = drs_image.resize(params, image2, **sargs)
        # print that image has been resize
        wargs = [dprtype, image1.shape, image2.shape]
        WLOG(params, '', textentry('40-014-00013', args=wargs))

    # ----------------------------------------------------------------------
    # image 3 is corrected for bad pixels
    # ----------------------------------------------------------------------
    if correctbad:
        # load the bad pix file
        cfile = CalibFile()
        cfile.load_calib_file(params, badkey, header, filename=badpixfile,
                              userinputkey='BADPIXFILE', database=calibdbm,
                              return_filename=True)
        # get properties from calibration file
        badpfile, badtime = cfile.filename, cfile.mjdmid
        # correct the image
        image3 = badpix.correction(params, image2, badpixfile=badpfile)
    else:
        image3 = np.array(image2)
        badpfile, badtime = 'None', np.nan
    # ----------------------------------------------------------------------
    # image 4 is corrected for background
    # ----------------------------------------------------------------------
    if correctback:
        # load background file from inputs/calibdb
        cfile = CalibFile()
        cfile.load_calib_file(params, backkey, header, filename=backfile,
                              userinputkey='BACKFILE', return_filename=True,
                              database=calibdbm)
        bkgrdfile, backtime = cfile.filename, cfile.mjdmid
        # correct image for background
        image4 = background.correction(recipe, params, infile, image3,
                                       bkgrdfile=bkgrdfile)
    else:
        image4 = np.array(image3)
        bkgrdfile, backtime = 'None', np.nan
    # ----------------------------------------------------------------------
    # image 4 may need to normalise by a percentile
    # ----------------------------------------------------------------------
    if n_percentile is not None:
        # log that we are normalising
        WLOG(params, '', textentry('40-014-00014', args=[n_percentile]))
        # normalise by nanpercentile
        image4 = image4 / np.nanpercentile(image4, n_percentile)

    # ----------------------------------------------------------------------
    # image 5 is cleaned from hot pixels
    # ----------------------------------------------------------------------
    if cleanhotpix:
        # log progress
        WLOG(params, '', textentry('40-014-00012'))
        # load the bad pix file
        cfile = CalibFile()
        cfile.load_calib_file(params, badkey, header, filename=badpixfile,
                              userinputkey='BADPIXFILE', database=calibdbm,
                              return_filename=True)
        # get properties from calibration file
        badpfile, badtime = cfile.filename, cfile.mjdmid
        # get bad pixel mask
        badpixmask = badpix.correction(params, None, badpixfile=badpfile,
                                       return_map=True)
        # clean hot pixels
        image5 = drs_image.clean_hotpix(image4, badpixmask)
    else:
        image5 = np.array(image4)

    # ----------------------------------------------------------------------
    # image 5 remove pixels that are out of bounds
    # ----------------------------------------------------------------------
    # Pixel values need to be within reasonable bounds considering the
    # physics of the IR array, and if they are not, we set them to NaN.
    # Upper bound is the saturation/frame time (we express things as slope).
    # A pixel with a value greater than can be recorded by the array is
    # nonphysical. The lower bound is set at -10 * readout noise.
    with warnings.catch_warnings(record=True) as _:
        mask = (image5 > upperlim) | (image5 < lowerlim)
    image5[mask] = np.nan

    # ----------------------------------------------------------------------
    # make properties dictionary
    # ----------------------------------------------------------------------
    props = ParamDict()
    # get basic properties
    props['FILENAME'] = infile.filename
    props['BASENAME'] = infile.basename
    props['SIGDET'] = sigdet
    props['EXPTIME'] = exptime
    props['GAIN'] = gain
    props['DPRTYPE'] = dprtype
    # get
    props['SHAPE'] = image5.shape
    props['DARKFILE'] = darkfile
    props['DARKTIME'] = darktime
    props['BADPFILE'] = badpfile
    props['BADTIME'] = badtime
    props['BACKFILE'] = bkgrdfile
    props['BACKTIME'] = backtime
    props['FLIPPED'] = flip
    props['CONVERT_E'] = converte
    props['RESIZED'] = resize
    if n_percentile is None:
        props['NORMALISED'] = False
    else:
        props['NORMALISED'] = n_percentile
    props['CLEANED'] = cleanhotpix
    # set source
    keys = ['FILENAME', 'BASENAME', 'SIGDET', 'EXPTIME', 'GAIN', 'DPRTYPE',
            'SHAPE', 'DARKFILE', 'DARKTIME', 'BADPFILE', 'BADTIME', 'BACKFILE',
            'BACKTIME', 'FLIPPED', 'CONVERT_E', 'RESIZED', 'NORMALISED',
            'CLEANED']
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # return image 5
    return props, image5


def add_calibs_to_header(outfile: DrsFitsFile,
                         props: ParamDict) -> DrsFitsFile:
    """
    Add the calibration properties to an outfile header

    The calibration header keys added are:
    - KW_CDBDARK, the dark file used to correct file
    - KW_CDBBAD, the bad file used to correct file
    - KW_CDBBACK, the background file used to correct file
    - KW_C_FLIP, whether the image was flipped
    - KW_C_CVRTE, whether the flux was converted to electrons
    - KW_C_RESIZE, whether the image was resized

    :param outfile: DrsFitsFile, the outfile to add header keys to
    :param props: ParamDict, the calibration properties parameter dictionary

    :return: outfile, DrsFitsFile, the input outfile with updated header
    """
    # define property keys (must be in calibrate_ppfile function)
    propkeys = ['DARKFILE', 'DARKTIME', 'BADPFILE', 'BADTIME',
                'BACKFILE', 'BACKTIME', 'FLIPPED', 'CONVERT_E', 'RESIZED']
    # define the header keywords to use for each
    headerkeys = ['KW_CDBDARK', 'KW_CDTDARK', 'KW_CDBBAD', 'KW_CDTBAD',
                  'KW_CDBBACK', 'KW_CDTBACK', 'KW_C_FLIP', 'KW_C_CVRTE',
                  'KW_C_RESIZE']
    # loop around property keys
    for it in range(len(propkeys)):
        # get header key
        hkey = headerkeys[it]
        # get property key
        pkey = propkeys[it]
        # add header key
        if pkey in props:
            # get value
            value = props[pkey]
            # check if path
            value = drs_fits.check_dtype_for_header(value)
            # push to header
            outfile.add_hkey(hkey, value=value)
    # return outfile
    return outfile


def calib_delta_time_check(params: ParamDict, inheader: DrsHeader,
                           calib_time: float, calib_filename: str,
                           master: bool, user: bool, key: str):
    """
    Check that the delta time between calibration and observation is
    valid (as defined by MAX_CALIB_DTIME)

    :param params: ParamDict, the parameter dictionary of constants
    :param inheader: Header, the header associated with the observation
    :param calib_time: float, the time of the calibration in MJD
    :param calib_filename: str, the name of the calibration file (for logging)
    :param master: bool, if True this is a master recipe and should not be
                   checked
    :param user: bool, if True this calib came from the user and should not
                 be checked
    :param key: str, the calibration key for the calib file

    :raises: DrsLogException if DO_CALIB_DTIME_CHECK = True and delta time is
             greater than MAX_CALIB_DTIME

    :return: None, raises an error or just returns
    """
    # set function ame
    func_name = display_func('calib_delta_time_check', __NAME__)
    # ---------------------------------------------------------------------
    # get parameters from params
    do_check = params['DO_CALIB_DTIME_CHECK']
    max_dtime = params['MAX_CALIB_DTIME']
    timekey = params['KW_MID_OBS_TIME'][0]
    # extra skip if we are in quick look mode
    quicklook = params['EXT_QUICK_LOOK']
    # ---------------------------------------------------------------------
    # deal with master and user flags
    if master or user:
        return
    # ---------------------------------------------------------------------
    # deal with check (if check is False we do not check)
    if not do_check:
        return
    # deal with quick look mode (extraction only)
    if quicklook:
        return
    # ---------------------------------------------------------------------
    # get and check observation time
    if timekey in inheader:
        # observation time (MJDMID)
        obstime = inheader[timekey]
    else:
        return
    # ---------------------------------------------------------------------
    # check calibration time is finite (if it isn't we can't check this)
    if not np.isfinite(calib_time):
        return
    # ---------------------------------------------------------------------
    # work out delta time
    delta_time = np.abs(obstime - calib_time)
    # now check delta time
    if delta_time > max_dtime:
        # get human-readable time
        hobstime = Time(obstime, format='mjd').iso
        hcalibtime = Time(calib_time, format='mjd').iso
        # log error
        eargs = [key, calib_filename, delta_time, max_dtime, hobstime,
                 hcalibtime, func_name]
        WLOG(params, 'error', textentry('09-002-00004', args=eargs))
    else:
        WLOG(params, '', textentry('40-005-10003', args=[max_dtime]))


def check_fp(params: ParamDict, image: np.ndarray, filename: str,
             percentile: Union[float, None] = None,
             fp_qc_thres: Union[float, None] = None,
             centersize: Union[int, None] = None,
             num_ref: Union[int, None] = None) -> bool:
    """
    Checks that a 2D image containing FP is valid

    :param params: ParamDict, parameter dictionary of constants
    :param image: numpy array, the FP image
    :param filename: str, the filename of the FP we are checking (for logging)
    :param percentile: None or float, overrides 'CALIB_CHECK_FP_PERCENTILE'
                       should be between 0 and 100
    :param fp_qc_thres: None or float, overrides 'CALIB_CHECK_FP_THES', this is
                        the quality control threshold for the measured FP
    :param centersize: None or int, overrides 'CALIB_CHECK_FP_CENT_SIZE', this
                       is the FP center size in pixels
    :param num_ref: None or int, overrides 'PP_NUM_REF_TOP', this is the number
                    of reference pixels at the top

    :return: bool, whether the FP file passes quality control
    """
    # set the function name
    func_name = __NAME__ + '.check_fp()'
    # log: Validating FP file
    WLOG(params, '', textentry('40-014-00043', args=[filename]))
    # get properties from params
    percentile = pcheck(params, 'CALIB_CHECK_FP_PERCENTILE', func=func_name,
                        override=percentile)
    fp_qc = pcheck(params, 'CALIB_CHECK_FP_THRES', 'fp_qc', func=func_name,
                   override=fp_qc_thres)
    centersize = pcheck(params, 'CALIB_CHECK_FP_CENT_SIZE', func=func_name,
                        override=centersize)
    num_ref = pcheck(params, 'PP_NUM_REF_TOP', func=func_name,
                     override=num_ref)
    # get the image size
    nbypix, nbxpix = image.shape
    # find the 95th percentile of the center of the image
    xlower, xupper = (nbxpix // 2) - centersize, (nbxpix // 2) + centersize
    ylower, yupper = (nbypix // 2) - centersize, (nbypix // 2) + centersize
    # get the center percentile of image
    cent = np.nanpercentile(image[xlower:xupper, ylower:yupper], percentile)
    # work out the residuals in the reference pixels
    residuals = np.abs(image[:num_ref]) - np.nanmedian(image[:num_ref])
    # get the quality control on fp
    passed = (cent / np.nanmedian(residuals)) > fp_qc
    # return passed
    return passed


def check_fp_files(params: ParamDict,
                   fpfiles: List[DrsFitsFile]) -> List[DrsFitsFile]:
    """
    Check a set of fpfiles for valid (2D) fp data

    :param params: ParamDict, the parameter dictionary of constants
    :param fpfiles: list of DrsFitsFiles, the FP fits files instances to check

    :return: list of DrsFitsFiles, the valid FP fits file (those that pass FP
             quality control checks)
    """
    # set the function name
    func_name = __NAME__ + '.check_fp_files()'
    # storage for valid fp files
    newfpfiles, fpfilenames = [], []
    # loop around fp files
    for fpfile in fpfiles:
        # add to list
        fpfilenames.append(fpfile.filename)
        # check if fp is good
        if check_fp(params, fpfile.get_data(), filename=fpfile.filename):
            newfpfiles.append(fpfile)
        else:
            # log a warning that file removed
            wargs = [fpfile.filename]
            WLOG(params, 'warning', textentry('10-001-00009', args=wargs),
                 sublevel=4)
    # deal with having no files left
    if len(newfpfiles) == 0:
        # log: No FP files passed 2D quality control. \n\t Function = {0}
        WLOG(params, 'error', textentry('09-000-00010', args=[func_name]))
    # return new fp files
    return newfpfiles


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
