#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Image processing module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouFITS
from . import spirouImage
from . import spirouTable

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouImage.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['AddKey', 'AddKey1DList', 'AddKey2DList',
           'ConvertToE', 'ConvertToADU',
           'CopyOriginalKeys', 'CopyRootKeys', 'CorrectForDark',
           'FitTilt', 'FlipImage',
           'GetAllSimilarFiles', 'GetAcqTime'
           'GetSigdet', 'GetExpTime', 'GetGain',
           'GetKey', 'GetKeys', 'GetTilt', 'GetTypeFromHeader',
           'LocateBadPixels', 'MakeTable', 'MeasureDark',
           'NormMedianFlat', 'ReadData',
           'ReadImage', 'ReadTable', 'ReadImageAndCombine',
           'ReadFlatFile', 'ReadHeader', 'ReadKey', 'Read2Dkey',
           'ReadTiltFile', 'ReadWaveFile', 'ReadOrderProfile',
           'ResizeImage', 'WriteImage', 'WriteTable']

# =============================================================================
# Function aliases
# =============================================================================
AddKey = spirouFITS.add_new_key
"""
Add a new key to hdict from keywordstore, if value is not None then the
keywordstore value is updated. Each keywordstore is in form:
        [key, value, comment]    where key and comment are strings
if hdict is None creates a new dictionary

:param hdict: dictionary or None, storage for adding to FITS rec
:param keywordstore: list, keyword list (defined in spirouKeywords.py)
                     must be in form [string, value, string]
:param value: object or None, if any python object (other than None) will
              replace the value in keywordstore (i.e. keywordstore[1]) with
              value, if None uses the value = keywordstore[1]

:return hdict: dictionary, storage for adding to FITS rec
"""

AddKey1DList = spirouFITS.add_key_1d_list
"""
Add a new 1d list to key using the keywordstorage[0] as prefix in form
keyword = kewordstoreage + row number

:param hdict: dictionary, storage for adding to FITS rec
:param keywordstore: list, keyword list (defined in spirouKeywords.py)
                     must be in form [string, value, string]
:param values: numpy array or 1D list of keys or None

              if numpy array or 1D list will create a set of keys in form
              keyword = kewordstoreage + row number
              where row number is the position in values
              with value = values[row number][column number]

              if None uses the value = keywordstore[1]
:param dim1name: string, the name for dimension 1 (rows), used in FITS rec
                 HEADER comments in form:
      COMMENT = keywordstore[2] dim1name={row number}

:return hdict: dictionary, storage for adding to FITS rec
"""

AddKey2DList = spirouFITS.add_key_2d_list
"""
Add a new 2d list to key using the keywordstorage[0] as prefix in form
keyword = kewordstoreage + number

where number = (row number * number of columns) + column number

:param hdict: dictionary, storage for adding to FITS rec
:param keywordstore: list, keyword list (defined in spirouKeywords.py)
                     must be in form [string, value, string]
:param values: numpy array or 2D list of keys or None

              if numpy array or 2D list will create a set of keys in form
              keyword = kewordstoreage + number
              where number = (row number*number of columns)+column number
              with value = values[row number][column number]

              if None uses the value = keywordstore[1]
:param dim1name: string, the name for dimension 1 (rows), used in FITS rec
                 HEADER comments in form:
      COMMENT = keywordstore[2] dim1name={row number} dim2name={col number}
:param dim2name: string, the name for dimension 2 (cols), used in FITS rec
                 HEADER comments in form:
      COMMENT = keywordstore[2] dim1name={row number} dim2name={col number}

:return hdict: dictionary, storage for adding to FITS rec
"""

ConvertToE = spirouImage.convert_to_e
"""
Converts image from ADU/s into e-

:param image:
:param p: dictionary or None, parameter dictionary, must contain 'exptime'
          and 'gain', if None gain and exptime must not be None
:param gain: float, if p is None, used as the gain to multiple the image by
:param exptime: float, if p is None, used as the exposure time the image
                is multiplied by

:return newimage: numpy array (2D), the image in e-
"""

ConvertToADU = spirouImage.convert_to_adu
"""
Converts image from ADU/s into ADU

:param image:
:param p: dictionary or None, parameter dictionary, must contain 'exptime'
          and 'gain', if None gain and exptime must not be None
:param exptime: float, if p is None, used as the exposure time the image
                is multiplied by

:return newimage: numpy array (2D), the image in e-
"""

CopyOriginalKeys = spirouFITS.copy_original_keys
"""
Copies keys from hdr dictionary to hdict, if forbid_keys is True some
keys will not be copies (defined in python code)

:param header: header dictionary from readimage (ReadImage) function

:param comments: comment dictionary from readimage (ReadImage) function

:param hdict: dictionary or None, header dictionary to write to fits file
              if None hdict is created

            Must be in form:

                    hdict[key] = (value, comment)
            or
                    hdict[key] = value     (comment will be equal to
                                            "UNKNOWN"
:param forbid_keys: bool, if True uses the forbidden copy keys (defined in
                    spirouConfig.Constants.FORBIDDEN_COPY_KEYS() to remove
                    certain keys from those being copied, if False copies
                    all keys from input header

:return hdict: dictionary, (updated or new) header dictionary containing
               key/value pairs from the header (that are NOT in 
               spirouConfig.spirouConst.FORBIDDEN_COPY_KEY)
"""

CopyRootKeys = spirouFITS.copy_root_keys
"""
Copy keys from a filename to hdict

:param hdict: dictionary or None, header dictionary to write to fits file
              if None hdict is created
:param filename: string, location and filename of the FITS rec to open

:param ext: int, the extension of the FITS rec to open header from
            (defaults to 0)
:return:
"""

CorrectForDark = spirouImage.correct_for_dark
"""
Corrects "data" for "dark" using calibDB file (header must contain
value of p['ACQTIME_KEY'] as a keyword)

:param p: dictionary, parameter dictionary
:param image: numpy array (2D), the image
:param header: dictionary, the header dictionary created by
               spirouFITS.ReadImage
:param nfiles: int or None, number of files that created image (need to
               multiply by this to get the total dark) if None uses
               p['nbframes']
:param return_dark: bool, if True returns corrected_image and dark
                    if False (default) returns corrected_image

:return corrected_image: numpy array (2D), the dark corrected image
                         only returned if return_dark = True:
:return darkimage: numpy array (2D), the dark
"""

FitTilt = spirouImage.fit_tilt
"""
Fit the tilt (lloc['tilt'] with a polynomial of size = p['ic_tilt_filt']
return the coefficients, fit and residual rms in lloc dictionary

:param pp: dictionary, parameter dictionary
:param lloc: dictionary, parameter dictionary containing the data

:return lloc: dictionary, parameter dictionary containing the data
"""

FlipImage = spirouImage.flip_image
"""
Flips the image in the x and/or the y direction

:param image: numpy array (2D), the image
:param fliprows: bool, if True reverses row order (axis = 0)
:param flipcols: bool, if True reverses column order (axis = 1)

:return newimage: numpy array (2D), the flipped image
"""

GetAllSimilarFiles = spirouImage.get_all_similar_files
"""
Get all similar files in a directory with matching prefix and suffix defined
either by "prefix" and "suffix" or by p["ARG_FILE_NAMES"][0]

:param p: parameter dictionary, ParamDict containing constants
:param directory: string, the directory to search for files
:param prefix: string or None, if not None the prefix to search for, if
               None defines the prefix from the first 5 characters of
               p["ARG_FILE_NAMES"][0]
:param suffix: string  or None, if not None the suffix to search for, if
               None defines the prefix from the last 8 characters of
               p["ARG_FILE_NAMES"][0]

:return filelist: list of strings, the full paths of all files that are in
                  "directory" with the matching prefix and suffix defined
                  either by "prefix" and "suffix" or by
                  p["ARG_FILE_NAMES"][0]
"""

GetSigdet = spirouImage.get_sigdet
"""
Get sigdet from HEADER. Wrapper for spirouImage.get_param

:param p: parameter dictionary, ParamDict of constants
:param hdr: dictionary, header dictionary to extract
:param name: string or None, if not None the name for the parameter
             logged if there is an error in getting parameter, if name is 
             None the name is taken as "keyword"
:param return_value: bool, if True returns parameter, if False adds 
                     parameter to "p" parameter dictionary (and sets source)

:return value: if return_value is True value of parameter is returned
:return p: if return_value is False, updated parameter dictionary p with
           key = name is returned
"""

GetExpTime = spirouImage.get_exptime
"""
Get Exposure time from HEADER. Wrapper for spirouImage.get_param

:param p: parameter dictionary, ParamDict of constants
:param hdr: dictionary, header dictionary to extract
:param name: string or None, if not None the name for the parameter
             logged if there is an error in getting parameter, if name is 
             None the name is taken as "keyword"
:param return_value: bool, if True returns parameter, if False adds 
                     parameter to "p" parameter dictionary (and sets source)

:return value: if return_value is True value of parameter is returned
:return p: if return_value is False, updated parameter dictionary p with
           key = name is returned
"""

GetGain = spirouImage.get_gain
"""
Get Gain from HEADER. Wrapper for spirouImage.get_param

:param p: parameter dictionary, ParamDict of constants
:param hdr: dictionary, header dictionary to extract
:param name: string or None, if not None the name for the parameter
             logged if there is an error in getting parameter, if name is 
             None the name is taken as "keyword"
:param return_value: bool, if True returns parameter, if False adds 
                     parameter to "p" parameter dictionary (and sets source)

:return value: if return_value is True value of parameter is returned
:return p: if return_value is False, updated parameter dictionary p with
           key = name is returned
"""

GetAcqTime = spirouImage.get_acqtime
"""
Get the acquision time from the header file, if there is not header file
use the parameter dictionary "p" to open the header in 'arg_file_names[0]'

:param p: dictionary, parameter dictionary
:param hdr: dictionary, the header dictionary created by
            spirouFITS.ReadImage
:param name: string, the name in parameter dictionary to give to value
             if return_value is False (i.e. p[name] = value)
:param kind: string, 'human' for 'YYYY-mm-dd-HH-MM-SS.ss' or 'unix'
             for time since 1970-01-01
:param return_value: bool, if False value is returned in p as p[name]
                     if True value is returned

:return p or value: dictionary or string or float, if return_value is False
                    parameter dictionary is returned, if return_value is
                    True and kind=='human' returns a string, if return_value
                    is True and kind=='unix' returns a float
"""

ReadParam = spirouImage.get_param
"""
Get parameter from header "hdr" using "keyword" (keyword store constant)

:param p: parameter dictionary, ParamDict containing constants
:param hdr: dictionary, HEADER dictionary containing key/value pairs
            extracted from a FITS rec header
:param keyword: string, the keyword key (taken from "p") this allows
                getting of the keyword store from the parameter dictionary
:param name: string or None, if not None the name for the parameter
             logged if there is an error in getting parameter, if name is 
             None the name is taken as "keyword"
:param return_value: bool, if True returns parameter, if False adds 
                     parameter to "p" parameter dictionary (and sets source)
:param dtype: type or None, if not None then tries to convert raw
              parameter to type=dtype

:return value: if return_value is True value of parameter is returned
:return p: if return_value is False, updated parameter dictionary p with
           key = name is returned
"""

GetKey = spirouFITS.keylookup
"""
Looks for a key in dictionary "p" or "d", if has_default is True sets 
value of key to 'default' if not found else logs an error

:param p: dictionary, any dictionary
:param d: dictionary, any dictionary, if None uses parameter dictionary
:param key: string, key in the dictionary to find
:param has_default: bool, if True uses "default" as the value if key
                    not found
:param default: object, value of the key if not found and
                has_default is True

:return value: object, value of p[key] or default (if has_default=True)
"""

GetKeys = spirouFITS.keyslookup
"""
Looks for keys in dictionary "p" or "d", if has_default is True sets 
value of key to 'default' if not found else logs an error

:param p: dictionary, any dictionary
:param d: dictionary, any dictionary, if None uses parameter dictionary
:param keys: list of strings, keys in the dictionary to find
:param has_default: bool, if True uses "default" as the value if key
                    not found
:param defaults: list of objects or None, values of the keys if not
                 found and has_default is True

:return values: list of objects, values of p[key] for key in keys
                or default value for each key (if has_default=True)
"""

GetTilt = spirouImage.get_tilt
"""
Get the tilt by correlating the extracted fibers

:param pp: dictionary, parameter dictionary
:param lloc: dictionary, parameter dictionary containing the data
:param image: numpy array (2D), the image

:return lloc: dictionary, parameter dictionary containing the data
"""

GetTypeFromHeader = spirouFITS.get_type_from_header
"""
Special FITS HEADER keyword - get the type of file from a FITS file HEADER
using "keywordstore"

:param p: parameter dictionary, ParamDict containing constants
:param keywordstore: list, a keyword store in the form
                     [name, value, comment] where the format is
                     [string, object, string]
:param hdict: dictionary or None, the HEADER dictionary containing
              key/value pairs from a FITS HEADER, if None uses the
              header from "FITSFILENAME" in "p", unless filename is not None
              This hdict is used to get the type of file
:param filename: string or None, if not None and hdict is None, this is the
                 file which is used to extract the HEADER from to get
                 the type of file

:return ftype: string, the type of file (extracted from a HEADER dictionary/
               file) if undefined set to 'UNKNOWN'
"""

LocateBadPixels = spirouImage.locate_bad_pixels
"""
Locate the bad pixels in the flat image and the dark image

:param p: dictionary, parameter dictionary
:param fimage: numpy array (2D), the flat normalised image
:param fmed: numpy array (2D), the flat median normalised image
:param dimage: numpy array (2D), the dark image
:param wmed: float or None, if not None defines the median filter width
             if None uses p["BADPIX_MED_WID", see
             scipy.ndimage.filters.median_filter "size" for more details

:return bad_pix_mask: numpy array (2D), the bad pixel mask image
:return badpix_stats: list of floats, the statistics array:
                        Fraction of hot pixels from dark [%]
                        Fraction of bad pixels from flat [%]
                        Fraction of NaN pixels in dark [%]
                        Fraction of NaN pixels in flat [%]
                        Fraction of bad pixels with all criteria [%]
"""

MakeTable = spirouTable.make_table
"""
Construct an astropy table from columns and values

:param columns: list of strings, the list of column names
:param values: list of lists or numpy array (2D), the list of lists/array
               of values, first dimension must have same length as number
               of columns, there must be the same number of values in each
               column
:param formats: list of strings, the astropy formats for each column
                i.e. 0.2f  for a float with two decimal places, must have 
                same length as number of columns
:param units: list of strings, the units for each column, must have 
              same length as number of columns

:return table: astropy.table.Table instance, the astropy table containing
               all columns and data 
"""

MeasureDark = spirouImage.measure_dark
"""
Measure the dark pixels in "image"

:param pp: dictionary, parameter dictionary
:param image: numpy array (2D), the image
:param image_name: string, the name of the image (for logging)
:param short_name: string, suffix (for parameter naming -
                    parmaeters added to pp with suffix i)

:return pp: dictionary, parameter dictionary
"""

NormMedianFlat = spirouImage.normalise_median_flat
"""
Applies a median filter and normalises. Median filter is applied with width
"wmed" or p["BADPIX_FLAT_MED_WID"] if wmed is None) and then normalising by
the 90th percentile

:param p: parameter dictionary, ParamDict containing constants
:param image: numpy array (2D), the iamge to median filter and normalise
:param method: string, "new" or "old" if "new" uses np.percentile else
               sorts the flattened image and takes the "percentile" (i.e.
               90th) pixel value to normalise
:param wmed: float or None, if not None defines the median filter width
             if None uses p["BADPIX_MED_WID", see
             scipy.ndimage.filters.median_filter "size" for more details
:param percentile: float or None, if not None degines the percentile to 
                   normalise the image at, if None used from
                   p["BADPIX_NORM_PERCENTILE"] 

:return norm_med_image: numpy array (2D), the median filtered and normalised
                        image
:return norm_image: numpy array (2D), the normalised image
"""

ReadData = spirouFITS.readdata
"""
Reads the image 'fitsfilename' defined in p and adds files defined in
'arg_file_names' if add is True

:param p: dictionary, parameter dictionary
:param filename: string, filename of the image to read
:param log: bool, if True logs opening and size

:return image: numpy array (2D), the image
:return header: dictionary, the header file of the image
:return nx: int, the shape in the first dimension, i.e. data.shape[0]
:return ny: int, the shape in the second dimension, i.e. data.shape[1]
"""

ReadImage = spirouFITS.readimage
"""
Reads the image 'fitsfilename' defined in p and adds files defined in
'arg_file_names' if add is True

:param p: dictionary, parameter dictionary
:param filename: string or None, filename of the image to read, if None
                 then p['fitsfilename'] is used
:param log: bool, if True logs opening and size
:param kind: string or None, if defined names the image else just image,
             used in logging (if log = True)

:return image: numpy array (2D), the image
:return header: dictionary, the header file of the image
:return nx: int, the shape in the first dimension, i.e. data.shape[0]
:return ny: int, the shape in the second dimension, i.e. data.shape[1]
"""

ReadTable = spirouTable.read_table
"""
Reads a table from file "filename" in format "fmt", if colnames are defined
renames the columns to these name

:param filename: string, the filename and location of the table to read
:param fmt: string, the format of the table to read from (must be valid
            for astropy.table to read - see below)
:param colnames: list of strings or None, if not None renames all columns
                 to these strings, must be the same length as columns
                 in file that is read

:return None:
"""

ReadImageAndCombine = spirouFITS.readimage_and_combine
"""
Reads the image 'fitsfilename' defined in p and adds files defined in
'arg_file_names' if add is True

:param p: dictionary, parameter dictionary
:param framemath: string, controls how files should be added

            currently supported are:
            'add' or '+'           - adds the frames
            'sub' or '-'           - subtracts the frames
            'average' or 'mean'    - averages the frames
            'multiply' or '*'      - multiplies the frames
            'divide' or '/'        - divides the frames
            'none'                 - does not add
:param filename: string or None, filename of the image to read, if None
                 then p['fitsfilename'] is used
:param log: bool, if True logs opening and size

:return image: numpy array (2D), the image
:return header: dictionary, the header file of the image
:return nx: int, the shape in the first dimension, i.e. data.shape[0]
:return ny: int, the shape in the second dimension, i.e. data.shape[1]
"""

ReadFlatFile = spirouFITS.read_flat_file
"""
Reads the wave file (from calib database or filename)

:param p: dictionary, parameter dictionary
:param hdr: dictionary or None, the header dictionary to look for the
                 acquisition time in, if None loads the header from
                 p['fitsfilename']
:param filename: string or None, the filename and path of the tilt file,
                 if None gets the TILT file from the calib database
                 keyword "TILT"
:param key: string or None, if None key='WAVE' else uses string as key
            from calibDB (first entry) to get wave file

:return wave: list of the tilt for each order
"""

ReadHeader = spirouFITS.read_header
"""
Read the header from a file at "filepath" with extention "ext" (default=0)

:param p: dictionary, parameter dictionary
:param filepath: string, filename and path of FITS file to open
:param ext: int, extension in FITS rec to open (default = 0)

:return hdict: dictionary, the dictionary with key value pairs
"""

ReadKey = spirouFITS.read_key
"""
Read a key from hdict (or p if hdict is not defined) and return it's 
value.

:param p: dictionary, any dictionary
:param hdict: dictionary or None, the dictionary to add the key to once
              found, if None creates a new dictionary
:param key: string, key in the dictionary to find

:return value: object, the value of the key from hdict 
               (or p if hdict is None) 
"""

Read2Dkey = spirouFITS.read_key_2d_list
"""
Read a set of header keys that were created from a 2D list

:param p: parameter dictionary, ParamDict containing constants
:param hdict: dictionary, HEADER dictionary to extract key/value pairs from
:param key: string, prefix of HEADER key to construct 2D list from
             key[number] 

             where number = (row number * number of columns) + column number
             where column number = dim2 and row number = range(0, dim1)
:param dim1: int, the number of elements in dimension 1 (number of rows)
:param dim2: int, the number of columns in dimension 2 (number of columns)

:return value: numpy array (2D), the reconstructed 2D list of variables
               from the HEADER dictionary keys 
"""

ReadTiltFile = spirouFITS.read_tilt_file
"""
Reads the tilt file (from calib database or filename) and using the
'kw_TILT' keyword-store extracts the tilts for each order

:param p: dictionary, parameter dictionary
:param hdr: dictionary or None, the header dictionary to look for the
                 acquisition time in, if None loads the header from
                 p['fitsfilename']
:param filename: string or None, the filename and path of the tilt file,
                 if None gets the TILT file from the calib database
                 keyword "TILT"
:param key: string or None, if None key='TILT' else uses string as key
            from calibDB (first entry) to get tilt file

:return tilt: list of the tilt for each order
"""

ReadWaveFile = spirouFITS.read_wave_file
"""
Reads the wave file (from calib database or filename)

:param p: dictionary, parameter dictionary
:param hdr: dictionary or None, the header dictionary to look for the
                 acquisition time in, if None loads the header from
                 p['fitsfilename']
:param filename: string or None, the filename and path of the tilt file,
                 if None gets the TILT file from the calib database
                 keyword "TILT"
:param key: string or None, if None key='WAVE' else uses string as key
            from calibDB (first entry) to get wave file

:param return_header: bool, if True returns header file else just returns
                      wave file
:return wave: list of the tilt for each order
"""

ReadOrderProfile = spirouFITS.read_order_profile_superposition
"""
Read the order profile superposition image from either "filename" (if not
None) or get filename from the calibration database using "p"

"ORDER_PROFILE_{X}" must be in calibration database if filename is None
where X is either p["ORDERP_FILE"] or p["FIBER"] (presedence in that order)

:param p: parameter dictionary, ParamDict containing constants
:param hdr: dictionary or None, header dictionary (used to get the 
            acquisition time if trying to get "ORDER_PROFILE_{X}" from 
            the calibration database, if None uses the header from the
            first file in "ARG_FILE_NAMES" i.e. "FITSFILENAME"
:param filename: string or None, if defined no need for "hdr" or keys from
                 "p" the order profile is read straight from "filename"

:return orderp: numpy array (2D), the order profile image read from file 
"""

ResizeImage = spirouImage.resize
"""
Resize an image based on a pixel values

:param image: numpy array (2D), the image
:param x: None or numpy array (1D), the list of x pixels
:param y: None or numpy array (1D), the list of y pixels
:param xlow: int, x pixel value (x, y) in the bottom left corner,
             default = 0
:param xhigh:  int, x pixel value (x, y) in the top right corner,
             if None default is image.shape(1)
:param ylow: int, y pixel value (x, y) in the bottom left corner,
             default = 0
:param yhigh: int, y pixel value (x, y) in the top right corner,
             if None default is image.shape(0)
:param getshape: bool, if True returns shape of newimage with newimage

if getshape = True
:return newimage: numpy array (2D), the new resized image
:return nx: int, the shape in the first dimension, i.e. data.shape[0]
:return ny: int, the shape in the second dimension, i.e. data.shape[1]

if getshape = False
:return newimage: numpy array (2D), the new resized image
"""

WriteImage = spirouFITS.writeimage
"""
Writes an image and its header to file

:param filename: string, filename to save the fits file to
:param image: numpy array (2D), the image
:param hdict: dictionary, header dictionary to write to fits file

            Must be in form:

                    hdict[key] = (value, comment)
            or
                    hdict[key] = value     (comment will be equal to
                                            "UNKNOWN"
:param dtype: None or hdu format type, forces the image to be in the
              format type specified (if not None)

              valid formats are for example: 'int32', 'float64'

:return:
"""

WriteTable = spirouTable.write_table
"""
Writes a table to file "filename" with format "fmt"

:param filename: string, the filename and location of the table to read
:param fmt: string, the format of the table to read from (must be valid
            for astropy.table to read - see below)

:return None:
"""