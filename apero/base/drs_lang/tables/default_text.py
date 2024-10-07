
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 09:10

@author: cook
"""
from apero.base import base
from apero.base.drs_lang import drs_lang_list


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.tables.default_text.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define functions
# =============================================================================
# Get the language list
langlist = drs_lang_list.LanguageList(__NAME__)


# =============================================================================
# 00-000-00000 
# =============================================================================
item = langlist.create('00-000-00000', kind='error-code')
item.value['ENG'] = 'This is the Default error message'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# 00-000-99999 
# =============================================================================
item = langlist.create('00-000-99999', kind='nan-code')
item.value['ENG'] = 'This is a test message'
item.value['FR'] = 'Ceci est un message test'
item.arguments = 'None'
item.comment = 'Test message'
langlist.add(item)

# =============================================================================
# 00-000-00001 
# =============================================================================
item = langlist.create('00-000-00001', kind='error-code')
item.value['ENG'] = 'Cannot find module \'{0}\' \n\t Problem with recipe defintion \n\tRecipe name must match recipe python file name and be in PYTHONPATH'
item.arguments = 'None'
item.comment = 'Means that recipe was not found in PYTHONPATH (either PYTHONPATH is wrong or recipe is not in PYTHONPATH)'
langlist.add(item)

# =============================================================================
# 00-000-00002 
# =============================================================================
item = langlist.create('00-000-00002', kind='error-code')
item.value['ENG'] = 'Error {0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Catch a error pushed out by python'
langlist.add(item)

# =============================================================================
# 00-000-00003 
# =============================================================================
item = langlist.create('00-000-00003', kind='error-code')
item.value['ENG'] = 'Cannot import module \'{0}\' from \'{1}\' \n\t Function = {2} \n\t Error {3}: {4} \n\n Traceback: \n\n {5}'
item.arguments = 'None'
item.comment = 'Means that cannot import module'
langlist.add(item)

# =============================================================================
# 00-000-00004 
# =============================================================================
item = langlist.create('00-000-00004', kind='error-code')
item.value['ENG'] = 'MainError: Module {0} has not attribute \'main\' \n\t Path = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that module does not have main function'
langlist.add(item)

# =============================================================================
# 00-000-00005 
# =============================================================================
item = langlist.create('00-000-00005', kind='error-code')
item.value['ENG'] = 'Error {0} does not support OS (OS = {1})'
item.arguments = 'None'
item.comment = 'Means that setup does not support OS type'
langlist.add(item)

# =============================================================================
# 00-000-00006 
# =============================================================================
item = langlist.create('00-000-00006', kind='error-code')
item.value['ENG'] = 'Error setup file \'{0}\' does not exist'
item.arguments = 'None'
item.comment = 'Means that setup file does not exist'
langlist.add(item)

# =============================================================================
# 00-000-00007 
# =============================================================================
item = langlist.create('00-000-00007', kind='error-code')
item.value['ENG'] = 'Error: Cannot chmod 777 on file {0}'
item.arguments = 'None'
item.comment = 'Means we cannot make file executable'
langlist.add(item)

# =============================================================================
# 00-000-00008 
# =============================================================================
item = langlist.create('00-000-00008', kind='error-code')
item.value['ENG'] = 'Error: Cannot run update. Must be in an apero environment (i.e. source apero.{SYSTEM}.setup).'
item.arguments = 'None'
item.comment = 'Means we cannot run setup update as we are not in an apero environment'
langlist.add(item)

# =============================================================================
# 00-000-00009 
# =============================================================================
item = langlist.create('00-000-00009', kind='error-code')
item.value['ENG'] = '\tFatal Error: Python 2 is not supported'
item.arguments = 'None'
item.comment = 'Means that user is using python 2'
langlist.add(item)

# =============================================================================
# 00-000-00010 
# =============================================================================
item = langlist.create('00-000-00010', kind='error-code')
item.value['ENG'] = 'Module name \'{0}\' error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that module name is bad'
langlist.add(item)

# =============================================================================
# 00-000-00011 
# =============================================================================
item = langlist.create('00-000-00011', kind='error-code')
item.value['ENG'] = '\tFatal Error: {0} requires module {1} to be installed \n\t i.e. {2}'
item.arguments = 'None'
item.comment = 'Means required module not installed'
langlist.add(item)

# =============================================================================
# 00-000-00012 
# =============================================================================
item = langlist.create('00-000-00012', kind='error-code')
item.value['ENG'] = 'Unable to find {0}'
item.arguments = 'None'
item.comment = 'Means that we were unable to find apero'
langlist.add(item)

# =============================================================================
# 00-000-00013 
# =============================================================================
item = langlist.create('00-000-00013', kind='error-code')
item.value['ENG'] = 'Cannot import {0}'
item.arguments = 'None'
item.comment = 'Means we cannot import module'
langlist.add(item)

# =============================================================================
# 00-000-00014 
# =============================================================================
item = langlist.create('00-000-00014', kind='error-code')
item.value['ENG'] = 'Language Error, cannot find key ‘{0}’ in language table.'
item.arguments = 'None'
item.comment = 'Means that we do not have the language entry given'
langlist.add(item)

# =============================================================================
# 00-001-00000 
# =============================================================================
item = langlist.create('00-001-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Function Input Error'
item.arguments = 'None'
item.comment = 'Dev Error: Class/Function Input Error'
langlist.add(item)

# =============================================================================
# 00-001-00001 
# =============================================================================
item = langlist.create('00-001-00001', kind='nan-code')
item.value['ENG'] = 'Must define an instrument. \n\t function = {0}'
item.value['FR'] = 'Doit définir un instrument. \n\t fonction = {0}'
item.arguments = 'None'
item.comment = 'In \'find_recipe\' function when instrument is None ? i.e. we must have an instrument to get a recipe'
langlist.add(item)

# =============================================================================
# 00-001-00002 
# =============================================================================
item = langlist.create('00-001-00002', kind='error-code')
item.value['ENG'] = '{0} : Filename is not set. Must set a filename with \'{1}\' first.'
item.arguments = 'None'
item.comment = 'Means that file was not set i.e. DrsInputFile.function was not used before using this function'
langlist.add(item)

# =============================================================================
# 00-001-00003 
# =============================================================================
item = langlist.create('00-001-00003', kind='error-code')
item.value['ENG'] = 'No params set for {0}: filename={1}. Run {2} first.'
item.arguments = 'None'
item.comment = 'Means that params was not set i.e. DrsInputFile.function was not used before using this function'
langlist.add(item)

# =============================================================================
# 00-001-00004 
# =============================================================================
item = langlist.create('00-001-00004', kind='error-code')
item.value['ENG'] = '{0}: Data is not set. Must read fits using {1} first.'
item.arguments = 'None'
item.comment = 'Means that data is not set i.e. DrsInputFile.function was not used before using this function'
langlist.add(item)

# =============================================================================
# 00-001-00005 
# =============================================================================
item = langlist.create('00-001-00005', kind='error-code')
item.value['ENG'] = ' \'keys\' must be a valid python list \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'keys\' input to DrsFitsFile.read_header_keys was not a list'
langlist.add(item)

# =============================================================================
# 00-001-00006 
# =============================================================================
item = langlist.create('00-001-00006', kind='error-code')
item.value['ENG'] = ' \'defaults\' must be same length as \'keys\' \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that list \'defaults\' was not the same length as \'key\'s (in DrsFitsFile)'
langlist.add(item)

# =============================================================================
# 00-001-00007 
# =============================================================================
item = langlist.create('00-001-00007', kind='error-code')
item.value['ENG'] = ' \'defaults\' must be a valid python list \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'defaults\' input to DrsFitsFile.read_header_keys was not a list'
langlist.add(item)

# =============================================================================
# 00-001-00008 
# =============================================================================
item = langlist.create('00-001-00008', kind='error-code')
item.value['ENG'] = 'Key was set (key = \'{0}\') but was not found in parameter dictionary. \n\t Either make sure key is in parameter dictionary or define \'keyword\', \'value\' and \'comment\'. \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'kwstore\' or \'key and \'comment\' were not defined (one or the other has to be) in add_header_key'
langlist.add(item)

# =============================================================================
# 00-001-00009 
# =============================================================================
item = langlist.create('00-001-00009', kind='error-code')
item.value['ENG'] = 'Either \'kwstore\' or (\'key\' and \'comment\') must be defined \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'kwstore\' or \'key and \'comment\' were not defined (one or the other has to be) in add_header_keys'
langlist.add(item)

# =============================================================================
# 00-001-00010 
# =============================================================================
item = langlist.create('00-001-00010', kind='error-code')
item.value['ENG'] = ' \'kwstores\' must be a list \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'kwstores\' input to DrsFitsFile.add_header_keys was not a list'
langlist.add(item)

# =============================================================================
# 00-001-00011 
# =============================================================================
item = langlist.create('00-001-00011', kind='error-code')
item.value['ENG'] = ' \'keys\' must be a list (or \'kwstores\' must be defined) \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'keys\' must be a list or \'kwstores\' must be defined  DrsFitsFile.add_header_keys'
langlist.add(item)

# =============================================================================
# 00-001-00012 
# =============================================================================
item = langlist.create('00-001-00012', kind='error-code')
item.value['ENG'] = ' \'comments\' must be a list (or \'kwstores\' must be defined) \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'comments\' must be a list or \'kwstores\' must be defined in DrsFitsFile.add_header_keys'
langlist.add(item)

# =============================================================================
# 00-001-00013 
# =============================================================================
item = langlist.create('00-001-00013', kind='error-code')
item.value['ENG'] = ' \'keys\' must be the same length as \'comment\' \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'keys\' and \'comments\' were not the same length in DrsFitsFile.add_header_keys'
langlist.add(item)

# =============================================================================
# 00-001-00014 
# =============================================================================
item = langlist.create('00-001-00014', kind='error-code')
item.value['ENG'] = 'Either \'kwstore\' or (\'key\' and \'comment\') must be defined \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'kwstore\' or \'key and \'comment\' were not defined (one or the other has to be) in DrsFitesFile.add_header_key_1d_list'
langlist.add(item)

# =============================================================================
# 00-001-00015 
# =============================================================================
item = langlist.create('00-001-00015', kind='error-code')
item.value['ENG'] = 'Either \'kwstore\' or (\'key\' and \'comment\') must be defined \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'kwstore\' or \'key and \'comment\' were not defined (one or the other has to be) in DrsFitesFile.add_header_key_2d_list'
langlist.add(item)

# =============================================================================
# 00-001-00016 
# =============================================================================
item = langlist.create('00-001-00016', kind='error-code')
item.value['ENG'] = 'There was a problem with the kwstore=\'{0}\' \n\t It must be a list/tuple with the following format \n\t\t [STRING, OBJECT, STRING] \n\t\t where the first element is the HEADER name of the keyword \n\t\t where the second is the default value of the keyword \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means there was a problem in the definition of the keyword store. (key word store should be a 3 element list = [key, value, comment]'
langlist.add(item)

# =============================================================================
# 00-001-00017 
# =============================================================================
item = langlist.create('00-001-00017', kind='error-code')
item.value['ENG'] = 'Function {0} requires \'infile\' to be set.'
item.arguments = 'None'
item.comment = 'output filenames function requires infile to be set'
langlist.add(item)

# =============================================================================
# 00-001-00018 
# =============================================================================
item = langlist.create('00-001-00018', kind='error-code')
item.value['ENG'] = 'Function {0} requires \'outfile\' to be set.'
item.arguments = 'None'
item.comment = 'output filenames function requires outfile to be set'
langlist.add(item)

# =============================================================================
# 00-001-00019 
# =============================================================================
item = langlist.create('00-001-00019', kind='error-code')
item.value['ENG'] = 'All QC parameters must be the same length \n\t Lengths = {0} \n\t function = {1}'
item.arguments = 'None'
item.comment = 'QC error on number of qc parameters'
langlist.add(item)

# =============================================================================
# 00-001-00020 
# =============================================================================
item = langlist.create('00-001-00020', kind='error-code')
item.value['ENG'] = '\'infiles\' must be a list of DrsFiles \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that the \'combine\' function was used by \'infiles\' was not a list'
langlist.add(item)

# =============================================================================
# 00-001-00021 
# =============================================================================
item = langlist.create('00-001-00021', kind='error-code')
item.value['ENG'] = 'All \'infiles\' must be the same type of DrsFile to combine.\n\t Input file 1: {0}\t Input file {1}: {2}  \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there were \'infiles\' that did not have the same name (and thus shouldn\'t be combined'
langlist.add(item)

# =============================================================================
# 00-001-00022 
# =============================================================================
item = langlist.create('00-001-00022', kind='error-code')
item.value['ENG'] = 'Math was defined incorrectly for combine function (math={0}). \n\t Available math functions are: {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the incorrect \'math\' was set in the call to combine function'
langlist.add(item)

# =============================================================================
# 00-001-00023 
# =============================================================================
item = langlist.create('00-001-00023', kind='error-code')
item.value['ENG'] = '{0}\' and \'{1}\' cannot have the same values (={2}). \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that xlow and xhigh (or ylow and yhigh) had the same value in the resize function'
langlist.add(item)

# =============================================================================
# 00-001-00024 
# =============================================================================
item = langlist.create('00-001-00024', kind='error-code')
item.value['ENG'] = 'Cannot resize image to ({0}-{1} by {2}-{3}) \n\t Error {4}: {5} \n\t function = {6}'
item.arguments = 'None'
item.comment = 'Means that there was an error using np.take in resize function'
langlist.add(item)

# =============================================================================
# 00-001-00025 
# =============================================================================
item = langlist.create('00-001-00025', kind='error-code')
item.value['ENG'] = 'All pixels were removed in resizing ({0}-{1} by {2}-{3})  \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that resize created a blank image'
langlist.add(item)

# =============================================================================
# 00-001-00026 
# =============================================================================
item = langlist.create('00-001-00026', kind='error-code')
item.value['ENG'] = '\'Image\' is not a valid numpy array. \n\t Error {0}: {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was an error doing np.array(data)'
langlist.add(item)

# =============================================================================
# 00-001-00027 
# =============================================================================
item = langlist.create('00-001-00027', kind='error-code')
item.value['ENG'] = 'Cannot update {0} database. \n\t Given \'outfile\' ({1}) does not have \'hdict\' or \'header\' defined. \n\t Outfile DrsFitsFile must have \'hdict\' or \'header\' to get required parameters from updating the database). \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that \'hdict\' was not found in outfile (when trying to update database)'
langlist.add(item)

# =============================================================================
# 00-001-00028 
# =============================================================================
item = langlist.create('00-001-00028', kind='error-code')
item.value['ENG'] = '{0}: Cannot get time from {1} (missing). \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that \'hdict\' (outfile.hdict or outfile.header) did not contain \'timekey\''
langlist.add(item)

# =============================================================================
# 00-001-00029 
# =============================================================================
item = langlist.create('00-001-00029', kind='error-code')
item.value['ENG'] = '{0}: Cannot convert time=\'{1}\' (format={2}, dtype={3}) to astropy time. \n\t Error {4}: {5} \n\t function = {6}'
item.arguments = 'None'
item.comment = 'Means that we could not convert \'raw_time\' to an astropy time object'
langlist.add(item)

# =============================================================================
# 00-001-00030 
# =============================================================================
item = langlist.create('00-001-00030', kind='error-code')
item.value['ENG'] = '{0}: Invalid kind. Kind = {1}. \n\t Should be: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that the \'kind\' was not valid for _get_time() function'
langlist.add(item)

# =============================================================================
# 00-001-00031 
# =============================================================================
item = langlist.create('00-001-00031', kind='error-code')
item.value['ENG'] = 'Could not construct output filename. Filename = {0} does not have required extension ({1}). \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that extension was wrong when trying to get outfilename'
langlist.add(item)

# =============================================================================
# 00-001-00032 
# =============================================================================
item = langlist.create('00-001-00032', kind='error-code')
item.value['ENG'] = 'Must define keyword “fiber” for drs file = {0}. \n\t Function = {1} (or in definition of drs file instance)'
item.arguments = 'None'
item.comment = 'Means that fiber was not defined when trying to get outfilename'
langlist.add(item)

# =============================================================================
# 00-001-00033 
# =============================================================================
item = langlist.create('00-001-00033', kind='error-code')
item.value['ENG'] = 'npy file must have extension \'.npy\'. Current value = {0} \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that .npy file did not have extension \'.npy\''
langlist.add(item)

# =============================================================================
# 00-001-00034 
# =============================================================================
item = langlist.create('00-001-00034', kind='error-code')
item.value['ENG'] = '\'filename\' or \'header\' must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'filename\' was None and header was None in \'load_calib_file\''
langlist.add(item)

# =============================================================================
# 00-001-00035 
# =============================================================================
item = langlist.create('00-001-00035', kind='error-code')
item.value['ENG'] = '\'filename\' or \'key\' must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'filename\' was None and key was None in \'load_calib_file\''
langlist.add(item)

# =============================================================================
# 00-001-00036 
# =============================================================================
item = langlist.create('00-001-00036', kind='error-code')
item.value['ENG'] = 'Calibration file could not be found. \n\t Tried: {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that we are in \'guess\' mode but could not find the calib file'
langlist.add(item)

# =============================================================================
# 00-001-00037 
# =============================================================================
item = langlist.create('00-001-00037', kind='error-code')
item.value['ENG'] = 'where\' was not valid. Must be {0}. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'where\' was not valid (must be \'calibration\' or \'telluric\' or \'guess\')'
langlist.add(item)

# =============================================================================
# 00-001-00038 
# =============================================================================
item = langlist.create('00-001-00038', kind='error-code')
item.value['ENG'] = 'kind\' was not valid. Must be {0}. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'kind\' was not valid (must be \'image\' or \'table\')'
langlist.add(item)

# =============================================================================
# 00-001-00039 
# =============================================================================
item = langlist.create('00-001-00039', kind='error-code')
item.value['ENG'] = 'Database {0}. \'hdict\' or \'header\' must be set. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'header\' and \'hdict\' were both not provided for \'_get_time\''
langlist.add(item)

# =============================================================================
# 00-001-00040 
# =============================================================================
item = langlist.create('00-001-00040', kind='error-code')
item.value['ENG'] = '\'recipe\' or \'recipename\' must be provided. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that \'recipe\' or \'recipename\' were not provided'
langlist.add(item)

# =============================================================================
# 00-001-00041 
# =============================================================================
item = langlist.create('00-001-00041', kind='error-code')
item.value['ENG'] = 'Function {0} requires ‘filename’ to be set in file definitions.'
item.arguments = 'None'
item.comment = 'Means that output_filenames ‘set_file’ did not have ‘filename’ set'
langlist.add(item)

# =============================================================================
# 00-001-00042 
# =============================================================================
item = langlist.create('00-001-00042', kind='error-code')
item.value['ENG'] = 'Cannot combine. Mode=\'{0}\' in invalid. \n\t Available modes = {1} \n\t Funcion = {2}'
item.arguments = 'None'
item.comment = 'Means that math defined for combine was not valid'
langlist.add(item)

# =============================================================================
# 00-001-00043 
# =============================================================================
item = langlist.create('00-001-00043', kind='error/warning_6-code')
item.value['ENG'] = 'Internal error in recipe {0}. Controller recipe ({1}) cannot continue'
item.arguments = 'None'
item.comment = 'Means that there was an error inside loop function'
langlist.add(item)

# =============================================================================
# 00-001-00044 
# =============================================================================
item = langlist.create('00-001-00044', kind='error-code')
item.value['ENG'] = 'Fmt=\'{0}\' is incorrect \n\t Must be: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that fmt is incorrect in large_image_combine'
langlist.add(item)

# =============================================================================
# 00-001-00045 
# =============================================================================
item = langlist.create('00-001-00045', kind='error-code')
item.value['ENG'] = 'Files are not the same shape\n\tFile[0] = ({0}x{1}) \n\tFile[{2}] = ({3}x{4})\n\tFile[0]: {5}\n\tFile[{2}]: {6}\n\tFunction={7}'
item.arguments = 'None'
item.comment = 'Means that files are not the same shape in large_image_combine'
langlist.add(item)

# =============================================================================
# 00-001-00046 
# =============================================================================
item = langlist.create('00-001-00046', kind='error-code')
item.value['ENG'] = 'Module \'{0}\' is required to have class \'{1}\' \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that module does not have class'
langlist.add(item)

# =============================================================================
# 00-001-00047 
# =============================================================================
item = langlist.create('00-001-00047', kind='error-code')
item.value['ENG'] = 'Dev Error: Const mod path \'{0}\' does not exist. \n\t Path = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that Const mod path does not exist'
langlist.add(item)

# =============================================================================
# 00-001-00048 
# =============================================================================
item = langlist.create('00-001-00048', kind='error-code')
item.value['ENG'] = 'DevError: No config directories found. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that no config directorys found'
langlist.add(item)

# =============================================================================
# 00-001-00049 
# =============================================================================
item = langlist.create('00-001-00049', kind='error-code')
item.value['ENG'] = 'DevError: Const mod scripts missing. \n\t Found = {0} \n\t Required = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that const mod script is missing entries'
langlist.add(item)

# =============================================================================
# 00-001-00050 
# =============================================================================
item = langlist.create('00-001-00050', kind='error-code')
item.value['ENG'] = '\'params\' must be None or ParamDict (type={0}) = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that display function params is not None or Paramdict'
langlist.add(item)

# =============================================================================
# 00-001-00051 
# =============================================================================
item = langlist.create('00-001-00051', kind='error-code')
item.value['ENG'] = 'Either \'header\' or \'infile\' (DrsFitsFile) must be set to get mid observation time. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that header and infile were not set in get_mid_obs_time'
langlist.add(item)

# =============================================================================
# 00-001-00052 
# =============================================================================
item = langlist.create('00-001-00052', kind='error-code')
item.value['ENG'] = 'Fiber Constant Error. Instrument requires key = {0}'
item.arguments = 'None'
item.comment = 'Means that we are missing key from constants'
langlist.add(item)

# =============================================================================
# 00-001-00053 
# =============================================================================
item = langlist.create('00-001-00053', kind='error-code')
item.value['ENG'] = 'DrsOutFile Error: pos must be an integer (value = {0) \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that pos was not an int when adding extension to DrsOutFile'
langlist.add(item)

# =============================================================================
# 00-001-00054 
# =============================================================================
item = langlist.create('00-001-00054', kind='error-code')
item.value['ENG'] = 'No good calibrations: \n{0}'
item.arguments = 'None'
item.comment = 'Means that no files were left after combine metric applied'
langlist.add(item)

# =============================================================================
# 00-001-00055 
# =============================================================================
item = langlist.create('00-001-00055', kind='error-code')
item.value['ENG'] = 'Input list ‘{0}’ was wrong length (length = {1} required = {2}) \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that snapshot table parameter was wrong length'
langlist.add(item)

# =============================================================================
# 00-001-00056 
# =============================================================================
item = langlist.create('00-001-00056', kind='error-code')
item.value['ENG'] = 'Input ‘{0}’ must be a list \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that snapshot table parameter was not a list'
langlist.add(item)

# =============================================================================
# 00-001-00057 
# =============================================================================
item = langlist.create('00-001-00057', kind='error-code')
item.value['ENG'] = 'Filename is neither set in the class definition or given as an argument. Function = {0}'
item.arguments = 'None'
item.comment = 'Means that filename was not set in id_drs_file'
langlist.add(item)

# =============================================================================
# 00-001-00058 
# =============================================================================
item = langlist.create('00-001-00058', kind='error-code')
item.value['ENG'] = 'Required header key \'{0}\' not found (file={1}) \n\t Function: {2}'
item.arguments = 'None'
item.comment = 'Means required header key was not found'
langlist.add(item)

# =============================================================================
# 00-001-00059 
# =============================================================================
item = langlist.create('00-001-00059', kind='error-code')
item.value['ENG'] = 'Units for key ‘{0}’ do not match. \n\tCurrent: {1}\n\tDesired: {2}'
item.arguments = 'None'
item.comment = 'Means that astropy units do not match and we cannot convert'
langlist.add(item)

# =============================================================================
# 00-002-00000 
# =============================================================================
item = langlist.create('00-002-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Class Input Error'
item.arguments = 'None'
item.comment = 'Dev Error: Database Errors'
langlist.add(item)

# =============================================================================
# 00-002-00001 
# =============================================================================
item = langlist.create('00-002-00001', kind='error-code')
item.value['ENG'] = 'Database name \'{0}\' invalid. Must be \'{1}\' \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that database name was not found'
langlist.add(item)

# =============================================================================
# 00-002-00002 
# =============================================================================
item = langlist.create('00-002-00002', kind='error-code')
item.value['ENG'] = '\'key_col\'={0} was not found in colnames for {1} database. \n\t columns are: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that database key_col was not found in database colnames'
langlist.add(item)

# =============================================================================
# 00-002-00003 
# =============================================================================
item = langlist.create('00-002-00003', kind='error-code')
item.value['ENG'] = '\'time_col\'={0} was not found in colnames for {1} database. \n\t columns are: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that database time_col was not found in database colnames'
langlist.add(item)

# =============================================================================
# 00-002-00004 
# =============================================================================
item = langlist.create('00-002-00004', kind='error-code')
item.value['ENG'] = '\'file_col\'={0} was not found in colnames for {1} database. \n\t columns are: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that database file_col was not found in database colnames'
langlist.add(item)

# =============================================================================
# 00-002-00005 
# =============================================================================
item = langlist.create('00-002-00005', kind='error-code')
item.value['ENG'] = 'Incorrect line in {0} database. \n\t Line {1}: \'{2}\' \n\t Should have values: {3}\n\t file = {4}  \n\t function = {5}'
item.arguments = 'None'
item.comment = 'Means that a line in database does not have the correct number of items'
langlist.add(item)

# =============================================================================
# 00-002-00006 
# =============================================================================
item = langlist.create('00-002-00006', kind='error-code')
item.value['ENG'] = 'No entries found in {0} database for key=\'{1} \n\t Keys must be older than: {2} \n\t  file = {3}  \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we have no entries for this key'
langlist.add(item)

# =============================================================================
# 00-002-00007 
# =============================================================================
item = langlist.create('00-002-00007', kind='error-code')
item.value['ENG'] = 'Cannot convert time in {0} database to astropy.time object. \n\t Line {1}: {2} \n\t Error {3}: {4} \n\t file = {5} \n\t function = {6} '
item.arguments = 'None'
item.comment = 'Means that we cannot convert unix time to astropy time object'
langlist.add(item)

# =============================================================================
# 00-002-00008 
# =============================================================================
item = langlist.create('00-002-00008', kind='error-code')
item.value['ENG'] = 'mode\' set to \'{0}\' for {1} database, must provide \'use_time\'. \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that mode was set but no time was given'
langlist.add(item)

# =============================================================================
# 00-002-00009 
# =============================================================================
item = langlist.create('00-002-00009', kind='error-code')
item.value['ENG'] = 'No entries found in {0} database for key=\'{1}\' older than {2} (mode = \'older\'). \n\t filename = {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that there were no files older than \'usetime\''
langlist.add(item)

# =============================================================================
# 00-002-00010 
# =============================================================================
item = langlist.create('00-002-00010', kind='error-code')
item.value['ENG'] = 'Database name not set for DrsFitsFile=\'{0}\'  \n\t Must be {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have database name set'
langlist.add(item)

# =============================================================================
# 00-002-00011 
# =============================================================================
item = langlist.create('00-002-00011', kind='error-code')
item.value['ENG'] = 'Database name invalid for DrsFitsFile=\'{0}\' (value=\'{1}\') \n\t Must be {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have valid database name'
langlist.add(item)

# =============================================================================
# 00-002-00012 
# =============================================================================
item = langlist.create('00-002-00012', kind='error-code')
item.value['ENG'] = 'Database key not set for DrsFitsFile=\'{0}\'  \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have database key set'
langlist.add(item)

# =============================================================================
# 00-002-00013 
# =============================================================================
item = langlist.create('00-002-00013', kind='error-code')
item.value['ENG'] = 'n_entries\' must be an integer or string (\'all\') \n\t n_entries = {0} (type={1}) \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that \'n_entries\' was invalid'
langlist.add(item)

# =============================================================================
# 00-002-00014 
# =============================================================================
item = langlist.create('00-002-00014', kind='error-code')
item.value['ENG'] = 'Database {0}. Error copying from {1} to {2} \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that there was an IO error copying database file'
langlist.add(item)

# =============================================================================
# 00-002-00015 
# =============================================================================
item = langlist.create('00-002-00015', kind='error-code')
item.value['ENG'] = 'No entries found in {0} database for key=\'{1} \n\t Available keys: {2} \n\t  file = {3}  \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we have no entries for this key'
langlist.add(item)

# =============================================================================
# 00-002-00016 
# =============================================================================
item = langlist.create('00-002-00016', kind='error-code')
item.value['ENG'] = 'Directory {0} invalid for database: {1} \n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means DatabaseManager could not set path dirname is bad'
langlist.add(item)

# =============================================================================
# 00-002-00017 
# =============================================================================
item = langlist.create('00-002-00017', kind='error-code')
item.value['ENG'] = 'Directory {0} does not exist (database = {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that DatabaseManager dirname does not exist'
langlist.add(item)

# =============================================================================
# 00-002-00018 
# =============================================================================
item = langlist.create('00-002-00018', kind='error-code')
item.value['ENG'] = 'Database path {0} does not exist (database = {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that DatabaseManager abs path for database does not exist'
langlist.add(item)

# =============================================================================
# 00-002-00019 
# =============================================================================
item = langlist.create('00-002-00019', kind='error-code')
item.value['ENG'] = 'Cannot add {0} to {1} database. Must be added to {2} database. \n\t Filename = {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that DatabaseManager and drsfile are not compatible'
langlist.add(item)

# =============================================================================
# 00-002-00020 
# =============================================================================
item = langlist.create('00-002-00020', kind='error-code')
item.value['ENG'] = 'Database {0} - file was defined in {1} but path does not exist. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that DatabaseManager could not get file from inputs (but they were defined)'
langlist.add(item)

# =============================================================================
# 00-002-00021 
# =============================================================================
item = langlist.create('00-002-00021', kind='error-code')
item.value['ENG'] = 'Time mode invalid for Calibration database. Input = {0}  Require: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that time mode was not valid for CalibrationDatabaseManager'
langlist.add(item)

# =============================================================================
# 00-002-00022 
# =============================================================================
item = langlist.create('00-002-00022', kind='error-code')
item.value['ENG'] = 'Database {0} - kind = \'{1}\' invalid. \n\t Valid kinds are: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that kind was not valid for IndexDatabaseManager'
langlist.add(item)

# =============================================================================
# 00-002-00023 
# =============================================================================
item = langlist.create('00-002-00023', kind='error-code')
item.value['ENG'] = 'Database {0} - filename = \'{1}\' was not found \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means filename was not found for IndexDatabaseManager'
langlist.add(item)

# =============================================================================
# 00-002-00024 
# =============================================================================
item = langlist.create('00-002-00024', kind='error-code')
item.value['ENG'] = 'Database {0} was not loaded (run database.load_db() first) \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that database was not loaded'
langlist.add(item)

# =============================================================================
# 00-002-00025 
# =============================================================================
item = langlist.create('00-002-00025', kind='error-code')
item.value['ENG'] = 'Key \'{0}\' does not exist in language database. \n\t args: {1} \n\t kwargs: {2}'
item.arguments = 'None'
item.comment = 'Means that key does not exist in language database'
langlist.add(item)

# =============================================================================
# 00-002-00026 
# =============================================================================
item = langlist.create('00-002-00026', kind='error-code')
item.value['ENG'] = 'Cannot open file = \'{0}\' \n\t Error was {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we cannot open xls language file'
langlist.add(item)

# =============================================================================
# 00-002-00027 
# =============================================================================
item = langlist.create('00-002-00027', kind='error-code')
item.value['ENG'] = 'Cannot find database file {0} in directory {1}'
item.arguments = 'None'
item.comment = 'Means that we cannot find database file in directory'
langlist.add(item)

# =============================================================================
# 00-002-00028 
# =============================================================================
item = langlist.create('00-002-00028', kind='error-code')
item.value['ENG'] = 'Database Error: {0}'
item.arguments = 'None'
item.comment = 'Prints the generic database error'
langlist.add(item)

# =============================================================================
# 00-002-00029 
# =============================================================================
item = langlist.create('00-002-00029', kind='error-code')
item.value['ENG'] = '\tDatabase path: {0}'
item.arguments = 'None'
item.comment = 'Adds database path to generic database error'
langlist.add(item)

# =============================================================================
# 00-002-00030 
# =============================================================================
item = langlist.create('00-002-00030', kind='error-code')
item.value['ENG'] = '\tFunction = {0}'
item.arguments = 'None'
item.comment = 'Adds database function name to generic database error'
langlist.add(item)

# =============================================================================
# 00-002-00031 
# =============================================================================
item = langlist.create('00-002-00031', kind='error-code')
item.value['ENG'] = 'Get condition must be a string (for WHERE) \n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Prints that WHERE condition must be a string'
langlist.add(item)

# =============================================================================
# 00-002-00032 
# =============================================================================
item = langlist.create('00-002-00032', kind='error-code')
item.value['ENG'] = '{0}: {1} \n\t Command: {2}\n\tpath: {3}\n\tFunction: {4}'
item.arguments = 'None'
item.comment = 'database error during execute command'
langlist.add(item)

# =============================================================================
# 00-002-00033 
# =============================================================================
item = langlist.create('00-002-00033', kind='error-code')
item.value['ENG'] = 'Get max_rows must be an integer (for LIMIT) \n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Prints that LIMIT (max_rows) must be an integer'
langlist.add(item)

# =============================================================================
# 00-002-00034 
# =============================================================================
item = langlist.create('00-002-00034', kind='error-code')
item.value['ENG'] = 'The column list must be same length as the value list\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Prints that column list must be same length as value list'
langlist.add(item)

# =============================================================================
# 00-002-00035 
# =============================================================================
item = langlist.create('00-002-00035', kind='error-code')
item.value['ENG'] = 'The column to set must be a string\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Prints that column must be a string'
langlist.add(item)

# =============================================================================
# 00-002-00036 
# =============================================================================
item = langlist.create('00-002-00036', kind='error-code')
item.value['ENG'] = 'field_names and field_types must be the same length\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means field_names and field_types were not the same length'
langlist.add(item)

# =============================================================================
# 00-002-00037 
# =============================================================================
item = langlist.create('00-002-00037', kind='error-code')
item.value['ENG'] = 'field_names must be strings\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means that field_names were not all strings'
langlist.add(item)

# =============================================================================
# 00-002-00038 
# =============================================================================
item = langlist.create('00-002-00038', kind='error-code')
item.value['ENG'] = 'field_types must be string or [int/float/str]\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means that field_types were not strings/int/float'
langlist.add(item)

# =============================================================================
# 00-002-00039 
# =============================================================================
item = langlist.create('00-002-00039', kind='error-code')
item.value['ENG'] = 'table \'name\' must be a string\n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means that table name must be a string'
langlist.add(item)

# =============================================================================
# 00-002-00040 
# =============================================================================
item = langlist.create('00-002-00040', kind='error-code')
item.value['ENG'] = '{0}: {1} \n\t Command: {2}\n\tpath: {3}\n\tTable name: {4}\n\tFunction: {5}'
item.arguments = 'None'
item.comment = 'Means that execute sql failed in colnames'
langlist.add(item)

# =============================================================================
# 00-002-00041 
# =============================================================================
item = langlist.create('00-002-00041', kind='error-code')
item.value['ENG'] = 'The are multiple tables in the database. You must pick one -- table cannot be None\n\tpath: {0}\n\tAvaiable tables: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means there are multiple tables defined but the user did not pick a table to use'
langlist.add(item)

# =============================================================================
# 00-002-00042 
# =============================================================================
item = langlist.create('00-002-00042', kind='error-code')
item.value['ENG'] = 'Cannot convert command to astropy table \n\t{0}: {1}\n\tpath: {2}\n\tTable name: {3}\n\tFunction: {4}'
item.arguments = 'None'
item.comment = 'Means that we could not convert sql result to astropy table'
langlist.add(item)

# =============================================================================
# 00-002-00043 
# =============================================================================
item = langlist.create('00-002-00043', kind='error-code')
item.value['ENG'] = '{0}: {1} \n\t Command: {2} \n\t Path: {3}\n\tFunction: {4}'
item.arguments = 'None'
item.comment = 'Means that sqlite connection failed'
langlist.add(item)

# =============================================================================
# 00-002-00044 
# =============================================================================
item = langlist.create('00-002-00044', kind='error-code')
item.value['ENG'] = 'Cannot import mysql.connector \n\t Please install with \'pip install mysql-connector-python\'\n\tpath: {0}\n\tFunction: {1}'
item.arguments = 'None'
item.comment = 'Means mysql.connector was not installed'
langlist.add(item)

# =============================================================================
# 00-002-00045 
# =============================================================================
item = langlist.create('00-002-00045', kind='error-code')
item.value['ENG'] = '{0}: {1} \n\t Command: {2}\n\tpath: {3}\n\tTable name: {4}\n\tFunction: {5}'
item.arguments = 'None'
item.comment = 'Means that mysql connection failed'
langlist.add(item)

# =============================================================================
# 00-002-00046 
# =============================================================================
item = langlist.create('00-002-00046', kind='error-code')
item.value['ENG'] = '\'if_exists\' must be either \'fail\', \'replace\' or \'append\''
item.arguments = 'None'
item.comment = 'Means that \'if_exists\' was incorrect'
langlist.add(item)

# =============================================================================
# 00-002-00047 
# =============================================================================
item = langlist.create('00-002-00047', kind='error-code')
item.value['ENG'] = 'Pandas.to_sql {0}: {1} \n\tpath: {0}\n\tTable name: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means that pandas.to_sql failed'
langlist.add(item)

# =============================================================================
# 00-002-00048 
# =============================================================================
item = langlist.create('00-002-00048', kind='error-code')
item.value['ENG'] = 'Could not read SQL command as pandas table \n\tCommand = {0} \n\tpath: {1}\n\tFunction: {2}'
item.arguments = 'None'
item.comment = 'Means that we could not read sql command'
langlist.add(item)

# =============================================================================
# 00-002-00049 
# =============================================================================
item = langlist.create('00-002-00049', kind='error-code')
item.value['ENG'] = 'Database kind \'{0}\' is invalid\n\tpath: {1}\n\tFunction:{2}'
item.arguments = 'None'
item.comment = 'Means the database name entered is invalid'
langlist.add(item)

# =============================================================================
# 00-002-00050 
# =============================================================================
item = langlist.create('00-002-00050', kind='error-code')
item.value['ENG'] = 'MySQL database = \'{0}\' could not be created. \n\t Error {1}: {2}\n\tpath:{3}\n\tFunction:{4}'
item.arguments = 'None'
item.comment = 'Means that MySQL database could not be created'
langlist.add(item)

# =============================================================================
# 00-002-00051 
# =============================================================================
item = langlist.create('00-002-00051', kind='error-code')
item.value['ENG'] = 'Problem connection to database. Invalid parameters: \n\t- host=\'{0}\'\n\t- username=\'{1}\'\n\t- passwd=\'{2}\''
item.arguments = 'None'
item.comment = 'Means that MySql database could not be connected to'
langlist.add(item)

# =============================================================================
# 00-002-00052 
# =============================================================================
item = langlist.create('00-002-00052', kind='error-code')
item.value['ENG'] = 'Index group error. Column {0} not in {1} (Group {2}) \n\t path: {3} \n\t Function : {4}'
item.arguments = 'None'
item.comment = 'Means that column not ground in index group'
langlist.add(item)

# =============================================================================
# 00-002-00053 
# =============================================================================
item = langlist.create('00-002-00053', kind='error-code')
item.value['ENG'] = 'Database table \"{0}\" not found in database\n\tpath: {1}\n\tAvaiable tables: {2}\n\tFunction: {3}'
item.arguments = 'None'
item.comment = 'Means tname is not in database list (table is not defined)'
langlist.add(item)

# =============================================================================
# 00-003-00000 
# =============================================================================
item = langlist.create('00-003-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Constant Error'
item.arguments = 'None'
item.comment = 'Dev Constant Errors'
langlist.add(item)

# =============================================================================
# 00-003-00001 
# =============================================================================
item = langlist.create('00-003-00001', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' was not found in constants parameter dictionary. \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means constant was not found in constant parameter dictionary'
langlist.add(item)

# =============================================================================
# 00-003-00002 
# =============================================================================
item = langlist.create('00-003-00002', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' can not be converted to a list. \n\t Error {1}: {2}. \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that parameter value could not be converted to a list'
langlist.add(item)

# =============================================================================
# 00-003-00003 
# =============================================================================
item = langlist.create('00-003-00003', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' can not be converted to a dictionary. \n\t Error {1}: {2}. \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that parameter value could not be converted to a dictionary'
langlist.add(item)

# =============================================================================
# 00-003-00004 
# =============================================================================
item = langlist.create('00-003-00004', kind='error-code')
item.value['ENG'] = 'Pcheck: \'key\' and \'name\' were both unset, at least one value must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that key and name were not set in find_param (pcheck)'
langlist.add(item)

# =============================================================================
# 00-003-00005 
# =============================================================================
item = langlist.create('00-003-00005', kind='error-code')
item.value['ENG'] = 'Folder \'{0}\' does not exist in {1}'
item.arguments = 'None'
item.comment = 'Means that config folder does not exist on disk'
langlist.add(item)

# =============================================================================
# 00-003-00006 
# =============================================================================
item = langlist.create('00-003-00006', kind='error-code')
item.value['ENG'] = 'Duplicate Const parameter \'{0}\' for instrument \'{1}\' \n\t Module list: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was a duplicated constant parameter'
langlist.add(item)

# =============================================================================
# 00-003-00007 
# =============================================================================
item = langlist.create('00-003-00007', kind='error-code')
item.value['ENG'] = 'Must define new source when copying a Constant \n\t Syntax: Constant.copy(source) \n\t where \'source\' is a string \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that source was not defined when copying a constant (it must be)'
langlist.add(item)

# =============================================================================
# 00-003-00008 
# =============================================================================
item = langlist.create('00-003-00008', kind='error-code')
item.value['ENG'] = 'Must define new source when copying a Keyword \n\t Syntax: Keyword.copy(source) \n\t where \'source\' is a string \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that source was not defined when copying a keyword (it must be)'
langlist.add(item)

# =============================================================================
# 00-003-00009 
# =============================================================================
item = langlist.create('00-003-00009', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' must be a string. \n\t Type: \'{1}\' \n\t Value: \'{2}\' \n\t Config File = \'{3}\' \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that dtype was meant to be a path and a string'
langlist.add(item)

# =============================================================================
# 00-003-00010 
# =============================================================================
item = langlist.create('00-003-00010', kind='error-code')
item.value['ENG'] = 'Const validate error - Key {0}: Path does not exist \'{1}\' \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that dtype was meant to be a path but path was not found'
langlist.add(item)

# =============================================================================
# 00-003-00011 
# =============================================================================
item = langlist.create('00-003-00011', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' should be a list not a string. \n\t Value = {1} \n\t Config File = \'{2}\' \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that dtype was meant to be a list and not a string'
langlist.add(item)

# =============================================================================
# 00-003-00012 
# =============================================================================
item = langlist.create('00-003-00012', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' dtype is incorrect.  Expected \'{1}\' value=\'{2}\' (dtype={3})  \n\t Error {4}: {5} \n\t Config File = {6} \n\t Function = {7}'
item.arguments = 'None'
item.comment = 'Means that dtype was not correct for what was given in constants definition'
langlist.add(item)

# =============================================================================
# 00-003-00013 
# =============================================================================
item = langlist.create('00-003-00013', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' dtype not set \n\t Config File = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that dtype was not set'
langlist.add(item)

# =============================================================================
# 00-003-00014 
# =============================================================================
item = langlist.create('00-003-00014', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' dtype is incorrect. Must be one of the following: \n\t {1} \n\t Config file: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that dtype wave not a simple data type (allowed listed)'
langlist.add(item)

# =============================================================================
# 00-003-00015 
# =============================================================================
item = langlist.create('00-003-00015', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' value is not set. \n\t Config file = \'{1}\' \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that data value is not set'
langlist.add(item)

# =============================================================================
# 00-003-00016 
# =============================================================================
item = langlist.create('00-003-00016', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' must be True or False or 1 or 0 \n\t Current value: \'{1}\' \n\t Config file: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that dtype must be boolean (True of False)'
langlist.add(item)

# =============================================================================
# 00-003-00017 
# =============================================================================
item = langlist.create('00-003-00017', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' value is incorrect. \n\t Options are: {1} \n\t Current value: \'{2}\' \n\t Config File = {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that the value was not found in options'
langlist.add(item)

# =============================================================================
# 00-003-00018 
# =============================================================================
item = langlist.create('00-003-00018', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' too large. \n\t Value must be less than {1} \n\t Current value: {2} \n\t Config File = {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that value exceed maximum allowed value'
langlist.add(item)

# =============================================================================
# 00-003-00019 
# =============================================================================
item = langlist.create('00-003-00019', kind='error-code')
item.value['ENG'] = 'Parameter \'{0}\' too small. \n\t Value must be greater than {1} \n\t Current value: {2} \n\t Config File = {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that value exceed minimum allowed value'
langlist.add(item)

# =============================================================================
# 00-003-00020 
# =============================================================================
item = langlist.create('00-003-00020', kind='error-code')
item.value['ENG'] = 'Invalid character(s) found in file = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that invalid character(s) were found in file'
langlist.add(item)

# =============================================================================
# 00-003-00021 
# =============================================================================
item = langlist.create('00-003-00021', kind='error-code')
item.value['ENG'] = '\t\t Line {0}: character = \'{1}\''
item.arguments = 'None'
item.comment = 'Line and char reference for 00-003-00020'
langlist.add(item)

# =============================================================================
# 00-003-00022 
# =============================================================================
item = langlist.create('00-003-00022', kind='error-code')
item.value['ENG'] = 'Wrong format for line {0} in file {1} \n\t Line {0}: {2} \n\t Lines must be in format: \'key = value\' \n\t where \'key\' and \'value\' are valid python strings containing no equal signs \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that the wrong line format was present in config file'
langlist.add(item)

# =============================================================================
# 00-003-00023 
# =============================================================================
item = langlist.create('00-003-00023', kind='error-code')
item.value['ENG'] = 'No valid lines found in file: {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that there were no valid lines found in config file'
langlist.add(item)

# =============================================================================
# 00-003-00024 
# =============================================================================
item = langlist.create('00-003-00024', kind='error-code')
item.value['ENG'] = 'ParamDict Error: Parameter \'{0}\' not found in parameter dictionary'
item.arguments = 'None'
item.comment = 'Means that parameter was not found in parameter dictionary'
langlist.add(item)

# =============================================================================
# 00-003-00025 
# =============================================================================
item = langlist.create('00-003-00025', kind='error-code')
item.value['ENG'] = 'ParamDict locked. \n\t Cannot add \'{0}\'=\'{1}\''
item.arguments = 'None'
item.comment = 'Means that parameter dictionary is locked and cannot add key'
langlist.add(item)

# =============================================================================
# 00-003-00026 
# =============================================================================
item = langlist.create('00-003-00026', kind='error-code')
item.value['ENG'] = 'ParamDict Error: Source cannot be added for key \'{0}\' \n\t \'{0}\' is not in parameter dictionary'
item.arguments = 'None'
item.comment = 'Means that source cannot be added for key as key is not in parameter dictionary'
langlist.add(item)

# =============================================================================
# 00-003-00027 
# =============================================================================
item = langlist.create('00-003-00027', kind='error-code')
item.value['ENG'] = 'ParamDict Error: Instance cannot be added for key \'{0}\' \n\t \'{0} is not in parameter dictionary'
item.arguments = 'None'
item.comment = 'Means that instance cannot be added for key as key is not in parameter dictionary'
langlist.add(item)

# =============================================================================
# 00-003-00028 
# =============================================================================
item = langlist.create('00-003-00028', kind='error-code')
item.value['ENG'] = 'ParamDict Error: No source set for key={0}'
item.arguments = 'None'
item.comment = 'Means that no source was set for this key when trying to use get_source'
langlist.add(item)

# =============================================================================
# 00-003-00029 
# =============================================================================
item = langlist.create('00-003-00029', kind='error-code')
item.value['ENG'] = 'ParamDict Error: No instance set for key={0}'
item.arguments = 'None'
item.comment = 'Means that no instance was set for this key when trying to use get_instance'
langlist.add(item)

# =============================================================================
# 00-003-00030 
# =============================================================================
item = langlist.create('00-003-00030', kind='error-code')
item.value['ENG'] = 'ParamDict Error: parameter \'{0}\' not found in parameter dictionary (via listp)'
item.arguments = 'None'
item.comment = 'Means that parameter was not found in parameter dictionary (via listp)'
langlist.add(item)

# =============================================================================
# 00-003-00031 
# =============================================================================
item = langlist.create('00-003-00031', kind='error-code')
item.value['ENG'] = 'ParamDict Error: parameter \'{0}\' not found in parameter dictionary (via dictp)'
item.arguments = 'None'
item.comment = 'Means that parameter was not found in parameter dictionary (via dictp)'
langlist.add(item)

# =============================================================================
# 00-003-00032 
# =============================================================================
item = langlist.create('00-003-00032', kind='error-code')
item.value['ENG'] = 'ParamDict Error: parameter \'{0}\' must be a string to convert (via listp)'
item.arguments = 'None'
item.comment = 'Means that listp was used but parameter was not a string -> cannot go to list from string'
langlist.add(item)

# =============================================================================
# 00-003-00033 
# =============================================================================
item = langlist.create('00-003-00033', kind='error-code')
item.value['ENG'] = 'ParamDict Error: parameter \'{0}\' must be a string to convert (via dictp)'
item.arguments = 'None'
item.comment = 'Means that dictp was used but parameter was not a string -> cannot go to a dict'
langlist.add(item)

# =============================================================================
# 00-003-00034 
# =============================================================================
item = langlist.create('00-003-00034', kind='error-code')
item.value['ENG'] = '{0} Error: must set source for {0}:{1}'
item.arguments = 'None'
item.comment = 'Means source is not set when constructing Const/Keyword'
langlist.add(item)

# =============================================================================
# 00-003-00035 
# =============================================================================
item = langlist.create('00-003-00035', kind='error-code')
item.value['ENG'] = 'Keyword instance \'{0}\' must have parameter \'key\' set'
item.arguments = 'None'
item.comment = 'Means Keyword instance does not have a key set'
langlist.add(item)

# =============================================================================
# 00-003-00036 
# =============================================================================
item = langlist.create('00-003-00036', kind='error-code')
item.value['ENG'] = 'User config defined but directory = \'{0}\' has not config files \n\t Valid config files: {1}'
item.arguments = 'None'
item.comment = 'Means user config defined but directory has not config files'
langlist.add(item)

# =============================================================================
# 00-004-00000 
# =============================================================================
item = langlist.create('00-004-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Deprecated Error'
item.arguments = 'None'
item.comment = 'Dev Indexing/IO/Path Errors'
langlist.add(item)

# =============================================================================
# 00-004-00001 
# =============================================================================
item = langlist.create('00-004-00001', kind='error-code')
item.value['ENG'] = 'Could not find files. Kwarg=\'{0}\' does not exist in index files. \n\t path = {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that kwarg was not in expected index file columns '
langlist.add(item)

# =============================================================================
# 00-004-00002 
# =============================================================================
item = langlist.create('00-004-00002', kind='error-code')
item.value['ENG'] = 'Could not find files. Kwarg=\'{0}\' does not exist in index file={1}. \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that kwarg was not in index file'
langlist.add(item)

# =============================================================================
# 00-004-00003 
# =============================================================================
item = langlist.create('00-004-00003', kind='error-code')
item.value['ENG'] = 'File \'{0}\' cannot be read by {1} \n\t Error {2}: {3}'
item.arguments = 'None'
item.comment = 'Means that config file cannot be read'
langlist.add(item)

# =============================================================================
# 00-004-00004 
# =============================================================================
item = langlist.create('00-004-00004', kind='error-code')
item.value['ENG'] = 'File \'{0}\' cannot be written by {1} \n\t Error {2}: {3}'
item.arguments = 'None'
item.comment = 'Means that config file cannot be written to'
langlist.add(item)

# =============================================================================
# 00-004-00005 
# =============================================================================
item = langlist.create('00-004-00005', kind='error-code')
item.value['ENG'] = 'File \'{0}\' cannot be copied to \'{1}\'. Input file does not exist. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that we could not copy file as input file does not exist'
langlist.add(item)

# =============================================================================
# 00-004-00006 
# =============================================================================
item = langlist.create('00-004-00006', kind='error-code')
item.value['ENG'] = 'File \'{0}\' cannot be copied to \'{1}\' \n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not copy file exception was generated'
langlist.add(item)

# =============================================================================
# 00-004-00007 
# =============================================================================
item = langlist.create('00-004-00007', kind='error-code')
item.value['ENG'] = 'DrsPath requires at least either ‘abspath’ or ‘block_kind’ or ‘block_name’'
item.arguments = 'None'
item.comment = 'Means DrsPath did not have the correct arguments'
langlist.add(item)

# =============================================================================
# 00-004-00008 
# =============================================================================
item = langlist.create('00-004-00008', kind='error-code')
item.value['ENG'] = 'DrsPath does not have absolute path set'
item.arguments = 'None'
item.comment = 'Means DrsPath does not have ‘abspath’ set'
langlist.add(item)

# =============================================================================
# 00-004-00009 
# =============================================================================
item = langlist.create('00-004-00009', kind='error-code')
item.value['ENG'] = 'DrsPath abspath=’{0}’ must be relatied to a valid block. \n\t Valid blocks are: {1}'
item.arguments = 'None'
item.comment = 'Means DrsPath abspath is invalid (must be one of the block paths defined)'
langlist.add(item)

# =============================================================================
# 00-004-00010 
# =============================================================================
item = langlist.create('00-004-00010', kind='error-code')
item.value['ENG'] = 'DrsPath: ‘{0}’ is not a valid block path. \n\t Valid blocks are: {1}'
item.arguments = 'None'
item.comment = 'Means that DrsPath block path is not valid'
langlist.add(item)

# =============================================================================
# 00-004-00011 
# =============================================================================
item = langlist.create('00-004-00011', kind='error-code')
item.value['ENG'] = 'DrsPath: ‘{0}’ is not a valid block kind. \n\t Valid blocks are: {1}'
item.arguments = 'None'
item.comment = 'Means that DrsPath block kind is not valid'
langlist.add(item)

# =============================================================================
# 00-004-00012 
# =============================================================================
item = langlist.create('00-004-00012', kind='error-code')
item.value['ENG'] = 'Filename must be set (self.filename) or given as argument (filename) \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that filename must be set or given before running get_infile_infilename'
langlist.add(item)

# =============================================================================
# 00-004-00013 
# =============================================================================
item = langlist.create('00-004-00013', kind='error-code')
item.value['ENG'] = 'Argument ‘fmt’ must be either ‘image’ or ‘table’. fmt =’{0}’'
item.arguments = 'None'
item.comment = 'Means that fmt was not ‘image’ or ‘table’'
langlist.add(item)

# =============================================================================
# 00-004-00014 
# =============================================================================
item = langlist.create('00-004-00014', kind='error-code')
item.value['ENG'] = 'Extension ‘{0}’ not in file: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means extension not in filename'
langlist.add(item)

# =============================================================================
# 00-004-00015 
# =============================================================================
item = langlist.create('00-004-00015', kind='error-code')
item.value['ENG'] = 'File {0} does not have extension {1} \n\t File may be corrupted or wrong type'
item.arguments = 'None'
item.comment = 'Means that file does not have extension (accessed with extension number)'
langlist.add(item)

# =============================================================================
# 00-004-00016 
# =============================================================================
item = langlist.create('00-004-00016', kind='error-code')
item.value['ENG'] = 'File {0} does not have extension name ‘{1}’ \n\t File may be corrupted or wrong type'
item.arguments = 'None'
item.comment = 'Means that file does not have extension (accessed with extension name)'
langlist.add(item)

# =============================================================================
# 00-004-00017 
# =============================================================================
item = langlist.create('00-004-00017', kind='error-code')
item.value['ENG'] = 'infile.basename must be set when defining infile = {0}'
item.arguments = 'None'
item.comment = 'Means that infile.basename must be set when defining this type of infile'
langlist.add(item)

# =============================================================================
# 00-005-00000 
# =============================================================================
item = langlist.create('00-005-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Logging Error'
item.arguments = 'None'
item.comment = 'Dev Log Error'
langlist.add(item)

# =============================================================================
# 00-005-00001 
# =============================================================================
item = langlist.create('00-005-00001', kind='error-code')
item.value['ENG'] = 'Log Error: Message: \'{0}\' is not a valid log message'
item.arguments = 'None'
item.comment = 'Log error input \'message\' is incorrect'
langlist.add(item)

# =============================================================================
# 00-005-00002 
# =============================================================================
item = langlist.create('00-005-00002', kind='error-code')
item.value['ENG'] = 'Log Error: Key \'{0}\' is not in \'{1}\''
item.arguments = 'None'
item.comment = 'Log error when \'key\' is not found in LOG_TRIG_KEYS()'
langlist.add(item)

# =============================================================================
# 00-005-00003 
# =============================================================================
item = langlist.create('00-005-00003', kind='error-code')
item.value['ENG'] = 'Log Error: Key \'{0}\' is not in \'{1}\''
item.arguments = 'None'
item.comment = 'Log error when \'key\' is not found in WRITE_LEVEL()'
langlist.add(item)

# =============================================================================
# 00-005-00004 
# =============================================================================
item = langlist.create('00-005-00004', kind='error-code')
item.value['ENG'] = 'Log Error: Key \'{0}\' is not in \'{1}\''
item.arguments = 'None'
item.comment = 'Log error when \'key\' is not found in COLOUREDLEVELS() '
langlist.add(item)

# =============================================================================
# 00-005-00005 
# =============================================================================
item = langlist.create('00-005-00005', kind='error-code')
item.value['ENG'] = 'Log Error: \'message\' must be a string or a list. \n\t Current value = \'{0}\''
item.arguments = 'None'
item.comment = 'Means that \'message\' is not a string or list'
langlist.add(item)

# =============================================================================
# 00-005-00006 
# =============================================================================
item = langlist.create('00-005-00006', kind='error-code')
item.value['ENG'] = '\n\n\tError found and running in DEBUG mode \n\n\t'
item.value['FR'] = '\n\n\tErreur trouvée et en cours d\'exécution en mode DEBUG \n\n\t'
item.arguments = 'None'
item.comment = 'The debug title'
langlist.add(item)

# =============================================================================
# 00-005-00007 
# =============================================================================
item = langlist.create('00-005-00007', kind='error-code')
item.value['ENG'] = '\tEnter:\n\t\t1: ipython debugger \n\t\t2: python debugger \n\t\tAny other key: exit \n\n\t Note: ipython debugger requires \'ipdb\' installed \n\n\t Choose \'1\', \'2\' or exit:'
item.value['FR'] = '\tEntrer:\n\t\t1: ipython debugger \n\t\t2: python debugger \n\t\tToute autre clé: quitter \n\n\t Remarque: ipython debugger nécessite l\'installation de \'ipdb\' \n\n\t Choisissez: 1, 2 ou quitter:'
item.arguments = 'None'
item.comment = 'The debug error message'
langlist.add(item)

# =============================================================================
# 00-005-00008 
# =============================================================================
item = langlist.create('00-005-00008', kind='error-code')
item.value['ENG'] = '\n\t ==== IPYTHON DEBUGGER ==== \n\n\t - type \'ipython()\' to user %paste %cpaste \n\t - type \'list\' to list code \n\t - type \'up\' to go up a level \n\t - type \'interact\' to go to an interactive shell \n\t - type \'print(variable)\' to print a variable \n\t - type \'continue\' to exit \n\t - type \'help\' to see all commands \n\n\t ==================\n\n'
item.value['FR'] = '\n\t ==== IPYTHON DEBUGGER ==== \n\n\t - tapez \'ipython()\' pour l\'utilisateur %paste et % cpaste  \n\t - tapez \'list\' pour lister le code \n\t - tapez \'up\' pour monter au niveau \n\t - tapez \'interact\' pour aller à un shell interactifl \n\t -tapez \'print (variable)\' pour imprimer une variable \n\t - tapez \'continue\' quitter \n\t - tapez \'help\' pour voir toutes les commandes \n\n\t ==================\n\n'
item.arguments = 'None'
item.comment = 'IPYTHON interactive mode instructions'
langlist.add(item)

# =============================================================================
# 00-005-00009 
# =============================================================================
item = langlist.create('00-005-00009', kind='error-code')
item.value['ENG'] = '\n\t ==== PYTHON DEBUGGER ==== \n\n\t - type \'list\' to list code \n\t - type \'up\' to go up a level \n\t - type \'interact\' to go to an interactive shell \n\t - type \'print(variable)\' to print a variable \n\t - type \'continue\' to exit \n\t - type \'help\' to see all commands \n\n\t ==================\n\n'
item.value['FR'] = '\n\t ==== DEBUGGER ==== \n\n\t - tapez \'list\' pour lister le code \n\t - tapez \'up\' pour monter au niveau \n\t - tapez \'interact\' pour aller à un shell interactifl \n\t -tapez \'print (variable)\' pour imprimer une variable \n\t - tapez \'continue\' quitter \n\t - tapez \'help\' pour voir toutes les commandes \n\n\t ==================\n\n'
item.arguments = 'None'
item.comment = 'PYTHON interactive mode instructions'
langlist.add(item)

# =============================================================================
# 00-005-00010 
# =============================================================================
item = langlist.create('00-005-00010', kind='error-code')
item.value['ENG'] = '\n\n Code Exited'
item.value['FR'] = '\n\n Code quitté'
item.arguments = 'None'
item.comment = 'exit code'
langlist.add(item)

# =============================================================================
# 00-005-00011 
# =============================================================================
item = langlist.create('00-005-00011', kind='error-code')
item.value['ENG'] = 'Log level \'{0}\' not in WRITE_LEVEL() \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'level\' was not in WRITE_LEVEL()'
langlist.add(item)

# =============================================================================
# 00-005-00012 
# =============================================================================
item = langlist.create('00-005-00012', kind='error-code')
item.value['ENG'] = 'Log key \'{0}\' not in WRITE_LEVEL() \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'key\' was not in WRITE_LEVEL()'
langlist.add(item)

# =============================================================================
# 00-005-00013 
# =============================================================================
item = langlist.create('00-005-00013', kind='error-code')
item.value['ENG'] = 'Log colour key \'{0}\' not in COLOUREDLEVELS() \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that colour level \'key\' was not in COLOUREDLEVELS()'
langlist.add(item)

# =============================================================================
# 00-005-00014 
# =============================================================================
item = langlist.create('00-005-00014', kind='error-code')
item.value['ENG'] = 'RecipeLogError: Cannot make path {0} for recipe log.'
item.arguments = 'None'
item.comment = 'Means that recipe log could not make log path'
langlist.add(item)

# =============================================================================
# 00-005-00015 
# =============================================================================
item = langlist.create('00-005-00015', kind='error-code')
item.value['ENG'] = 'RecipeLogError: Cannot write file {0} \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that we could not write recipe log file'
langlist.add(item)

# =============================================================================
# 00-005-00016 
# =============================================================================
item = langlist.create('00-005-00016', kind='error-code')
item.value['ENG'] = 'RecipeLogError: Cannot read file {0} \n\t {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that we could not read recipe log file'
langlist.add(item)

# =============================================================================
# 00-006-00000 
# =============================================================================
item = langlist.create('00-006-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Argument Error'
item.arguments = 'None'
item.comment = 'Dev Argument Error'
langlist.add(item)

# =============================================================================
# 00-006-00001 
# =============================================================================
item = langlist.create('00-006-00001', kind='error-code')
item.value['ENG'] = 'Cannot find input \'{0}\' for recipe \'{1}\''
item.arguments = 'None'
item.comment = 'Cannot find input name in recipe definition (means there was a problem with \'recipe_setup\' when parsing to argparse)'
langlist.add(item)

# =============================================================================
# 00-006-00002 
# =============================================================================
item = langlist.create('00-006-00002', kind='error-code')
item.value['ENG'] = 'Attribute \'default_ref\' is unset for \'{0}\' for recipe \'{1}\''
item.arguments = 'None'
item.comment = 'Means that we need a default reference but it is not defined'
langlist.add(item)

# =============================================================================
# 00-006-00003 
# =============================================================================
item = langlist.create('00-006-00003', kind='error-code')
item.value['ENG'] = 'Attribute \'default_ref\' is not found in constants for \'{1}\' for recipe \'{2}\''
item.arguments = 'None'
item.comment = 'Means that the default reference (which has to also be in the constants parameter dictionary) is not present in constants parameter dictionary'
langlist.add(item)

# =============================================================================
# 00-006-00004 
# =============================================================================
item = langlist.create('00-006-00004', kind='error-code')
item.value['ENG'] = 'Logic is wrong for argument \'{0}\' for recipe \'{1}\'. \n\t Must be \'exclusive\' or \'inclusive\''
item.arguments = 'None'
item.comment = 'Means that logic was set incorrectly in recipe definition of argument'
langlist.add(item)

# =============================================================================
# 00-006-00005 
# =============================================================================
item = langlist.create('00-006-00005', kind='error-code')
item.value['ENG'] = 'Cannot have \'files\' in both positional and optional args\n\tfunction = {0}'
item.arguments = 'None'
item.comment = 'Means that there were \'files\' in both positional and optional arguments'
langlist.add(item)

# =============================================================================
# 00-006-00006 
# =============================================================================
item = langlist.create('00-006-00006', kind='error-code')
item.value['ENG'] = 'Kind=\'{0}\' not supported. \n\tfunction={1}'
item.arguments = 'None'
item.comment = 'Means that \'kind\' was wrong for \'_generate_arg_groups\'  (used in generate_runs_from_filelist)'
langlist.add(item)

# =============================================================================
# 00-006-00007 
# =============================================================================
item = langlist.create('00-006-00007', kind='error-code')
item.value['ENG'] = '{0} \'{1}\' is not defined in call to function = {1}'
item.arguments = 'None'
item.comment = 'Means that the argument is a positional argument but was not defined at run time'
langlist.add(item)

# =============================================================================
# 00-006-00008 
# =============================================================================
item = langlist.create('00-006-00008', kind='error-code')
item.value['ENG'] = 'DrsArgument arg \'filelogic\' must be equal to \'inclusive\' or \'exclusive\' only. \n\t Current value is \'{0}\''
item.arguments = 'None'
item.comment = 'Means that DrsArgument arg \'filelogic\' was st to an incorrect value (must be \'inclusive\' or \'exclusive\')'
langlist.add(item)

# =============================================================================
# 00-006-00009 
# =============================================================================
item = langlist.create('00-006-00009', kind='error-code')
item.value['ENG'] = 'DrsArgument kwargs error: call to DrsArgument must have keyword \'default\' or \'default_ref\' when DrsArgumet kind is \'kwarg\''
item.arguments = 'None'
item.comment = 'Means that DrsArgument kwargs must contain either \'default_ref\' or \'default\' to be a valid keyword argument'
langlist.add(item)

# =============================================================================
# 00-006-00010 
# =============================================================================
item = langlist.create('00-006-00010', kind='error-code')
item.value['ENG'] = 'DrsArgument arg \'dtype\' is not valid. Must be equal to one of the following: \n\t {0} \n\t Current value is \'{1}\''
item.arguments = 'None'
item.comment = 'Means that DrsArgument arg \'dtype\' was set incorrectly'
langlist.add(item)

# =============================================================================
# 00-006-00011 
# =============================================================================
item = langlist.create('00-006-00011', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': not found in recipe.  \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that argument was not matched to self.dest (in _CheckType._check_limits)'
langlist.add(item)

# =============================================================================
# 00-006-00012 
# =============================================================================
item = langlist.create('00-006-00012', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': The value \'{1}\'=\'{2}\' cannot be used.  \n\t Error {3}: {4}'
item.arguments = 'None'
item.comment = 'Means that the \"{1}\" value for argument was not the correct dtype'
langlist.add(item)

# =============================================================================
# 00-006-00013 
# =============================================================================
item = langlist.create('00-006-00013', kind='error-code')
item.value['ENG'] = 'sys.argv was not a list. \n\t sys.argv = \'{0}\' \n\t type = \'{1}\' \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was a problem with sys.argv'
langlist.add(item)

# =============================================================================
# 00-006-00014 
# =============================================================================
item = langlist.create('00-006-00014', kind='error-code')
item.value['ENG'] = 'Could not parse arguments to argparse. \n\t sys.argv = {0} \n\t call arguments = {1} \n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not parse arguments to the argument parser'
langlist.add(item)

# =============================================================================
# 00-006-00015 
# =============================================================================
item = langlist.create('00-006-00015', kind='error-code')
item.value['ENG'] = 'Positional argument \'{0}\' cannot start with a \'-\''
item.arguments = 'None'
item.comment = 'Means that positional argument started with a \'-\''
langlist.add(item)

# =============================================================================
# 00-006-00016 
# =============================================================================
item = langlist.create('00-006-00016', kind='error-code')
item.value['ENG'] = 'Keyword argument \'{0}\' must start with a \'-\''
item.arguments = 'None'
item.comment = 'Means that keyword argument did not start with a \'-\''
langlist.add(item)

# =============================================================================
# 00-006-00017 
# =============================================================================
item = langlist.create('00-006-00017', kind='error-code')
item.value['ENG'] = 'Special argument \'{0}\' must start with a \'-\''
item.arguments = 'None'
item.comment = 'Means that special argument did not start with a \'-\''
langlist.add(item)

# =============================================================================
# 00-006-00018 
# =============================================================================
item = langlist.create('00-006-00018', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': The \'path\' was set but not a valid directory \n\t Current value = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that argument \'path\' was set but not a valid path'
langlist.add(item)

# =============================================================================
# 00-006-00019 
# =============================================================================
item = langlist.create('00-006-00019', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': dtype was set to \'file\' or \'files\' but the \'files\' argument was not set \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that we have a \'file\' or \'files\' argument (in dtype) but files was not set'
langlist.add(item)

# =============================================================================
# 00-006-00020 
# =============================================================================
item = langlist.create('00-006-00020', kind='error-code')
item.value['ENG'] = 'Cannot get {0} directory, requires valid directory (in force mode) or forced_dir to be set elsewise (both are set to None). \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means we have to get input/output dir and do not have a directory so need to have one set by forced_dir but forced_dir is None'
langlist.add(item)

# =============================================================================
# 00-006-00021 
# =============================================================================
item = langlist.create('00-006-00021', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': tried to set \'files\' attribute, however files attributes must be {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means files contained a file that was not a DrsInputfile instance'
langlist.add(item)

# =============================================================================
# 00-006-00022 
# =============================================================================
item = langlist.create('00-006-00022', kind='error-code')
item.value['ENG'] = 'DrsFile: {0}  key \"{1}\" is not allowed in hkeys. \n\t Valid keys defined here: {2} \n\t Allowed keys: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that required header keys are not allowed (we have a list of allowed header keys in pseudo const FILEDEF_HEADER_KEYS)'
langlist.add(item)

# =============================================================================
# 00-006-00023 
# =============================================================================
item = langlist.create('00-006-00023', kind='error-code')
item.value['ENG'] = '{0}'
item.arguments = 'None'
item.comment = 'Argument error passed up the chain (no text)'
langlist.add(item)

# =============================================================================
# 00-006-00024 
# =============================================================================
item = langlist.create('00-006-00024', kind='error-code')
item.value['ENG'] = 'alldict[{0}][{1}] is not a valid astropy table (and not None) \n\t Function: {2}'
item.arguments = 'None'
item.comment = 'Means that alldict is not valid and we have a problem'
langlist.add(item)

# =============================================================================
# 00-006-00025 
# =============================================================================
item = langlist.create('00-006-00025', kind='error-code')
item.value['ENG'] = 'Cannot use group filter with more than 1 file argument'
item.arguments = 'None'
item.comment = 'Means we cannot use group function with more than 1 file argument'
langlist.add(item)

# =============================================================================
# 00-007-00000 
# =============================================================================
item = langlist.create('00-007-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: Recipe Definition Error'
item.arguments = 'None'
item.comment = 'Dev Error: Recipe / Recipe Definition Error'
langlist.add(item)

# =============================================================================
# 00-007-00001 
# =============================================================================
item = langlist.create('00-007-00001', kind='error-code')
item.value['ENG'] = 'No recipe named \'{0}\''
item.arguments = 'None'
item.comment = 'Means that no recipe was found (recipe defintion name did not match the name given to input_setup'
langlist.add(item)

# =============================================================================
# 00-007-00002 
# =============================================================================
item = langlist.create('00-007-00002', kind='error-code')
item.value['ENG'] = 'Problem with recipe definition: \'{0}\' directory must be either \'RAW\', \'REDUCED\', or \'TMP\' \n\tCurrent value is=\'{1}\''
item.arguments = 'None'
item.comment = 'Means that \'inputdir\' was not one of the required values (i.e. \'RAW\', \'REDUCED\', or \'TMP\')'
langlist.add(item)

# =============================================================================
# 00-007-00003 
# =============================================================================
item = langlist.create('00-007-00003', kind='error-code')
item.value['ENG'] = 'No valid groups. Function={0}'
item.arguments = 'None'
item.comment = 'Means there were no valid groups for recipe'
langlist.add(item)

# =============================================================================
# 00-007-00004 
# =============================================================================
item = langlist.create('00-007-00004', kind='error-code')
item.value['ENG'] = 'Recipe {0} flag ‘{1}’ not in base.LOG_FLAGS. Please add to use.'
item.arguments = 'None'
item.comment = 'Means that flag was not defined in base.LOG_FLAGS'
langlist.add(item)

# =============================================================================
# 00-008-00000 
# =============================================================================
item = langlist.create('00-008-00000', kind='error-code')
item.value['ENG'] = 'Dev Error: File Definition Error'
item.arguments = 'None'
item.comment = 'Dev Error: File/Path errors'
langlist.add(item)

# =============================================================================
# 00-008-00001 
# =============================================================================
item = langlist.create('00-008-00001', kind='error-code')
item.value['ENG'] = 'Package name = \'{0}\' is invalid (function = {1})'
item.arguments = 'None'
item.comment = 'Means that package name was invalid for function'
langlist.add(item)

# =============================================================================
# 00-008-00002 
# =============================================================================
item = langlist.create('00-008-00002', kind='error-code')
item.value['ENG'] = 'Directory \'{0}\' does not exist in \'{1}\'. \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the data folder does not exist'
langlist.add(item)

# =============================================================================
# 00-008-00003 
# =============================================================================
item = langlist.create('00-008-00003', kind='error-code')
item.value['ENG'] = 'Read Error: For file \'{0}\' format=\'{1}\' is incorrect. \n\t Allowed formats are: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that wrong format was given for fits read function'
langlist.add(item)

# =============================================================================
# 00-008-00004 
# =============================================================================
item = langlist.create('00-008-00004', kind='error-code')
item.value['ENG'] = 'File definition error: \'outfunc\' must be set in file definition. \n\t File = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'outfunc\' was not set but \'construct_filename\' was called'
langlist.add(item)

# =============================================================================
# 00-008-00005 
# =============================================================================
item = langlist.create('00-008-00005', kind='error-code')
item.value['ENG'] = 'Database name not set for DrsFitsFile=\'{0}\'  \n\t Must be {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have database name set'
langlist.add(item)

# =============================================================================
# 00-008-00006 
# =============================================================================
item = langlist.create('00-008-00006', kind='error-code')
item.value['ENG'] = 'Database name invalid for DrsFitsFile=\'{0}\' (value=\'{1}\') \n\t Must be {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have valid database name'
langlist.add(item)

# =============================================================================
# 00-008-00007 
# =============================================================================
item = langlist.create('00-008-00007', kind='error-code')
item.value['ENG'] = 'Database key not set for DrsFitsFile=\'{0}\'  \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that drs file does not have database key set'
langlist.add(item)

# =============================================================================
# 00-008-00008 
# =============================================================================
item = langlist.create('00-008-00008', kind='error-code')
item.value['ENG'] = 'Unit Conversion Error: {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that there was a unit conversion error'
langlist.add(item)

# =============================================================================
# 00-008-00009 
# =============================================================================
item = langlist.create('00-008-00009', kind='error-code')
item.value['ENG'] = '{0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was another unit error'
langlist.add(item)

# =============================================================================
# 00-008-00010 
# =============================================================================
item = langlist.create('00-008-00010', kind='error-code')
item.value['ENG'] = 'Time unit = \'{0}\' not supported. \n\t Must be \'hours\' or \'days\' or a astropy.unit time quantity. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that the time units given were not supported'
langlist.add(item)

# =============================================================================
# 00-008-00011 
# =============================================================================
item = langlist.create('00-008-00011', kind='error-code')
item.value['ENG'] = 'No file of filetype \'{0}\' in function {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that no file was found in that matched a file_definition'
langlist.add(item)

# =============================================================================
# 00-008-00012 
# =============================================================================
item = langlist.create('00-008-00012', kind='error-code')
item.value['ENG'] = 'No cavity file found. File = {0}. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that the cavity file was not found (when trying to load it)'
langlist.add(item)

# =============================================================================
# 00-008-00013 
# =============================================================================
item = langlist.create('00-008-00013', kind='error-code')
item.value['ENG'] = 'NpyFile must have filename set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that filename was not set for drsfile.npyfile'
langlist.add(item)

# =============================================================================
# 00-008-00014 
# =============================================================================
item = langlist.create('00-008-00014', kind='error-code')
item.value['ENG'] = 'NpyFile must have data set. \n\t Filename = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that data is not set for drsfile.npyfile'
langlist.add(item)

# =============================================================================
# 00-008-00015 
# =============================================================================
item = langlist.create('00-008-00015', kind='error-code')
item.value['ENG'] = 'NpyFile could not read file. \n\t Filename = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means there was a problem reading data for drsfile.npyfile'
langlist.add(item)

# =============================================================================
# 00-008-00016 
# =============================================================================
item = langlist.create('00-008-00016', kind='error-code')
item.value['ENG'] = 'Output file = {0} has no attribute ‘output_dict’ and therefore cannot be added to output_files. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that ‘add_output_file’ was used by outfile has no attribute ‘output_dict’ and therefore cannot be added to output_files'
langlist.add(item)

# =============================================================================
# 00-008-00017 
# =============================================================================
item = langlist.create('00-008-00017', kind='error-code')
item.value['ENG'] = '\'infile\' is not valid. Current infile=\'{0}\' required infile=\'{1}\' \n\t Constructed filename = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that construct file infile was not suitably defined (must have infile set)'
langlist.add(item)

# =============================================================================
# 00-008-00018 
# =============================================================================
item = langlist.create('00-008-00018', kind='error-code')
item.value['ENG'] = 'Could not load NPY file. \n\t Error {0}: {1} \n\t File = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not load npy file'
langlist.add(item)

# =============================================================================
# 00-008-00019 
# =============================================================================
item = langlist.create('00-008-00019', kind='error-code')
item.value['ENG'] = 'Error reading file, format was incorrect (fmt=\'{1}\'). \n\t File = {0} \n\t Valid formats = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that defined format was incorrect'
langlist.add(item)

# =============================================================================
# 00-008-00020 
# =============================================================================
item = langlist.create('00-008-00020', kind='error-code')
item.value['ENG'] = 'Could not save text file: {0} \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not save text file'
langlist.add(item)

# =============================================================================
# 00-008-00021 
# =============================================================================
item = langlist.create('00-008-00021', kind='error-code')
item.value['ENG'] = 'Could not copy file to {0} database. \n\t File = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that file copy to database dir failed'
langlist.add(item)

# =============================================================================
# 00-009-00001 
# =============================================================================
item = langlist.create('00-009-00001', kind='error-code')
item.value['ENG'] = 'Error opening index file: \'{0}\' \n\t Error was {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that we couldn\'t open index file with astropy.Table'
langlist.add(item)

# =============================================================================
# 00-009-10001 
# =============================================================================
item = langlist.create('00-009-10001', kind='error-code')
item.value['ENG'] = 'Mode \'{0}\' is not recognized for continuum fit'
item.arguments = 'None'
item.comment = 'Mode is not recognized for continuum fit'
langlist.add(item)

# =============================================================================
# 00-009-10002 
# =============================================================================
item = langlist.create('00-009-10002', kind='error-code')
item.value['ENG'] = 'x (data type: \'{0}\') must be an array/list/float/int'
item.arguments = 'None'
item.comment = 'Means sigfig x value is not an array/list/float or integer'
langlist.add(item)

# =============================================================================
# 00-009-10003 
# =============================================================================
item = langlist.create('00-009-10003', kind='error-code')
item.value['ENG'] = '{0} must be a factor of {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means medbin binning factor was not a factor of dimension'
langlist.add(item)

# =============================================================================
# 00-010-00001 
# =============================================================================
item = langlist.create('00-010-00001', kind='error-code')
item.value['ENG'] = 'Generic Drs File \'{0}\' has no associated files \n\t filename = {1} \n{2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not file a file for file set'
langlist.add(item)

# =============================================================================
# 00-010-00002 
# =============================================================================
item = langlist.create('00-010-00002', kind='error-code')
item.value['ENG'] = 'Full flat ({0}) not found in directory {1}. Please correct.'
item.arguments = 'None'
item.comment = 'Means that full flat file is missing from data dir'
langlist.add(item)

# =============================================================================
# 00-010-00003 
# =============================================================================
item = langlist.create('00-010-00003', kind='error-code')
item.value['ENG'] = 'Could not find pp file with name \'{0}\'. '
item.arguments = 'None'
item.comment = 'Means that the output file was not found in pp fileset'
langlist.add(item)

# =============================================================================
# 00-010-00004 
# =============================================================================
item = langlist.create('00-010-00004', kind='error-code')
item.value['ENG'] = 'Tapas file ({0}) not found in directory {1}. Please correct.'
item.arguments = 'None'
item.comment = 'Means that tapas file was not found'
langlist.add(item)

# =============================================================================
# 00-010-00005 
# =============================================================================
item = langlist.create('00-010-00005', kind='error-code')
item.value['ENG'] = 'Gaia lookup table ({0}) not found in directory {1}. Please correct'
item.arguments = 'None'
item.comment = 'Means that the gaia look up table was not found'
langlist.add(item)

# =============================================================================
# 00-010-00006 
# =============================================================================
item = langlist.create('00-010-00006', kind='error-code')
item.value['ENG'] = 'Could not find file = {0} in fileset. Allowed names are: \n\t {0} \n\n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that infile was not found in out fileset'
langlist.add(item)

# =============================================================================
# 00-010-00007 
# =============================================================================
item = langlist.create('00-010-00007', kind='error-code')
item.value['ENG'] = 'Generic Drs File \'{0}\' has no associated files \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that drs file set hase no associated files'
langlist.add(item)

# =============================================================================
# 00-010-00008 
# =============================================================================
item = langlist.create('00-010-00008', kind='error-code')
item.value['ENG'] = 'Reject list cannot be loaded. Column \'{0}\' does not exist. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that reject list column was not valid'
langlist.add(item)

# =============================================================================
# 00-010-00009 
# =============================================================================
item = langlist.create('00-010-00009', kind='error-code')
item.value['ENG'] = 'Could not load table from url: {0} \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not load table from url'
langlist.add(item)

# =============================================================================
# 00-010-00010 
# =============================================================================
item = langlist.create('00-010-00010', kind='error-code')
item.value['ENG'] = 'Could not load table from url: {0} \n\t Tried 10 times \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that we could not load table from url and tried 10 times'
langlist.add(item)

# =============================================================================
# 00-010-00011 
# =============================================================================
item = langlist.create('00-010-00011', kind='error-code')
item.value['ENG'] = 'Must define ‘objname’ or ‘header’'
item.arguments = 'None'
item.comment = 'Means that objname and header were both None – must define one or the other'
langlist.add(item)

# =============================================================================
# 00-010-00012 
# =============================================================================
item = langlist.create('00-010-00012', kind='error-code')
item.value['ENG'] = 'Header must be fixed (header must contain {0})'
item.arguments = 'None'
item.comment = 'Means that header supplied was not fixed'
langlist.add(item)

# =============================================================================
# 00-011-00001 
# =============================================================================
item = langlist.create('00-011-00001', kind='error-code')
item.value['ENG'] = 'No valid DARK/SKYDARK in {0} database {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that no valid dark or sky was found (and either allowed to be used)'
langlist.add(item)

# =============================================================================
# 00-011-00002 
# =============================================================================
item = langlist.create('00-011-00002', kind='error-code')
item.value['ENG'] = 'No valid DARK in {0} database {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that no valid dark was found (and skydark was not allowed to be used)'
langlist.add(item)

# =============================================================================
# 00-011-00003 
# =============================================================================
item = langlist.create('00-011-00003', kind='error-code')
item.value['ENG'] = 'No valid SKYDARK in {0} database {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that no valid skydark was found (and dark was not allowed to be used)'
langlist.add(item)

# =============================================================================
# 00-011-00004 
# =============================================================================
item = langlist.create('00-011-00004', kind='error-code')
item.value['ENG'] = '(with time <= {0})'
item.arguments = 'None'
item.comment = 'Means that database get mode was \'older\' '
langlist.add(item)

# =============================================================================
# 00-012-00001 
# =============================================================================
item = langlist.create('00-012-00001', kind='error-code')
item.value['ENG'] = 'Badpix engineering full flat not found \n\t filename = {0} \n\t directory = {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Reports that full engineering flat for badpix was not found'
langlist.add(item)

# =============================================================================
# 00-012-00002 
# =============================================================================
item = langlist.create('00-012-00002', kind='error-code')
item.value['ENG'] = 'Header must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Reports that header was not set in badpix correction'
langlist.add(item)

# =============================================================================
# 00-012-00003 
# =============================================================================
item = langlist.create('00-012-00003', kind='error-code')
item.value['ENG'] = 'Image must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Reports that image was not set in badpix correction'
langlist.add(item)

# =============================================================================
# 00-013-00001 
# =============================================================================
item = langlist.create('00-013-00001', kind='error-code')
item.value['ENG'] = 'File DPRTYPE={0} was not valid for recipe {1}, thus fiber not assigned. \n\t Allowed DPRTYPES are: {2} \n\t filename = {3}'
item.arguments = 'None'
item.comment = 'Means that DPRTYPE was not correct type and thus fiber type could not be found'
langlist.add(item)

# =============================================================================
# 00-013-00002 
# =============================================================================
item = langlist.create('00-013-00002', kind='error-code')
item.value['ENG'] = 'Kind = \'{0}\' must be either \'center\' or \'fwhm\' \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'kind\' was wrong must be \'center\' of \'fwhm\' for initial fit'
langlist.add(item)

# =============================================================================
# 00-013-00003 
# =============================================================================
item = langlist.create('00-013-00003', kind='error-code')
item.value['ENG'] = 'Kind = \'{0}\' must be either \'center\' or \'fwhm\' \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'kind\' was wrong must be \'center\' of \'fwhm\' for sigma clip'
langlist.add(item)

# =============================================================================
# 00-013-00004 
# =============================================================================
item = langlist.create('00-013-00004', kind='error-code')
item.value['ENG'] = 'Length of header={2} not consistent with length of data={1}\n\tFile={0}\n\tfunction={3}'
item.arguments = 'None'
item.comment = 'Means that header list and data list were different lengths in write function'
langlist.add(item)

# =============================================================================
# 00-013-00005 
# =============================================================================
item = langlist.create('00-013-00005', kind='error-code')
item.value['ENG'] = 'Length of datatype={2} not consistent with length of data={1}\n\tFile={0}\n\tfunction={3}'
item.arguments = 'None'
item.comment = 'Means that datatype list and data list were different lengths in write function'
langlist.add(item)

# =============================================================================
# 00-013-00006 
# =============================================================================
item = langlist.create('00-013-00006', kind='error-code')
item.value['ENG'] = 'Length of dtype={2} not consistent with length of data={1}\n\tFile={0}\n\tfunction={3}'
item.arguments = 'None'
item.comment = 'Means that dtype list and data list were different lengths in write function'
langlist.add(item)

# =============================================================================
# 00-013-00007 
# =============================================================================
item = langlist.create('00-013-00007', kind='error-code')
item.value['ENG'] = 'Length of name={2} not constistent with length of data={1}\n\tFile={0}\n\tfunction={3}'
item.arguments = 'None'
item.comment = 'Means that extension names list and data list were different lengths in write function'
langlist.add(item)

# =============================================================================
# 00-013-00008 
# =============================================================================
item = langlist.create('00-013-00008', kind='error-code')
item.value['ENG'] = 'Inconsistent number of orders between fiber {0} (={1}) and fiber {2} (={3}) \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that there was an inconsistent number of orders between fibers'
langlist.add(item)

# =============================================================================
# 00-014-00001 
# =============================================================================
item = langlist.create('00-014-00001', kind='error-code')
item.value['ENG'] = 'Image 1 (shape={0}) not the same shape as image 2 (shape={1}). \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that image1 and image2 were not the same size (in get linear transform parameters function)'
langlist.add(item)

# =============================================================================
# 00-014-00002 
# =============================================================================
item = langlist.create('00-014-00002', kind='error-code')
item.value['ENG'] = 'Incorrect shape for dx map (shape={0}) must be {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that dx map was not the same shape as image'
langlist.add(item)

# =============================================================================
# 00-014-00003 
# =============================================================================
item = langlist.create('00-014-00003', kind='error-code')
item.value['ENG'] = 'Incorrect shape for dy map (shape={0}) must be {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the dy map was not the same shape as image'
langlist.add(item)

# =============================================================================
# 00-016-00001 
# =============================================================================
item = langlist.create('00-016-00001', kind='error-code')
item.value['ENG'] = 'start order value was set but was not a valid integer (value = {0}) \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'means that start order value was not an integer'
langlist.add(item)

# =============================================================================
# 00-016-00002 
# =============================================================================
item = langlist.create('00-016-00002', kind='error-code')
item.value['ENG'] = 'end order value was set but was not a valid integer (value = {0}) \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'means the end order value was not an integer'
langlist.add(item)

# =============================================================================
# 00-016-00003 
# =============================================================================
item = langlist.create('00-016-00003', kind='error-code')
item.value['ENG'] = 'start order was set but value was not 0 or greater. Value = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'means that start order was given but was not 0 or greater'
langlist.add(item)

# =============================================================================
# 00-016-00004 
# =============================================================================
item = langlist.create('00-016-00004', kind='error-code')
item.value['ENG'] = 'start order (value = {0}) was greater than end order (value = {1}). \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'means that start order was greater than end order'
langlist.add(item)

# =============================================================================
# 00-016-00005 
# =============================================================================
item = langlist.create('00-016-00005', kind='error-code')
item.value['ENG'] = 'skip_orders is not a valid list of integers (value = {0}) \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'means that skip orders could not be converted to a list of integers'
langlist.add(item)

# =============================================================================
# 00-016-00006 
# =============================================================================
item = langlist.create('00-016-00006', kind='error-code')
item.value['ENG'] = 'shape of image {0} not the same as order profile {1}. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'means that order profile and image do not have same dimensions'
langlist.add(item)

# =============================================================================
# 00-016-00007 
# =============================================================================
item = langlist.create('00-016-00007', kind='error-code')
item.value['ENG'] = 'Could not convert range dictionary to dict. \n\t Check parameter {0} or {1} (if set). \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'means that range dictionary was not a valid python dictionary'
langlist.add(item)

# =============================================================================
# 00-016-00008 
# =============================================================================
item = langlist.create('00-016-00008', kind='error-code')
item.value['ENG'] = 'Range dictionary does not have entry for fiber=\'{0}\'. \n\t RangeDict = {1}  \n\t Check parameter {2} or {3} (if set). \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'means that the range dictionary does not have the fiber specified in it'
langlist.add(item)

# =============================================================================
# 00-016-00009 
# =============================================================================
item = langlist.create('00-016-00009', kind='error-code')
item.value['ENG'] = 'Range dictionary entry for fiber=\'{0}\' was not a valid float.  \n\t RangeDict = {1} \n\t Check parameter {2} or {3} (if set). \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'means that the range dictionary fiber value was not a integer'
langlist.add(item)

# =============================================================================
# 00-016-00010 
# =============================================================================
item = langlist.create('00-016-00010', kind='error-code')
item.value['ENG'] = 'Range dictionary entry for fiber=\'{0}\' wave not valid. \n\t RangeDict = {1} \n\t Error {2}: {3} \n\t Check parameter {4} or {5} (if set). \n\t Function = {6}'
item.arguments = 'None'
item.comment = 'means that there was another problem with the range dictionary fiber value'
langlist.add(item)

# =============================================================================
# 00-016-00011 
# =============================================================================
item = langlist.create('00-016-00011', kind='error-code')
item.value['ENG'] = 'Could not find BERV parameter \'{0}\' in \'infile\' or \'header\' or \'props\' or kwargs. \n\t Must be defined in one of these places. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that we could not find a berv parameter in \'infile\' or \'header\' or \'props\' or \'kwargs\''
langlist.add(item)

# =============================================================================
# 00-016-00012 
# =============================================================================
item = langlist.create('00-016-00012', kind='error-code')
item.value['ENG'] = 'Could not convert BERV unit parameter \'{0}\'=\'{1}\' to units \'{2}\'. \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that there was a problem pushing input units to BERV parameter'
langlist.add(item)

# =============================================================================
# 00-016-00013 
# =============================================================================
item = langlist.create('00-016-00013', kind='error-code')
item.value['ENG'] = 'Could not convert BERV time parameter \'{0}\'=\'{1}\' to time \'{2}\' \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that there was a problem pushing input (time) to BERV parameter'
langlist.add(item)

# =============================================================================
# 00-016-00014 
# =============================================================================
item = langlist.create('00-016-00014', kind='error-code')
item.value['ENG'] = 'Could not convert BERV parameter \'{0}\'=\'{1}\' to dtype \'{2}\' \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that there was a problem pushing input dtype to BERV parameter'
langlist.add(item)

# =============================================================================
# 00-016-00015 
# =============================================================================
item = langlist.create('00-016-00015', kind='error-code')
item.value['ENG'] = 'Could not convert BERV parameter \'{0}\'=\'{1}\' from {2} to {3}.  \n\t Error {4}: {5} \n\t Function = {6}'
item.arguments = 'None'
item.comment = 'Means that we could not convert input BERV parameter units to output BERV units'
langlist.add(item)

# =============================================================================
# 00-016-00016 
# =============================================================================
item = langlist.create('00-016-00016', kind='error-code')
item.value['ENG'] = 'Could not convert BERV parameter \'{0}\'=\'{1}\' from {2} to {3}.  \n\t Error {4}: {5} \n\t Function = {6}'
item.arguments = 'None'
item.comment = 'Means that we could not convert input BERV parameter time to output BERV time'
langlist.add(item)

# =============================================================================
# 00-016-00017 
# =============================================================================
item = langlist.create('00-016-00017', kind='error-code')
item.value['ENG'] = 'Could not calculate the BERV estimate for time={0}. \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not calculate the BERV estimate'
langlist.add(item)

# =============================================================================
# 00-016-00018 
# =============================================================================
item = langlist.create('00-016-00018', kind='error-code')
item.value['ENG'] = 'Could not use units = \'{0}\' for exposure time conversion \n\t Must be either {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the exposure time units were not valid'
langlist.add(item)

# =============================================================================
# 00-016-00019 
# =============================================================================
item = langlist.create('00-016-00019', kind='error-code')
item.value['ENG'] = '\'infile\' or \'header\' must be defined. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that both \'header\' and \'infile\' were not defined'
langlist.add(item)

# =============================================================================
# 00-016-00020 
# =============================================================================
item = langlist.create('00-016-00020', kind='error-code')
item.value['ENG'] = 'BERV_KEYS was badly defined. Input key = {0} (parameter = {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that BERV_KEYS had key that was badly defined'
langlist.add(item)

# =============================================================================
# 00-016-00021 
# =============================================================================
item = langlist.create('00-016-00021', kind='error-code')
item.value['ENG'] = 'Gaia crossmatch error: Must provide either a \'gaiaid\' or a \'objname\' or an \'ra and dec\' \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that the cross match to gaia failed due to no gaiaid and no objname and no ra / dec'
langlist.add(item)

# =============================================================================
# 00-016-00022 
# =============================================================================
item = langlist.create('00-016-00022', kind='error-code')
item.value['ENG'] = 'Gaia crossmatch error: Could not update lookup table (filename={0}) \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not update lookup table'
langlist.add(item)

# =============================================================================
# 00-016-00023 
# =============================================================================
item = langlist.create('00-016-00023', kind='error-code')
item.value['ENG'] = 'File instance for order profile tmp file must be a DrsNpyFile. \n\t Current file = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that order profile npy file was defined incorrectly'
langlist.add(item)

# =============================================================================
# 00-016-00024 
# =============================================================================
item = langlist.create('00-016-00024', kind='error-code')
item.value['ENG'] = 'Reference fiber \'{0}\' not found in extraction dictionary. \n\t Possible fibers are: [1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that reference fiber was not found in extraction dictionary'
langlist.add(item)

# =============================================================================
# 00-016-00025 
# =============================================================================
item = langlist.create('00-016-00025', kind='error-code')
item.value['ENG'] = 'Reference fiber \'{0}\' must be a FP. DPRTYPE = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that reference file (for reference fiber) did not contain an FP'
langlist.add(item)

# =============================================================================
# 00-016-00026 
# =============================================================================
item = langlist.create('00-016-00026', kind='error-code')
item.value['ENG'] = 'Science fiber \'{0}\' not found in extraction dictionary. \n\t Possible fibers are: [1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that science fiber was not found in extraction dictionary'
langlist.add(item)

# =============================================================================
# 00-016-00027 
# =============================================================================
item = langlist.create('00-016-00027', kind='error-code')
item.value['ENG'] = 'Cannot copy extract file fiber=\'{0}\' filetype=\'{1}\' - file does not exist. File = {2}'
item.arguments = 'None'
item.comment = 'Means that we could not save uncorrected extracted file as it does not exist'
langlist.add(item)

# =============================================================================
# 00-016-00028 
# =============================================================================
item = langlist.create('00-016-00028', kind='error-code')
item.value['ENG'] = 'Cannot apply space motion for object={0} \n\t ra: {1:.4f} dec: {2:.4f} \n\tpmra: {3:.4f} pmde: {4:.4f} \nplx: {5:.4f} epoch: {6}'
item.arguments = 'None'
item.comment = 'Means applying space motion failed'
langlist.add(item)

# =============================================================================
# 00-017-00001 
# =============================================================================
item = langlist.create('00-017-00001', kind='error-code')
item.value['ENG'] = 'If “infile” is provided must be a DrsFitsFile Instance. Infile={0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that “infile” was provided by was not a valid DrsFitsFile'
langlist.add(item)

# =============================================================================
# 00-017-00002 
# =============================================================================
item = langlist.create('00-017-00002', kind='error-code')
item.value['ENG'] = 'Line list not found. File = {0}; \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that the line list could not be loaded'
langlist.add(item)

# =============================================================================
# 00-017-00003 
# =============================================================================
item = langlist.create('00-017-00003', kind='error-code')
item.value['ENG'] = 'Insufficient number of lines found. \n\t Found = {0} Required = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that an insufficient number of lines were found in triplet fit'
langlist.add(item)

# =============================================================================
# 00-017-00004 
# =============================================================================
item = langlist.create('00-017-00004', kind='error-code')
item.value['ENG'] = '[LITTROW] Remove order warning: {0}={1} in {2} \n\tPlease check constants file \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that current order is in remove orders [in littrow]'
langlist.add(item)

# =============================================================================
# 00-017-00005 
# =============================================================================
item = langlist.create('00-017-00005', kind='error-code')
item.value['ENG'] = '[LITTROW] Invalid order number={0} in {1} \n\t Must be between {2} and {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that remove order was not in valid range of orders [in littrow]'
langlist.add(item)

# =============================================================================
# 00-017-00006 
# =============================================================================
item = langlist.create('00-017-00006', kind='error-code')
item.value['ENG'] = '[LITTROW] Cannot remove all orders. \n\t Please check {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means we removed all orders in the remove order process'
langlist.add(item)

# =============================================================================
# 00-017-00007 
# =============================================================================
item = langlist.create('00-017-00007', kind='error-code')
item.value['ENG'] = 'Order {0}: Sigma clipping in 1D fit solution failed. \n\t RMS > MAX_RMS={1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that sigma clipping failed in the fp 1d fit solution'
langlist.add(item)

# =============================================================================
# 00-017-00008 
# =============================================================================
item = langlist.create('00-017-00008', kind='error-code')
item.value['ENG'] = 'Cannot get wavelength solution from header. \n\t Key ‘{0}’ is not present, file in valid. {1} = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that header comes from a pp file (no output key) and thus we cannot get a wavelength solution'
langlist.add(item)

# =============================================================================
# 00-017-00009 
# =============================================================================
item = langlist.create('00-017-00009', kind='error-code')
item.value['ENG'] = 'No header defined. Cannot continue. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'cannot get wavelines because there was no header'
langlist.add(item)

# =============================================================================
# 00-017-00010 
# =============================================================================
item = langlist.create('00-017-00010', kind='error-code')
item.value['ENG'] = 'No reference {0} line file found in calibration database. Please run {1} recipe. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'No entries found in calibration database for HC/FP reference line list. Solution is to run wave_reference'
langlist.add(item)

# =============================================================================
# 00-017-00011 
# =============================================================================
item = langlist.create('00-017-00011', kind='error-code')
item.value['ENG'] = 'Key \'{0}\' not found in {1} reference table. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means hc/fp lines did not have the correct columns'
langlist.add(item)

# =============================================================================
# 00-017-00012 
# =============================================================================
item = langlist.create('00-017-00012', kind='error-code')
item.value['ENG'] = 'e2ds file = \"{0}\" (dprtype={1} fiber={2}) not valid for {3}\n\t Valid HC types: {4} \n\t Valid FP types = {5}'
item.arguments = 'None'
item.comment = 'Means that e2ds file was not valid type to get reference wave lines'
langlist.add(item)

# =============================================================================
# 00-017-00013 
# =============================================================================
item = langlist.create('00-017-00013', kind='error-code')
item.value['ENG'] = 'Number of Echelle orders (={0}) must be the same as number of orders (={1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the number of echelle orders did not match the number of orders'
langlist.add(item)

# =============================================================================
# 00-017-00014 
# =============================================================================
item = langlist.create('00-017-00014', kind='error-code')
item.value['ENG'] = 'Cannot have fit_achromatic=True without cavity_update input'
item.arguments = 'None'
item.comment = 'Means that we cannot fit achromatically as we don’t have a cavity update'
langlist.add(item)

# =============================================================================
# 00-018-00001 
# =============================================================================
item = langlist.create('00-018-00001', kind='warning_2-code')
item.value['ENG'] = '\tCurve Fit Warning (N={0}): {1}'
item.arguments = 'None'
item.comment = 'Means that curve_fit caused an error that was skipped'
langlist.add(item)

# =============================================================================
# 00-019-00001 
# =============================================================================
item = langlist.create('00-019-00001', kind='error-code')
item.value['ENG'] = 'Internal error in recipe {0}. Controller recipe ({1}) cannot continue'
item.arguments = 'None'
item.comment = 'Means that there was an error inside loop function (mk_tellu / fit_tellu or mk_template)'
langlist.add(item)

# =============================================================================
# 00-020-00001 
# =============================================================================
item = langlist.create('00-020-00001', kind='error-code')
item.value['ENG'] = 'Length of rv vector (len={0}) and ccf vector (len={1}) are not the same. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the length of the rv vector and the ccf vector were not the same'
langlist.add(item)

# =============================================================================
# 00-020-00002 
# =============================================================================
item = langlist.create('00-020-00002', kind='error-code')
item.value['ENG'] = 'Cannot find ccf mask file {0} in directory {1}'
item.arguments = 'None'
item.comment = 'Means that CCF mask file was not found'
langlist.add(item)

# =============================================================================
# 00-020-00003 
# =============================================================================
item = langlist.create('00-020-00003', kind='error-code')
item.value['ENG'] = 'Could not locate reference file for infile=\'{0}\' (Intype=\'{1}\' was not a pp file) \n\t Infilename = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was a problem locating the reference file (intype was not a pp file)'
langlist.add(item)

# =============================================================================
# 00-021-00001 
# =============================================================================
item = langlist.create('00-021-00001', kind='error-code')
item.value['ENG'] = 'Unsupported number of valid fibers. Value = {0}. Constant = {1}. Can only support 2 fibers. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that number of valid fibers was not 2. Only 2 valid fibers are supported'
langlist.add(item)

# =============================================================================
# 00-021-00002 
# =============================================================================
item = langlist.create('00-021-00002', kind='error-code')
item.value['ENG'] = 'Fit function=\'{0}\' is invalid \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that function is invalid for fit_continuum'
langlist.add(item)

# =============================================================================
# 00-090-00001 
# =============================================================================
item = langlist.create('00-090-00001', kind='error-code')
item.value['ENG'] = 'Cannot process links. Infile not set for primary extension. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that filename of extension 0 did not exist'
langlist.add(item)

# =============================================================================
# 00-090-00002 
# =============================================================================
item = langlist.create('00-090-00002', kind='error-code')
item.value['ENG'] = 'Link name={0} not valid for extension {1} ({2}) \n\t Valid link names: {3}\n\tFunction: {4}'
item.arguments = 'None'
item.comment = 'Means that link name is not valid for extension'
langlist.add(item)

# =============================================================================
# 00-090-00003 
# =============================================================================
item = langlist.create('00-090-00003', kind='error-code')
item.value['ENG'] = 'Header link key={0} not valid for link name={1}\n\tlink file={2}\n\tFunction = {3}'
item.arguments = 'None'
item.comment = 'Means that header key link is not valid for extension'
langlist.add(item)

# =============================================================================
# 00-090-00004 
# =============================================================================
item = langlist.create('00-090-00004', kind='error-code')
item.value['ENG'] = 'Header link key={0} is not valid for link name={1}\n\theader key \"{2}\" not found \n\tlink file={3}\n\tFunction={4}'
item.arguments = 'None'
item.comment = 'Means that header key for header link was not valid for link'
langlist.add(item)

# =============================================================================
# 00-090-00005 
# =============================================================================
item = langlist.create('00-090-00005', kind='error-code')
item.value['ENG'] = 'No entries found for extension {0} ({1}) \n\t Condition = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that file was not found for extension'
langlist.add(item)

# =============================================================================
# 00-090-00006 
# =============================================================================
item = langlist.create('00-090-00006', kind='error-code')
item.value['ENG'] = 'Could not add {0} extension {1} ({2})\n\tFilename: {3} \n\tError {4}: {5}\n\tFunction: {6}'
item.arguments = 'None'
item.comment = 'Means that we could not load image extension for some reason'
langlist.add(item)

# =============================================================================
# 00-090-00007 
# =============================================================================
item = langlist.create('00-090-00007', kind='error-code')
item.value['ENG'] = 'Column file for EXT={0} ({1}) not found. \n\t Condition = {2}\n\tFunction = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not find a file to add to the table column'
langlist.add(item)

# =============================================================================
# 00-090-00008 
# =============================================================================
item = langlist.create('00-090-00008', kind='error-code')
item.value['ENG'] = 'Column for EXT={0} ({1}) not found \n\tFilename={2}\n\tColumn name = {3} \n\tFunction = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not find a column in a file to add to the table column'
langlist.add(item)

# =============================================================================
# 00-090-00009 
# =============================================================================
item = langlist.create('00-090-00009', kind='error-code')
item.value['ENG'] = 'Column for EXT={0} ({1}) not found \n\tFilename={2}\n\tColumn name = {3} \n\tColumn \'{4}\' length={5} (File: {6}) \n\tColumn \'{7}\' length={8} (File: {9})\n\tFunction: {10}'
item.arguments = 'None'
item.comment = 'Means that column had the wrong length for the table column'
langlist.add(item)

# =============================================================================
# 00-090-00010 
# =============================================================================
item = langlist.create('00-090-00010', kind='error-code')
item.value['ENG'] = '{0} error(s) occurred for {1}'
item.arguments = 'None'
item.comment = 'Report how many errors found'
langlist.add(item)

# =============================================================================
# 00-090-00011 
# =============================================================================
item = langlist.create('00-090-00011', kind='error-code')
item.value['ENG'] = 'Cannot add hkey {0} (in extension {1} does not exist) [{2}]'
item.arguments = 'None'
item.comment = 'Means that we don\'t have the in/out extension key'
langlist.add(item)

# =============================================================================
# 00-090-00012 
# =============================================================================
item = langlist.create('00-090-00012', kind='error-code')
item.value['ENG'] = 'Cannot add hkey {0} (in extension {1} does not exist) [key not found]'
item.arguments = 'None'
item.comment = 'Means that we don\'t have the in/out extension key'
langlist.add(item)

# =============================================================================
# 00-090-00013 
# =============================================================================
item = langlist.create('00-090-00013', kind='error-code')
item.value['ENG'] = 'No valid calibration entry dbkey=\"{0}\" for extension {1} ({2} \n\t Link {3} ({4}) \n\t Link file: {5} \n\t Function: {6}'
item.arguments = 'None'
item.comment = 'Means that we don\'t have valid calibration entry for this file'
langlist.add(item)

# =============================================================================
# 00-090-00014 
# =============================================================================
item = langlist.create('00-090-00014', kind='error-code')
item.value['ENG'] = 'No valid telluric entry dbkey=\"{0}\" for extension {1} ({2} \n\t Link {3} ({4}) \n\t Link file: {5} \n\t Function: {6}'
item.arguments = 'None'
item.comment = 'Means that we don\'t have valid telluric entry for this file'
langlist.add(item)

# =============================================================================
# 00-090-00015 
# =============================================================================
item = langlist.create('00-090-00015', kind='error-code')
item.value['ENG'] = 'Cannot use {0} entry for extension {1} ({2}) \n\t Column = {3}'
item.arguments = 'None'
item.comment = 'Means that user tried to use a calib/tellu entry for a column'
langlist.add(item)

# =============================================================================
# 00-100-00001 
# =============================================================================
item = langlist.create('00-100-00001', kind='error-code')
item.value['ENG'] = 'Plotter error: graph name = \'{0}\' was not found in plotting definitions. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that graph \'name\' was not found in definitions'
langlist.add(item)

# =============================================================================
# 00-100-00002 
# =============================================================================
item = langlist.create('00-100-00002', kind='error-code')
item.value['ENG'] = 'Plotter error: graph name = \'{0}\' was not defined for recipe {1}. \n\t Please check recipe definitions (\'set_debug_plots\' and \'set_summary_plots\')'
item.arguments = 'None'
item.comment = 'Means that graph was not defined in recipe debug or summary plots'
langlist.add(item)

# =============================================================================
# 00-100-00003 
# =============================================================================
item = langlist.create('00-100-00003', kind='error-code')
item.value['ENG'] = 'Plotter error: must set file location before any plotting is called with plot(). \n\t Please set with plot.set_location() \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that file location was not set for plotting (must be done before any plotting is done)'
langlist.add(item)

# =============================================================================
# 00-502-00001 
# =============================================================================
item = langlist.create('00-502-00001', kind='error-code')
item.value['ENG'] = 'Reset {0} directory: Default directory not found at location {1}'
item.arguments = 'None'
item.comment = 'Means that the \'directory\' reset folder could not be found in drs data'
langlist.add(item)

# =============================================================================
# 00-502-00002 
# =============================================================================
item = langlist.create('00-502-00002', kind='error-code')
item.value['ENG'] = 'Directory does not exist: {0}'
item.arguments = 'None'
item.comment = 'Means that directory does not exist and user chose not to create it'
langlist.add(item)

# =============================================================================
# 00-503-00001 
# =============================================================================
item = langlist.create('00-503-00001', kind='error-code')
item.value['ENG'] = 'Cannot send email (need pip install yagmail)'
item.arguments = 'None'
item.comment = 'Means that we could not import yagmail'
langlist.add(item)

# =============================================================================
# 00-503-00002 
# =============================================================================
item = langlist.create('00-503-00002', kind='error-code')
item.value['ENG'] = 'Error {0}: {1} \n\t file = \'{2}\' \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was another problem with yagmail'
langlist.add(item)

# =============================================================================
# 00-503-00003 
# =============================================================================
item = langlist.create('00-503-00003', kind='error-code')
item.value['ENG'] = 'Problem with paths: {0} and {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was a problem with the uncommon paths'
langlist.add(item)

# =============================================================================
# 00-503-00004 
# =============================================================================
item = langlist.create('00-503-00004', kind='warning_8-code')
item.value['ENG'] = 'Unexpected error occurred in run \'{0}\''
item.arguments = 'None'
item.comment = 'Means that an unexpected error was caught'
langlist.add(item)

# =============================================================================
# 00-503-00005 
# =============================================================================
item = langlist.create('00-503-00005', kind='warning_8-code')
item.value['ENG'] = 'Expected error occurred in run \'{0}\''
item.arguments = 'None'
item.comment = 'Means that an expected (WLOG) error was caught'
langlist.add(item)

# =============================================================================
# 00-503-00006 
# =============================================================================
item = langlist.create('00-503-00006', kind='error-code')
item.value['ENG'] = 'Run file error: \'CORES\'=\'{0}\' must be an integer \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that \'cores\' in run file was not an integer and caused a value error'
langlist.add(item)

# =============================================================================
# 00-503-00007 
# =============================================================================
item = langlist.create('00-503-00007', kind='error-code')
item.value['ENG'] = 'Run file error: \'CORES\' must be an integer \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that \'cores\' in run file lead to an error'
langlist.add(item)

# =============================================================================
# 00-503-00008 
# =============================================================================
item = langlist.create('00-503-00008', kind='warning_6-code')
item.value['ENG'] = 'Run file error: Number of cores must be greater than 0 \n\t Current value = {0}'
item.arguments = 'None'
item.comment = 'Means that number of cores was less than 1'
langlist.add(item)

# =============================================================================
# 00-503-00009 
# =============================================================================
item = langlist.create('00-503-00009', kind='warning_2-code')
item.value['ENG'] = 'Run file error: Number of cores must be less than {0} \n\t Current value = {1}'
item.arguments = 'None'
item.comment = 'Means that number of cores exceeds allowed number of cores'
langlist.add(item)

# =============================================================================
# 00-503-00010 
# =============================================================================
item = langlist.create('00-503-00010', kind='error-code')
item.value['ENG'] = 'Run table generation error: argument \'{0}\' was a list but not the correct length (needs to be {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that in generate_run_table kwargs or args were lists but not the same length'
langlist.add(item)

# =============================================================================
# 00-503-00011 
# =============================================================================
item = langlist.create('00-503-00011', kind='error-code')
item.value['ENG'] = 'Run table generation error: recipe \'{0}\' is not valid for instrument \'{1}\'. \n\t Please check instruments: \n\t - recipe definitions \n\t - \'recipes\' list \n\t - sequences definitions \n\t - \'sequences\' list. \n Function = {2}'
item.arguments = 'None'
item.comment = 'Means that recipe (from run table) was not valid for instrument'
langlist.add(item)

# =============================================================================
# 00-503-00012 
# =============================================================================
item = langlist.create('00-503-00012', kind='error-code')
item.value['ENG'] = 'Overwrite argument: Argument {0} not found in args/kwargs. Correct DrsSequence. \n\t {0} = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that overwrite “arguments” was set but we could not add argument '
langlist.add(item)

# =============================================================================
# 00-503-00013 
# =============================================================================
item = langlist.create('00-503-00013', kind='error-code')
item.value['ENG'] = 'User input error: \'--cores\'=\'{0}\' must be an integer \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means that \'cores\'  was defiend by user but was not an integer and caused a value error'
langlist.add(item)

# =============================================================================
# 00-503-00014 
# =============================================================================
item = langlist.create('00-503-00014', kind='error-code')
item.value['ENG'] = 'User input error: \'--cores\' must be an integer \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'to de-sim'
langlist.add(item)

# =============================================================================
# 00-503-00015 
# =============================================================================
item = langlist.create('00-503-00015', kind='warning_8-code')
item.value['ENG'] = 'System exit occurred in run \'{0}\''
item.arguments = 'None'
item.comment = 'Means that an system exit error was caught'
langlist.add(item)

# =============================================================================
# 00-503-00016 
# =============================================================================
item = langlist.create('00-503-00016', kind='error-code')
item.value['ENG'] = 'Creating lock directory failed. \n\t Error {0}: {1} \n\t Directory = {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that creation of lock file failed'
langlist.add(item)

# =============================================================================
# 00-503-00017 
# =============================================================================
item = langlist.create('00-503-00017', kind='warning_6-code')
item.value['ENG'] = 'Filter error: Filter {0} = \'{1}\' not valid for recipe {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means sequence defined an invalid filter'
langlist.add(item)

# =============================================================================
# 00-503-00018 
# =============================================================================
item = langlist.create('00-503-00018', kind='error-code')
item.value['ENG'] = 'No rows in database (after reference conditions applied) \n\t Condition = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means we have no rows in database - i.e. no data'
langlist.add(item)

# =============================================================================
# 00-505-00001 
# =============================================================================
item = langlist.create('00-505-00001', kind='error-code')
item.value['ENG'] = 'Instrument does not have {0} sequence defined. \n\t Please define \'{1}\' in \'{2}\'. \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that instrument does not have \'file_set_name\' defined'
langlist.add(item)

# =============================================================================
# 01-000-00000 
# =============================================================================
item = langlist.create('01-000-00000', kind='error-code')
item.value['ENG'] = 'IO Error: General Error'
item.arguments = 'None'
item.comment = 'IO Error'
langlist.add(item)

# =============================================================================
# 01-000-00001 
# =============================================================================
item = langlist.create('01-000-00001', kind='error-code')
item.value['ENG'] = 'Could not create directory \'{0}\'. Error was {1}:'
item.arguments = 'None'
item.comment = 'Error making a path'
langlist.add(item)

# =============================================================================
# 01-001-00000 
# =============================================================================
item = langlist.create('01-001-00000', kind='error-code')
item.value['ENG'] = 'IO Error: File Error'
item.arguments = 'None'
item.comment = 'IO File Error'
langlist.add(item)

# =============================================================================
# 01-001-00001 
# =============================================================================
item = langlist.create('01-001-00001', kind='error-code')
item.value['ENG'] = 'Recovery failed: Fatal I/O error cannot load file. \n\t filename=\'{0}\''
item.arguments = 'None'
item.comment = 'Means that we cannot open the fits file in question'
langlist.add(item)

# =============================================================================
# 01-001-00002 
# =============================================================================
item = langlist.create('01-001-00002', kind='error-code')
item.value['ENG'] = 'File \'{0}\' cannot be accessed (file locked and max wait time exceeded. \n\t Please make sure \'{0}\' is not being used and manually delete \'{1}\'.'
item.arguments = 'None'
item.comment = 'Means that we exceeded the make wait time for a locked file'
langlist.add(item)

# =============================================================================
# 01-001-00003 
# =============================================================================
item = langlist.create('01-001-00003', kind='error-code')
item.value['ENG'] = 'File \'{0}\' already exits and cannot be overwritten. \n\tError {1}: {2}\n\tfunction = {3}'
item.arguments = 'None'
item.comment = 'Means that file already exits and we cannot overwrite it for some reach (using os.remove)'
langlist.add(item)

# =============================================================================
# 01-001-00004 
# =============================================================================
item = langlist.create('01-001-00004', kind='error-code')
item.value['ENG'] = 'Cannot open image with astropy.io.fits \n\tError {0}: {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was an error using astropy.io.fits when trying to open a Primary HDU for writing'
langlist.add(item)

# =============================================================================
# 01-001-00005 
# =============================================================================
item = langlist.create('01-001-00005', kind='error-code')
item.value['ENG'] = 'Cannot write image to fits file \'{0}\' \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was an error using hdu.writeto when trying to write filename to disk'
langlist.add(item)

# =============================================================================
# 01-001-00006 
# =============================================================================
item = langlist.create('01-001-00006', kind='error-code')
item.value['ENG'] = 'File = \'{0}\' cannot be opened by astropy.io.fits \n\tError {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was a problem using astropy.io.fits when trying to open a Primary HDU for reading'
langlist.add(item)

# =============================================================================
# 01-001-00007 
# =============================================================================
item = langlist.create('01-001-00007', kind='error-code')
item.value['ENG'] = 'Could not open data for file \'{0}\' extension={1} \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not open the data for file (using hdu[ext].data) in DrsFitsFile.read'
langlist.add(item)

# =============================================================================
# 01-001-00008 
# =============================================================================
item = langlist.create('01-001-00008', kind='error-code')
item.value['ENG'] = 'Could not open header for file \'{0}\' extension={1} \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not open the header for file (using hdu[ext].header) in DrsFitsfile.read'
langlist.add(item)

# =============================================================================
# 01-001-00009 
# =============================================================================
item = langlist.create('01-001-00009', kind='error-code')
item.value['ENG'] = 'Could not open data for file \'{0}\' extension={1} \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means there was a problem with \'fits.getdata\' in DrsFitsFile.read_data'
langlist.add(item)

# =============================================================================
# 01-001-00010 
# =============================================================================
item = langlist.create('01-001-00010', kind='error-code')
item.value['ENG'] = 'Could not open header for file \'{0}\' extension={1} \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that there was a problem with \'fits.getheader\' in Drsfitsfile.read_header'
langlist.add(item)

# =============================================================================
# 01-001-00011 
# =============================================================================
item = langlist.create('01-001-00011', kind='error-code')
item.value['ENG'] = 'Cannot open log file {0} \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was a problem doing \'open(filename, \'a\') on log file'
langlist.add(item)

# =============================================================================
# 01-001-00012 
# =============================================================================
item = langlist.create('01-001-00012', kind='error-code')
item.value['ENG'] = 'Read Error: File \'{0}\' could not be found in directory \'{1}\'. \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that filename does not exist (in read function)'
langlist.add(item)

# =============================================================================
# 01-001-00013 
# =============================================================================
item = langlist.create('01-001-00013', kind='error-code')
item.value['ENG'] = 'Read Error: Directory \'{0}\' could not be found (file=\'{1}\'). \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the filename\'s directory does not exist (in read function)'
langlist.add(item)

# =============================================================================
# 01-001-00014 
# =============================================================================
item = langlist.create('01-001-00014', kind='error-code')
item.value['ENG'] = 'Read Error: Fits-Image (data) could not be read. \n\t Filename = {0} {1} \n\t Error was type {2}'
item.arguments = 'None'
item.comment = 'Means that fits-image data could not be opened in read function'
langlist.add(item)

# =============================================================================
# 01-001-00015 
# =============================================================================
item = langlist.create('01-001-00015', kind='error-code')
item.value['ENG'] = 'Read Error: Fits-Image (header) could not be read. \n\t Filename = {0} {1} \n\t Error was type {2}'
item.arguments = 'None'
item.comment = 'Means that fits-image header could not be opened in read function'
langlist.add(item)

# =============================================================================
# 01-001-00016 
# =============================================================================
item = langlist.create('01-001-00016', kind='error-code')
item.value['ENG'] = 'Read Error: Fits-Table (data) could not be read. \n\t Filename = {0}, Ext = {1} \n\t Error was type {2}'
item.arguments = 'None'
item.comment = 'Means that fits-table data could not be opened in read function'
langlist.add(item)

# =============================================================================
# 01-001-00017 
# =============================================================================
item = langlist.create('01-001-00017', kind='error-code')
item.value['ENG'] = 'Read Error: Fits-Table (header) could not be read. \n\t Filename = {0}, Ext = {1} \n\t Error was type {2}'
item.arguments = 'None'
item.comment = 'Means that fits-table header could not be opened in read function'
langlist.add(item)

# =============================================================================
# 01-001-00018 
# =============================================================================
item = langlist.create('01-001-00018', kind='error-code')
item.value['ENG'] = 'Cannot write to {0} database (key = {1}). \n\t Error {2}: {3} \n\t file = {4} \n\t function = {5}'
item.arguments = 'None'
item.comment = 'Means that database file could not be written to'
langlist.add(item)

# =============================================================================
# 01-001-00019 
# =============================================================================
item = langlist.create('01-001-00019', kind='error-code')
item.value['ENG'] = 'Cannot read {0} database \n\t Error {1}: {2} \n\t file = {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that database file could not be read from'
langlist.add(item)

# =============================================================================
# 01-001-00020 
# =============================================================================
item = langlist.create('01-001-00020', kind='error-code')
item.value['ENG'] = 'Invalid file type = \'{0}\'. \n\t function = {1}. \n Must be one of the following:'
item.arguments = 'None'
item.comment = 'Means that “filetype” was not in “allowedtypes” in function'
langlist.add(item)

# =============================================================================
# 01-001-00021 
# =============================================================================
item = langlist.create('01-001-00021', kind='error-code')
item.value['ENG'] = 'No index files found at path = {0}. \n\t Please run an off_listing script to continue. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that no index files were found in path'
langlist.add(item)

# =============================================================================
# 01-001-00022 
# =============================================================================
item = langlist.create('01-001-00022', kind='error-code')
item.value['ENG'] = 'Could not load drs data file = {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that no file was found when trying to load a drs data file'
langlist.add(item)

# =============================================================================
# 01-001-00023 
# =============================================================================
item = langlist.create('01-001-00023', kind='error-code')
item.value['ENG'] = 'Path is unset and \'OUTPATH\' (in params) is unset. One of these must be set. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that path is unset and params[\'OUTPATH\'] is unset when trying to construct a path'
langlist.add(item)

# =============================================================================
# 01-001-00024 
# =============================================================================
item = langlist.create('01-001-00024', kind='error-code')
item.value['ENG'] = 'Text file {0} could not be read. \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that text file cannot be read'
langlist.add(item)

# =============================================================================
# 01-001-00025 
# =============================================================================
item = langlist.create('01-001-00025', kind='error-code')
item.value['ENG'] = 'Text file {0} could not be read (wrong format) \n\t Line {1}: {2} \n\t Lines must be in format: value1 {3} value2 \n\t\t where value1 and value2 are valid python strings \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that there was bad formating in text file'
langlist.add(item)

# =============================================================================
# 01-001-00026 
# =============================================================================
item = langlist.create('01-001-00026', kind='error-code')
item.value['ENG'] = 'No valid lines found in text file: {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that there were no valid lines in file'
langlist.add(item)

# =============================================================================
# 01-001-00027 
# =============================================================================
item = langlist.create('01-001-00027', kind='error-code')
item.value['ENG'] = 'Cannot fix header key=\'{0}\' missing \n\t File = {1}'
item.arguments = 'None'
item.comment = 'Means that a header key used to ID a file was not found in header'
langlist.add(item)

# =============================================================================
# 01-002-00000 
# =============================================================================
item = langlist.create('01-002-00000', kind='error-code')
item.value['ENG'] = 'IO Error: System Error'
item.arguments = 'None'
item.comment = 'IO Table Error'
langlist.add(item)

# =============================================================================
# 01-002-00001 
# =============================================================================
item = langlist.create('01-002-00001', kind='error-code')
item.value['ENG'] = 'Column names (length = {0}) must be equal to length of \'values\' (length = {1}) \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the length of \'values\' was not equal to the length of \'columns\''
langlist.add(item)

# =============================================================================
# 01-002-00002 
# =============================================================================
item = langlist.create('01-002-00002', kind='error-code')
item.value['ENG'] = 'Column names (length = {0}) must be equal to length of \'formats\' (length = {1}) \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the length of \'formats\' was not equal to the length of \'columns\''
langlist.add(item)

# =============================================================================
# 01-002-00003 
# =============================================================================
item = langlist.create('01-002-00003', kind='error-code')
item.value['ENG'] = 'Column names (length = {0}) must be equal to length of \'units\' (length = {1}) \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the length of \'units\' was not equal to the length of \'columns\''
langlist.add(item)

# =============================================================================
# 01-002-00004 
# =============================================================================
item = langlist.create('01-002-00004', kind='error-code')
item.value['ENG'] = 'All column-values must have the same number of rows \n\t function = {0}'
item.arguments = 'None'
item.comment = 'Means that all the rows in values are the same length as each other, i.e. that each column has the same number of values'
langlist.add(item)

# =============================================================================
# 01-002-00005 
# =============================================================================
item = langlist.create('01-002-00005', kind='error-code')
item.value['ENG'] = 'Format \'{0}\' is invalid (Column = \'{1}\') \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that the format that is wanted (set by \'formats\') for this column is not a valid format for an astropy.table column'
langlist.add(item)

# =============================================================================
# 01-002-00006 
# =============================================================================
item = langlist.create('01-002-00006', kind='error-code')
item.value['ENG'] = 'Table format = {0} not valid for astropy.table. \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that the table format was not valid for file (i.e. not \'fits\' or \'ascii\' etc)'
langlist.add(item)

# =============================================================================
# 01-002-00007 
# =============================================================================
item = langlist.create('01-002-00007', kind='error-code')
item.value['ENG'] = 'Table format = {0} cannot be written by astropy.table \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that the table format was not valid for writing a file (i.e. not \'fits\' or \'ascii\' etc)'
langlist.add(item)

# =============================================================================
# 01-002-00008 
# =============================================================================
item = langlist.create('01-002-00008', kind='error-code')
item.value['ENG'] = 'Cannot write table to file. \n\t Error {0}: {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that there was an error using astropy.table.write'
langlist.add(item)

# =============================================================================
# 01-002-00009 
# =============================================================================
item = langlist.create('01-002-00009', kind='error-code')
item.value['ENG'] = 'Cannot write header to file. \n\t Error {0}: {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means we had a fits file but could not add header to fits file'
langlist.add(item)

# =============================================================================
# 01-002-00010 
# =============================================================================
item = langlist.create('01-002-00010', kind='error-code')
item.value['ENG'] = 'Cannot merge file={0} \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that we cannot merge file into table'
langlist.add(item)

# =============================================================================
# 01-002-00011 
# =============================================================================
item = langlist.create('01-002-00011', kind='error-code')
item.value['ENG'] = 'File does not exist. \n\t file = \'{0}\' \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that we could not find file to read'
langlist.add(item)

# =============================================================================
# 01-002-00012 
# =============================================================================
item = langlist.create('01-002-00012', kind='error-code')
item.value['ENG'] = 'Error {0}: {1} \n\t file = \'{2}\' \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that there was an error inside Table.read'
langlist.add(item)

# =============================================================================
# 01-002-00013 
# =============================================================================
item = langlist.create('01-002-00013', kind='error-code')
item.value['ENG'] = 'Number of columns ({0}) not equal to number of columns in table ({1}) \n\t file = \'{2}\' \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that colnames was defined but the number of columns found in table does not match this - so we cannot rename columns'
langlist.add(item)

# =============================================================================
# 01-002-00014 
# =============================================================================
item = langlist.create('01-002-00014', kind='error-code')
item.value['ENG'] = 'Fits file {0} does not exist \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that fits file does not exist'
langlist.add(item)

# =============================================================================
# 01-002-00015 
# =============================================================================
item = langlist.create('01-002-00015', kind='error-code')
item.value['ENG'] = 'Cannot open {0} as a fits table \n\t Error was {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not use Table.read to open file and there was an error reported'
langlist.add(item)

# =============================================================================
# 01-002-00016 
# =============================================================================
item = langlist.create('01-002-00016', kind='error-code')
item.value['ENG'] = 'Directory {0} does not exist \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that directory for \'output_filename\' does not exist'
langlist.add(item)

# =============================================================================
# 01-002-00017 
# =============================================================================
item = langlist.create('01-002-00017', kind='error-code')
item.value['ENG'] = 'Cannot write {0} as a fits table. \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that astropy.table.write caused an error'
langlist.add(item)

# =============================================================================
# 01-002-00018 
# =============================================================================
item = langlist.create('01-002-00018', kind='error-code')
item.value['ENG'] = 'Cannot open {0} as a fits table \n\t Error was {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that we couldn\'t open file as a fits file (i.e. hdu.data[0] and hdu.data[1] were both None)'
langlist.add(item)

# =============================================================================
# 01-002-00019 
# =============================================================================
item = langlist.create('01-002-00019', kind='error-code')
item.value['ENG'] = 'Cannot open {0} as a fits table \n\t Error was: data cannot read \'columns\' \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means the hdu.data opened has no attribute \'columns\''
langlist.add(item)

# =============================================================================
# 01-002-00020 
# =============================================================================
item = langlist.create('01-002-00020', kind='error-code')
item.value['ENG'] = 'Cannot open {0} as a fits table \n\t Error was: data cannot read \'columns.names\' \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means the hdu.data opened has no attribute \'names\''
langlist.add(item)

# =============================================================================
# 01-002-00021 
# =============================================================================
item = langlist.create('01-002-00021', kind='error-code')
item.value['ENG'] = 'Column \'{0}\' not in file \'{1}\' \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that we could not find \'column\' in file'
langlist.add(item)

# =============================================================================
# 01-002-00022 
# =============================================================================
item = langlist.create('01-002-00022', kind='error-code')
item.value['ENG'] = 'Incompatible data types for column = \'{0}\' for file \'{1}\' \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that there was an error when trying to set the format type'
langlist.add(item)

# =============================================================================
# 01-002-00023 
# =============================================================================
item = langlist.create('01-002-00023', kind='error-code')
item.value['ENG'] = 'Cannot backup {0} as a fits table. \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not back up astropy table'
langlist.add(item)

# =============================================================================
# 01-010-00000 
# =============================================================================
item = langlist.create('01-010-00000', kind='error-code')
item.value['ENG'] = 'IO Error: System Error'
item.arguments = 'None'
item.comment = 'IO System Error'
langlist.add(item)

# =============================================================================
# 01-010-00001 
# =============================================================================
item = langlist.create('01-010-00001', kind='error-code')
item.value['ENG'] = 'Unhandled error has occurred: Error {0}'
item.arguments = 'None'
item.comment = 'Unhandled error (i.e. non-handled error message)'
langlist.add(item)

# =============================================================================
# 01-010-00002 
# =============================================================================
item = langlist.create('01-010-00002', kind='error-code')
item.value['ENG'] = 'Could not create directory \'{0}\' \n\t Error {1}: {2} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means we could not make directory with os.makedirs'
langlist.add(item)

# =============================================================================
# 09-000-00000 
# =============================================================================
item = langlist.create('09-000-00000', kind='error-code')
item.value['ENG'] = 'User Error: General Error'
item.arguments = 'None'
item.comment = 'User Error'
langlist.add(item)

# =============================================================================
# 09-000-00001 
# =============================================================================
item = langlist.create('09-000-00001', kind='error-code')
item.value['ENG'] = 'File \'{0}\' found in directory \'{1}\''
item.arguments = 'None'
item.comment = 'File found (for DrsFile)'
langlist.add(item)

# =============================================================================
# 09-000-00002 
# =============================================================================
item = langlist.create('09-000-00002', kind='error-code')
item.value['ENG'] = 'File \'{0}\' does not exist in directory \'{1}\''
item.arguments = 'None'
item.comment = 'File not found (for DrsFile)'
langlist.add(item)

# =============================================================================
# 09-000-00003 
# =============================================================================
item = langlist.create('09-000-00003', kind='error-code')
item.value['ENG'] = 'File \'{0}\' extension not checked.'
item.arguments = 'None'
item.comment = 'File extension not checked (for DrsFile)'
langlist.add(item)

# =============================================================================
# 09-000-00004 
# =============================================================================
item = langlist.create('09-000-00004', kind='error-code')
item.value['ENG'] = 'File \'{0}\' has correct extension (\'{1}\')'
item.arguments = 'None'
item.comment = 'File extension is correct (for DrsFile)'
langlist.add(item)

# =============================================================================
# 09-000-00005 
# =============================================================================
item = langlist.create('09-000-00005', kind='error-code')
item.value['ENG'] = 'File \'{0}\' must have extension \'{1}\''
item.arguments = 'None'
item.comment = 'File extension is incorrect  (for DrsFile)'
langlist.add(item)

# =============================================================================
# 09-000-00006 
# =============================================================================
item = langlist.create('09-000-00006', kind='error-code')
item.value['ENG'] = 'Key \'{0}\' not found in header of file \'{1}\' \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that header key was not found in fits file'
langlist.add(item)

# =============================================================================
# 09-000-00007 
# =============================================================================
item = langlist.create('09-000-00007', kind='error-code')
item.value['ENG'] = 'Key \'{0}\' (\'{2}\') not found in header of file \'{1}\' \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that header key was not found in fits file (when key is taken from constants)'
langlist.add(item)

# =============================================================================
# 09-000-00008 
# =============================================================================
item = langlist.create('09-000-00008', kind='error-code')
item.value['ENG'] = 'Cannot find key \'{0}\' with dim={1} in header for file={2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means \'key\' was not found in the header of \'file\' for the read_key_1d_list function'
langlist.add(item)

# =============================================================================
# 09-000-00009 
# =============================================================================
item = langlist.create('09-000-00009', kind='error-code')
item.value['ENG'] = 'Cannot find key \'{0}\' (input={1}) with dim1={2} dim2={3} in header for file={4} \n\t function = {5}'
item.arguments = 'None'
item.comment = 'Means \'key\' was not found in the header of \'file\' for the read_key_2d_list function'
langlist.add(item)

# =============================================================================
# 09-000-00010 
# =============================================================================
item = langlist.create('09-000-00010', kind='error-code')
item.value['ENG'] = 'No FP files passed 2D quality control. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that all FP files were not valid'
langlist.add(item)

# =============================================================================
# 09-000-00011 
# =============================================================================
item = langlist.create('09-000-00011', kind='error-code')
item.value['ENG'] = 'QC failure of reference recipe: {0}'
item.arguments = 'None'
item.comment = 'Means a reference recipe failed QC - this is not allowed'
langlist.add(item)

# =============================================================================
# 09-001-00000 
# =============================================================================
item = langlist.create('09-001-00000', kind='error-code')
item.value['ENG'] = 'User Error: Argument Error'
item.arguments = 'None'
item.comment = 'User Argument Error'
langlist.add(item)

# =============================================================================
# 09-001-00001 
# =============================================================================
item = langlist.create('09-001-00001', kind='error-code')
item.value['ENG'] = 'Argument Error (Error from ArgParse): \n\t {0} \n\t Use: \'{1}.py --help\' for help.  '
item.arguments = 'None'
item.comment = 'User Argument Error in DRSArgumentParser message is an internal ArgParse error message'
langlist.add(item)

# =============================================================================
# 09-001-00002 
# =============================================================================
item = langlist.create('09-001-00002', kind='error-code')
item.value['ENG'] = 'unrecognized arguments: {0}'
item.arguments = 'None'
item.comment = 'Text for ArgParse: arguments were unrecognized'
langlist.add(item)

# =============================================================================
# 09-001-00003 
# =============================================================================
item = langlist.create('09-001-00003', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Directory = \'{1}\' is not valid (type = \'{2}\')'
item.arguments = 'None'
item.comment = 'Directory type must be a string'
langlist.add(item)

# =============================================================================
# 09-001-00004 
# =============================================================================
item = langlist.create('09-001-00004', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Directory = \'{1}\' not found \n\tTried \n\t\t{1}\n\t\t{2}'
item.arguments = 'None'
item.comment = 'Directory was not found and prints paths tried'
langlist.add(item)

# =============================================================================
# 09-001-00005 
# =============================================================================
item = langlist.create('09-001-00005', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': File =\'{1}\' was not found \n\tTried:\n\t\t\'{1}\'\n\t\t\'{2}\''
item.arguments = 'None'
item.comment = 'Argument Error: Argument is file but was not found'
langlist.add(item)

# =============================================================================
# 09-001-00006 
# =============================================================================
item = langlist.create('09-001-00006', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Extension of file not valid \n\t\tRequired extension=\'{1}\''
item.arguments = 'None'
item.comment = 'Argument Error: Extension for file is not valid'
langlist.add(item)

# =============================================================================
# 09-001-00007 
# =============================================================================
item = langlist.create('09-001-00007', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Header key \'{1}\' not found.'
item.arguments = 'None'
item.comment = 'Argument Error: A required header key was not found in the file header'
langlist.add(item)

# =============================================================================
# 09-001-00008 
# =============================================================================
item = langlist.create('09-001-00008', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': File identified as \'{1}\'\n\tHowever, previous file(s) identified as \'{2}\'\n\tFiles must match (logic set to \'exclusive\')'
item.arguments = 'None'
item.comment = 'Argument Error: Current file identified as being a different type than previous files and recipe demands exclusivity (defined in recipe definitions)'
langlist.add(item)

# =============================================================================
# 09-001-00009 
# =============================================================================
item = langlist.create('09-001-00009', kind='error-code')
item.value['ENG'] = 'Current file has:'
item.arguments = 'None'
item.comment = 'partial error wrapper for drs_file.construct_header_error. Precedes the list: Key1 = value1, Key2 = value2, Key3 = value3 for the current file'
langlist.add(item)

# =============================================================================
# 09-001-00010 
# =============================================================================
item = langlist.create('09-001-00010', kind='error-code')
item.value['ENG'] = 'Recipe required values are:'
item.arguments = 'None'
item.comment = 'partial error wrapper for drs_file.construct_header_error. Precedes the list: Key1 = value1, Key2 = value2, Key3 = value3 required by this recipe'
langlist.add(item)

# =============================================================================
# 09-001-00011 
# =============================================================================
item = langlist.create('09-001-00011', kind='error-code')
item.value['ENG'] = 'exclusive'
item.arguments = 'None'
item.comment = 'partial error that shows files are exclusive (i.e. X OR Y OR Z in any combination)'
langlist.add(item)

# =============================================================================
# 09-001-00012 
# =============================================================================
item = langlist.create('09-001-00012', kind='error-code')
item.value['ENG'] = 'inclusive'
item.arguments = 'None'
item.comment = 'partial error that shows files are exclusive (i.e. X OR Y OR Z in any combination)'
langlist.add(item)

# =============================================================================
# 09-001-00013 
# =============================================================================
item = langlist.create('09-001-00013', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Value must be a boolean (True/False) \n\t Current value = \'{1}\'  \n\t Acceptable values for True are: true, yes, 1 \n\t Acceptable values for False are: false, no, 0'
item.arguments = 'None'
item.comment = 'Means that the \'current value\' was not in the following acceptable criteria: [\'yes\', \'true\', \'t\', \'y\', \'1\', \'no\', \'false\', \'f\', \'n\', \'0\']'
langlist.add(item)

# =============================================================================
# 09-001-00014 
# =============================================================================
item = langlist.create('09-001-00014', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Value must be of type \'{1}\' (ValueError) \n\t Current value = \'{2}\''
item.arguments = 'None'
item.comment = 'Means that the \'current value\' was not correct for the required dtype set value was raised by a ValueError'
langlist.add(item)

# =============================================================================
# 09-001-00015 
# =============================================================================
item = langlist.create('09-001-00015', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Value must be of type \'{1}\' (TypeError) \n\t Current value = \'{2}\''
item.arguments = 'None'
item.comment = 'Means that the \'current value\' was not correct for the required dtype set value was raised by a TypeError'
langlist.add(item)

# =============================================================================
# 09-001-00016 
# =============================================================================
item = langlist.create('09-001-00016', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Value must not be an empty list'
item.arguments = 'None'
item.comment = 'Means that \'value\' was an empty list (in DrsRecipe._check_type)'
langlist.add(item)

# =============================================================================
# 09-001-00017 
# =============================================================================
item = langlist.create('09-001-00017', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Too many values for argument. (Expected {1} got {2})'
item.arguments = 'None'
item.comment = 'Means that we found too many args when evaluating input. Number of args is set by DrsRecipe.nargs (set in recipe definition) '
langlist.add(item)

# =============================================================================
# 09-001-00018 
# =============================================================================
item = langlist.create('09-001-00018', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': List was expected with {1} argument(s) but type found was \'{2}\' \n\t Current value = \'{3}\''
item.arguments = 'None'
item.comment = 'Means that the dtype was not correct and that dtype is not a list (in DrsRecipe._check_type)'
langlist.add(item)

# =============================================================================
# 09-001-00019 
# =============================================================================
item = langlist.create('09-001-00019', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Value must be one of the following: {1} \n\t Current value = \'{2}\''
item.arguments = 'None'
item.comment = 'Means that options were set for argument and the current value did not match one of those options'
langlist.add(item)

# =============================================================================
# 09-001-00020 
# =============================================================================
item = langlist.create('09-001-00020', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': Debug mode = \'{1}\' not understood.'
item.arguments = 'None'
item.comment = 'Means that the debug value was set incorrectly (in ActivateDebug._set_debug()'
langlist.add(item)

# =============================================================================
# 09-001-00021 
# =============================================================================
item = langlist.create('09-001-00021', kind='error-code')
item.value['ENG'] = '\t- File is not a \'{0}\' file'
item.arguments = 'None'
item.comment = 'Means that file was not the correct DrsFile type'
langlist.add(item)

# =============================================================================
# 09-001-00022 
# =============================================================================
item = langlist.create('09-001-00022', kind='error-code')
item.value['ENG'] = '\t\t {0} = \'{1}\' (Required: {2})'
item.arguments = 'None'
item.comment = 'Means that {2} was required for key {0} but we got {1} instead'
langlist.add(item)

# =============================================================================
# 09-001-00023 
# =============================================================================
item = langlist.create('09-001-00023', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': File could not be identified - incorrect HEADER values: '
item.arguments = 'None'
item.comment = 'Mean that file could not be identified because of incorrect header values'
langlist.add(item)

# =============================================================================
# 09-001-00024 
# =============================================================================
item = langlist.create('09-001-00024', kind='error-code')
item.value['ENG'] = ' File = \'{0}\''
item.arguments = 'None'
item.comment = 'Prints the file as part of the error'
langlist.add(item)

# =============================================================================
# 09-001-00025 
# =============================================================================
item = langlist.create('09-001-00025', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': \'{1}\' is not a valid file (and not a directory)'
item.arguments = 'None'
item.comment = 'Means that os.path.dir and os.path.file returned False in drs_recipe._check_file_location()'
langlist.add(item)

# =============================================================================
# 09-001-00026 
# =============================================================================
item = langlist.create('09-001-00026', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': \'{1}\' is a directory'
item.arguments = 'None'
item.comment = 'Means that os.path.dir returned True in drs_recipe._check_file_location()'
langlist.add(item)

# =============================================================================
# 09-001-00027 
# =============================================================================
item = langlist.create('09-001-00027', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': value=\'{1}\' must be larger than or equal to \'{2}\''
item.arguments = 'None'
item.comment = 'Means that the user entered a number that was too small'
langlist.add(item)

# =============================================================================
# 09-001-00028 
# =============================================================================
item = langlist.create('09-001-00028', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': value=\'{1}\' must be smaller than or equal to \'{2}\''
item.arguments = 'None'
item.comment = 'Means that the user entered a number that was too larger'
langlist.add(item)

# =============================================================================
# 09-001-00029 
# =============================================================================
item = langlist.create('09-001-00029', kind='error-code')
item.value['ENG'] = 'Argument \'{0}\': value=\'{1}\' must be between \'{2}\' and \'{3}\''
item.arguments = 'None'
item.comment = 'Means that the user entered a number that was too small or too large'
langlist.add(item)

# =============================================================================
# 09-001-00030 
# =============================================================================
item = langlist.create('09-001-00030', kind='error-code')
item.value['ENG'] = 'User requested fiber={0} however fiber must be: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the user defined “fiber” but it did not match one of the fibers in FIBER_TYPES (from constants)'
langlist.add(item)

# =============================================================================
# 09-001-00031 
# =============================================================================
item = langlist.create('09-001-00031', kind='error-code')
item.value['ENG'] = 'User input file {0} = {1} was not found. Please find file or check recipe inputs.'
item.arguments = 'None'
item.comment = 'Prints that input file was not found'
langlist.add(item)

# =============================================================================
# 09-001-00032 
# =============================================================================
item = langlist.create('09-001-00032', kind='error-code')
item.value['ENG'] = 'Cannot use argument \'{0}\'. ({1} database required and INSTRUMENT=\'None\') \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that we cannot use argument as INSTRUMENT = None and database is required'
langlist.add(item)

# =============================================================================
# 09-001-00033 
# =============================================================================
item = langlist.create('09-001-00033', kind='error-code')
item.value['ENG'] = 'No valid input {0} files after QC test:'
item.arguments = 'None'
item.comment = 'prints that there are no valid inputs after testing for QC'
langlist.add(item)

# =============================================================================
# 09-002-00000 
# =============================================================================
item = langlist.create('09-002-00000', kind='error-code')
item.value['ENG'] = 'User Error: Constant Error'
item.arguments = 'None'
item.comment = 'User Constant Error'
langlist.add(item)

# =============================================================================
# 09-002-00000 
# =============================================================================
item = langlist.create('09-002-00000', kind='error-code')
item.value['ENG'] = 'User Error: Constant Error'
item.arguments = 'None'
item.comment = 'User Database Error'
langlist.add(item)

# =============================================================================
# 09-002-00001 
# =============================================================================
item = langlist.create('09-002-00001', kind='error-code')
item.value['ENG'] = '{0} database: could not copy file {1} to {2}. \n\t Error {3}: {4} \n\t function = {5}'
item.arguments = 'None'
item.comment = 'Means we could not copy the file to the database folder'
langlist.add(item)

# =============================================================================
# 09-002-00002 
# =============================================================================
item = langlist.create('09-002-00002', kind='error-code')
item.value['ENG'] = 'Incorrectly formatted line in {0} database. \n\t file = {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that one of the database lines was incorrectly formatted'
langlist.add(item)

# =============================================================================
# 09-002-00003 
# =============================================================================
item = langlist.create('09-002-00003', kind='error-code')
item.value['ENG'] = 'No entries found in {0} database. \n\t file = {1} \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Means that there were no entries found in database'
langlist.add(item)

# =============================================================================
# 09-002-00004 
# =============================================================================
item = langlist.create('09-002-00004', kind='error-code')
item.value['ENG'] = 'Calibration file ({0}) was selected as the calibration file but is not within desired limits ({2}>{3} days) \n\tObsTime: {4}\n\tCalibTime:{5}\n\tFile: {1} \n\t Function: {6}'
item.arguments = 'None'
item.comment = 'Means that time between calibration and observation is not within desired limits'
langlist.add(item)

# =============================================================================
# 09-002-00005 
# =============================================================================
item = langlist.create('09-002-00005', kind='error-code')
item.value['ENG'] = 'OBJ_LIST_GOOGLE_SHEET_URL = {0}. \n\t If OBJ_LIST_GOOGLE_SHEET_URL is a local directory ‘main_id’ must be a valid csv file. \n\tError {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that OBJ_LIST_GOOGLE_SHEET_URL was a local path but that main_id was not a valid csv file'
langlist.add(item)

# =============================================================================
# 09-002-00006 
# =============================================================================
item = langlist.create('09-002-00006', kind='error-code')
item.value['ENG'] = 'REJECT_LIST_GOOGLE_SHEET_URL = {0} \n\t If REJECT_LIST_GOOGLE_SHEET_URL is a local directory ‘main_id’ must be a valid csv file. \n\tError {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that REJET_LIST_GOOGLE_SHEET_URL was a local path but that main_id was not a valid csv file'
langlist.add(item)

# =============================================================================
# 09-002-00000 
# =============================================================================
item = langlist.create('09-002-00000', kind='error-code')
item.value['ENG'] = 'User Error: Constant Error'
item.arguments = 'None'
item.comment = 'User io function error'
langlist.add(item)

# =============================================================================
# 09-003-00001 
# =============================================================================
item = langlist.create('09-003-00001', kind='error-code')
item.value['ENG'] = 'Image must have at least two dimensions to flip. \n\t Shape: {0} \n\t function = {1}'
item.arguments = 'None'
item.comment = 'Means that image did not have two dimensions for flip'
langlist.add(item)

# =============================================================================
# 09-003-00002 
# =============================================================================
item = langlist.create('09-003-00002', kind='error-code')
item.value['ENG'] = 'Could not make night name directory {0} (in directory {1}) \n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not make the night name directory'
langlist.add(item)

# =============================================================================
# 09-003-00003 
# =============================================================================
item = langlist.create('09-003-00003', kind='error-code')
item.value['ENG'] = 'Could not make night name directory {0} (in directory {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that we could not make the night name directory'
langlist.add(item)

# =============================================================================
# 09-010-00001 
# =============================================================================
item = langlist.create('09-010-00001', kind='error-code')
item.value['ENG'] = 'Filetype \'{0}\' is not valid for recipe={0} instrument={1}. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that input filetype was not valid for recipe/instrument'
langlist.add(item)

# =============================================================================
# 09-011-00005 
# =============================================================================
item = langlist.create('09-011-00005', kind='error-code')
item.value['ENG'] = 'No DARK_DARK files found in {0}'
item.arguments = 'None'
item.comment = 'Means no darks were found for dark reference'
langlist.add(item)

# =============================================================================
# 09-012-00001 
# =============================================================================
item = langlist.create('09-012-00001', kind='error-code')
item.value['ENG'] = 'Shapes do not match for engineering full flat: \'{0}\' and image: \'{1}\' \n\t function: {2}'
item.arguments = 'None'
item.comment = 'Error when engineering image is not the same shape as data'
langlist.add(item)

# =============================================================================
# 09-012-00002 
# =============================================================================
item = langlist.create('09-012-00002', kind='error-code')
item.value['ENG'] = 'Shapes do not match for flat image \'{0}\' and dark image \'{1}\' \n\t function = {2}'
item.arguments = 'None'
item.comment = 'Tells the user the dark and flat inputted have different shapes - these must be the same'
langlist.add(item)

# =============================================================================
# 09-016-00001 
# =============================================================================
item = langlist.create('09-016-00001', kind='error-code')
item.value['ENG'] = 'Extraction failed (see above error)'
item.arguments = 'None'
item.comment = 'Means that cal_extract failed in cal_thermal'
langlist.add(item)

# =============================================================================
# 09-016-00002 
# =============================================================================
item = langlist.create('09-016-00002', kind='error-code')
item.value['ENG'] = 'Extraction failed for {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that cal_extract failed for recipe'
langlist.add(item)

# =============================================================================
# 09-016-00003 
# =============================================================================
item = langlist.create('09-016-00003', kind='error-code')
item.value['ENG'] = 'QC Failed for extraction of {0} file. File = {1} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that the quality control was not passed for the extraction of {kind} file'
langlist.add(item)

# =============================================================================
# 09-016-00004 
# =============================================================================
item = langlist.create('09-016-00004', kind='error-code')
item.value['ENG'] = 'BERV value unusable. BERV = \'{0}\' \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that input berv was incorrect'
langlist.add(item)

# =============================================================================
# 09-016-00005 
# =============================================================================
item = langlist.create('09-016-00005', kind='error-code')
item.value['ENG'] = 'DPRTYPE = \'{0}\' not valid for thermal recipe \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'means that thermal dprtype was incorrect (this should be possible)'
langlist.add(item)

# =============================================================================
# 09-017-00001 
# =============================================================================
item = langlist.create('09-017-00001', kind='error-code')
item.value['ENG'] = 'Wave mode = \'{0}\' is currently unsupported (for HC)'
item.arguments = 'None'
item.comment = 'Means that \'WAVE_MODE_HC\' was incorrect'
langlist.add(item)

# =============================================================================
# 09-017-00002 
# =============================================================================
item = langlist.create('09-017-00002', kind='error-code')
item.value['ENG'] = 'Resolution map curve_fit error \n\t {0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that curve_fit incountered an error (when generating resolution map)'
langlist.add(item)

# =============================================================================
# 09-017-00003 
# =============================================================================
item = langlist.create('09-017-00003', kind='error-code')
item.value['ENG'] = 'Wave mode = \'{0}\' is currently unsupported (for FP)'
item.arguments = 'None'
item.comment = 'Means that \'WAVE_MODE_FP\' was incorrect'
langlist.add(item)

# =============================================================================
# 09-017-00004 
# =============================================================================
item = langlist.create('09-017-00004', kind='error-code')
item.value['ENG'] = 'WAVE_FP_LLFIT_MODE was incorrect. Must be 0 or 1. \n\t Current value = \'{0}\' \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that \'WAVE_FP_LLFIT_MODE\' was incorrect'
langlist.add(item)

# =============================================================================
# 09-017-00005 
# =============================================================================
item = langlist.create('09-017-00005', kind='error-code')
item.value['ENG'] = 'Calculated pixel index out of bound. Order = {0} Line = {1} \n\t pixel vals = {2} \n\t pixel cent = {3} width = {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that wave solution is not valid for this line'
langlist.add(item)

# =============================================================================
# 09-017-00006 
# =============================================================================
item = langlist.create('09-017-00006', kind='warning_4-code')
item.value['ENG'] = 'Pixel fit not possible - not enough points to fit. Order = {0} Line = {1} \n\t pixel vals = {2} \n\t flux values = {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that there were not enough values xpixi +/i wfit to fit wave sol to lines'
langlist.add(item)

# =============================================================================
# 09-017-00007 
# =============================================================================
item = langlist.create('09-017-00007', kind='error-code')
item.value['ENG'] = 'No reference wave solutions found in calibration database. \n\t Keys checked: {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that there were no reference wave solutions in calibration database'
langlist.add(item)

# =============================================================================
# 09-017-00008 
# =============================================================================
item = langlist.create('09-017-00008', kind='error-code')
item.value['ENG'] = 'Cannot calculate wavemap as ‘infile’ was not given and we required a header AND the size of each order in pixels \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means header was given to wave solution but the size of the pixels was not given and is required'
langlist.add(item)

# =============================================================================
# 09-017-00009 
# =============================================================================
item = langlist.create('09-017-00009', kind='error-code')
item.value['ENG'] = 'Too many iterations for bulk offset N={0}'
item.arguments = 'None'
item.comment = 'Means that we had too many iterations to figure out the bulk offset'
langlist.add(item)

# =============================================================================
# 09-018-00001 
# =============================================================================
item = langlist.create('09-018-00001', kind='error-code')
item.value['ENG'] = 'Observation directory = \"{0}\" is not a valid reduced sub-directory'
item.arguments = 'None'
item.comment = 'Report that observation directory is invalid'
langlist.add(item)

# =============================================================================
# 09-018-00002 
# =============================================================================
item = langlist.create('09-018-00002', kind='error-code')
item.value['ENG'] = 'User input error: fiber={0} is invalid. \n\t Fiber must be {1}'
item.arguments = 'None'
item.comment = 'user input fiber is invalid'
langlist.add(item)

# =============================================================================
# 09-019-00001 
# =============================================================================
item = langlist.create('09-019-00001', kind='error-code')
item.value['ENG'] = 'One of the orders in ‘{0}’ is out of bounds. \n\t Must be between 0 and {1} \n\t Fucntion = {2}'
item.arguments = 'None'
item.comment = 'Means MKTELLU_CLEAN_ORDERS had an invalid order present'
langlist.add(item)

# =============================================================================
# 09-019-00002 
# =============================================================================
item = langlist.create('09-019-00002', kind='error-code')
item.value['ENG'] = 'Telluric database does not have valid ‘{0}’ key. \n\t Required file name = {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that obj_fit_tellu could not load tapas convolve file for current reference wave solution'
langlist.add(item)

# =============================================================================
# 09-019-00003 
# =============================================================================
item = langlist.create('09-019-00003', kind='error-code')
item.value['ENG'] = 'Not enough transmission maps ({0}) in database to run PCA analysis \n\t Number of maps = {1}  number of principle components = {2} \n\t Add more maps or reduced number of principle components ({3}). \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that there were not enough transmission maps to run pca analysis (number of maps < number of principle components)'
langlist.add(item)

# =============================================================================
# 09-019-00004 
# =============================================================================
item = langlist.create('09-019-00004', kind='error-code')
item.value['ENG'] = 'Spectrum (shape = {0}) cannot be reshaped to match wave solution (shape = {1}) \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that spectrum has incorrect shape compared to wave solution map'
langlist.add(item)

# =============================================================================
# 09-019-00005 
# =============================================================================
item = langlist.create('09-019-00005', kind='error-code')
item.value['ENG'] = 'User defined template file (--template) does not exist. \n\t Tried: {0} \n\t Tried: {1}'
item.arguments = 'None'
item.comment = 'Means that user template file does not exist'
langlist.add(item)

# =============================================================================
# 09-019-00006 
# =============================================================================
item = langlist.create('09-019-00006', kind='error-code')
item.value['ENG'] = 'Curve fit failure (tellu_preclean) kind={0} Guess={1}'
item.arguments = 'None'
item.comment = 'Means that curve fitting failed in the tellu preclean'
langlist.add(item)

# =============================================================================
# 09-020-00001 
# =============================================================================
item = langlist.create('09-020-00001', kind='error-code')
item.value['ENG'] = 'Fiber={0} is not valid for \'science\'. (Required \'{1}\') \n\t File {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that the file provided for cal ccf was not the correct fiber for \'science\''
langlist.add(item)

# =============================================================================
# 09-020-00002 
# =============================================================================
item = langlist.create('09-020-00002', kind='error-code')
item.value['ENG'] = 'Fiber={0} is not valid for \'reference\'. (Required \'{1}\') \n\t File {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that the file provided for cal ccf did not have the correct \'reference\' fiber'
langlist.add(item)

# =============================================================================
# 09-020-00003 
# =============================================================================
item = langlist.create('09-020-00003', kind='error-code')
item.value['ENG'] = 'Cannot remove telluric domain for file: {0} \n\t The {1} file was not found: {2}'
item.arguments = 'None'
item.comment = 'Means that e2ds file or recon file did not exist for tellu file'
langlist.add(item)

# =============================================================================
# 09-020-00004 
# =============================================================================
item = langlist.create('09-020-00004', kind='error-code')
item.value['ENG'] = 'Astropy.units did not understand the units \'{0}\' used for the CCF mask file. \n\t {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'Means that the units the user set for the ccf mask were not correct'
langlist.add(item)

# =============================================================================
# 09-020-00005 
# =============================================================================
item = langlist.create('09-020-00005', kind='error-code')
item.value['ENG'] = 'CCF step much not be greater than CCF width / {2}. \n\t Current CCF step = {0} \n\t Current CCF width = {1} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that the ccf step was to small compared to ccf width'
langlist.add(item)

# =============================================================================
# 09-020-00006 
# =============================================================================
item = langlist.create('09-020-00006', kind='warning_2-code')
item.value['ENG'] = 'RV not found in header. Setting input RV to 0.0 \n\t Key={0}) \n\t File = {1}'
item.arguments = 'None'
item.comment = 'Means that the rv was not found in header'
langlist.add(item)

# =============================================================================
# 09-020-00007 
# =============================================================================
item = langlist.create('09-020-00007', kind='warning_2-code')
item.value['ENG'] = 'RV null value found in header. Setting input RV to 0.0 \n\t Key={0} Nullvalue={1} \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means that the rv in header was the null value'
langlist.add(item)

# =============================================================================
# 09-020-00008 
# =============================================================================
item = langlist.create('09-020-00008', kind='error-code')
item.value['ENG'] = 'Object temperature header key ‘{0}’ not in header.'
item.arguments = 'None'
item.comment = 'Means that the object teff header key is not in the header'
langlist.add(item)

# =============================================================================
# 09-020-00009 
# =============================================================================
item = langlist.create('09-020-00009', kind='error-code')
item.value['ENG'] = 'Cannot use {0} – must have default value in teff table kind column'
item.arguments = 'None'
item.comment = 'Means we have not got a default teff mask defined'
langlist.add(item)

# =============================================================================
# 09-021-00001 
# =============================================================================
item = langlist.create('09-021-00001', kind='error-code')
item.value['ENG'] = 'No polar files found in input files: {0}'
item.arguments = 'None'
item.comment = 'Means that no valid polar files were found'
langlist.add(item)

# =============================================================================
# 09-021-00002 
# =============================================================================
item = langlist.create('09-021-00002', kind='error-code')
item.value['ENG'] = 'Minimum number of polar files ({0}) not found. Files: {1}'
item.arguments = 'None'
item.comment = 'Means that minimum number of polar files were not found'
langlist.add(item)

# =============================================================================
# 09-021-00003 
# =============================================================================
item = langlist.create('09-021-00003', kind='error-code')
item.value['ENG'] = 'Multiple stokes parameters found can only accept one valid. \n\t Stokes parameters found = {0}'
item.arguments = 'None'
item.comment = 'Means that multiple stokes parameters were found'
langlist.add(item)

# =============================================================================
# 09-021-00004 
# =============================================================================
item = langlist.create('09-021-00004', kind='error-code')
item.value['ENG'] = 'Number of {0} and {1} files were the wrong number or inconsistent. \n\t Number of {0} files: {2} \n\t Number of {1} files: {3} \n\t Number of each should be {4}'
item.arguments = 'None'
item.comment = 'Means that number of A and B files were inconsistent'
langlist.add(item)

# =============================================================================
# 09-021-00005 
# =============================================================================
item = langlist.create('09-021-00005', kind='error-code')
item.value['ENG'] = 'Number of {0} and {1} files incorrect. Total number must be {2}'
item.arguments = 'None'
item.comment = 'Means that number of files was not valid'
langlist.add(item)

# =============================================================================
# 09-021-00006 
# =============================================================================
item = langlist.create('09-021-00006', kind='error-code')
item.value['ENG'] = 'Polarimetry method invalid (must be a python string)'
item.arguments = 'None'
item.comment = 'Means that polar method was not a valid python string'
langlist.add(item)

# =============================================================================
# 09-021-00007 
# =============================================================================
item = langlist.create('09-021-00007', kind='error-code')
item.value['ENG'] = 'Polarimetry method invalid (must be \'difference\' or \'ratio\')'
item.arguments = 'None'
item.comment = 'Means that polar method was not valid'
langlist.add(item)

# =============================================================================
# 09-021-00008 
# =============================================================================
item = langlist.create('09-021-00008', kind='error-code')
item.value['ENG'] = 'Number of exposures (={0}) is not sufficient for polarimetry calcaultions. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that the number of polar files was not valid'
langlist.add(item)

# =============================================================================
# 09-021-00009 
# =============================================================================
item = langlist.create('09-021-00009', kind='error-code')
item.value['ENG'] = 'Cannot load LSD spectral mask from file {0} \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that the temperature could not be obtained from mask file'
langlist.add(item)

# =============================================================================
# 09-021-00010 
# =============================================================================
item = langlist.create('09-021-00010', kind='error-code')
item.value['ENG'] = 'Exposure {0} must have keys ‘{1}’ and ‘{2}’ \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that exposure could not be set'
langlist.add(item)

# =============================================================================
# 09-021-00011 
# =============================================================================
item = langlist.create('09-021-00011', kind='error-code')
item.value['ENG'] = 'Exposure {0} has not been set correctly'
item.arguments = 'None'
item.comment = 'print that exposure N has been set correctly'
langlist.add(item)

# =============================================================================
# 09-021-00012 
# =============================================================================
item = langlist.create('09-021-00012', kind='error-code')
item.value['ENG'] = 'Identified more than one stokes parameters in input data'
item.arguments = 'None'
item.comment = 'prints that we identified more than one stokes parameter in input data'
langlist.add(item)

# =============================================================================
# 09-021-00013 
# =============================================================================
item = langlist.create('09-021-00013', kind='error-code')
item.value['ENG'] = '\n\tFile: {0}\tExp: {1}\tStokes: {2}'
item.arguments = 'None'
item.comment = 'prints the exposure parameters when we identify more then one stokes parameter'
langlist.add(item)

# =============================================================================
# 09-021-00014 
# =============================================================================
item = langlist.create('09-021-00014', kind='error-code')
item.value['ENG'] = 'Object name from header ({0}) not consistent between files'
item.arguments = 'None'
item.comment = 'prints that object name is not consistent between polar files'
langlist.add(item)

# =============================================================================
# 09-021-00015 
# =============================================================================
item = langlist.create('09-021-00015', kind='error-code')
item.value['ENG'] = '\n\t File: {0}\t{1} = {2}'
item.arguments = 'None'
item.comment = 'prints the exposure file + object name for all files when object name is inconsistent'
langlist.add(item)

# =============================================================================
# 09-021-00016 
# =============================================================================
item = langlist.create('09-021-00016', kind='error-code')
item.value['ENG'] = 'Method: ‘{0}’ not valid for polarimetry calculation'
item.arguments = 'None'
item.comment = 'prints that method is not valid for polarimetry calculation'
langlist.add(item)

# =============================================================================
# 09-021-00017 
# =============================================================================
item = langlist.create('09-021-00017', kind='error-code')
item.value['ENG'] = 'Stokes I continuum detection algorithm invalid\n\t Must be \"MOVING_MEDIAN\" or \"IRAF\"\n\tCurrent: {0}\n\tFunction={1}'
item.arguments = 'None'
item.comment = 'prints that stokes I continuum detection algoirthm invalid'
langlist.add(item)

# =============================================================================
# 09-021-00018 
# =============================================================================
item = langlist.create('09-021-00018', kind='error-code')
item.value['ENG'] = 'Can not recognize selected continuum mode: {0} \n\t Function={1}'
item.arguments = 'None'
item.comment = 'prints that we cannot recognize continnum mode'
langlist.add(item)

# =============================================================================
# 09-021-00019 
# =============================================================================
item = langlist.create('09-021-00019', kind='error-code')
item.value['ENG'] = 'Continuum function ‘{0}’ not valid for {1}'
item.arguments = 'None'
item.comment = 'prints that fit continuum function is not valid'
langlist.add(item)

# =============================================================================
# 09-021-00020 
# =============================================================================
item = langlist.create('09-021-00020', kind='error-code')
item.value['ENG'] = 'Cannot recognize selected mode: ‘{0}’ \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'prints that we cannot recognize polar mode'
langlist.add(item)

# =============================================================================
# 09-100-00001 
# =============================================================================
item = langlist.create('09-100-00001', kind='error-code')
item.value['ENG'] = 'OSX Error: Matplotlib MacOSX backend not supported by the DRS and could not change to another backend'
item.arguments = 'None'
item.comment = 'Means that backend is still mac osx which is unsupported by the drs'
langlist.add(item)

# =============================================================================
# 09-503-00001 
# =============================================================================
item = langlist.create('09-503-00001', kind='error-code')
item.value['ENG'] = 'Must define run path (DRS_DATA_RUN)'
item.arguments = 'None'
item.comment = 'Means that DRS_DAT_RUN was not defined'
langlist.add(item)

# =============================================================================
# 09-503-00002 
# =============================================================================
item = langlist.create('09-503-00002', kind='error-code')
item.value['ENG'] = 'Cannot find run file {0}'
item.arguments = 'None'
item.comment = 'Means we cannot find the run file'
langlist.add(item)

# =============================================================================
# 09-503-00003 
# =============================================================================
item = langlist.create('09-503-00003', kind='error-code')
item.value['ENG'] = 'Cannot open run file {0} \n\t Error {1}: {2} \n\t {3}'
item.arguments = 'None'
item.comment = 'Means we cannot open run file'
langlist.add(item)

# =============================================================================
# 09-503-00004 
# =============================================================================
item = langlist.create('09-503-00004', kind='error-code')
item.value['ENG'] = 'Problem reading run file key {0} = {1} \n\t Key must be {2}#### = command where #### is an integer. \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means we cannot read run file key'
langlist.add(item)

# =============================================================================
# 09-503-00005 
# =============================================================================
item = langlist.create('09-503-00005', kind='error-code')
item.value['ENG'] = 'Recipe {0} has invalid value for \'outputdir\'=\'{1}\'. Must be \'raw\', \'tmp\' or \'red\'. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means we could not use recipe.outputdir (must be raw tmp or red)'
langlist.add(item)

# =============================================================================
# 09-503-00006 
# =============================================================================
item = langlist.create('09-503-00006', kind='error-code')
item.value['ENG'] = 'Cannot construct valid outpath for recipe {0} \n\t Run string = {1} \n\t path = {2} \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that the constructed outpath for finding a file was incorrect'
langlist.add(item)

# =============================================================================
# 09-503-00007 
# =============================================================================
item = langlist.create('09-503-00007', kind='error-code')
item.value['ENG'] = 'Recipe {0} has invalid value for \'inputdir\'=\'{1}\'. Must be \'raw\', \'tmp\' or \'red\'. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means we could not user recipe.inputdir (must be raw tmp or red)'
langlist.add(item)

# =============================================================================
# 09-503-00008 
# =============================================================================
item = langlist.create('09-503-00008', kind='error-code')
item.value['ENG'] = 'Cannot construct valid inpath for recipe {0} \n\t Run string = {1} \n\t path = {2} \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Means that the constructed inpath for finding a file was incorrect'
langlist.add(item)

# =============================================================================
# 09-503-00009 
# =============================================================================
item = langlist.create('09-503-00009', kind='error-code')
item.value['ENG'] = 'For file defintion {0} (recipe={1}) \'outfunc\' is unset. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that outfunc is not defined for recipe/file'
langlist.add(item)

# =============================================================================
# 09-503-00010 
# =============================================================================
item = langlist.create('09-503-00010', kind='error-code')
item.value['ENG'] = 'Trigger mode activate. Must define a night name.'
item.arguments = 'None'
item.comment = 'Means that night name is not defined but trigger mode is activated'
langlist.add(item)

# =============================================================================
# 09-504-00001 
# =============================================================================
item = langlist.create('09-504-00001', kind='error-code')
item.value['ENG'] = 'Night name = {0} was not found in directory {1}'
item.arguments = 'None'
item.comment = 'Means that night name was not valid for path'
langlist.add(item)

# =============================================================================
# 09-505-00001 
# =============================================================================
item = langlist.create('09-505-00001', kind='error-code')
item.value['ENG'] = 'Database kind inputted was incorrect. \n\t Database kind = {0}'
item.arguments = 'None'
item.comment = 'Means that db type given was invalid'
langlist.add(item)

# =============================================================================
# 09-506-00001 
# =============================================================================
item = langlist.create('09-506-00001', kind='error-code')
item.value['ENG'] = 'Argument Error: --exportdb must be {0}'
item.arguments = 'None'
item.comment = 'Means that export db was not correct'
langlist.add(item)

# =============================================================================
# 09-506-00002 
# =============================================================================
item = langlist.create('09-506-00002', kind='error-code')
item.value['ENG'] = 'Database Error: Cannot load \"{0}\" database'
item.arguments = 'None'
item.comment = 'Means that we cannot load database for some reason'
langlist.add(item)

# =============================================================================
# 09-506-00003 
# =============================================================================
item = langlist.create('09-506-00003', kind='error-code')
item.value['ENG'] = 'Argument Error: --importdb must be {0}'
item.arguments = 'None'
item.comment = 'Means that import db was not correct'
langlist.add(item)

# =============================================================================
# 09-506-00004 
# =============================================================================
item = langlist.create('09-506-00004', kind='error-code')
item.value['ENG'] = 'Argument Error: Join mode = \'{0}\'. Must be either \'append\' or \'replace\''
item.arguments = 'None'
item.comment = 'Means that join mode was invalid'
langlist.add(item)

# =============================================================================
# 09-507-00001 
# =============================================================================
item = langlist.create('09-507-00001', kind='error-code')
item.value['ENG'] = 'Argument Error: --csv file is required'
item.arguments = 'None'
item.comment = 'prints that --csv file is required'
langlist.add(item)

# =============================================================================
# 09-508-00001 
# =============================================================================
item = langlist.create('09-508-00001', kind='error-code')
item.value['ENG'] = 'No observation directories found.'
item.arguments = 'None'
item.comment = 'prints that we found no observation directories'
langlist.add(item)

# =============================================================================
# 09-508-00002 
# =============================================================================
item = langlist.create('09-508-00002', kind='error-code')
item.value['ENG'] = 'Time ‘{0}’=’{1}’ not understood. \n\t {2}: {3}'
item.arguments = 'None'
item.comment = 'prints that input time was not understood'
langlist.add(item)

# =============================================================================
# 10-000-00000 
# =============================================================================
item = langlist.create('10-000-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Warning Messages'
langlist.add(item)

# =============================================================================
# 10-000-00001 
# =============================================================================
item = langlist.create('10-000-00001', kind='warning_6-code')
item.value['ENG'] = '\tSkipping group'
item.arguments = 'None'
item.comment = 'Warns that we are skipping group due to event handling'
langlist.add(item)

# =============================================================================
# 10-001-00000 
# =============================================================================
item = langlist.create('10-001-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'IO Warning Messages'
langlist.add(item)

# =============================================================================
# 10-001-00001 
# =============================================================================
item = langlist.create('10-001-00001', kind='warning_4-code')
item.value['ENG'] = 'Partially recovered fits file \n\t Problem with extension=\'{0}\' \n\t filename=\'{1}\''
item.arguments = 'None'
item.comment = 'States that there was a problem with opening the fits file (but all extensions were opened up to extension X)'
langlist.add(item)

# =============================================================================
# 10-001-00002 
# =============================================================================
item = langlist.create('10-001-00002', kind='warning-code')
item.value['ENG'] = 'File \'{0}\' is locked. Waiting... (Ctrl+C to unlock)'
item.arguments = 'None'
item.comment = 'States that there is a lock file present and we are waiting to continue'
langlist.add(item)

# =============================================================================
# 10-001-00003 
# =============================================================================
item = langlist.create('10-001-00003', kind='warning-code')
item.value['ENG'] = 'Waiting to open lock file {0}. (Ctrl+C to unlock)'
item.arguments = 'None'
item.comment = 'States that we are waiting to open the lock file (as the lock file is already being opened)'
langlist.add(item)

# =============================================================================
# 10-001-00004 
# =============================================================================
item = langlist.create('10-001-00004', kind='warning-code')
item.value['ENG'] = 'Waiting to close lock file {0}. (Ctrl+C to unlock)'
item.arguments = 'None'
item.comment = 'States that we are waiting to close (delete) the lock file (as the lock file is already being closed)'
langlist.add(item)

# =============================================================================
# 10-001-00005 
# =============================================================================
item = langlist.create('10-001-00005', kind='warning_2-code')
item.value['ENG'] = 'Problem with one of the fits file extensions: \n\t Error {0}: {1} \n\t Attempting to open available extensions manually.'
item.arguments = 'None'
item.comment = 'Means there was a problem reading one of the extensions'
langlist.add(item)

# =============================================================================
# 10-001-00006 
# =============================================================================
item = langlist.create('10-001-00006', kind='warning_2-code')
item.value['ENG'] = 'Error was found type{0} = {1} \n\t Corrected by manually reading extension {2} as a table \n\t Saving over file \'{3}\' \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we corrected the error found by reading just the first (or second) extension and have replaced the old file'
langlist.add(item)

# =============================================================================
# 10-001-00007 
# =============================================================================
item = langlist.create('10-001-00007', kind='warning-code')
item.value['ENG'] = '{0} database: Unable to chmod on file {1} \n\t Error {2}: {3} \n\t function = {4}'
item.arguments = 'None'
item.comment = 'Means that we were unable to do chmod Oo0644 on file'
langlist.add(item)

# =============================================================================
# 10-001-00008 
# =============================================================================
item = langlist.create('10-001-00008', kind='warning-code')
item.value['ENG'] = 'Cannot fix header, header key \'{0}\' missing. \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'Means that key X (to id file) was not found in header'
langlist.add(item)

# =============================================================================
# 10-001-00009 
# =============================================================================
item = langlist.create('10-001-00009', kind='warning_4-code')
item.value['ENG'] = 'FP file does not pass 2D quality control. \n\t Filename = {0}'
item.arguments = 'None'
item.comment = 'Means that a file did not pass the 2D FP quality checks'
langlist.add(item)

# =============================================================================
# 10-001-00010 
# =============================================================================
item = langlist.create('10-001-00010', kind='warning_4-code')
item.value['ENG'] = 'HDU[{0}]=\'{1}\' has incorrect data type (Must be \'table\' or \'image\') - skipping extension \n\t data type = \'{2}\''
item.arguments = 'None'
item.comment = 'Means that a header extension was not table/image datatype'
langlist.add(item)

# =============================================================================
# 10-001-00011 
# =============================================================================
item = langlist.create('10-001-00011', kind='warning_2-code')
item.value['ENG'] = '{0} locked. Trying again in 5s.'
item.arguments = 'None'
item.comment = 'Means that file was locked - we are trying again'
langlist.add(item)

# =============================================================================
# 10-001-00012 
# =============================================================================
item = langlist.create('10-001-00012', kind='warning_2-code')
item.value['ENG'] = 'User file: {0} not found. \n\t Using calibration database to find suitable {1} file.'
item.arguments = 'None'
item.comment = 'Means that user defined calibration file was not found so we are using the calibration database to find a suitable calibration file'
langlist.add(item)

# =============================================================================
# 10-001-00013 
# =============================================================================
item = langlist.create('10-001-00013', kind='warning_3-code')
item.value['ENG'] = '\tSome input {0} failed QC test – removing: '
item.arguments = 'None'
item.comment = 'prints that we are removing some input files due to QC failure'
langlist.add(item)

# =============================================================================
# 10-001-00014 
# =============================================================================
item = langlist.create('10-001-00014', kind='warning_2-code')
item.value['ENG'] = 'Lock cannot remove directory {0}. \n\t Error {1}: {2} \n\t function = {3}'
item.arguments = 'None'
item.comment = 'prints that lock cannot remove a directory'
langlist.add(item)

# =============================================================================
# 10-002-00000 
# =============================================================================
item = langlist.create('10-002-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Constant/Config/Database Warning Messages'
langlist.add(item)

# =============================================================================
# 10-002-00001 
# =============================================================================
item = langlist.create('10-002-00001', kind='warning-code')
item.value['ENG'] = 'User config defined in {0} but instrument “{1}” directory not found. \n\t Directory = {2} \n\t Using default configuration files.'
item.arguments = 'None'
item.comment = 'Means that config file was defined but directory was not found'
langlist.add(item)

# =============================================================================
# 10-002-00002 
# =============================================================================
item = langlist.create('10-002-00002', kind='warning-code')
item.value['ENG'] = 'Key \'{0}\' duplicated in \'{1}\' \n\t Other configs: {2} \n\t Config File = {3}'
item.arguments = 'None'
item.comment = 'Means that key was duplicated in another config file'
langlist.add(item)

# =============================================================================
# 10-002-00003 
# =============================================================================
item = langlist.create('10-002-00003', kind='warning_2-code')
item.value['ENG'] = 'Database {0}: Header key \"{1}\"=\"{2}\" must of of data type \"{3}\" \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that header key value was not the correct data type'
langlist.add(item)

# =============================================================================
# 10-002-00004 
# =============================================================================
item = langlist.create('10-002-00004', kind='warning-code')
item.value['ENG'] = 'Database {0}: Header key \"{1}\" invalid for database. \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that header key was not valid for database (and will be skipped)'
langlist.add(item)

# =============================================================================
# 10-002-00005 
# =============================================================================
item = langlist.create('10-002-00005', kind='warning-code')
item.value['ENG'] = 'Index database has wrong number of columns \n\t Num columns = {0}   num values = {1}'
item.arguments = 'None'
item.comment = 'Means index database has wrong number of columns'
langlist.add(item)

# =============================================================================
# 10-002-00006 
# =============================================================================
item = langlist.create('10-002-00006', kind='warning-code')
item.value['ENG'] = 'Reset database? [Y]es or [N]o?\t'
item.arguments = 'None'
item.comment = 'Reset database user prompt for wrong number of columns'
langlist.add(item)

# =============================================================================
# 10-002-00007 
# =============================================================================
item = langlist.create('10-002-00007', kind='warning-code')
item.value['ENG'] = '\nWarning: Bad profile name changed from \'{0}\' to \'{1}\''
item.arguments = 'None'
item.comment = 'Means that bad profile name was given and it has been changed'
langlist.add(item)

# =============================================================================
# 10-002-00008 
# =============================================================================
item = langlist.create('10-002-00008', kind='warning_2-code')
item.value['ENG'] = '\t\tFile no longer on disk – removing from file index database: {0}'
item.arguments = 'None'
item.comment = 'Warns that a file is no longer on disk and we are removing from the file index database'
langlist.add(item)

# =============================================================================
# 10-002-00009 
# =============================================================================
item = langlist.create('10-002-00009', kind='warning_6-code')
item.value['ENG'] = 'Skipping file {0}\n\tError{1}: {2}'
item.arguments = 'None'
item.comment = 'warns that we are skipping a file due to an error'
langlist.add(item)

# =============================================================================
# 10-003-00000 
# =============================================================================
item = langlist.create('10-003-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Class/Function Warning Messages'
langlist.add(item)

# =============================================================================
# 10-003-00001 
# =============================================================================
item = langlist.create('10-003-00001', kind='warning_3-code')
item.value['ENG'] = 'File was rejected from combining process: {0}'
item.arguments = 'None'
item.comment = 'Means that a file was rejected from the combining process'
langlist.add(item)

# =============================================================================
# 10-003-00002 
# =============================================================================
item = langlist.create('10-003-00002', kind='warning_4-code')
item.value['ENG'] = '{0} file(s) were rejected from combining process'
item.arguments = 'None'
item.comment = 'Means that some files were rejected from the combining process'
langlist.add(item)

# =============================================================================
# 10-004-00000 
# =============================================================================
item = langlist.create('10-004-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Index Warning Messages'
langlist.add(item)

# =============================================================================
# 10-004-00001 
# =============================================================================
item = langlist.create('10-004-00001', kind='warning-code')
item.value['ENG'] = 'Index file does not have column=\'{0}\' \n\t Please run \'{1}\'.'
item.arguments = 'None'
item.comment = 'Warning the user when column isn\'t in index file'
langlist.add(item)

# =============================================================================
# 10-004-00002 
# =============================================================================
item = langlist.create('10-004-00002', kind='warning-code')
item.value['ENG'] = 'No index file for \'{0}\'. Please run \'{1}\''
item.arguments = 'None'
item.comment = 'Warning that there was no index file found'
langlist.add(item)

# =============================================================================
# 10-005-00000 
# =============================================================================
item = langlist.create('10-005-00000', kind='warning-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Log Warning Message'
langlist.add(item)

# =============================================================================
# 10-005-00001 
# =============================================================================
item = langlist.create('10-005-00001', kind='warning_1-code')
item.value['ENG'] = 'Python Warning Line: {0} {1} warning reads: \'{2}\''
item.arguments = 'None'
item.comment = 'Warning from python (passed via function \'warninglogger\')'
langlist.add(item)

# =============================================================================
# 10-005-00002 
# =============================================================================
item = langlist.create('10-005-00002', kind='warning-code')
item.value['ENG'] = 'Cannot write to log file. Key = \'{0}\' missing from config'
item.arguments = 'None'
item.comment = 'Means that the log directory \'key\' was not in parameter dict (i.e. not in config file)'
langlist.add(item)

# =============================================================================
# 10-005-00003 
# =============================================================================
item = langlist.create('10-005-00003', kind='warning-code')
item.value['ENG'] = 'Cannot write to log file \n\t Directory = \'{0}\' does not exist \n\t \'{0}\' = \'{1}\''
item.arguments = 'None'
item.comment = 'Means the \'dir_data_msg\' directory does not exist'
langlist.add(item)

# =============================================================================
# 10-005-00004 
# =============================================================================
item = langlist.create('10-005-00004', kind='warning-code')
item.value['ENG'] = 'Breakpoint reached (breakfunc={0})'
item.arguments = 'None'
item.comment = 'Means that a break point (via function name) was reached'
langlist.add(item)

# =============================================================================
# 10-005-00005 
# =============================================================================
item = langlist.create('10-005-00005', kind='warning-code')
item.value['ENG'] = 'Undefined PID not recommended (params is None)'
item.arguments = 'None'
item.comment = 'Means that PID is undefined as params is None'
langlist.add(item)

# =============================================================================
# 10-005-00006 
# =============================================================================
item = langlist.create('10-005-00006', kind='warning-code')
item.value['ENG'] = 'Undefined PID not recommended (PID is missing)'
item.arguments = 'None'
item.comment = 'Means that PID is undefined as PID is missing'
langlist.add(item)

# =============================================================================
# 10-010-00001 
# =============================================================================
item = langlist.create('10-010-00001', kind='warning_8-code')
item.value['ENG'] = 'Error {0}: {1}'
item.arguments = 'None'
item.comment = 'resolve pre-processing error'
langlist.add(item)

# =============================================================================
# 10-010-00002 
# =============================================================================
item = langlist.create('10-010-00002', kind='warning_8-code')
item.value['ENG'] = 'Error {0}: {1}'
item.arguments = 'None'
item.comment = 'resolve pre-processing error'
langlist.add(item)

# =============================================================================
# 10-010-00003 
# =============================================================================
item = langlist.create('10-010-00003', kind='warning_8-code')
item.value['ENG'] = 'Error {0}: {1}'
item.arguments = 'None'
item.comment = 'resolve pre-processing error'
langlist.add(item)

# =============================================================================
# 10-010-00004 
# =============================================================================
item = langlist.create('10-010-00004', kind='warning_8-code')
item.value['ENG'] = 'Error {0}: {1}'
item.arguments = 'None'
item.comment = 'resolve pre-processing error'
langlist.add(item)

# =============================================================================
# 10-010-00005 
# =============================================================================
item = langlist.create('10-010-00005', kind='warning_7-code')
item.value['ENG'] = 'Object {0} is not in the astrometric database. Using header values for astrometric parameters'
item.arguments = 'None'
item.comment = 'Means object was not in the astrometric database'
langlist.add(item)

# =============================================================================
# 10-010-00006 
# =============================================================================
item = langlist.create('10-010-00006', kind='warning_8-code')
item.value['ENG'] = 'Full image is NaN -- cannot fix'
item.arguments = 'None'
item.comment = 'Means image is all nans and we cannot fix it (will fail QC)'
langlist.add(item)

# =============================================================================
# 10-010-00007 
# =============================================================================
item = langlist.create('10-010-00007', kind='warning_3-code')
item.value['ENG'] = 'Cannot read reject list: {0}. Skipping rejection. \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Means we couldn’t get the reject table – we will skip rejection'
langlist.add(item)

# =============================================================================
# 10-010-00008 
# =============================================================================
item = langlist.create('10-010-00008', kind='warning_3-code')
item.value['ENG'] = 'Cannot use astrometric database entry for object=’{0}’. \n\t {1}: {2}'
item.arguments = 'None'
item.comment = 'Means we cannot use astrometric parameters from database (for some reason)'
langlist.add(item)

# =============================================================================
# 10-012-00001 
# =============================================================================
item = langlist.create('10-012-00001', kind='error-code')
item.value['ENG'] = 'Inconsistent number of input flat / dark files (No. flat={0}, No. dark={1}) and combine set to False.'
item.arguments = 'None'
item.comment = 'Tells the user that there were a different amount of dark to flat files in badpixs (only true when combine set to False)'
langlist.add(item)

# =============================================================================
# 10-014-00001 
# =============================================================================
item = langlist.create('10-014-00001', kind='warning_6-code')
item.value['ENG'] = 'Quality control failed for group {0} \n\t Image quality too poor (sigma clip failed)'
item.arguments = 'None'
item.comment = 'Means that shape reference transforms iteration failed the quality control'
langlist.add(item)

# =============================================================================
# 10-014-00002 
# =============================================================================
item = langlist.create('10-014-00002', kind='warning_6-code')
item.value['ENG'] = 'Quality control failed for group {0} \n\t XRES = {0} YRES = {1} (limit = {2})'
item.arguments = 'None'
item.comment = 'Means that shape reference xres or yres iteration failed the quality control'
langlist.add(item)

# =============================================================================
# 10-014-00003 
# =============================================================================
item = langlist.create('10-014-00003', kind='warning_6-code')
item.value['ENG'] = 'QUALITY CONTROL FAILED: The std of the dxmap for order {0} y—pixel {1} is too large. \n\t std = {2:.5f} (limit = {3:.5f}) \n\t Cannot continue. Exiting.'
item.arguments = 'None'
item.comment = 'Means that QC failed (during creation of dxmap) and file will not be written'
langlist.add(item)

# =============================================================================
# 10-015-00001 
# =============================================================================
item = langlist.create('10-015-00001', kind='warning_2-code')
item.value['ENG'] = 'Sinc curve fit failed. Trying again. Tries = {0}'
item.arguments = 'None'
item.comment = 'Means curve fit failed - we will try again'
langlist.add(item)

# =============================================================================
# 10-016-00001 
# =============================================================================
item = langlist.create('10-016-00001', kind='warning_4-code')
item.value['ENG'] = 'Skipping order {0} (not in valid orders) values will be set to NaN'
item.arguments = 'None'
item.comment = 'Means that order was skipped at user request in extraction process'
langlist.add(item)

# =============================================================================
# 10-016-00002 
# =============================================================================
item = langlist.create('10-016-00002', kind='warning_4-code')
item.value['ENG'] = 'SATURATION LEVEL REACHED on Fiber {0} order={1} \n\t flux ({2}) > limit ({3})'
item.arguments = 'None'
item.comment = 'Means that the saturation level was exceeded'
langlist.add(item)

# =============================================================================
# 10-016-00003 
# =============================================================================
item = langlist.create('10-016-00003', kind='warning_8_-code')
item.value['ENG'] = 'Could not import barycorrpy. \n\t Using BERV estimate (+/- {0} m/s) instead. \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Means that we could not import barycorrpy (and using estimate instead)'
langlist.add(item)

# =============================================================================
# 10-016-00004 
# =============================================================================
item = langlist.create('10-016-00004', kind='warning_8-code')
item.value['ENG'] = 'Could not calculate BERV using barycorrpy. \n\t Error {0}: {1} \n\t Using BERV estimate (+/- {2} m/s) instead. \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not calculate berv using barycorrpy (and using estimate instead)'
langlist.add(item)

# =============================================================================
# 10-016-00005 
# =============================================================================
item = langlist.create('10-016-00005', kind='warning_8-code')
item.value['ENG'] = 'Calculating BERV using estimate (+/- {0} m/s)'
item.arguments = 'None'
item.comment = 'Print warning that we are calculating BERV using estimate'
langlist.add(item)

# =============================================================================
# 10-016-00006 
# =============================================================================
item = langlist.create('10-016-00006', kind='warning-code')
item.value['ENG'] = 'Gaia Crossmatch error: Could not use ra=\'{0}\' and dec=\'{1}\' to crossmatch (radius={2}). \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Prints a warning that we could not use ra and dec to crossmatch with obj_list lookup table'
langlist.add(item)

# =============================================================================
# 10-016-00007 
# =============================================================================
item = langlist.create('10-016-00007', kind='warning_8-code')
item.value['ENG'] = 'Gaia crossmatch error: Cannot create query \n\t Must provide either a \'gaiaid\' or a \'objname\' or an \'ra and dec\' or a \'query\' \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that the query was not defined (i.e. gaiaid/objname/ra/dec/query were unset)'
langlist.add(item)

# =============================================================================
# 10-016-00008 
# =============================================================================
item = langlist.create('10-016-00008', kind='warning_8-code')
item.value['ENG'] = 'Gaia crossmatch error: Cannot use astroquery TapPlus. \n\t URL={0} \n\nquery = {1}\n\n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Means that we could not use astroquery TapPlus to query gaia'
langlist.add(item)

# =============================================================================
# 10-016-00009 
# =============================================================================
item = langlist.create('10-016-00009', kind='warning_8-code')
item.value['ENG'] = 'Gaia crossmatch error: Must has astroquery installed to crossmatch with gaia. \n\t Error {0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that we cannot use astroquery (not found) to cross match to gaia'
langlist.add(item)

# =============================================================================
# 10-016-00010 
# =============================================================================
item = langlist.create('10-016-00010', kind='warning_8-code')
item.value['ENG'] = 'Gaia Crossmatch error: Could not use ra=\'{0}\' and dec=\'{1}\' to query gaia - via astroquery TapPlus (radius={2}). \n\t Error {3}: {4} \n\t Function = {5}'
item.arguments = 'None'
item.comment = 'Prints a warning that we could not use ra and dec to crossmatch with gaia (via astroquery TapPlus)'
langlist.add(item)

# =============================================================================
# 10-016-00011 
# =============================================================================
item = langlist.create('10-016-00011', kind='warning_8-code')
item.value['ENG'] = 'Gaia Crossmatch error: No entries found after crossmatch with gaia. \n\t Function = {0}'
item.arguments = 'None'
item.comment = 'Means that no rows were found after querying gaia (via astroquery TapPlus)'
langlist.add(item)

# =============================================================================
# 10-016-00012 
# =============================================================================
item = langlist.create('10-016-00012', kind='warning_2-code')
item.value['ENG'] = 'Skipping extraction DPRTYPE = {0} (Required = {1}) \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means that file will be skipped due to incorrect DPRTYPE'
langlist.add(item)

# =============================================================================
# 10-016-00013 
# =============================================================================
item = langlist.create('10-016-00013', kind='warning_2-code')
item.value['ENG'] = 'Skipping extraction OBJNAME = {0} (Required = {1}) \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means that file will be skipped due to incorrect OBJNAME'
langlist.add(item)

# =============================================================================
# 10-016-00014 
# =============================================================================
item = langlist.create('10-016-00014', kind='warning-code')
item.value['ENG'] = 'No barycorrpy berv values found, using pyasl estimate. \n\t Only good to  +/- {0:.3f} m/s \n\t For precise RV must have barycorrpy working (see extraction log)'
item.arguments = 'None'
item.comment = 'Means that no berv values found so using estimated values'
langlist.add(item)

# =============================================================================
# 10-016-00015 
# =============================================================================
item = langlist.create('10-016-00015', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query: No results found for object: {0}'
item.arguments = 'None'
item.comment = 'means in simbad query no results were found for object'
langlist.add(item)

# =============================================================================
# 10-016-00016 
# =============================================================================
item = langlist.create('10-016-00016', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query: \'RA\' not found in simbad results for object: {0}. \n\t Cols found: {1}'
item.arguments = 'None'
item.comment = 'means that \'RA\' was not found in simbad query'
langlist.add(item)

# =============================================================================
# 10-016-00017 
# =============================================================================
item = langlist.create('10-016-00017', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query: \'DEC\' not found in simbad results for object: {0}. \n\t Cols found: {1}'
item.arguments = 'None'
item.comment = 'means that \'DEC\' was not found in simbad query'
langlist.add(item)

# =============================================================================
# 10-016-00018 
# =============================================================================
item = langlist.create('10-016-00018', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query: \'RA\' units not understood for object: {0}. Found units=\'{1}\''
item.arguments = 'None'
item.comment = 'means that \'RA\' units were not understood in simbad query'
langlist.add(item)

# =============================================================================
# 10-016-00019 
# =============================================================================
item = langlist.create('10-016-00019', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query: \'DEC\' units not understood for object: {0}. Found units=\'{1}\''
item.arguments = 'None'
item.comment = 'means that \'DEC\' units were not understood in simbad query'
langlist.add(item)

# =============================================================================
# 10-016-00020 
# =============================================================================
item = langlist.create('10-016-00020', kind='warning_8-code')
item.value['ENG'] = 'Simbad Query error for object \'{0}\'. \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'means there was an error in the simbad query'
langlist.add(item)

# =============================================================================
# 10-016-00021 
# =============================================================================
item = langlist.create('10-016-00021', kind='warning_4-code')
item.value['ENG'] = 'Wrong DPRTYPE for leak correction. \n\t DPRTYPE: \'{0}\' \n\t Allowed DPRTYPEs: {1} \n\t Input file name: {2}'
item.arguments = 'None'
item.comment = 'means that infile dprtype was wrong for leak correction'
langlist.add(item)

# =============================================================================
# 10-016-00022 
# =============================================================================
item = langlist.create('10-016-00022', kind='warning_4-code')
item.value['ENG'] = 'Wrong fiber for leak correction. \n\t fiber: \'{0}\' \n\t Allowed fibers: {1} \n\t Input file name: {2}'
item.arguments = 'None'
item.comment = 'means that infile fiber was wrong for leak correction (must be science fiber)'
langlist.add(item)

# =============================================================================
# 10-016-00023 
# =============================================================================
item = langlist.create('10-016-00023', kind='warning_2-code')
item.value['ENG'] = 'Leakage already corrected for file: {0}'
item.arguments = 'None'
item.comment = 'means that leak correction header key was found and was true there for correction was already done'
langlist.add(item)

# =============================================================================
# 10-016-00024 
# =============================================================================
item = langlist.create('10-016-00024', kind='warning_4-code')
item.value['ENG'] = 'Spurious reference FP found (Order = {0}). \n\t Ratio={1:.3e} Approx={2:.3e} Fraction={3:.3f} (Fraction must agree within {4} to {5})'
item.arguments = 'None'
item.comment = 'means that ratio/approx ratio was out of bounds'
langlist.add(item)

# =============================================================================
# 10-016-00025 
# =============================================================================
item = langlist.create('10-016-00025', kind='warning_4-code')
item.value['ENG'] = 'No dark fp files found for night={0}. Skipping leak reference.'
item.arguments = 'None'
item.comment = 'means that no dark fp files were found for this reference night'
langlist.add(item)

# =============================================================================
# 10-016-00026 
# =============================================================================
item = langlist.create('10-016-00026', kind='warning_2-code')
item.value['ENG'] = 'Straightened order profile found but could not be read. Recreating. \n\tFile: {0} \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that order profile existed by could not be read (parallelisation issue?)'
langlist.add(item)

# =============================================================================
# 10-017-00001 
# =============================================================================
item = langlist.create('10-017-00001', kind='warning-code')
item.value['ENG'] = 'Could not find wave key \'{0}\' in calibDB using wave reference.'
item.arguments = 'None'
item.comment = 'Means that could not find a wave key so using wave reference'
langlist.add(item)

# =============================================================================
# 10-017-00002 
# =============================================================================
item = langlist.create('10-017-00002', kind='warning-code')
item.value['ENG'] = 'Inconsistent number of input hc / fp files (No. hc={0}, No. fp={1}) and combine set to False.'
item.arguments = 'None'
item.comment = 'Tells the user that there were a different amount of hc to fp files in wave recipe (only true when combine set to False)'
langlist.add(item)

# =============================================================================
# 10-017-00003 
# =============================================================================
item = langlist.create('10-017-00003', kind='warning_2-code')
item.value['ENG'] = 'Inconsistent wave solution fit degree ({0}) expected {1} \n\t Re-mapping onto expected fit degree.'
item.arguments = 'None'
item.comment = 'Means that the wavelength solution fit degree was inconsistent with requirement'
langlist.add(item)

# =============================================================================
# 10-017-00004 
# =============================================================================
item = langlist.create('10-017-00004', kind='warning-code')
item.value['ENG'] = 'Pixel shift is not 0 (slope={0} intercept={1}) check that this is desired'
item.arguments = 'None'
item.comment = 'Means that pixel shift parameters are not zero'
langlist.add(item)

# =============================================================================
# 10-017-00005 
# =============================================================================
item = langlist.create('10-017-00005', kind='warning-code')
item.value['ENG'] = 'No value found for order {0}'
item.arguments = 'None'
item.comment = 'Means that no lines were found for this order'
langlist.add(item)

# =============================================================================
# 10-017-00006 
# =============================================================================
item = langlist.create('10-017-00006', kind='warning-code')
item.value['ENG'] = 'HC wave solution failed quality control. FP wave solution not processed'
item.arguments = 'None'
item.comment = 'Means that HC solution failed QC and FP was expected'
langlist.add(item)

# =============================================================================
# 10-017-00007 
# =============================================================================
item = langlist.create('10-017-00007', kind='warning-code')
item.value['ENG'] = 'No FP files given. FP wave solution not generated.'
item.arguments = 'None'
item.comment = 'Means that FP wave solution was not expected'
langlist.add(item)

# =============================================================================
# 10-017-00008 
# =============================================================================
item = langlist.create('10-017-00008', kind='warning-code')
item.value['ENG'] = 'No overlap for order {0}'
item.arguments = 'None'
item.comment = 'prints that there is no overlap for order'
langlist.add(item)

# =============================================================================
# 10-017-00009 
# =============================================================================
item = langlist.create('10-017-00009', kind='warning-code')
item.value['ENG'] = 'No overlap for order {0}, estimating gap size'
item.arguments = 'None'
item.comment = 'prints that there was no overlap for order so having to estimate gap size'
langlist.add(item)

# =============================================================================
# 10-017-00010 
# =============================================================================
item = langlist.create('10-017-00010', kind='warning-code')
item.value['ENG'] = 'Missing line estimate miss-match: {0} v {1} from {2:.5f} v {3:.5f}'
item.arguments = 'None'
item.comment = 'prints that there was a missing line estimate miss-match'
langlist.add(item)

# =============================================================================
# 10-017-00011 
# =============================================================================
item = langlist.create('10-017-00011', kind='warning-code')
item.value['ENG'] = 'Cavity length fit files missing. Cavity length fits will be created.'
item.arguments = 'None'
item.comment = 'prints that cavity length files do not exist so we have to create them'
langlist.add(item)

# =============================================================================
# 10-017-00012 
# =============================================================================
item = langlist.create('10-017-00012', kind='warning-code')
item.value['ENG'] = 'First order for multi-wave plot \'{0}\' is higher than final wavelength solution order \'{1}\'. Plotting of {2} skipped.'
item.arguments = 'None'
item.comment = 'means that the multi wave plot start order is larger than final order'
langlist.add(item)

# =============================================================================
# 10-017-00013 
# =============================================================================
item = langlist.create('10-017-00013', kind='warning_4-code')
item.value['ENG'] = 'Fit failed for order bin {0} spectral bin {1}  (Nvalid = {2}) \n\t Order {3} to {4}, pixel {5} to {6} \n\t Error {7}: {8}'
item.arguments = 'None'
item.comment = 'Means that the gen res curve fit failed for this bin'
langlist.add(item)

# =============================================================================
# 10-018-00001 
# =============================================================================
item = langlist.create('10-018-00001', kind='warning-code')
item.value['ENG'] = 'Skipping fiber {0} = {1} (Not of type ‘{2}’)'
item.arguments = 'None'
item.comment = 'prints that we are skipping fiber (as not in valid types)'
langlist.add(item)

# =============================================================================
# 10-019-00001 
# =============================================================================
item = langlist.create('10-019-00001', kind='warning_4-code')
item.value['ENG'] = 'DPRTYPE = ‘{0}’ is not valid for {1}. \n\t Allowed DPRTYPES are: {2} \n\t Skipping filename = {3}'
item.arguments = 'None'
item.comment = 'Means that dprtype was not valid'
langlist.add(item)

# =============================================================================
# 10-019-00002 
# =============================================================================
item = langlist.create('10-019-00002', kind='warning_2-code')
item.value['ENG'] = 'File {0} is blacklisted ({1} = ‘{2}’) \n\t Skipping file.'
item.arguments = 'None'
item.comment = 'Means that objname was in blacklist'
langlist.add(item)

# =============================================================================
# 10-019-00003 
# =============================================================================
item = langlist.create('10-019-00003', kind='warning-code')
item.value['ENG'] = 'Recovered water vapor optical depth invalid (value = {0:.2f}) \n\t Must be between {1:.2f} and {2:.2f}'
item.arguments = 'None'
item.comment = 'Means that recovered water vapor optical depth not between limits'
langlist.add(item)

# =============================================================================
# 10-019-00004 
# =============================================================================
item = langlist.create('10-019-00004', kind='warning-code')
item.value['ENG'] = 'Recovered optical depth invalid (value={0:.3f} \n\t Too different from airmass (airmass = {1:.3f})'
item.arguments = 'None'
item.comment = 'Means that recovered optical depth of others is too different from airmass'
langlist.add(item)

# =============================================================================
# 10-019-00005 
# =============================================================================
item = langlist.create('10-019-00005', kind='warning_2-code')
item.value['ENG'] = 'No files were found for object name = {0}, file type = {1}'
item.arguments = 'None'
item.comment = 'Means that no files were found for object name and file type'
langlist.add(item)

# =============================================================================
# 10-019-00006 
# =============================================================================
item = langlist.create('10-019-00006', kind='warning_4-code')
item.value['ENG'] = 'Skipping file {0} of {1}. SNR (order {2}) = {3} (Limit = {4})'
item.arguments = 'None'
item.comment = 'Means that template file was skipped due to poor snr'
langlist.add(item)

# =============================================================================
# 10-019-00007 
# =============================================================================
item = langlist.create('10-019-00007', kind='warning-code')
item.value['ENG'] = 'No good files found for object = {0}. Skipping.'
item.arguments = 'None'
item.comment = 'Means that no good files were found for template cube'
langlist.add(item)

# =============================================================================
# 10-019-00008 
# =============================================================================
item = langlist.create('10-019-00008', kind='warning-code')
item.value['ENG'] = 'Skipping pre-cleaning (user switch)'
item.arguments = 'None'
item.comment = 'Means that the user decided not to do pre-cleaning'
langlist.add(item)

# =============================================================================
# 10-019-00009 
# =============================================================================
item = langlist.create('10-019-00009', kind='warning_2-code')
item.value['ENG'] = 'Object=\'{0}\' is not a vliad telluric (hot) star.'
item.arguments = 'None'
item.comment = 'Means that object was not in telluric whitelist'
langlist.add(item)

# =============================================================================
# 10-019-00010 
# =============================================================================
item = langlist.create('10-019-00010', kind='warning_8-code')
item.value['ENG'] = 'Telluric pre-cleaning failed QC \n\t Required: {0} \n\t {1} = {2}'
item.arguments = 'None'
item.comment = 'Means that the telluric pre-cleaning failed (a quality control qc parameter failed)'
langlist.add(item)

# =============================================================================
# 10-019-00011 
# =============================================================================
item = langlist.create('10-019-00011', kind='warning-code')
item.value['ENG'] = 'Insufficient BERV coverage to build template. \n\t BERV coverage was: {0} km/s required > {1} km/s'
item.arguments = 'None'
item.comment = 'Means that template was not created as we didn\'t have sufficient berv coverage'
langlist.add(item)

# =============================================================================
# 10-019-00012 
# =============================================================================
item = langlist.create('10-019-00012', kind='warning_2-code')
item.value['ENG'] = 'Removing/Writing of abso npy file failed. Trying again. \n\t Function = {0} \n\t {1}: {2}'
item.arguments = 'None'
item.comment = 'warns that we could not remove abso npy file'
langlist.add(item)

# =============================================================================
# 10-020-00001 
# =============================================================================
item = langlist.create('10-020-00001', kind='warning-code')
item.value['ENG'] = 'All NaN slice found when fitting CCF (Order = {0}). Returning NaNs instead of fit.'
item.arguments = 'None'
item.comment = 'Means that an all NaN array was found when trying to fit the CCF'
langlist.add(item)

# =============================================================================
# 10-020-00002 
# =============================================================================
item = langlist.create('10-020-00002', kind='warning_2-code')
item.value['ENG'] = 'NaNs found in image. Replacing NaNs with values smoothed by kernel.'
item.arguments = 'None'
item.comment = 'Means that we found NaNs and need to replace the NaNs by something'
langlist.add(item)

# =============================================================================
# 10-020-00003 
# =============================================================================
item = langlist.create('10-020-00003', kind='warning_2-code')
item.value['ENG'] = 'Reference wave solution time did not match science wave solution time. Using science wave solution for reference fiber. \n\t Reference wave time = {0}   science wave time = {1} \n\t Reference wave file: {2} \n\t Science wave file: {3}'
item.arguments = 'None'
item.comment = 'Means that the reference wave solution did not match the science wave solution in time'
langlist.add(item)

# =============================================================================
# 10-020-00004 
# =============================================================================
item = langlist.create('10-020-00004', kind='warning_4-code')
item.value['ENG'] = 'Order {0} has no finite values. CCF set to NaNs.'
item.arguments = 'None'
item.comment = 'Means that whole order is full of NaNS so CCF will be NaN'
langlist.add(item)

# =============================================================================
# 10-020-00005 
# =============================================================================
item = langlist.create('10-020-00005', kind='warning_4-code')
item.value['ENG'] = 'Order {0} CCF generated a non-finite value. CCF set to NaNs.'
item.arguments = 'None'
item.comment = 'Means that the CCF had NaNs in'
langlist.add(item)

# =============================================================================
# 10-020-00006 
# =============================================================================
item = langlist.create('10-020-00006', kind='warning_4-code')
item.value['ENG'] = 'Order {0} CCF mask for this order has no lines. CCF set to NaNs. \n\t order wavelength: {1:.3f} to {2:.3f}'
item.arguments = 'None'
item.comment = 'Means that mask has no lines for this order'
langlist.add(item)

# =============================================================================
# 10-020-00007 
# =============================================================================
item = langlist.create('10-020-00007', kind='warning_4-code')
item.value['ENG'] = 'Order {0} CCF mask for this order only has lines in invalid blaze locations. CCF set to NaNs'
item.arguments = 'None'
item.comment = 'Means that mask is only in the blaze cut off, i.e. no valid lines'
langlist.add(item)

# =============================================================================
# 10-020-00008 
# =============================================================================
item = langlist.create('10-020-00008', kind='warning_4-code')
item.value['ENG'] = 'Order {0} nphot negative (poor spectrum) cannot calculate CCF noise – setting noise and SNR to NaNs'
item.arguments = 'None'
item.comment = 'Means wsum was less than zero and cannot calculate wnoise'
langlist.add(item)

# =============================================================================
# 10-021-00001 
# =============================================================================
item = langlist.create('10-021-00001', kind='warning-code')
item.value['ENG'] = 'Could not extract exposure number from {0} \n\t {0} = {1} \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means we could not extract exposure number out of CMMTSEQ'
langlist.add(item)

# =============================================================================
# 10-021-00002 
# =============================================================================
item = langlist.create('10-021-00002', kind='warning-code')
item.value['ENG'] = 'Could not extract sequence number from {0} \n\t {0} = {1} \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means we could not extract sequence number out of CMMTSEQ'
langlist.add(item)

# =============================================================================
# 10-021-00003 
# =============================================================================
item = langlist.create('10-021-00003', kind='warning-code')
item.value['ENG'] = 'Could not extract total number of sequences from {0} \n\t {0} = {1} \n\t File = {2}'
item.arguments = 'None'
item.comment = 'Means we could not extract total number of sequences out of CMMTSEQ'
langlist.add(item)

# =============================================================================
# 10-021-00004 
# =============================================================================
item = langlist.create('10-021-00004', kind='warning-code')
item.value['ENG'] = 'Key = {0} incorrect for file = {1}'
item.arguments = 'None'
item.comment = 'Means that file is not a polar file (CMMTSEQ incorrect)'
langlist.add(item)

# =============================================================================
# 10-021-00005 
# =============================================================================
item = langlist.create('10-021-00005', kind='warning-code')
item.value['ENG'] = 'Fiber={0} is not valid for file: {1}'
item.arguments = 'None'
item.comment = 'Means that fiber is not valid for polar recipe'
langlist.add(item)

# =============================================================================
# 10-021-00006 
# =============================================================================
item = langlist.create('10-021-00006', kind='warning_2-code')
item.value['ENG'] = 'Exposure {0} in spectroscopic mode, set exposure number = {1}'
item.arguments = 'None'
item.comment = 'Means that exposure N was in spectroscopic mode'
langlist.add(item)

# =============================================================================
# 10-021-00007 
# =============================================================================
item = langlist.create('10-021-00007', kind='warning_2-code')
item.value['ENG'] = 'Minimum number of points required reached (={0}) - stopping rejection'
item.arguments = 'None'
item.comment = 'Means that the minimum number of points are left (after rejection) so stopping rejecting points'
langlist.add(item)

# =============================================================================
# 10-021-00008 
# =============================================================================
item = langlist.create('10-021-00008', kind='warning_4-code')
item.value['ENG'] = 'Failed to fit gaussian to LSD profile \n\t{0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means curve fit failed in LSD profile fitting'
langlist.add(item)

# =============================================================================
# 10-021-00009 
# =============================================================================
item = langlist.create('10-021-00009', kind='warning_6-code')
item.value['ENG'] = 'Input data did not pass QC. Skipping (use –noqccheck to force).'
item.arguments = 'None'
item.comment = 'Means that input data did not pass qc and we are skipping'
langlist.add(item)

# =============================================================================
# 10-021-00010 
# =============================================================================
item = langlist.create('10-021-00010', kind='warning_4-code')
item.value['ENG'] = 'Object temperatures do not match – taking finite median. Individual values are:'
item.arguments = 'None'
item.comment = 'Means that object temperatures do not match between files'
langlist.add(item)

# =============================================================================
# 10-090-00001 
# =============================================================================
item = langlist.create('10-090-00001', kind='warning_2-code')
item.value['ENG'] = 'Removing reduced file: {0}'
item.arguments = 'None'
item.comment = 'prints we are removing red file (clear = True)'
langlist.add(item)

# =============================================================================
# 10-090-00002 
# =============================================================================
item = langlist.create('10-090-00002', kind='warning_2-code')
item.value['ENG'] = '\tSkipping output {0} -- files not found \n\t File: {1}'
item.arguments = 'None'
item.comment = 'prints that we are skipping a file as input files not found'
langlist.add(item)

# =============================================================================
# 10-090-00003 
# =============================================================================
item = langlist.create('10-090-00003', kind='warning_2-code')
item.value['ENG'] = '\t\tFile not found for ext {0} ({1})'
item.arguments = 'None'
item.comment = 'Means that file was not found for extension'
langlist.add(item)

# =============================================================================
# 10-090-00004 
# =============================================================================
item = langlist.create('10-090-00004', kind='warning_2-code')
item.value['ENG'] = 'Header key {0} expected in extension {1} ({2}) but value changed.'
item.arguments = 'None'
item.comment = 'Log that header key was expected but value changed'
langlist.add(item)

# =============================================================================
# 10-100-01001 
# =============================================================================
item = langlist.create('10-100-01001', kind='warning-code')
item.value['ENG'] = 'Latex document construction failed. \n\t Error {0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the latex document construction failed'
langlist.add(item)

# =============================================================================
# 10-100-01002 
# =============================================================================
item = langlist.create('10-100-01002', kind='warning-code')
item.value['ENG'] = 'HTML document construction failed. \n\t Error {0}: {1} \n\t Function = {2}'
item.arguments = 'None'
item.comment = 'Means that the html document construction failed'
langlist.add(item)

# =============================================================================
# 10-100-01003 
# =============================================================================
item = langlist.create('10-100-01003', kind='warning-code')
item.value['ENG'] = 'Latex could not compile pdf document (File = {0})'
item.arguments = 'None'
item.comment = 'Means that latex did not compile a pdf'
langlist.add(item)

# =============================================================================
# 10-101-00001 
# =============================================================================
item = langlist.create('10-101-00001', kind='warning-code')
item.value['ENG'] = 'Lock: Make loc dir waiting {0}'
item.arguments = 'None'
item.comment = 'Warn that lock is waiting due to making the lock dir'
langlist.add(item)

# =============================================================================
# 10-101-00002 
# =============================================================================
item = langlist.create('10-101-00002', kind='warning-code')
item.value['ENG'] = 'Lock: Make lock file waiting {0} {1}'
item.arguments = 'None'
item.comment = 'Warn that lock is waiting due to making the lock file'
langlist.add(item)

# =============================================================================
# 10-101-00003 
# =============================================================================
item = langlist.create('10-101-00003', kind='warning-code')
item.value['ENG'] = 'Lock: Waiting in queue {0} {1} ({2})'
item.arguments = 'None'
item.comment = 'Warn that lock is waiting (in queue)'
langlist.add(item)

# =============================================================================
# 10-101-00004 
# =============================================================================
item = langlist.create('10-101-00004', kind='warning-code')
item.value['ENG'] = 'Lock: Waiting in queue {0} {1} ({2}) Error: {3}'
item.arguments = 'None'
item.comment = 'Warn that lock is waiting (error generated)'
langlist.add(item)

# =============================================================================
# 10-101-00005 
# =============================================================================
item = langlist.create('10-101-00005', kind='warning-code')
item.value['ENG'] = 'Lock: Cannot reset lock dir {0} \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Warn that lock cannot reset directory'
langlist.add(item)

# =============================================================================
# 10-101-00006 
# =============================================================================
item = langlist.create('10-101-00006', kind='warning-code')
item.value['ENG'] = 'Lock: Cannot remove lock file {0}  (reset) \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Warn that lock cannot remove file (reset)'
langlist.add(item)

# =============================================================================
# 10-101-00007 
# =============================================================================
item = langlist.create('10-101-00007', kind='warning-code')
item.value['ENG'] = 'Lock: Cannot remove lock file {0} (dequeue) \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'Warn that lock cannot remove file (dequeue)'
langlist.add(item)

# =============================================================================
# 10-502-00001 
# =============================================================================
item = langlist.create('10-502-00001', kind='all-code')
item.value['ENG'] = 'File \'{0}\' does not exist in \'{1}\' - cannot add'
item.arguments = 'None'
item.comment = 'Prints that file does not exist in reset directory'
langlist.add(item)

# =============================================================================
# 10-502-00002 
# =============================================================================
item = langlist.create('10-502-00002', kind='warning_2-code')
item.value['ENG'] = 'Cannot remove path: {0} \n\t {1}: {2}'
item.arguments = 'None'
item.comment = 'prints that we cannot remove path'
langlist.add(item)

# =============================================================================
# 10-503-00001 
# =============================================================================
item = langlist.create('10-503-00001', kind='warning_2-code')
item.value['ENG'] = 'Overwriting row {0} \n\t Old value: {1} = {2} \n\t {3} = {4}'
item.arguments = 'None'
item.comment = 'Prints that we are overwriting a row and gives the new and old values'
langlist.add(item)

# =============================================================================
# 10-503-00002 
# =============================================================================
item = langlist.create('10-503-00002', kind='warning_2-code')
item.value['ENG'] = 'Overwriting constant {0} \n\t Old value: {1} \t New value: {2}'
item.arguments = 'None'
item.comment = 'Prints that we are overwriting a constant in the parameter dictionary'
langlist.add(item)

# =============================================================================
# 10-503-00003 
# =============================================================================
item = langlist.create('10-503-00003', kind='warning_8-code')
item.value['ENG'] = 'No files with nightname = {0}. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that the table was empty (after filtering for night name)'
langlist.add(item)

# =============================================================================
# 10-503-00004 
# =============================================================================
item = langlist.create('10-503-00004', kind='warning_8-code')
item.value['ENG'] = 'Master nightname = ‘{0}’ invalid. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that reference night name was invalid'
langlist.add(item)

# =============================================================================
# 10-503-00005 
# =============================================================================
item = langlist.create('10-503-00005', kind='warning-code')
item.value['ENG'] = 'Key = {0} not found in run file using default value ({1})'
item.arguments = 'None'
item.comment = 'Prints that we did not have a key in run file so using default value'
langlist.add(item)

# =============================================================================
# 10-503-00006 
# =============================================================================
item = langlist.create('10-503-00006', kind='warning_8-code')
item.value['ENG'] = 'No files after blacklisting. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that we are skipping after black listing due to no files left.'
langlist.add(item)

# =============================================================================
# 10-503-00007 
# =============================================================================
item = langlist.create('10-503-00007', kind='warning_8-code')
item.value['ENG'] = 'No files after whitelisting. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that we are skipping after white listing due to no files left'
langlist.add(item)

# =============================================================================
# 10-503-00008 
# =============================================================================
item = langlist.create('10-503-00008', kind='warning_4-code')
item.value['ENG'] = 'Input directory for recipe not found. Pre-run check failed. \n\t Directory = {0}'
item.arguments = 'None'
item.comment = 'Means that the input directory was not found while prerun test was performed'
langlist.add(item)

# =============================================================================
# 10-503-00009 
# =============================================================================
item = langlist.create('10-503-00009', kind='warning_4-code')
item.value['ENG'] = 'Night name \'directory\' inputted not found. Pre-run check failed. \n\t Night name = {0} \n\t Directory = {1}'
item.arguments = 'None'
item.comment = 'Means that the night name (\'directory\') was not found while prerun test was performed'
langlist.add(item)

# =============================================================================
# 10-503-00010 
# =============================================================================
item = langlist.create('10-503-00010', kind='warning_4-code')
item.value['ENG'] = 'File not found on disk for argument: {0} \n\t Path = {1}'
item.arguments = 'None'
item.comment = 'Means that file was not found in prerun test'
langlist.add(item)

# =============================================================================
# 10-503-00011 
# =============================================================================
item = langlist.create('10-503-00011', kind='warning_4-code')
item.value['ENG'] = 'Processing stats: Could not create directory \'{0}\' \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not write statistics file (could not make dir)'
langlist.add(item)

# =============================================================================
# 10-503-00012 
# =============================================================================
item = langlist.create('10-503-00012', kind='warning_4-code')
item.value['ENG'] = 'Processing stats: Could not save fits file \'{0}\'  \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not write stats fits file'
langlist.add(item)

# =============================================================================
# 10-503-00013 
# =============================================================================
item = langlist.create('10-503-00013', kind='warning-code')
item.value['ENG'] = 'Processing stats: Could not save text file \'{0}\'  \n\t Error {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'Means that we could not write stats txt file'
langlist.add(item)

# =============================================================================
# 10-503-00014 
# =============================================================================
item = langlist.create('10-503-00014', kind='warning_2-code')
item.value['ENG'] = 'Remove Engineering Nights: Directory {0} was removed - no OBJECT type found. Set \"ENGINEERING=True\" to include this directory.'
item.arguments = 'None'
item.comment = 'Means that directory was disregarded due to not object files (ENGINEERING = False)'
langlist.add(item)

# =============================================================================
# 10-503-00015 
# =============================================================================
item = langlist.create('10-503-00015', kind='warning_8-code')
item.value['ENG'] = 'No files after pi name filter. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that we are skipping after pi name filter due to no files left'
langlist.add(item)

# =============================================================================
# 10-503-00016 
# =============================================================================
item = langlist.create('10-503-00016', kind='warning_8-code')
item.value['ENG'] = 'No files after removing engineering data. Skipping.'
item.arguments = 'None'
item.comment = 'Prints that index database was empty (after filtering by engineering data)'
langlist.add(item)

# =============================================================================
# 10-503-00017 
# =============================================================================
item = langlist.create('10-503-00017', kind='warning-code')
item.value['ENG'] = '\tSkipping group'
item.arguments = 'None'
item.comment = 'prints that we are skipping a group'
langlist.add(item)

# =============================================================================
# 10-503-00018 
# =============================================================================
item = langlist.create('10-503-00018', kind='warning_6-code')
item.value['ENG'] = '\tNo runs produced for {0} - No group function given.'
item.arguments = 'None'
item.comment = 'prints that no runs were produced for this recipe (due to no group function)'
langlist.add(item)

# =============================================================================
# 10-503-00019 
# =============================================================================
item = langlist.create('10-503-00019', kind='warning_4-code')
item.value['ENG'] = 'Bad list drs key ‘{0}’ invalid (not in params)'
item.arguments = 'None'
item.comment = 'prints that bad list header key was invalid'
langlist.add(item)

# =============================================================================
# 10-503-00020 
# =============================================================================
item = langlist.create('10-503-00020', kind='warning_4-code')
item.value['ENG'] = 'Bad list header key ‘{0}’ not in header (drs key = {1})'
item.arguments = 'None'
item.comment = 'prints that bad list header key was not in header'
langlist.add(item)

# =============================================================================
# 10-503-00021 
# =============================================================================
item = langlist.create('10-503-00021', kind='warning_4-code')
item.value['ENG'] = 'Bad list cannot access googesheet \n\t Link: {0} \n\t {1}: {2} \n\t Function = {3}'
item.arguments = 'None'
item.comment = 'prints that could not get bad list from google sheet'
langlist.add(item)

# =============================================================================
# 10-503-00022 
# =============================================================================
item = langlist.create('10-503-00022', kind='warning_2-code')
item.value['ENG'] = 'File in reject list - skipping.'
item.arguments = 'None'
item.comment = 'prints that file is bad from google spreadsheet'
langlist.add(item)

# =============================================================================
# 10-503-00023 
# =============================================================================
item = langlist.create('10-503-00023', kind='warning_2-code')
item.value['ENG'] = 'RECAL_TEMPLATES = False. Found {0} templates. Recipes requiring templates where templates were found will be skipped.'
item.arguments = 'None'
item.comment = 'prints that we were asked not to recalculate templates and we have found templates'
langlist.add(item)

# =============================================================================
# 10-503-00024 
# =============================================================================
item = langlist.create('10-503-00024', kind='warning_2-code')
item.value['ENG'] = '\trecipe = {0} skipping runs with known templates.'
item.arguments = 'None'
item.comment = 'prints that this specifc recipe is skipping recipes with found templates'
langlist.add(item)

# =============================================================================
# 10-503-00025 
# =============================================================================
item = langlist.create('10-503-00025', kind='warning_2-code')
item.value['ENG'] = '\t\tMissing {0}\t(OBS_DIR={1} RECIPE={2})'
item.arguments = 'None'
item.comment = 'prints missing filetype from observation directory'
langlist.add(item)

# =============================================================================
# 10-503-00026 
# =============================================================================
item = langlist.create('10-503-00026', kind='warning_2-code')
item.value['ENG'] = 'No telluric RUN instances in run file ‘{0}’. Skipping'
item.arguments = 'None'
item.comment = 'prints that no telluric run instances were found in run.ini'
langlist.add(item)

# =============================================================================
# 10-503-00027 
# =============================================================================
item = langlist.create('10-503-00027', kind='warning_2-code')
item.value['ENG'] = 'No science RUN instances in run file ‘{0}’. Skipping'
item.arguments = 'None'
item.comment = 'prints that no science run instances were found in run.ini'
langlist.add(item)

# =============================================================================
# 10-503-00028 
# =============================================================================
item = langlist.create('10-503-00028', kind='warning_2-code')
item.value['ENG'] = '\tNo telluric files found for observation directory: {0}'
item.arguments = 'None'
item.comment = 'prints that no telluric files were found for this observation directory'
langlist.add(item)

# =============================================================================
# 10-503-00029 
# =============================================================================
item = langlist.create('10-503-00029', kind='warning_2-code')
item.value['ENG'] = '\tNo science files found for observation directory: {0}'
item.arguments = 'None'
item.comment = 'prints that no science files were found for this observation directory'
langlist.add(item)

# =============================================================================
# 10-503-00030 
# =============================================================================
item = langlist.create('10-503-00030', kind='warning_8-code')
item.value['ENG'] = 'The following observation directories will causes errors:'
item.arguments = 'None'
item.comment = 'prints that the following observation directories will cause errors'
langlist.add(item)

# =============================================================================
# 10-503-00031 
# =============================================================================
item = langlist.create('10-503-00031', kind='warning_3-code')
item.value['ENG'] = 'The following observation directories will be skipped as engineering directories:'
item.arguments = 'None'
item.comment = 'prints that the following observations directories will be skipped as engineering directories'
langlist.add(item)

# =============================================================================
# 10-505-00001 
# =============================================================================
item = langlist.create('10-505-00001', kind='warning-code')
item.value['ENG'] = 'Warning file {0} exists!'
item.arguments = 'None'
item.comment = 'warns that reference db file exists'
langlist.add(item)

# =============================================================================
# 10-506-00001 
# =============================================================================
item = langlist.create('10-506-00001', kind='warning_4-code')
item.value['ENG'] = 'Section text file ‘{0}’ does not exist'
item.arguments = 'None'
item.comment = 'Means that section text does not exist'
langlist.add(item)

# =============================================================================
# 10-508-00001 
# =============================================================================
item = langlist.create('10-508-00001', kind='warning_2-code')
item.value['ENG'] = 'Did not find recipe ‘{0}’ - not filtering by this recipe'
item.arguments = 'None'
item.comment = 'Log that we did not find recipe so we are not filtering by recipe'
langlist.add(item)

# =============================================================================
# 10-508-00002 
# =============================================================================
item = langlist.create('10-508-00002', kind='warning_2-code')
item.value['ENG'] = '\t - No log file: {0}'
item.arguments = 'None'
item.comment = 'warns that no log file found'
langlist.add(item)

# =============================================================================
# 10-508-00003 
# =============================================================================
item = langlist.create('10-508-00003', kind='warning_2-code')
item.value['ENG'] = 'Skipping Line({0}): {1} \n\t {2}: {3}'
item.arguments = 'None'
item.comment = 'prints that we are skipping line'
langlist.add(item)

# =============================================================================
# 20-000-00000 
# =============================================================================
item = langlist.create('20-000-00000', kind='info-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Info Messages'
langlist.add(item)

# =============================================================================
# 30-000-00000 
# =============================================================================
item = langlist.create('30-000-00000', kind='graph-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Graph Messages'
langlist.add(item)

# =============================================================================
# 40-000-00000 
# =============================================================================
item = langlist.create('40-000-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'All Messages'
langlist.add(item)

# =============================================================================
# 40-000-00001 
# =============================================================================
item = langlist.create('40-000-00001', kind='all-code')
item.value['ENG'] = 'ParamDict Info: Key = \'{0}\' not found'
item.arguments = 'None'
item.comment = 'Prints that parameter dict info was used but key was invalid'
langlist.add(item)

# =============================================================================
# 40-000-00002 
# =============================================================================
item = langlist.create('40-000-00002', kind='all-code')
item.value['ENG'] = 'Information for key = \'{0}\''
item.arguments = 'None'
item.comment = 'Prints info title for parameter dict info'
langlist.add(item)

# =============================================================================
# 40-000-00003 
# =============================================================================
item = langlist.create('40-000-00003', kind='all-code')
item.value['ENG'] = '\tData Type: \t\t {0}'
item.arguments = 'None'
item.comment = 'prints the data type for parameter dict info'
langlist.add(item)

# =============================================================================
# 40-000-00004 
# =============================================================================
item = langlist.create('40-000-00004', kind='all-code')
item.value['ENG'] = '\tMin Value: \t\t {0} \n\tMax Value: \t\t {1} \n\t Has NaNs: \t\t {2} \n\t Values: \t\t {3}'
item.arguments = 'None'
item.comment = 'prints the info for lists and numpy arrays (parameter dict info)'
langlist.add(item)

# =============================================================================
# 40-000-00005 
# =============================================================================
item = langlist.create('40-000-00005', kind='all-code')
item.value['ENG'] = '\t Num Keys: \t\t {0} \n\t Values: \t\t {1}'
item.arguments = 'None'
item.comment = 'prints the info for dicts (parameter dict info)'
langlist.add(item)

# =============================================================================
# 40-000-00006 
# =============================================================================
item = langlist.create('40-000-00006', kind='all-code')
item.value['ENG'] = '\tValue: \t\t {0}'
item.arguments = 'None'
item.comment = 'prints the info for everything else (parameter dict info)'
langlist.add(item)

# =============================================================================
# 40-000-00007 
# =============================================================================
item = langlist.create('40-000-00007', kind='all-code')
item.value['ENG'] = '\tSource: \t\t {0}'
item.arguments = 'None'
item.comment = 'prints the source (parameter dict info)'
langlist.add(item)

# =============================================================================
# 40-000-00008 
# =============================================================================
item = langlist.create('40-000-00008', kind='all-code')
item.value['ENG'] = '\tInstance: \t\t {0}'
item.arguments = 'None'
item.comment = 'prints the instance (parameter dict info)'
langlist.add(item)

# =============================================================================
# 40-000-00009 
# =============================================================================
item = langlist.create('40-000-00009', kind='all-code')
item.value['ENG'] = 'History for key = \'{0}\''
item.arguments = 'None'
item.comment = 'prints the history (when found) for key'
langlist.add(item)

# =============================================================================
# 40-000-00010 
# =============================================================================
item = langlist.create('40-000-00010', kind='all-code')
item.value['ENG'] = 'No history found for key=\'{0}\''
item.arguments = 'None'
item.comment = 'prints that no history was found for key'
langlist.add(item)

# =============================================================================
# 40-000-00011 
# =============================================================================
item = langlist.create('40-000-00011', kind='all-code')
item.value['ENG'] = 'Copying file {0} to {1}'
item.arguments = 'None'
item.comment = 'prints that we are copying input file to output file'
langlist.add(item)

# =============================================================================
# 40-000-00012 
# =============================================================================
item = langlist.create('40-000-00012', kind='all-code')
item.value['ENG'] = 'Processing file {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are processing files in large_image_combine function'
langlist.add(item)

# =============================================================================
# 40-000-00013 
# =============================================================================
item = langlist.create('40-000-00013', kind='all-code')
item.value['ENG'] = '\tSaving ribbon file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving large_image_combine ribbon'
langlist.add(item)

# =============================================================================
# 40-000-00014 
# =============================================================================
item = langlist.create('40-000-00014', kind='all-code')
item.value['ENG'] = 'Combining ribbon {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are combining ribbon in large_image_combine'
langlist.add(item)

# =============================================================================
# 40-000-00015 
# =============================================================================
item = langlist.create('40-000-00015', kind='all-code')
item.value['ENG'] = '\tLoading ribbon file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading ribbon file'
langlist.add(item)

# =============================================================================
# 40-000-00016 
# =============================================================================
item = langlist.create('40-000-00016', kind='all-code')
item.value['ENG'] = '\tRemoving ribbon file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing ribbon file'
langlist.add(item)

# =============================================================================
# 40-000-00017 
# =============================================================================
item = langlist.create('40-000-00017', kind='all-code')
item.value['ENG'] = '\n Currently installed python modules:'
item.arguments = 'None'
item.comment = 'print the log message for currently installed python modules'
langlist.add(item)

# =============================================================================
# 40-000-00018 
# =============================================================================
item = langlist.create('40-000-00018', kind='all-code')
item.value['ENG'] = '\n Raw arguments used:'
item.arguments = 'None'
item.comment = 'print the log message for raw arguments used'
langlist.add(item)

# =============================================================================
# 40-001-00000 
# =============================================================================
item = langlist.create('40-001-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Setup/Database Messages'
langlist.add(item)

# =============================================================================
# 40-001-00001 
# =============================================================================
item = langlist.create('40-001-00001', kind='all-code')
item.value['ENG'] = ' NAME'
item.value['FR'] = 'NOM'
item.arguments = 'None'
item.comment = 'Name string - used in setup'
langlist.add(item)

# =============================================================================
# 40-001-00002 
# =============================================================================
item = langlist.create('40-001-00002', kind='all-code')
item.value['ENG'] = ' VERSION'
item.value['FR'] = 'VERSION'
item.arguments = 'None'
item.comment = 'Version string - used in setup'
langlist.add(item)

# =============================================================================
# 40-001-00003 
# =============================================================================
item = langlist.create('40-001-00003', kind='all-code')
item.value['ENG'] = ' AUTHORS'
item.value['FR'] = 'AUTEURS'
item.arguments = 'None'
item.comment = 'Authors string - used in setup'
langlist.add(item)

# =============================================================================
# 40-001-00004 
# =============================================================================
item = langlist.create('40-001-00004', kind='all-code')
item.value['ENG'] = ' LAST UPDATED'
item.value['FR'] = 'DERNIÈRE MISE À JOUR'
item.arguments = 'None'
item.comment = 'last updated string - used in setup'
langlist.add(item)

# =============================================================================
# 40-001-00005 
# =============================================================================
item = langlist.create('40-001-00005', kind='all-code')
item.value['ENG'] = ' RELEASE STATUS'
item.value['FR'] = 'STATUS DE LIBERATION'
item.arguments = 'None'
item.comment = 'release string - used in setup'
langlist.add(item)

# =============================================================================
# 40-001-00006 
# =============================================================================
item = langlist.create('40-001-00006', kind='all-code')
item.value['ENG'] = 'DRS Setup:'
item.value['FR'] = 'Configuration de DRS:'
item.arguments = 'None'
item.comment = 'setup title text'
langlist.add(item)

# =============================================================================
# 40-001-00007 
# =============================================================================
item = langlist.create('40-001-00007', kind='all-code')
item.value['ENG'] = '\t{0} is not set, running in on-line mode'
item.value['FR'] = '\t{0} n\'est pas défini, fonctionne en mode en ligne'
item.arguments = 'None'
item.comment = 'display for interactive mode set off'
langlist.add(item)

# =============================================================================
# 40-001-00008 
# =============================================================================
item = langlist.create('40-001-00008', kind='all-code')
item.value['ENG'] = '\t{0} is set'
item.value['FR'] = '\t est défini'
item.arguments = 'None'
item.comment = 'display for interactive mode set on'
langlist.add(item)

# =============================================================================
# 40-001-00009 
# =============================================================================
item = langlist.create('40-001-00009', kind='all-code')
item.value['ENG'] = '\t{0} is set, debug mode level: {1}'
item.value['FR'] = '\t{0} est défini, niveau de mode débogage: {1}'
item.arguments = 'None'
item.comment = 'display for debug mode'
langlist.add(item)

# =============================================================================
# 40-001-00010 
# =============================================================================
item = langlist.create('40-001-00010', kind='all-code')
item.value['ENG'] = 'System information'
item.value['FR'] = 'Le système d\'information'
item.arguments = 'None'
item.comment = 'system information title text'
langlist.add(item)

# =============================================================================
# 40-001-00011 
# =============================================================================
item = langlist.create('40-001-00011', kind='all-code')
item.value['ENG'] = '\t Path = \'{0}\''
item.value['FR'] = '\t Répertoire = \'{0}\''
item.arguments = 'None'
item.comment = 'system info path text'
langlist.add(item)

# =============================================================================
# 40-001-00012 
# =============================================================================
item = langlist.create('40-001-00012', kind='all-code')
item.value['ENG'] = '\t Platform = \'{0}\''
item.value['FR'] = '\t Système d\'exploitation = \'{0}\''
item.arguments = 'None'
item.comment = 'system info platform text'
langlist.add(item)

# =============================================================================
# 40-001-00013 
# =============================================================================
item = langlist.create('40-001-00013', kind='all-code')
item.value['ENG'] = '\t Python version = \'{0}\''
item.value['FR'] = '\t Version de Python = \'{0}\''
item.arguments = 'None'
item.comment = 'system info version'
langlist.add(item)

# =============================================================================
# 40-001-00014 
# =============================================================================
item = langlist.create('40-001-00014', kind='all-code')
item.value['ENG'] = '\t Python distribution = \'{0}\''
item.value['FR'] = '\t Distribution Python = \'{0}\''
item.arguments = 'None'
item.comment = 'system info python distribution'
langlist.add(item)

# =============================================================================
# 40-001-00015 
# =============================================================================
item = langlist.create('40-001-00015', kind='all-code')
item.value['ENG'] = '\t Distribution date = \'{0}\''
item.value['FR'] = '\t La date de distribution =\'{0}\''
item.arguments = 'None'
item.comment = 'system info distribution date'
langlist.add(item)

# =============================================================================
# 40-001-00016 
# =============================================================================
item = langlist.create('40-001-00016', kind='all-code')
item.value['ENG'] = '\t Other information = \'{0}\''
item.value['FR'] = '\tD\'autres informations = \'{0}\''
item.arguments = 'None'
item.comment = '40-004-'
langlist.add(item)

# =============================================================================
# 40-001-00017 
# =============================================================================
item = langlist.create('40-001-00017', kind='all-code')
item.value['ENG'] = 'Arguments used:'
item.value['FR'] = 'Arguments servant:'
item.arguments = 'None'
item.comment = 'text for arguments used'
langlist.add(item)

# =============================================================================
# 40-001-00018 
# =============================================================================
item = langlist.create('40-001-00018', kind='all-code')
item.value['ENG'] = 'Unknown'
item.value['FR'] = 'Inconnu'
item.arguments = 'None'
item.comment = 'text for name of an unknown argument'
langlist.add(item)

# =============================================================================
# 40-001-00019 
# =============================================================================
item = langlist.create('40-001-00019', kind='all-code')
item.value['ENG'] = '\n\nAll files checked:'
item.arguments = 'None'
item.comment = 'display message for all files that have been checked (lists below)'
langlist.add(item)

# =============================================================================
# 40-001-00020 
# =============================================================================
item = langlist.create('40-001-00020', kind='all-code')
item.value['ENG'] = 'Processing file {0} of {1}'
item.arguments = 'None'
item.comment = 'Prints the file we are iterating on'
langlist.add(item)

# =============================================================================
# 40-001-00021 
# =============================================================================
item = langlist.create('40-001-00021', kind='all-code')
item.value['ENG'] = 'Passing data (via DATA_DICT) to function. \n\t Keys = {0}'
item.arguments = 'None'
item.comment = 'Prints that we are passing data to a function via DATA_DICT'
langlist.add(item)

# =============================================================================
# 40-001-00022 
# =============================================================================
item = langlist.create('40-001-00022', kind='all-code')
item.value['ENG'] = 'Processing fiber {0}'
item.arguments = 'None'
item.comment = 'Prints that we are iterating on a fiber'
langlist.add(item)

# =============================================================================
# 40-001-00023 
# =============================================================================
item = langlist.create('40-001-00023', kind='all-code')
item.value['ENG'] = 'Making dir(s): {0}'
item.arguments = 'None'
item.comment = 'Prints that we are making directory'
langlist.add(item)

# =============================================================================
# 40-001-00024 
# =============================================================================
item = langlist.create('40-001-00024', kind='all-code')
item.value['ENG'] = 'Not adding key {0} to database (User input --database = False) \n\t File = {1}'
item.arguments = 'None'
item.comment = 'Print that we are not adding file to database (due to user input)'
langlist.add(item)

# =============================================================================
# 40-001-00025 
# =============================================================================
item = langlist.create('40-001-00025', kind='all-code')
item.value['ENG'] = 'Writing combined file: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are writing combined file to disk'
langlist.add(item)

# =============================================================================
# 40-001-00026 
# =============================================================================
item = langlist.create('40-001-00026', kind='all-code')
item.value['ENG'] = 'Loading database from file=\'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are loading database xls file'
langlist.add(item)

# =============================================================================
# 40-001-00027 
# =============================================================================
item = langlist.create('40-001-00027', kind='all-code')
item.value['ENG'] = 'Analyzing sheet \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are analying language database xls sheet'
langlist.add(item)

# =============================================================================
# 40-001-00028 
# =============================================================================
item = langlist.create('40-001-00028', kind='all-code')
item.value['ENG'] = 'Saving reset file = \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are saving reset file'
langlist.add(item)

# =============================================================================
# 40-001-00029 
# =============================================================================
item = langlist.create('40-001-00029', kind='all-code')
item.value['ENG'] = 'Backing up database to \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are backing up xls file'
langlist.add(item)

# =============================================================================
# 40-001-00030 
# =============================================================================
item = langlist.create('40-001-00030', kind='all-code')
item.value['ENG'] = 'Removing file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are removing old language db files'
langlist.add(item)

# =============================================================================
# 40-001-00031 
# =============================================================================
item = langlist.create('40-001-00031', kind='all-code')
item.value['ENG'] = '\tSkipping search (already run)'
item.arguments = 'None'
item.comment = 'Prints that we are skipping search as its already been run'
langlist.add(item)

# =============================================================================
# 40-001-00032 
# =============================================================================
item = langlist.create('40-001-00032', kind='all-code')
item.value['ENG'] = '\tReading headers of {0} files (to be updated)'
item.arguments = 'None'
item.comment = 'Prints that we are reading headers of N files'
langlist.add(item)

# =============================================================================
# 40-001-00033 
# =============================================================================
item = langlist.create('40-001-00033', kind='all-code')
item.value['ENG'] = '\tSearching all directories'
item.arguments = 'None'
item.comment = 'Prints that we are searching all directories for files'
langlist.add(item)

# =============================================================================
# 40-001-00034 
# =============================================================================
item = langlist.create('40-001-00034', kind='all-code')
item.value['ENG'] = 'Response must be valid {0}'
item.arguments = 'None'
item.comment = 'Prints that install response must be valid'
langlist.add(item)

# =============================================================================
# 40-001-00035 
# =============================================================================
item = langlist.create('40-001-00035', kind='all-code')
item.value['ENG'] = 'Response invalid'
item.arguments = 'None'
item.comment = 'Prints that install response is invalid'
langlist.add(item)

# =============================================================================
# 40-001-00036 
# =============================================================================
item = langlist.create('40-001-00036', kind='all-code')
item.value['ENG'] = 'Response must be a valid path or \'None\''
item.arguments = 'None'
item.comment = 'Prints that install response must be valid path or None'
langlist.add(item)

# =============================================================================
# 40-001-00037 
# =============================================================================
item = langlist.create('40-001-00037', kind='all-code')
item.value['ENG'] = 'Response must be a valid path'
item.arguments = 'None'
item.comment = 'Prints that install response must be valid path'
langlist.add(item)

# =============================================================================
# 40-001-00038 
# =============================================================================
item = langlist.create('40-001-00038', kind='all-code')
item.value['ENG'] = 'Path \'{0}\' does not exist. Create?'
item.arguments = 'None'
item.comment = 'Prints that path does not exist and we should create it'
langlist.add(item)

# =============================================================================
# 40-001-00039 
# =============================================================================
item = langlist.create('40-001-00039', kind='all-code')
item.value['ENG'] = 'Response must be {0}'
item.arguments = 'None'
item.comment = 'Prints that response must be value'
langlist.add(item)

# =============================================================================
# 40-001-00040 
# =============================================================================
item = langlist.create('40-001-00040', kind='all-code')
item.value['ENG'] = '\t - {0} set from cmd ({1})'
item.arguments = 'None'
item.comment = 'Print that arg was set from command'
langlist.add(item)

# =============================================================================
# 40-001-00041 
# =============================================================================
item = langlist.create('40-001-00041', kind='all-code')
item.value['ENG'] = 'Installation for {0}'
item.arguments = 'None'
item.comment = 'Prints this is the installation for package name'
langlist.add(item)

# =============================================================================
# 40-001-00042 
# =============================================================================
item = langlist.create('40-001-00042', kind='all-code')
item.value['ENG'] = 'Choose instrument in install'
item.arguments = 'None'
item.comment = 'Prints that the user should choose which instrument to install'
langlist.add(item)

# =============================================================================
# 40-001-00043 
# =============================================================================
item = langlist.create('40-001-00043', kind='all-code')
item.value['ENG'] = 'Choose a database mode:'
item.arguments = 'None'
item.comment = 'Prints question about choosing database mode'
langlist.add(item)

# =============================================================================
# 40-001-00044 
# =============================================================================
item = langlist.create('40-001-00044', kind='all-code')
item.value['ENG'] = '1. sqlite (recommended for single machine use) - no setup required'
item.arguments = 'None'
item.comment = 'Database sqlite option'
langlist.add(item)

# =============================================================================
# 40-001-00045 
# =============================================================================
item = langlist.create('40-001-00045', kind='all-code')
item.value['ENG'] = '2. mysql (required for multple core/machine use) - setup required'
item.arguments = 'None'
item.comment = 'Database mysql option'
langlist.add(item)

# =============================================================================
# 40-001-00046 
# =============================================================================
item = langlist.create('40-001-00046', kind='all-code')
item.value['ENG'] = 'Settings for {0}'
item.arguments = 'None'
item.comment = 'Prints settings for instrument'
langlist.add(item)

# =============================================================================
# 40-001-00047 
# =============================================================================
item = langlist.create('40-001-00047', kind='all-code')
item.value['ENG'] = 'Data directory'
item.arguments = 'None'
item.comment = 'Prints data directory question'
langlist.add(item)

# =============================================================================
# 40-001-00048 
# =============================================================================
item = langlist.create('40-001-00048', kind='all-code')
item.value['ENG'] = '\n\t - Making directory \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are making directory'
langlist.add(item)

# =============================================================================
# 40-001-00049 
# =============================================================================
item = langlist.create('40-001-00049', kind='all-code')
item.value['ENG'] = '\t - {0} set from datadir ({1})'
item.arguments = 'None'
item.comment = 'Prints that arg was set from data dir'
langlist.add(item)

# =============================================================================
# 40-001-00050 
# =============================================================================
item = langlist.create('40-001-00050', kind='all-code')
item.value['ENG'] = 'Plot mode required'
item.arguments = 'None'
item.comment = 'Prints question for plot mode'
langlist.add(item)

# =============================================================================
# 40-001-00051 
# =============================================================================
item = langlist.create('40-001-00051', kind='all-code')
item.value['ENG'] = '0: No plotting'
item.arguments = 'None'
item.comment = 'option 0 plot mode'
langlist.add(item)

# =============================================================================
# 40-001-00052 
# =============================================================================
item = langlist.create('40-001-00052', kind='all-code')
item.value['ENG'] = '1: Only summary plots (saved to disk)'
item.arguments = 'None'
item.comment = 'option 1 plot mode'
langlist.add(item)

# =============================================================================
# 40-001-00053 
# =============================================================================
item = langlist.create('40-001-00053', kind='all-code')
item.value['ENG'] = '2: Plots displayed at end of code'
item.arguments = 'None'
item.comment = 'option 2 plot mode'
langlist.add(item)

# =============================================================================
# 40-001-00054 
# =============================================================================
item = langlist.create('40-001-00054', kind='all-code')
item.value['ENG'] = '\t - DRS_PLOT set from cmd ({0})'
item.arguments = 'None'
item.comment = 'Prints that DRS_PLOT was set from cmd'
langlist.add(item)

# =============================================================================
# 40-001-00055 
# =============================================================================
item = langlist.create('40-001-00055', kind='all-code')
item.value['ENG'] = '\t - CLEAN set from cmd ({0})'
item.arguments = 'None'
item.comment = 'Prints that CLEAN_INSTALL set from cmd'
langlist.add(item)

# =============================================================================
# 40-001-00056 
# =============================================================================
item = langlist.create('40-001-00056', kind='all-code')
item.value['ENG'] = 'Enter database {{{0}}}:'
item.arguments = 'None'
item.comment = 'Print question to ask for database variable'
langlist.add(item)

# =============================================================================
# 40-001-00057 
# =============================================================================
item = langlist.create('40-001-00057', kind='all-code')
item.value['ENG'] = 'Enter mysql database name'
item.arguments = 'None'
item.comment = 'Prints question to ask for mysql database name'
langlist.add(item)

# =============================================================================
# 40-001-00058 
# =============================================================================
item = langlist.create('40-001-00058', kind='all-code')
item.value['ENG'] = 'Enter table suffix for {0} database table (leave blank for default: {2})\n\nNote \'{1}_{{SUFFIX}}_DB\' will be the final table name.\ni.e. by default: \'{1}_{2}_DB\''
item.arguments = 'None'
item.comment = 'Prints question to enter table suffix for database'
langlist.add(item)

# =============================================================================
# 40-001-00059 
# =============================================================================
item = langlist.create('40-001-00059', kind='all-code')
item.value['ENG'] = '\t - Empty directory found -- forcing clean install.'
item.arguments = 'None'
item.comment = 'Prints that empty directory was found'
langlist.add(item)

# =============================================================================
# 40-001-00060 
# =============================================================================
item = langlist.create('40-001-00060', kind='all-code')
item.value['ENG'] = '\t - Performing clean installation'
item.arguments = 'None'
item.comment = 'Prints that we are performing clean installation'
langlist.add(item)

# =============================================================================
# 40-001-00061 
# =============================================================================
item = langlist.create('40-001-00061', kind='all-code')
item.value['ENG'] = '\n\t Populating {0} directory\n'
item.arguments = 'None'
item.comment = 'Prints that we are populating directory'
langlist.add(item)

# =============================================================================
# 40-001-00062 
# =============================================================================
item = langlist.create('40-001-00062', kind='all-code')
item.value['ENG'] = 'To run {0} do the following:'
item.arguments = 'None'
item.comment = 'Prints instructions required by user to run apero (title)'
langlist.add(item)

# =============================================================================
# 40-001-00063 
# =============================================================================
item = langlist.create('40-001-00063', kind='all-code')
item.value['ENG'] = 'DEV MODE: Add all constants in group \'{0}\' to file: {1}?'
item.arguments = 'None'
item.comment = 'Prints we are in dev mode and should add all constants'
langlist.add(item)

# =============================================================================
# 40-001-00064 
# =============================================================================
item = langlist.create('40-001-00064', kind='all-code')
item.value['ENG'] = '\n Conflicting line found in current {0} file for constant \'{1}\''
item.arguments = 'None'
item.comment = 'Prints that there is a conflicting line found for constants'
langlist.add(item)

# =============================================================================
# 40-001-00065 
# =============================================================================
item = langlist.create('40-001-00065', kind='all-code')
item.value['ENG'] = 'Replacing default: \n\t{0} \nwith current:\n\t{1}'
item.arguments = 'None'
item.comment = 'Prints that we are replacing default constant value'
langlist.add(item)

# =============================================================================
# 40-001-00066 
# =============================================================================
item = langlist.create('40-001-00066', kind='all-code')
item.value['ENG'] = 'GUI features not implemented yet.'
item.arguments = 'None'
item.comment = 'Prints that GUI features not implemented yet'
langlist.add(item)

# =============================================================================
# 40-001-00067 
# =============================================================================
item = langlist.create('40-001-00067', kind='all-code')
item.value['ENG'] = 'Installing'
item.arguments = 'None'
item.comment = 'Prints that we are installing apero'
langlist.add(item)

# =============================================================================
# 40-001-00068 
# =============================================================================
item = langlist.create('40-001-00068', kind='all-code')
item.value['ENG'] = '\n - Getting binary paths'
item.arguments = 'None'
item.comment = 'Prints that we are getting binary paths'
langlist.add(item)

# =============================================================================
# 40-001-00069 
# =============================================================================
item = langlist.create('40-001-00069', kind='all-code')
item.value['ENG'] = '\n - Creating config files'
item.arguments = 'None'
item.comment = 'Prints that we are creating config files'
langlist.add(item)

# =============================================================================
# 40-001-00070 
# =============================================================================
item = langlist.create('40-001-00070', kind='all-code')
item.value['ENG'] = '\n - Updating config files'
item.arguments = 'None'
item.comment = 'Prints that we are updating config file'
langlist.add(item)

# =============================================================================
# 40-001-00071 
# =============================================================================
item = langlist.create('40-001-00071', kind='all-code')
item.value['ENG'] = '\n - Creating shell scripts'
item.arguments = 'None'
item.comment = 'Prints that we are creating shell scripts'
langlist.add(item)

# =============================================================================
# 40-001-00072 
# =============================================================================
item = langlist.create('40-001-00072', kind='all-code')
item.value['ENG'] = '\n - Copying files\n\n'
item.arguments = 'None'
item.comment = 'Prints that we are copying files'
langlist.add(item)

# =============================================================================
# 40-001-00073 
# =============================================================================
item = langlist.create('40-001-00073', kind='all-code')
item.value['ENG'] = '\n - Creating symlinks\n'
item.arguments = 'None'
item.comment = 'Prints that we are creating sym links'
langlist.add(item)

# =============================================================================
# 40-001-00074 
# =============================================================================
item = langlist.create('40-001-00074', kind='all-code')
item.value['ENG'] = 'Installation complete'
item.arguments = 'None'
item.comment = 'Prints that installation is complete'
langlist.add(item)

# =============================================================================
# 40-001-00075 
# =============================================================================
item = langlist.create('40-001-00075', kind='all-code')
item.value['ENG'] = '\n\nExiting installation script'
item.arguments = 'None'
item.comment = 'Prints we are exiting installation script'
langlist.add(item)

# =============================================================================
# 40-001-00076 
# =============================================================================
item = langlist.create('40-001-00076', kind='all-code')
item.value['ENG'] = 'Module check:'
item.arguments = 'None'
item.comment = 'Prints that we are doing a module check'
langlist.add(item)

# =============================================================================
# 40-001-00077 
# =============================================================================
item = langlist.create('40-001-00077', kind='all-code')
item.value['ENG'] = 'pip install {0}'
item.arguments = 'None'
item.comment = 'Prints suggested install method'
langlist.add(item)

# =============================================================================
# 40-001-00078 
# =============================================================================
item = langlist.create('40-001-00078', kind='all-code')
item.value['ENG'] = '\t{0} recommends {1} to be installed (dev only) \n\t i.e. {2}'
item.arguments = 'None'
item.comment = 'Prints that in dev mode we recommend this module to be installed'
langlist.add(item)

# =============================================================================
# 40-001-00079 
# =============================================================================
item = langlist.create('40-001-00079', kind='all-code')
item.value['ENG'] = '\t{0} recommends {1} to be updated ({3} < {2})\n\t i.e {4}\'.format(*args)'
item.arguments = 'None'
item.comment = 'Prints that we recommend module to be updated'
langlist.add(item)

# =============================================================================
# 40-001-00080 
# =============================================================================
item = langlist.create('40-001-00080', kind='all-code')
item.value['ENG'] = '\tFatal Error: {0} requires module {1} ({3} < {2})\n\t i.e {4}\'.format(*args)'
item.arguments = 'None'
item.comment = 'Prints that we require module to be a newer version'
langlist.add(item)

# =============================================================================
# 40-001-00081 
# =============================================================================
item = langlist.create('40-001-00081', kind='all-code')
item.value['ENG'] = '\tPassed: {1} ({3} >= {2})'
item.arguments = 'None'
item.comment = 'Prints that module passed version check'
langlist.add(item)

# =============================================================================
# 40-001-00082 
# =============================================================================
item = langlist.create('40-001-00082', kind='all-code')
item.value['ENG'] = '3: Plots displayed immediately and code paused'
item.arguments = 'None'
item.comment = 'option 3 plot mode'
langlist.add(item)

# =============================================================================
# 40-001-00083 
# =============================================================================
item = langlist.create('40-001-00083', kind='all-code')
item.value['ENG'] = '\n\nError resetting database (see above) cannot install apero'
item.arguments = 'None'
item.comment = 'prints that there was an error resetting database'
langlist.add(item)

# =============================================================================
# 40-002-00000 
# =============================================================================
item = langlist.create('40-002-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Help Messages'
langlist.add(item)

# =============================================================================
# 40-002-00001 
# =============================================================================
item = langlist.create('40-002-00001', kind='all-code')
item.value['ENG'] = 'Help for: \'{0}.py\''
item.value['FR'] = 'Aide pour: \'{0}.py\''
item.arguments = 'None'
item.comment = 'Help title'
langlist.add(item)

# =============================================================================
# 40-002-00002 
# =============================================================================
item = langlist.create('40-002-00002', kind='all-code')
item.value['ENG'] = 'Required Arguments:'
item.value['FR'] = 'Arguments requis:'
item.arguments = 'None'
item.comment = 'Required arguments'
langlist.add(item)

# =============================================================================
# 40-002-00003 
# =============================================================================
item = langlist.create('40-002-00003', kind='all-code')
item.value['ENG'] = 'Optional Arguments:'
item.value['FR'] = 'Arguments optionnels:'
item.arguments = 'None'
item.comment = 'Optional arguments'
langlist.add(item)

# =============================================================================
# 40-002-00004 
# =============================================================================
item = langlist.create('40-002-00004', kind='all-code')
item.value['ENG'] = 'Special Arguments:'
item.value['FR'] = 'Arguments spéciaux:'
item.arguments = 'None'
item.comment = 'Special Arguments'
langlist.add(item)

# =============================================================================
# 40-002-00005 
# =============================================================================
item = langlist.create('40-002-00005', kind='all-code')
item.value['ENG'] = 'show this help message and exit'
item.value['FR'] = 'afficher ce message d\'aide et quitter'
item.arguments = 'None'
item.comment = 'help message'
langlist.add(item)

# =============================================================================
# 40-002-00006 
# =============================================================================
item = langlist.create('40-002-00006', kind='all-code')
item.value['ENG'] = 'Info for: {0}'
item.value['FR'] = 'Info pour: {0}'
item.arguments = 'None'
item.comment = 'info title message'
langlist.add(item)

# =============================================================================
# 40-002-00007 
# =============================================================================
item = langlist.create('40-002-00007', kind='all-code')
item.value['ENG'] = 'Usage: '
item.value['FR'] = ' L\'utilisation:'
item.arguments = 'None'
item.comment = 'usage message'
langlist.add(item)

# =============================================================================
# 40-002-00008 
# =============================================================================
item = langlist.create('40-002-00008', kind='all-code')
item.value['ENG'] = 'use --help for more detailed help'
item.value['FR'] = 'utilisez \'--help\' pour une aide plus détaillée'
item.arguments = 'None'
item.comment = 'tell user to use --help for more detailed help menu'
langlist.add(item)

# =============================================================================
# 40-003-00000 
# =============================================================================
item = langlist.create('40-003-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Exit Messages'
langlist.add(item)

# =============================================================================
# 40-003-00001 
# =============================================================================
item = langlist.create('40-003-00001', kind='all-code')
item.value['ENG'] = 'Recipe {0} has been successfully completed'
item.value['FR'] = 'La recette {0} a été complétée avec succès'
item.arguments = 'None'
item.comment = 'Successful completion message'
langlist.add(item)

# =============================================================================
# 40-003-00002 
# =============================================================================
item = langlist.create('40-003-00002', kind='all-code')
item.value['ENG'] = 'Press \'Enter\' to exit or [Y]es to continue in {0}'
item.value['FR'] = 'Appuyez sur \'Entrée\' pour quitter ou sur [Y] pour continuer dans {0}'
item.arguments = 'None'
item.comment = 'Enter to exit message. Note currently options must be [Y]es or [N]o'
langlist.add(item)

# =============================================================================
# 40-003-00003 
# =============================================================================
item = langlist.create('40-003-00003', kind='all-code')
item.value['ENG'] = 'Close plots? [Y]es or [N]o '
item.value['FR'] = 'Fermer les graphique(s) ? [Y]es ou [N]o'
item.arguments = 'None'
item.comment = 'Question whether to close plots. Note currently options must be [Y]es or [N]o'
langlist.add(item)

# =============================================================================
# 40-003-00004 
# =============================================================================
item = langlist.create('40-003-00004', kind='all-code')
item.value['ENG'] = 'Starting interactive session ({0})'
item.value['FR'] = 'Commencer une session interactive ({0})'
item.arguments = 'None'
item.comment = 'Message to show starting of interactive session'
langlist.add(item)

# =============================================================================
# 40-003-00005 
# =============================================================================
item = langlist.create('40-003-00005', kind='warning_8-code')
item.value['ENG'] = 'Recipe {0} has NOT been successfully completed'
item.value['FR'] = 'La recette {0} N\'A PAS été complétée avec succès'
item.arguments = 'None'
item.comment = 'Unsuccessful completion message'
langlist.add(item)

# =============================================================================
# 40-004-00000 
# =============================================================================
item = langlist.create('40-004-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Indexing/IO/Path Messages'
langlist.add(item)

# =============================================================================
# 40-004-00001 
# =============================================================================
item = langlist.create('40-004-00001', kind='all-code')
item.value['ENG'] = 'No outputs to index, skipping indexing'
item.value['FR'] = 'Aucune sortie à indexer, sautant l\'indexation'
item.arguments = 'None'
item.comment = 'When we have no outputs we skip indexing'
langlist.add(item)

# =============================================================================
# 40-004-00002 
# =============================================================================
item = langlist.create('40-004-00002', kind='all-code')
item.value['ENG'] = 'Indexing outputs onto {0}'
item.value['FR'] = 'Indexer la sortie dans  {0}'
item.arguments = 'None'
item.comment = 'Show progress of indexing and index file path'
langlist.add(item)

# =============================================================================
# 40-004-00003 
# =============================================================================
item = langlist.create('40-004-00003', kind='all-code')
item.value['ENG'] = 'Found {0} index files'
item.arguments = 'None'
item.comment = 'lists how many index files were found'
langlist.add(item)

# =============================================================================
# 40-004-00004 
# =============================================================================
item = langlist.create('40-004-00004', kind='all-code')
item.value['ENG'] = 'Found {0} {1} file(s)'
item.arguments = 'None'
item.comment = 'lists how many files were found by \'find_filetypes\''
langlist.add(item)

# =============================================================================
# 40-004-00005 
# =============================================================================
item = langlist.create('40-004-00005', kind='all-code')
item.value['ENG'] = 'Reading data for file: {0}'
item.arguments = 'None'
item.comment = 'Means we are reading data for file (when getting another fibers file)'
langlist.add(item)

# =============================================================================
# 40-004-00006 
# =============================================================================
item = langlist.create('40-004-00006', kind='all-code')
item.value['ENG'] = 'Reading header for file: {0}'
item.arguments = 'None'
item.comment = 'Means we are reading header for file (when getting another fibers file)'
langlist.add(item)

# =============================================================================
# 40-005-00000 
# =============================================================================
item = langlist.create('40-005-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Listing Messages'
langlist.add(item)

# =============================================================================
# 40-005-00001 
# =============================================================================
item = langlist.create('40-005-00001', kind='all-code')
item.value['ENG'] = 'Listing for: {0}'
item.value['FR'] = 'Liste pour: {0}'
item.arguments = 'None'
item.comment = 'Listing title'
langlist.add(item)

# =============================================================================
# 40-005-00002 
# =============================================================================
item = langlist.create('40-005-00002', kind='all-code')
item.value['ENG'] = 'Possible inputs for \'directory\' \n (displaying first {0} directories in location=\'{1}\')'
item.value['FR'] = 'Entrées possibles pour \'directory\' \n (affichant les premiers {0} répertoires de location = \'{1}\')'
item.arguments = 'None'
item.comment = 'Prints the list message directory mode, when we have a limit on number'
langlist.add(item)

# =============================================================================
# 40-005-00003 
# =============================================================================
item = langlist.create('40-005-00003', kind='all-code')
item.value['ENG'] = 'Possible inputs for \'{2}\' \n (displaying first {0} files in directory=\'{1}\')'
item.value['FR'] = 'Entrées possibles pour \'{2}\' \n (affichant les premiers {0} fichiers du répertoire = \'{1}\')'
item.arguments = 'None'
item.comment = 'Prints the list message file mode, when we have a limit on number. Note {0} not used'
langlist.add(item)

# =============================================================================
# 40-005-00004 
# =============================================================================
item = langlist.create('40-005-00004', kind='all-code')
item.value['ENG'] = 'Possible inputs for \'directory\' \n (displaying all directories in location=\'{1}\')'
item.value['FR'] = 'Entrées possibles pour \'directory\' \n (affichant tous les répertoires de location = \'{1}\')'
item.arguments = 'None'
item.comment = 'Prints the list message directory mode, when we have no limit on number'
langlist.add(item)

# =============================================================================
# 40-005-00005 
# =============================================================================
item = langlist.create('40-005-00005', kind='all-code')
item.value['ENG'] = 'Possible inputs for \'{2}\' \n (displaying all files in directory=\'{1}\')'
item.value['FR'] = 'Entrées possibles pour \'{2}\' \n (affichant tous les fichiers du répertoire = \'{1}\')'
item.arguments = 'None'
item.comment = 'Prints the list message file mode, when we have no limit on number. Note {0} not used'
langlist.add(item)

# =============================================================================
# 40-005-00006 
# =============================================================================
item = langlist.create('40-005-00006', kind='all-code')
item.value['ENG'] = 'Updating listing for block_kind={0}'
item.arguments = 'None'
item.comment = 'Prints that we are updating the listing for block kind'
langlist.add(item)

# =============================================================================
# 40-005-10000 
# =============================================================================
item = langlist.create('40-005-10000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'General QC Messages'
langlist.add(item)

# =============================================================================
# 40-005-10001 
# =============================================================================
item = langlist.create('40-005-10001', kind='all-code')
item.value['ENG'] = 'QUALITY CONTROL SUCCESSFUL - Well Done -'
item.arguments = 'None'
item.comment = 'The qc successful message'
langlist.add(item)

# =============================================================================
# 40-005-10002 
# =============================================================================
item = langlist.create('40-005-10002', kind='warning_6-code')
item.value['ENG'] = 'QUALITY CONTROL FAILED:'
item.arguments = 'None'
item.comment = 'the qc fail message (followed by how it failed)'
langlist.add(item)

# =============================================================================
# 40-005-10003 
# =============================================================================
item = langlist.create('40-005-10003', kind='all-code')
item.value['ENG'] = 'Calibration {0} within delta time threshold ({1}<{2} days) \n\t File: {3}'
item.arguments = 'None'
item.comment = 'Means that we checked the delta time between observation and calibration and the delta time is within limits'
langlist.add(item)

# =============================================================================
# 40-005-10004 
# =============================================================================
item = langlist.create('40-005-10004', kind='all-code')
item.value['ENG'] = 'Checking input qc for: {0}'
item.arguments = 'None'
item.comment = 'Message that we are checking inputs for quality control criteria'
langlist.add(item)

# =============================================================================
# 40-005-10005 
# =============================================================================
item = langlist.create('40-005-10005', kind='all-code')
item.value['ENG'] = '\tAll input {0} files passed QC'
item.arguments = 'None'
item.comment = 'prints that all input files passed qc check'
langlist.add(item)

# =============================================================================
# 40-006-00000 
# =============================================================================
item = langlist.create('40-006-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'General Database messages'
langlist.add(item)

# =============================================================================
# 40-006-00001 
# =============================================================================
item = langlist.create('40-006-00001', kind='all-code')
item.value['ENG'] = 'Updating {0} database with key {1}'
item.arguments = 'None'
item.comment = 'Prints that we updated database with specific key'
langlist.add(item)

# =============================================================================
# 40-006-00002 
# =============================================================================
item = langlist.create('40-006-00002', kind='all-code')
item.value['ENG'] = '{0} file \'{1}\' already exists - not copied'
item.arguments = 'None'
item.comment = 'Prints that we are skipping copying database file'
langlist.add(item)

# =============================================================================
# 40-006-00003 
# =============================================================================
item = langlist.create('40-006-00003', kind='all-code')
item.value['ENG'] = '{0} file \'{1}\' copied to dir {2}'
item.arguments = 'None'
item.comment = 'Prints that we are copying database file'
langlist.add(item)

# =============================================================================
# 40-006-00004 
# =============================================================================
item = langlist.create('40-006-00004', kind='all-code')
item.value['ENG'] = '{0}: Copy to database successful. File = {1}'
item.arguments = 'None'
item.comment = 'Prints that file was copied to database'
langlist.add(item)

# =============================================================================
# 40-006-00005 
# =============================================================================
item = langlist.create('40-006-00005', kind='all-code')
item.value['ENG'] = 'Loading database {0}: {1}'
item.arguments = 'None'
item.comment = 'Prints that we are loading sql database'
langlist.add(item)

# =============================================================================
# 40-006-00006 
# =============================================================================
item = langlist.create('40-006-00006', kind='all-code')
item.value['ENG'] = 'Rebuilding {0} index entries'
item.arguments = 'None'
item.comment = 'Prints that we are rebuilding entries in a database'
langlist.add(item)

# =============================================================================
# 40-006-00007 
# =============================================================================
item = langlist.create('40-006-00007', kind='all-code')
item.value['ENG'] = 'Updating {0} database'
item.arguments = 'None'
item.comment = 'Prints that we are updating the {0} database'
langlist.add(item)

# =============================================================================
# 40-006-00008 
# =============================================================================
item = langlist.create('40-006-00008', kind='all-code')
item.value['ENG'] = 'Found {0} object observations'
item.arguments = 'None'
item.comment = 'Prints that we found N object observations'
langlist.add(item)

# =============================================================================
# 40-006-00009 
# =============================================================================
item = langlist.create('40-006-00009', kind='all-code')
item.value['ENG'] = 'Found {0} unique object names'
item.arguments = 'None'
item.comment = 'Prints that we found N  unique object names'
langlist.add(item)

# =============================================================================
# 40-006-00010 
# =============================================================================
item = langlist.create('40-006-00010', kind='all-code')
item.value['ENG'] = 'Analysing {0}={1}   ({2}/{3})'
item.arguments = 'None'
item.comment = 'Print that we are analysing a certain column and row'
langlist.add(item)

# =============================================================================
# 40-006-00011 
# =============================================================================
item = langlist.create('40-006-00011', kind='all-code')
item.value['ENG'] = 'Found {0} objects with Gaia entries'
item.arguments = 'None'
item.comment = 'Prints that we found N objects with Gaia ID'
langlist.add(item)

# =============================================================================
# 40-006-00012 
# =============================================================================
item = langlist.create('40-006-00012', kind='all-code')
item.value['ENG'] = 'Saving reset file to: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving reset file to path'
langlist.add(item)

# =============================================================================
# 40-006-00013 
# =============================================================================
item = langlist.create('40-006-00013', kind='all-code')
item.value['ENG'] = 'Reading {0} object headers...'
item.arguments = 'None'
item.comment = 'Prints taht we are reading N object headers'
langlist.add(item)

# =============================================================================
# 40-010-00000 
# =============================================================================
item = langlist.create('40-010-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Preprocessing messages'
langlist.add(item)

# =============================================================================
# 40-010-00001 
# =============================================================================
item = langlist.create('40-010-00001', kind='all-code')
item.value['ENG'] = 'File identified as {0}'
item.arguments = 'None'
item.comment = 'Prints that file was identified as a valid raw drs_file (preprocessing.drs_file_id)'
langlist.add(item)

# =============================================================================
# 40-010-00002 
# =============================================================================
item = langlist.create('40-010-00002', kind='all-code')
item.value['ENG'] = 'File not identified. \n\t Skipping file {0}'
item.arguments = 'None'
item.comment = 'Prints that file was not identified as a valid raw drs_file (preprocessing.drs_file_id)'
langlist.add(item)

# =============================================================================
# 40-010-00003 
# =============================================================================
item = langlist.create('40-010-00003', kind='all-code')
item.value['ENG'] = 'Correcting for top and bottom pixels'
item.arguments = 'None'
item.comment = 'Prints that we are correcting for top and bottom pixels'
langlist.add(item)

# =============================================================================
# 40-010-00004 
# =============================================================================
item = langlist.create('40-010-00004', kind='all-code')
item.value['ENG'] = 'Correcting by the median filter from dark amplifiers'
item.arguments = 'None'
item.comment = 'Prints that we are correcting by the median filter from dark amplifiers'
langlist.add(item)

# =============================================================================
# 40-010-00005 
# =============================================================================
item = langlist.create('40-010-00005', kind='all-code')
item.value['ENG'] = 'Correcting for the 1/f noise'
item.arguments = 'None'
item.comment = 'Prints that we are correcting the 1/f noise'
langlist.add(item)

# =============================================================================
# 40-010-00006 
# =============================================================================
item = langlist.create('40-010-00006', kind='all-code')
item.value['ENG'] = 'Corruption check: SNR Hotpix value = {0:.5e}'
item.arguments = 'None'
item.comment = 'Prints the corruption check SNR hotpix value'
langlist.add(item)

# =============================================================================
# 40-010-00007 
# =============================================================================
item = langlist.create('40-010-00007', kind='all-code')
item.value['ENG'] = 'File was found to be corrupted. \n\t SNR_HOTPIX < threshold \n\t {0:.4e} < {1:4e}. \n\t File will not be saved. \n\t File = {2}'
item.arguments = 'None'
item.comment = 'QC failure message for presprocess SNR hotpix'
langlist.add(item)

# =============================================================================
# 40-010-00008 
# =============================================================================
item = langlist.create('40-010-00008', kind='all-code')
item.value['ENG'] = 'File was found to be corrupted. \n\t RMS < threshold \n\t {0:.4e} > {1:.4e}. \n\t File will not be saved. \n\t File = {2}'
item.arguments = 'None'
item.comment = 'QC failure message for preprocessing rms'
langlist.add(item)

# =============================================================================
# 40-010-00009 
# =============================================================================
item = langlist.create('40-010-00009', kind='all-code')
item.value['ENG'] = 'Saving rotated image in {0}'
item.arguments = 'None'
item.comment = 'Prints where we are saving the rotated image to'
langlist.add(item)

# =============================================================================
# 40-010-00010 
# =============================================================================
item = langlist.create('40-010-00010', kind='all-code')
item.value['ENG'] = 'Saving image to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving image to file'
langlist.add(item)

# =============================================================================
# 40-010-00011 
# =============================================================================
item = langlist.create('40-010-00011', kind='all-code')
item.value['ENG'] = 'Reading engineering full flat image: \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are reading the full flat for preprocessing'
langlist.add(item)

# =============================================================================
# 40-010-00012 
# =============================================================================
item = langlist.create('40-010-00012', kind='all-code')
item.value['ENG'] = 'File already exists and skipping done files activated. \n\t Skipping file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are skipping done file'
langlist.add(item)

# =============================================================================
# 40-010-00013 
# =============================================================================
item = langlist.create('40-010-00013', kind='all-code')
item.value['ENG'] = 'Image found to be offset from engineering flat. \n\t Shifting image by dx = {0} dy = {1}'
item.arguments = 'None'
item.comment = 'Prints that we are shifting image'
langlist.add(item)

# =============================================================================
# 40-010-00014 
# =============================================================================
item = langlist.create('40-010-00014', kind='all-code')
item.value['ENG'] = 'Constructing preprocessing reference mask (Filetype = {0})'
item.arguments = 'None'
item.comment = 'Prints that we are making reference mask for filetype'
langlist.add(item)

# =============================================================================
# 40-010-00015 
# =============================================================================
item = langlist.create('40-010-00015', kind='all-code')
item.value['ENG'] = 'Saving preprocessing reference mask: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving reference mask'
langlist.add(item)

# =============================================================================
# 40-010-00016 
# =============================================================================
item = langlist.create('40-010-00016', kind='all-code')
item.value['ENG'] = 'Correcting PP file (1/f and median)'
item.arguments = 'None'
item.comment = 'Prints that we are correcting pp files'
langlist.add(item)

# =============================================================================
# 40-010-00017 
# =============================================================================
item = langlist.create('40-010-00017', kind='all-code')
item.value['ENG'] = 'Minimum exposure time not met \n\t Actual Exposure time: {0} \n\t Minimum required exposure time: {1}'
item.arguments = 'None'
item.comment = 'Prints that minimum exposure time not met'
langlist.add(item)

# =============================================================================
# 40-010-00018 
# =============================================================================
item = langlist.create('40-010-00018', kind='all-code')
item.value['ENG'] = 'Correcting for cosmics'
item.arguments = 'None'
item.comment = 'Prints that we are correcting for cosmics'
langlist.add(item)

# =============================================================================
# 40-010-00019 
# =============================================================================
item = langlist.create('40-010-00019', kind='all-code')
item.value['ENG'] = 'Masking bright pixels'
item.arguments = 'None'
item.comment = 'prints that we are masking bright pixels'
langlist.add(item)

# =============================================================================
# 40-010-00020 
# =============================================================================
item = langlist.create('40-010-00020', kind='all-code')
item.value['ENG'] = 'Finding low frequencies'
item.arguments = 'None'
item.comment = 'prints that we are finding low frequencies'
langlist.add(item)

# =============================================================================
# 40-010-00021 
# =============================================================================
item = langlist.create('40-010-00021', kind='all-code')
item.value['ENG'] = 'Correcting intercept'
item.arguments = 'None'
item.comment = 'prints that we are correcting intercept'
langlist.add(item)

# =============================================================================
# 40-010-00022 
# =============================================================================
item = langlist.create('40-010-00022', kind='all-code')
item.value['ENG'] = 'Correcting error on slope'
item.arguments = 'None'
item.comment = 'prints that we are correction error on slope'
langlist.add(item)

# =============================================================================
# 40-010-00023 
# =============================================================================
item = langlist.create('40-010-00023', kind='all-code')
item.value['ENG'] = 'DPRTYPE={0} (dark) was not found to be a valid dark. Value = {1:.4f} > {2} '
item.arguments = 'None'
item.comment = 'Prints that the dark was found to not be an actual dark'
langlist.add(item)

# =============================================================================
# 40-011-00000 
# =============================================================================
item = langlist.create('40-011-00000', kind='all-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Dark messages'
langlist.add(item)

# =============================================================================
# 40-011-00001 
# =============================================================================
item = langlist.create('40-011-00001', kind='all-code')
item.value['ENG'] = 'Doing Dark measurement'
item.arguments = 'None'
item.comment = 'Prints that we are doing dark measurement'
langlist.add(item)

# =============================================================================
# 40-011-00002 
# =============================================================================
item = langlist.create('40-011-00002', kind='all-code')
item.value['ENG'] = 'In {0:12s}: Frac dead pixels= {1:.4f} % - Median= {2:.3f} ADU/s - Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s'
item.arguments = 'None'
item.comment = 'Prints the number of dead pixels found in measure_dark'
langlist.add(item)

# =============================================================================
# 40-011-00003 
# =============================================================================
item = langlist.create('40-011-00003', kind='all-code')
item.value['ENG'] = 'Whole detector'
item.arguments = 'None'
item.comment = 'Describes the whole detector'
langlist.add(item)

# =============================================================================
# 40-011-00004 
# =============================================================================
item = langlist.create('40-011-00004', kind='all-code')
item.value['ENG'] = 'Blue part'
item.arguments = 'None'
item.comment = 'Describes the blue part of the detector'
langlist.add(item)

# =============================================================================
# 40-011-00005 
# =============================================================================
item = langlist.create('40-011-00005', kind='all-code')
item.value['ENG'] = 'Red part'
item.arguments = 'None'
item.comment = 'Describes the red part of the detector'
langlist.add(item)

# =============================================================================
# 40-011-00006 
# =============================================================================
item = langlist.create('40-011-00006', kind='all-code')
item.value['ENG'] = 'Fraction of pixels with DARK > {0:.2f} ADU/s = {1:.3f} %'
item.arguments = 'None'
item.comment = 'Prints the fraction of pixels with dark less than a certain value'
langlist.add(item)

# =============================================================================
# 40-011-00007 
# =============================================================================
item = langlist.create('40-011-00007', kind='all-code')
item.value['ENG'] = 'Total fraction of dead pixels (NaN + DARK > {0:.2f} ADU/s = {1:.3f} %'
item.arguments = 'None'
item.comment = 'Prints the total fraction of dead pixels and their contributions'
langlist.add(item)

# =============================================================================
# 40-011-00008 
# =============================================================================
item = langlist.create('40-011-00008', kind='all-code')
item.value['ENG'] = 'Unexpected Median Dark level  ({0:5.2f} > {1:5.2f} ADU/s)'
item.arguments = 'None'
item.comment = 'QC failure message for max dark level'
langlist.add(item)

# =============================================================================
# 40-011-00009 
# =============================================================================
item = langlist.create('40-011-00009', kind='all-code')
item.value['ENG'] = 'Unexpected Fraction of dead pixels ({0:5.2f} > {1:5.2f} %)'
item.arguments = 'None'
item.comment = 'QC failure message for fraction of dead pixels'
langlist.add(item)

# =============================================================================
# 40-011-00010 
# =============================================================================
item = langlist.create('40-011-00010', kind='all-code')
item.value['ENG'] = 'Unexpected Fraction of dark pixels > {0:.2f} ADU/s ({1:.2f} > {2:.2f}'
item.arguments = 'None'
item.comment = 'QC failure message for fraction of dark pixels'
langlist.add(item)

# =============================================================================
# 40-011-00011 
# =============================================================================
item = langlist.create('40-011-00011', kind='all-code')
item.value['ENG'] = 'Doing dark correction using {0}: {1}'
item.arguments = 'None'
item.comment = 'Prints that we are doing dark correction'
langlist.add(item)

# =============================================================================
# 40-011-00012 
# =============================================================================
item = langlist.create('40-011-00012', kind='all-code')
item.value['ENG'] = 'Saving dark file to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving dark file to file'
langlist.add(item)

# =============================================================================
# 40-011-10001 
# =============================================================================
item = langlist.create('40-011-10001', kind='all-code')
item.value['ENG'] = 'Reading all dark file headers'
item.arguments = 'None'
item.comment = 'dark reference: prints that we are reading all dark file headers'
langlist.add(item)

# =============================================================================
# 40-011-10002 
# =============================================================================
item = langlist.create('40-011-10002', kind='all-code')
item.value['ENG'] = 'Matching dark files by observation time (+/- {0} hrs)'
item.arguments = 'None'
item.comment = 'prints the time threshold for matching dark files'
langlist.add(item)

# =============================================================================
# 40-011-10003 
# =============================================================================
item = langlist.create('40-011-10003', kind='all-code')
item.value['ENG'] = 'Reading Dark files and combining groups'
item.arguments = 'None'
item.comment = 'prints that we are reading dark files and combining groups'
langlist.add(item)

# =============================================================================
# 40-011-10004 
# =============================================================================
item = langlist.create('40-011-10004', kind='all-code')
item.value['ENG'] = '\t Group {0} of {1}'
item.arguments = 'None'
item.comment = 'prints the group we are combining'
langlist.add(item)

# =============================================================================
# 40-011-10005 
# =============================================================================
item = langlist.create('40-011-10005', kind='all-code')
item.value['ENG'] = 'Performing median filter for {0} bins'
item.arguments = 'None'
item.comment = 'prints that we are performing the median filter and for how many bins'
langlist.add(item)

# =============================================================================
# 40-011-10006 
# =============================================================================
item = langlist.create('40-011-10006', kind='all-code')
item.value['ENG'] = 'Saving dark reference file to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving dark reference file to file'
langlist.add(item)

# =============================================================================
# 40-011-10007 
# =============================================================================
item = langlist.create('40-011-10007', kind='all-code')
item.value['ENG'] = 'Normalizing cube groups'
item.arguments = 'None'
item.comment = 'Prints that we are normalising the dark'
langlist.add(item)

# =============================================================================
# 40-011-10008 
# =============================================================================
item = langlist.create('40-011-10008', kind='all-code')
item.value['ENG'] = 'Medianing cube to produce reference dark'
item.arguments = 'None'
item.comment = 'Prints that we are medianing cube to produce reference dark'
langlist.add(item)

# =============================================================================
# 40-012-00001 
# =============================================================================
item = langlist.create('40-012-00001', kind='all-code')
item.value['ENG'] = 'Normalising the flat'
item.arguments = 'None'
item.comment = 'Prints that we are normalising the flat'
langlist.add(item)

# =============================================================================
# 40-012-00002 
# =============================================================================
item = langlist.create('40-012-00002', kind='all-code')
item.value['ENG'] = 'Looking for bad pixels in the full flat image'
item.arguments = 'None'
item.comment = 'Prints that we are looking for bad pixels in the full flat image'
langlist.add(item)

# =============================================================================
# 40-012-00003 
# =============================================================================
item = langlist.create('40-012-00003', kind='all-code')
item.value['ENG'] = 'Reading engineering full flat image: \'{0}\''
item.arguments = 'None'
item.comment = 'Print that we are reading the full engineering flat'
langlist.add(item)

# =============================================================================
# 40-012-00004 
# =============================================================================
item = langlist.create('40-012-00004', kind='all-code')
item.value['ENG'] = 'Fraction of un-illuminated pixels in engineering flat {0:.4f} %'
item.arguments = 'None'
item.comment = 'Prints the fraction of unilluminated pixels in the engineering flat'
langlist.add(item)

# =============================================================================
# 40-012-00005 
# =============================================================================
item = langlist.create('40-012-00005', kind='all-code')
item.value['ENG'] = 'Looking for bad pixels'
item.arguments = 'None'
item.comment = 'Prints that we are looking for bad pixels in the flat/dark'
langlist.add(item)

# =============================================================================
# 40-012-00006 
# =============================================================================
item = langlist.create('40-012-00006', kind='all-code')
item.value['ENG'] = 'Fraction of hot pixels from dark: {0:.4f} % \n Fraction of bad pixels from flat: {1:.4f} % \n Fraction of non-finite pixels in dark: {2:.4f} % \n Fraction of non-finite pixels in flat: {3:.4f} % \n Fraction of bad pixels with all criteria: {4:.4f} %'
item.arguments = 'None'
item.comment = 'Prints the stats from the getting the bad pixels from flat/dark'
langlist.add(item)

# =============================================================================
# 40-012-00007 
# =============================================================================
item = langlist.create('40-012-00007', kind='all-code')
item.value['ENG'] = 'Fraction of total bad pixels: {0:.4f} %'
item.arguments = 'None'
item.comment = 'Prints the total number of bad pixels'
langlist.add(item)

# =============================================================================
# 40-012-00008 
# =============================================================================
item = langlist.create('40-012-00008', kind='all-code')
item.value['ENG'] = 'Correcting for bad pixels (setting bad pixels to NaN) \n\t file = {0}'
item.arguments = 'None'
item.comment = 'Prints that we are setting bad pixels to NaN'
langlist.add(item)

# =============================================================================
# 40-012-00009 
# =============================================================================
item = langlist.create('40-012-00009', kind='all-code')
item.value['ENG'] = 'Correcting for global background using file = {0}'
item.arguments = 'None'
item.comment = 'Prints that we are correcting global background'
langlist.add(item)

# =============================================================================
# 40-012-00010 
# =============================================================================
item = langlist.create('40-012-00010', kind='all-code')
item.value['ENG'] = 'Measuring local background using 2D Gaussian Kernel'
item.arguments = 'None'
item.comment = 'Prints that we are measure local background'
langlist.add(item)

# =============================================================================
# 40-012-00011 
# =============================================================================
item = langlist.create('40-012-00011', kind='all-code')
item.value['ENG'] = '\tPadding NaNs'
item.arguments = 'None'
item.comment = 'Prints that we are padding nans for local background correction'
langlist.add(item)

# =============================================================================
# 40-012-00012 
# =============================================================================
item = langlist.create('40-012-00012', kind='all-code')
item.value['ENG'] = '\tCalculating 2D convolution'
item.arguments = 'None'
item.comment = 'Prints that we are calculating the 2D convolution '
langlist.add(item)

# =============================================================================
# 40-012-00013 
# =============================================================================
item = langlist.create('40-012-00013', kind='all-code')
item.value['ENG'] = 'Saving badpix map to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving badpixmap file to file'
langlist.add(item)

# =============================================================================
# 40-012-00014 
# =============================================================================
item = langlist.create('40-012-00014', kind='all-code')
item.value['ENG'] = 'Saving background map to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving background map file to file'
langlist.add(item)

# =============================================================================
# 40-013-00001 
# =============================================================================
item = langlist.create('40-013-00001', kind='all-code')
item.value['ENG'] = 'Creating Order Profile'
item.arguments = 'None'
item.comment = 'Prints that we are creating order profile'
langlist.add(item)

# =============================================================================
# 40-013-00002 
# =============================================================================
item = langlist.create('40-013-00002', kind='all-code')
item.value['ENG'] = 'Saving order profile to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving order profile to file'
langlist.add(item)

# =============================================================================
# 40-013-00003 
# =============================================================================
item = langlist.create('40-013-00003', kind='all-code')
item.value['ENG'] = 'Maximum flux/pixel in the spectrum: {0:.1f} [e-]'
item.arguments = 'None'
item.comment = 'Prints the maximum flux per pixel in the spectrum'
langlist.add(item)

# =============================================================================
# 40-013-00004 
# =============================================================================
item = langlist.create('40-013-00004', kind='all-code')
item.value['ENG'] = 'Average background level: {0:.2f} [%]'
item.arguments = 'None'
item.comment = 'Prints the average background level'
langlist.add(item)

# =============================================================================
# 40-013-00005 
# =============================================================================
item = langlist.create('40-013-00005', kind='all-code')
item.value['ENG'] = 'Searching order center on central column'
item.arguments = 'None'
item.comment = 'Prints that we are searching for order center on central column'
langlist.add(item)

# =============================================================================
# 40-013-00006 
# =============================================================================
item = langlist.create('40-013-00006', kind='all-code')
item.value['ENG'] = 'On fiber {0} {1} orders have been detected on {2} fiber(s)'
item.arguments = 'None'
item.comment = 'Prints the number of orders found for number of fibers'
langlist.add(item)

# =============================================================================
# 40-013-00007 
# =============================================================================
item = langlist.create('40-013-00007', kind='all-code')
item.value['ENG'] = 'ORDER: {0} center at pixel {1:.1f} width {2:.1f} rms {3:.3f}'
item.arguments = 'None'
item.comment = 'Prints the width and center fit for order'
langlist.add(item)

# =============================================================================
# 40-013-00008 
# =============================================================================
item = langlist.create('40-013-00008', kind='all-code')
item.value['ENG'] = '\t {0} fit converging with rms/ptp/{1}: {2:.3f}/{3:.3f}/{4:.3f}'
item.arguments = 'None'
item.comment = 'Print that fit is converging with stats'
langlist.add(item)

# =============================================================================
# 40-013-00009 
# =============================================================================
item = langlist.create('40-013-00009', kind='all-code')
item.value['ENG'] = '\t {0} fit rms/ptp/{1}: {4:.3f} with {5} rejected points'
item.arguments = 'None'
item.comment = 'Print the fit is rejecting points with stats'
langlist.add(item)

# =============================================================================
# 40-013-00010 
# =============================================================================
item = langlist.create('40-013-00010', kind='all-code')
item.value['ENG'] = 'Order found to be too incomplete, discarded'
item.arguments = 'None'
item.comment = 'Print that order was too incomplete'
langlist.add(item)

# =============================================================================
# 40-013-00011 
# =============================================================================
item = langlist.create('40-013-00011', kind='all-code')
item.value['ENG'] = 'On fiber {0} {1} orders geometry have been measured'
item.arguments = 'None'
item.comment = 'Prints the number of orders geometry that was found'
langlist.add(item)

# =============================================================================
# 40-013-00012 
# =============================================================================
item = langlist.create('40-013-00012', kind='all-code')
item.value['ENG'] = 'Average uncertainty on position: {0:.2f} [mpix]'
item.arguments = 'None'
item.comment = 'Prints the average uncertainty on position'
langlist.add(item)

# =============================================================================
# 40-013-00013 
# =============================================================================
item = langlist.create('40-013-00013', kind='all-code')
item.value['ENG'] = 'Average uncertainty on width: {0:.2f} [mpix]'
item.arguments = 'None'
item.comment = 'Prints the average uncertainty on the width'
langlist.add(item)

# =============================================================================
# 40-013-00014 
# =============================================================================
item = langlist.create('40-013-00014', kind='all-code')
item.value['ENG'] = 'abnormal points rejection during ctr fit ({0:.2f} > {1:.2f}'
item.arguments = 'None'
item.comment = 'Prints that the QC failed for number of points rejected (position)'
langlist.add(item)

# =============================================================================
# 40-013-00015 
# =============================================================================
item = langlist.create('40-013-00015', kind='all-code')
item.value['ENG'] = 'abnormal points rejection during width fit ({0:.2f} > {1:.2f})'
item.arguments = 'None'
item.comment = 'Prints that the QC failed for number of points rejected (width)'
langlist.add(item)

# =============================================================================
# 40-013-00016 
# =============================================================================
item = langlist.create('40-013-00016', kind='all-code')
item.value['ENG'] = 'too high rms on center fitting ({0:.2f} > {1:.2f})'
item.arguments = 'None'
item.comment = 'Prints that the QC failed for rms for the center'
langlist.add(item)

# =============================================================================
# 40-013-00017 
# =============================================================================
item = langlist.create('40-013-00017', kind='all-code')
item.value['ENG'] = 'too high rms on profile fwhm fitting ({0:.2f} > {1:.2f})'
item.arguments = 'None'
item.comment = 'Prints that the QC failed for rms for the width'
langlist.add(item)

# =============================================================================
# 40-013-00018 
# =============================================================================
item = langlist.create('40-013-00018', kind='all-code')
item.value['ENG'] = 'abnormal number of identified orders (found {0:.2f} expected {1:.2f}'
item.arguments = 'None'
item.comment = 'Prints that the QC failed for the number of orders found'
langlist.add(item)

# =============================================================================
# 40-013-00019 
# =============================================================================
item = langlist.create('40-013-00019', kind='all-code')
item.value['ENG'] = 'Saving loco1 file to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving the loco1 file to file'
langlist.add(item)

# =============================================================================
# 40-013-00020 
# =============================================================================
item = langlist.create('40-013-00020', kind='all-code')
item.value['ENG'] = 'Saving loco2 file to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving the loco2 file to file'
langlist.add(item)

# =============================================================================
# 40-013-00021 
# =============================================================================
item = langlist.create('40-013-00021', kind='all-code')
item.value['ENG'] = 'Saving loco3 file to {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving the loco3 file to file'
langlist.add(item)

# =============================================================================
# 40-013-00022 
# =============================================================================
item = langlist.create('40-013-00022', kind='all-code')
item.value['ENG'] = 'Reading order profile from file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are loading the order profile from file'
langlist.add(item)

# =============================================================================
# 40-013-00023 
# =============================================================================
item = langlist.create('40-013-00023', kind='all-code')
item.value['ENG'] = 'Reading order profile from npy file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are loading the order profile from npy file'
langlist.add(item)

# =============================================================================
# 40-013-00024 
# =============================================================================
item = langlist.create('40-013-00024', kind='all-code')
item.value['ENG'] = 'Saving order profile to npy file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving the order profile to npy file'
langlist.add(item)

# =============================================================================
# 40-013-00025 
# =============================================================================
item = langlist.create('40-013-00025', kind='all-code')
item.value['ENG'] = 'Saving debug background file {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving background debug file'
langlist.add(item)

# =============================================================================
# 40-013-00026 
# =============================================================================
item = langlist.create('40-013-00026', kind='all-code')
item.value['ENG'] = 'Cleaning coeffs for p={0}'
item.arguments = 'None'
item.comment = 'Prints that we are cleaning coefficients for specific parity'
langlist.add(item)

# =============================================================================
# 40-013-00027 
# =============================================================================
item = langlist.create('40-013-00027', kind='all-code')
item.value['ENG'] = 'The difference in y central positions is not positive. Localisation has failed due to calculated orders crossing in the y-direction.'
item.arguments = 'None'
item.comment = 'Prints that QC failed for orders crossing'
langlist.add(item)

# =============================================================================
# 40-013-00028 
# =============================================================================
item = langlist.create('40-013-00028', kind='all-code')
item.value['ENG'] = 'Finding and fitting orders for fiber = {0}'
item.arguments = 'None'
item.comment = 'Means we are finding and fitting orders for fiber'
langlist.add(item)

# =============================================================================
# 40-013-00029 
# =============================================================================
item = langlist.create('40-013-00029', kind='all-code')
item.value['ENG'] = '\tMasking orders'
item.arguments = 'None'
item.comment = 'Means that we are masking orders'
langlist.add(item)

# =============================================================================
# 40-013-00030 
# =============================================================================
item = langlist.create('40-013-00030', kind='all-code')
item.value['ENG'] = '\tFound {0} order blobs'
item.arguments = 'None'
item.comment = 'Print that we found N order blobs'
langlist.add(item)

# =============================================================================
# 40-013-00031 
# =============================================================================
item = langlist.create('40-013-00031', kind='all-code')
item.value['ENG'] = '\tKeeping {0} orders'
item.arguments = 'None'
item.comment = 'Print that we are keeping N orders'
langlist.add(item)

# =============================================================================
# 40-014-00001 
# =============================================================================
item = langlist.create('40-014-00001', kind='all-code')
item.value['ENG'] = 'Processing FP reference file'
item.arguments = 'None'
item.comment = 'prints that we are correcting the fp file (ref) in shape reference'
langlist.add(item)

# =============================================================================
# 40-014-00002 
# =============================================================================
item = langlist.create('40-014-00002', kind='all-code')
item.value['ENG'] = 'Processing HC reference file'
item.arguments = 'None'
item.comment = 'prints that we are correcting the hc file (ref) in shape reference'
langlist.add(item)

# =============================================================================
# 40-014-00003 
# =============================================================================
item = langlist.create('40-014-00003', kind='all-code')
item.value['ENG'] = 'Constructing FP table and reading all fp file headers'
item.arguments = 'None'
item.comment = 'shape reference: prints that we are reading all fp file headers'
langlist.add(item)

# =============================================================================
# 40-014-00004 
# =============================================================================
item = langlist.create('40-014-00004', kind='all-code')
item.value['ENG'] = 'Matching FP files by observation time (+/- {0} hrs)'
item.arguments = 'None'
item.comment = 'prints the time threshold for matching fp files'
langlist.add(item)

# =============================================================================
# 40-014-00005 
# =============================================================================
item = langlist.create('40-014-00005', kind='all-code')
item.value['ENG'] = 'Reading FP files and combining groups'
item.arguments = 'None'
item.comment = 'prints that we are reading and combining FP file groups'
langlist.add(item)

# =============================================================================
# 40-014-00006 
# =============================================================================
item = langlist.create('40-014-00006', kind='all-code')
item.value['ENG'] = 'Combining FP Group {0} of {1}'
item.arguments = 'None'
item.comment = 'prints the FP group we are currently processing'
langlist.add(item)

# =============================================================================
# 40-014-00007 
# =============================================================================
item = langlist.create('40-014-00007', kind='all-code')
item.value['ENG'] = 'Reading file {0} ({1} / {2})'
item.arguments = 'None'
item.comment = 'prints the FP file (from current FP group) we are currently reading'
langlist.add(item)

# =============================================================================
# 40-014-00008 
# =============================================================================
item = langlist.create('40-014-00008', kind='all-code')
item.value['ENG'] = 'Calculating median of {0} images'
item.arguments = 'None'
item.comment = 'prints that we are calculating the mean of FP files in FP reference'
langlist.add(item)

# =============================================================================
# 40-014-00009 
# =============================================================================
item = langlist.create('40-014-00009', kind='all-code')
item.value['ENG'] = 'Linear transform starting point:'
item.arguments = 'None'
item.comment = 'prints the linear transform starting point'
langlist.add(item)

# =============================================================================
# 40-014-00010 
# =============================================================================
item = langlist.create('40-014-00010', kind='all-code')
item.value['ENG'] = 'Iteration {0}/{1}'
item.arguments = 'None'
item.comment = 'print the linear transform iteration number'
langlist.add(item)

# =============================================================================
# 40-014-00011 
# =============================================================================
item = langlist.create('40-014-00011', kind='all-code')
item.value['ENG'] = 'Master FP construction complete. \n\tAdding {0} group images to form FP reference image'
item.arguments = 'None'
item.comment = 'prints that the reference fp construction was completed and how many groups were used'
langlist.add(item)

# =============================================================================
# 40-014-00012 
# =============================================================================
item = langlist.create('40-014-00012', kind='all-code')
item.value['ENG'] = 'Cleaning FP hot pixels'
item.arguments = 'None'
item.comment = 'prints that we are cleaning hot pixels'
langlist.add(item)

# =============================================================================
# 40-014-00013 
# =============================================================================
item = langlist.create('40-014-00013', kind='all-code')
item.value['ENG'] = 'Image {0} resized from {1} to {2}'
item.arguments = 'None'
item.comment = 'prints that we are re-sizing image'
langlist.add(item)

# =============================================================================
# 40-014-00014 
# =============================================================================
item = langlist.create('40-014-00014', kind='all-code')
item.value['ENG'] = 'Normalising image by percentile = {0}'
item.arguments = 'None'
item.comment = 'prints that we are re-normalizing image'
langlist.add(item)

# =============================================================================
# 40-014-00015 
# =============================================================================
item = langlist.create('40-014-00015', kind='all-code')
item.value['ENG'] = 'Skipping group {0}. Not enough files (minimum = {1})'
item.arguments = 'None'
item.comment = 'prints that we are skipping group due to insufficient numbers'
langlist.add(item)

# =============================================================================
# 40-014-00016 
# =============================================================================
item = langlist.create('40-014-00016', kind='all-code')
item.value['ENG'] = 'Banana iteration: {0}/{1}: Order {2}/{3}'
item.arguments = 'None'
item.comment = 'prints the banana iteration we are currently on'
langlist.add(item)

# =============================================================================
# 40-014-00017 
# =============================================================================
item = langlist.create('40-014-00017', kind='all-code')
item.value['ENG'] = '\tRange slope exploration: {0:.3f} -> {1:.3f} deg'
item.arguments = 'None'
item.comment = 'prints the slope range we are exploring'
langlist.add(item)

# =============================================================================
# 40-014-00018 
# =============================================================================
item = langlist.create('40-014-00018', kind='all-code')
item.value['ENG'] = '\tSlope at pixel {0}: {1:.5f} deg'
item.arguments = 'None'
item.comment = 'prints the slope at pixel value'
langlist.add(item)

# =============================================================================
# 40-014-00019 
# =============================================================================
item = langlist.create('40-014-00019', kind='all-code')
item.value['ENG'] = '\tPredicted FP peak #: {0} Measured FP peak #: {1}'
item.arguments = 'None'
item.comment = 'prints the predicted FP peak number vs measured FP peak number'
langlist.add(item)

# =============================================================================
# 40-014-00020 
# =============================================================================
item = langlist.create('40-014-00020', kind='all-code')
item.value['ENG'] = '\t\tstddev pixel error relative to fit: {0:.5f} pix \n\t\t absdev pixel error relative to fit: {1:.5f} pix \n\t\t median pixel error relative to zero: {2:.5f} \n\t\t stddev applied correction: {3:.5f} pix \n\t\t med applied correction: {4:.5f} \n\t\t Nth FP peak at center of order: {5:.5f}'
item.arguments = 'None'
item.comment = 'prints the stats for getting the peak offset value'
langlist.add(item)

# =============================================================================
# 40-014-00021 
# =============================================================================
item = langlist.create('40-014-00021', kind='all-code')
item.value['ENG'] = 'Update of the big dx map after filtering of pre-order dx: {0}/{1}'
item.arguments = 'None'
item.comment = 'prints that we are updating the dx map after filtering'
langlist.add(item)

# =============================================================================
# 40-014-00022 
# =============================================================================
item = langlist.create('40-014-00022', kind='all-code')
item.value['ENG'] = '\tData along slice. Start={0} End={1}'
item.arguments = 'None'
item.comment = 'prints the good starting and end points along the slice'
langlist.add(item)

# =============================================================================
# 40-014-00023 
# =============================================================================
item = langlist.create('40-014-00023', kind='all-code')
item.value['ENG'] = 'Creating DY map from localisation'
item.arguments = 'None'
item.comment = 'prints that we are creating the dy map'
langlist.add(item)

# =============================================================================
# 40-014-00024 
# =============================================================================
item = langlist.create('40-014-00024', kind='all-code')
item.value['ENG'] = 'Loading localisation for fiber = {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading the localisation for fiber'
langlist.add(item)

# =============================================================================
# 40-014-00025 
# =============================================================================
item = langlist.create('40-014-00025', kind='all-code')
item.value['ENG'] = 'Shape map-making complete. Applying transforms.'
item.arguments = 'None'
item.comment = 'prints that we are done with shape map making and are now applying transforms'
langlist.add(item)

# =============================================================================
# 40-014-00026 
# =============================================================================
item = langlist.create('40-014-00026', kind='all-code')
item.value['ENG'] = 'Saving shape x information in file: {0}'
item.arguments = 'None'
item.comment = 'print that we are writing the dxmap to file'
langlist.add(item)

# =============================================================================
# 40-014-00027 
# =============================================================================
item = langlist.create('40-014-00027', kind='all-code')
item.value['ENG'] = 'Saving shape y information in file: {0}'
item.arguments = 'None'
item.comment = 'print that we are writing the dymap to file'
langlist.add(item)

# =============================================================================
# 40-014-00028 
# =============================================================================
item = langlist.create('40-014-00028', kind='all-code')
item.value['ENG'] = 'Saving reference FP file: {0}'
item.arguments = 'None'
item.comment = 'print that we are writing the reference_fp to file'
langlist.add(item)

# =============================================================================
# 40-014-00029 
# =============================================================================
item = langlist.create('40-014-00029', kind='all-code')
item.value['ENG'] = 'Saving shape debug files'
item.arguments = 'None'
item.comment = 'print that we are writing shape debug files'
langlist.add(item)

# =============================================================================
# 40-014-00030 
# =============================================================================
item = langlist.create('40-014-00030', kind='all-code')
item.value['ENG'] = 'Reading reference FP file: {0}'
item.arguments = 'None'
item.comment = 'prints which reference fp file we are using'
langlist.add(item)

# =============================================================================
# 40-014-00031 
# =============================================================================
item = langlist.create('40-014-00031', kind='all-code')
item.value['ENG'] = 'Reading shape dxmap file: {0}'
item.arguments = 'None'
item.comment = 'prints which shape dxmap file we are using'
langlist.add(item)

# =============================================================================
# 40-014-00032 
# =============================================================================
item = langlist.create('40-014-00032', kind='all-code')
item.value['ENG'] = 'Reading shape dymap file: {0}'
item.arguments = 'None'
item.comment = 'prints which shape dymap file we are using'
langlist.add(item)

# =============================================================================
# 40-014-00033 
# =============================================================================
item = langlist.create('40-014-00033', kind='all-code')
item.value['ENG'] = 'Calculating transformation of image onto reference FP'
item.arguments = 'None'
item.comment = 'prints that we are transforming image onto reference fp'
langlist.add(item)

# =============================================================================
# 40-014-00034 
# =============================================================================
item = langlist.create('40-014-00034', kind='all-code')
item.value['ENG'] = 'FP Image quality too poor (sigma clip failed)'
item.arguments = 'None'
item.comment = 'prints that the QC failed because image quliaty was too poor (transform=None)'
langlist.add(item)

# =============================================================================
# 40-014-00035 
# =============================================================================
item = langlist.create('40-014-00035', kind='all-code')
item.value['ENG'] = 'x-residuals too high {0} > {1}'
item.arguments = 'None'
item.comment = 'prints that the QC failed because XRES was too high'
langlist.add(item)

# =============================================================================
# 40-014-00036 
# =============================================================================
item = langlist.create('40-014-00036', kind='all-code')
item.value['ENG'] = 'y-residuals too high {0} > {1}'
item.arguments = 'None'
item.comment = 'prints that the QC failed because YRES was too high'
langlist.add(item)

# =============================================================================
# 40-014-00037 
# =============================================================================
item = langlist.create('40-014-00037', kind='all-code')
item.value['ENG'] = 'Saving shape transforms in file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are writing the shape transforms to file'
langlist.add(item)

# =============================================================================
# 40-014-00038 
# =============================================================================
item = langlist.create('40-014-00038', kind='all-code')
item.value['ENG'] = 'Calibrating file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are calibration a pp file'
langlist.add(item)

# =============================================================================
# 40-014-00039 
# =============================================================================
item = langlist.create('40-014-00039', kind='all-code')
item.value['ENG'] = 'Reading night shape file: {0}'
item.arguments = 'None'
item.comment = 'prints which shape local file we are using'
langlist.add(item)

# =============================================================================
# 40-014-00040 
# =============================================================================
item = langlist.create('40-014-00040', kind='warning_4-code')
item.value['ENG'] = '\t No UNe lines found for order {0}'
item.arguments = 'None'
item.comment = 'prints that no Une lines were found for this order'
langlist.add(item)

# =============================================================================
# 40-014-00041 
# =============================================================================
item = langlist.create('40-014-00041', kind='all-code')
item.value['ENG'] = '\tTransforming (dxmap={0}, dymap={1}, trans={2})'
item.arguments = 'None'
item.comment = 'prints how we are transforming image'
langlist.add(item)

# =============================================================================
# 40-014-00042 
# =============================================================================
item = langlist.create('40-014-00042', kind='all-code')
item.value['ENG'] = 'dx-ddx rms (Order {0}) too high: {1} > {2})'
item.arguments = 'None'
item.comment = 'prints that QC failed for order for dx rms'
langlist.add(item)

# =============================================================================
# 40-014-00043 
# =============================================================================
item = langlist.create('40-014-00043', kind='all-code')
item.value['ENG'] = 'Validating FP file: {0}'
item.arguments = 'None'
item.comment = 'Means that we are validating FP file'
langlist.add(item)

# =============================================================================
# 40-015-00001 
# =============================================================================
item = langlist.create('40-015-00001', kind='all-code')
item.value['ENG'] = 'On fiber {0} order {1}: S/N= {2:.1f}  - FF rms={3:.2f} %'
item.arguments = 'None'
item.comment = 'prints the extracted orders S/N and flat field rms'
langlist.add(item)

# =============================================================================
# 40-015-00002 
# =============================================================================
item = langlist.create('40-015-00002', kind='all-code')
item.value['ENG'] = 'Fiber {0} Abnormal RMS of FF ({1:.3f} > {2:.3f})'
item.arguments = 'None'
item.comment = 'prints that an abnormal rms of the flat field was found'
langlist.add(item)

# =============================================================================
# 40-015-00003 
# =============================================================================
item = langlist.create('40-015-00003', kind='all-code')
item.value['ENG'] = 'Saving blaze file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving blaze to file'
langlist.add(item)

# =============================================================================
# 40-015-00004 
# =============================================================================
item = langlist.create('40-015-00004', kind='all-code')
item.value['ENG'] = 'Saving flat file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving flat to file'
langlist.add(item)

# =============================================================================
# 40-015-00005 
# =============================================================================
item = langlist.create('40-015-00005', kind='all-code')
item.value['ENG'] = 'Saving E2DSLL file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving e2dsll to file'
langlist.add(item)

# =============================================================================
# 40-015-00006 
# =============================================================================
item = langlist.create('40-015-00006', kind='all-code')
item.value['ENG'] = 'Reading flat dymap file: {0}'
item.arguments = 'None'
item.comment = 'prints which flat dymap file we are using'
langlist.add(item)

# =============================================================================
# 40-015-00007 
# =============================================================================
item = langlist.create('40-015-00007', kind='all-code')
item.value['ENG'] = 'Reading blaze dymap file: {0}'
item.arguments = 'None'
item.comment = 'prints which blaze dymap file we are using'
langlist.add(item)

# =============================================================================
# 40-015-00008 
# =============================================================================
item = langlist.create('40-015-00008', kind='all-code')
item.value['ENG'] = 'Fiber {0}: Max RMS was greater than expected. {1} > limit ({2})'
item.arguments = 'None'
item.comment = 'prints that ff_rms failed QC'
langlist.add(item)

# =============================================================================
# 40-015-00009 
# =============================================================================
item = langlist.create('40-015-00009', kind='all-code')
item.value['ENG'] = 'Error fitting sinc to blaze. Order = {0} Fiber = {1} Iteration = {2} \n\t Guess: {3} \n\t Lower: {4} \n\t Upper: {5} \n\t Error {6}: {7} \n\t Function = {8}'
item.arguments = 'None'
item.comment = 'prints that the sinc fitting failed'
langlist.add(item)

# =============================================================================
# 40-016-00001 
# =============================================================================
item = langlist.create('40-016-00001', kind='all-code')
item.value['ENG'] = 'On fiber {0} order {1}: S/N= {2:.1f} Nbcosmic= {3}'
item.arguments = 'None'
item.comment = 'prints the extracted orders S/N and number of cosmic rays'
langlist.add(item)

# =============================================================================
# 40-016-00002 
# =============================================================================
item = langlist.create('40-016-00002', kind='all-code')
item.value['ENG'] = 'On fiber {0} order {1}: S/N= {2:.1f}'
item.arguments = 'None'
item.comment = 'prints the extracted orders S/N'
langlist.add(item)

# =============================================================================
# 40-016-00003 
# =============================================================================
item = langlist.create('40-016-00003', kind='all-code')
item.value['ENG'] = 'Straightening Order Profile fiber = {0}'
item.arguments = 'None'
item.comment = 'prints that we are straightening order profiles for fiber'
langlist.add(item)

# =============================================================================
# 40-016-00004 
# =============================================================================
item = langlist.create('40-016-00004', kind='all-code')
item.value['ENG'] = 'Straightening Image'
item.arguments = 'None'
item.comment = 'prints that we are straightening image '
langlist.add(item)

# =============================================================================
# 40-016-00005 
# =============================================================================
item = langlist.create('40-016-00005', kind='all-code')
item.value['ENG'] = 'Saving E2DS file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the e2ds to file'
langlist.add(item)

# =============================================================================
# 40-016-00006 
# =============================================================================
item = langlist.create('40-016-00006', kind='all-code')
item.value['ENG'] = 'Saving E2DSFF file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the e2dsff to file'
langlist.add(item)

# =============================================================================
# 40-016-00007 
# =============================================================================
item = langlist.create('40-016-00007', kind='all-code')
item.value['ENG'] = 'Saving E2DSLL file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the e2dsll to file'
langlist.add(item)

# =============================================================================
# 40-016-00008 
# =============================================================================
item = langlist.create('40-016-00008', kind='all-code')
item.value['ENG'] = 'E2DS image is all NaNs'
item.arguments = 'None'
item.comment = 'prints that E2DS was all NaNs'
langlist.add(item)

# =============================================================================
# 40-016-00009 
# =============================================================================
item = langlist.create('40-016-00009', kind='all-code')
item.value['ENG'] = 'Calculating S1D ({0})'
item.arguments = 'None'
item.comment = 'prints that we are creating the s1d and for which wavegrid type'
langlist.add(item)

# =============================================================================
# 40-016-00010 
# =============================================================================
item = langlist.create('40-016-00010', kind='all-code')
item.value['ENG'] = 'Saving S1D ({0}) file: {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving the s1d file'
langlist.add(item)

# =============================================================================
# 40-016-00011 
# =============================================================================
item = langlist.create('40-016-00011', kind='all-code')
item.value['ENG'] = 'Extracting straightened image'
item.arguments = 'None'
item.comment = 'prints that we are extracting straightened image'
langlist.add(item)

# =============================================================================
# 40-016-00012 
# =============================================================================
item = langlist.create('40-016-00012', kind='all-code')
item.value['ENG'] = 'Correcting thermal for fiber type = {0} (mode={1})'
item.arguments = 'None'
item.comment = 'prints that we are correcting thermal'
langlist.add(item)

# =============================================================================
# 40-016-00013 
# =============================================================================
item = langlist.create('40-016-00013', kind='all-code')
item.value['ENG'] = 'Not correcting thermal for fiber type = {0}'
item.arguments = 'None'
item.comment = 'prints that we are not correcting thermal'
langlist.add(item)

# =============================================================================
# 40-016-00014 
# =============================================================================
item = langlist.create('40-016-00014', kind='all-code')
item.value['ENG'] = 'Processing fiber {0} of [{1}]'
item.arguments = 'None'
item.comment = 'prints the process which fiber we are processing now'
langlist.add(item)

# =============================================================================
# 40-016-00015 
# =============================================================================
item = langlist.create('40-016-00015', kind='all-code')
item.value['ENG'] = 'Querying Gaia using {0}'
item.arguments = 'None'
item.comment = 'prints that we are querying gaia using gaiaid or objname or ra/dec'
langlist.add(item)

# =============================================================================
# 40-016-00016 
# =============================================================================
item = langlist.create('40-016-00016', kind='all-code')
item.value['ENG'] = 'Using positional parameters from {0}'
item.arguments = 'None'
item.comment = 'prints that we are using parameters from source'
langlist.add(item)

# =============================================================================
# 40-016-00017 
# =============================================================================
item = langlist.create('40-016-00017', kind='all-code')
item.value['ENG'] = 'Calculating Barycentric Corrections'
item.arguments = 'None'
item.comment = 'prints that we are calculating the BERV'
langlist.add(item)

# =============================================================================
# 40-016-00018 
# =============================================================================
item = langlist.create('40-016-00018', kind='all-code')
item.value['ENG'] = '\t Skipping Barycentric correction (type={0})'
item.arguments = 'None'
item.comment = 'prints that we have skipped BERV calculation (dprtype wrong)'
langlist.add(item)

# =============================================================================
# 40-016-00019 
# =============================================================================
item = langlist.create('40-016-00019', kind='all-code')
item.value['ENG'] = '\t Skipping Barycentric correction (Turned off by user)'
item.arguments = 'None'
item.comment = 'prints that we have skipped BERV calculation (turned off)'
langlist.add(item)

# =============================================================================
# 40-016-00020 
# =============================================================================
item = langlist.create('40-016-00020', kind='all-code')
item.value['ENG'] = '\t Obtained BERV values from header'
item.arguments = 'None'
item.comment = 'prints that we have got BERV parameters from header'
langlist.add(item)

# =============================================================================
# 40-016-00021 
# =============================================================================
item = langlist.create('40-016-00021', kind='all-code')
item.value['ENG'] = 'Found and reading extracted file {0}'
item.arguments = 'None'
item.comment = 'prints that we found extracted file and we are reading it from file'
langlist.add(item)

# =============================================================================
# 40-016-00022 
# =============================================================================
item = langlist.create('40-016-00022', kind='all-code')
item.value['ENG'] = 'Saving Thermal file {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving thermal files'
langlist.add(item)

# =============================================================================
# 40-016-00023 
# =============================================================================
item = langlist.create('40-016-00023', kind='all-code')
item.value['ENG'] = 'Successfully extracted file {0}'
item.arguments = 'None'
item.comment = 'prints that we extracted file and are pushing in back into code'
langlist.add(item)

# =============================================================================
# 40-016-00024 
# =============================================================================
item = langlist.create('40-016-00024', kind='all-code')
item.value['ENG'] = 'Correcting leakage in reference for files: \n\t {0}'
item.arguments = 'None'
item.comment = 'prints that we are correcting the dark fp in leak reference'
langlist.add(item)

# =============================================================================
# 40-016-00025 
# =============================================================================
item = langlist.create('40-016-00025', kind='all-code')
item.value['ENG'] = 'Saving leak reference fiber \'{0}\': {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving leak reference file for fiber'
langlist.add(item)

# =============================================================================
# 40-016-00026 
# =============================================================================
item = langlist.create('40-016-00026', kind='all-code')
item.value['ENG'] = 'Quality control for fiber \'{0}\''
item.arguments = 'None'
item.comment = 'prints that we are doing QC for a specific fiber'
langlist.add(item)

# =============================================================================
# 40-016-00027 
# =============================================================================
item = langlist.create('40-016-00027', kind='all-code')
item.value['ENG'] = 'Reading thermal file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading the thermal file'
langlist.add(item)

# =============================================================================
# 40-016-00028 
# =============================================================================
item = langlist.create('40-016-00028', kind='all-code')
item.value['ENG'] = 'Reading leak reference file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading the leak reference file'
langlist.add(item)

# =============================================================================
# 40-016-00029 
# =============================================================================
item = langlist.create('40-016-00029', kind='all-code')
item.value['ENG'] = 'Correcting extracted file fiber=\'{0}\' filetype=\'{1}\''
item.arguments = 'None'
item.comment = 'prints that we are correcting extracted file for fiber'
langlist.add(item)

# =============================================================================
# 40-016-00030 
# =============================================================================
item = langlist.create('40-016-00030', kind='all-code')
item.value['ENG'] = 'Saving leak-corrected extracted file fiber=\'{0}\' filetype=\'{1} file: {2}'
item.arguments = 'None'
item.comment = 'prints that we are saving leak corrected extracted file for fiber'
langlist.add(item)

# =============================================================================
# 40-016-00031 
# =============================================================================
item = langlist.create('40-016-00031', kind='all-code')
item.value['ENG'] = 'Saving leak-corrected S1D ({1}) fiber=\'{0}\' file: {2}'
item.arguments = 'None'
item.comment = 'prints that we are saving leak corrected s1d file for fiber'
langlist.add(item)

# =============================================================================
# 40-016-00032 
# =============================================================================
item = langlist.create('40-016-00032', kind='all-code')
item.value['ENG'] = 'File identified as {0} (OBJ={1})'
item.arguments = 'None'
item.comment = 'prints that we found a file of dprtype / objname'
langlist.add(item)

# =============================================================================
# 40-016-00033 
# =============================================================================
item = langlist.create('40-016-00033', kind='all-code')
item.value['ENG'] = 'Correcting FP leakage for fiber={0} dprtype={1}'
item.arguments = 'None'
item.comment = 'Means we are correcting thermal'
langlist.add(item)

# =============================================================================
# 40-016-00034 
# =============================================================================
item = langlist.create('40-016-00034', kind='all-code')
item.value['ENG'] = 'Not correcting FP leakage: {0}'
item.arguments = 'None'
item.comment = 'Means we are not correcting thermal'
langlist.add(item)

# =============================================================================
# 40-016-00035 
# =============================================================================
item = langlist.create('40-016-00035', kind='all-code')
item.value['ENG'] = 'Identified object as {0} with BERV = {1:.4f} km/s'
item.arguments = 'None'
item.comment = 'prints that we identified object and found a  berv measurement'
langlist.add(item)

# =============================================================================
# 40-017-00001 
# =============================================================================
item = langlist.create('40-017-00001', kind='all-code')
item.value['ENG'] = 'Read line list from file {0}'
item.arguments = 'None'
item.comment = 'prints that line list was read correctly'
langlist.add(item)

# =============================================================================
# 40-017-00002 
# =============================================================================
item = langlist.create('40-017-00002', kind='all-code')
item.value['ENG'] = 'Wave solution fit degree ({0}) consistent with requirements.'
item.arguments = 'None'
item.comment = 'prints that wave solution fit degrees are consistent'
langlist.add(item)

# =============================================================================
# 40-017-00003 
# =============================================================================
item = langlist.create('40-017-00003', kind='all-code')
item.value['ENG'] = 'Calculating initial Gaussian peaks for HC wave solution'
item.arguments = 'None'
item.comment = 'prints that we are calculating initial hc gauss peaks'
langlist.add(item)

# =============================================================================
# 40-017-00004 
# =============================================================================
item = langlist.create('40-017-00004', kind='all-code')
item.value['ENG'] = '\tProcessing order {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are processing order N of M'
langlist.add(item)

# =============================================================================
# 40-017-00005 
# =============================================================================
item = langlist.create('40-017-00005', kind='all-code')
item.value['ENG'] = '\t\tNumber of peaks found = {0}'
item.arguments = 'None'
item.comment = 'prints the number of initial HC gaussian peaks found'
langlist.add(item)

# =============================================================================
# 40-017-00006 
# =============================================================================
item = langlist.create('40-017-00006', kind='all-code')
item.value['ENG'] = 'Writing HC line-list to file {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving hc line-list to file'
langlist.add(item)

# =============================================================================
# 40-017-00007 
# =============================================================================
item = langlist.create('40-017-00007', kind='all-code')
item.value['ENG'] = 'Fit Triplet {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are running triplet N of M'
langlist.add(item)

# =============================================================================
# 40-017-00008 
# =============================================================================
item = langlist.create('40-017-00008', kind='all-code')
item.value['ENG'] = '\t Order {0}: Number of valid lines = {1} / {2}'
item.arguments = 'None'
item.comment = 'prints the number of valid lines found'
langlist.add(item)

# =============================================================================
# 40-017-00009 
# =============================================================================
item = langlist.create('40-017-00009', kind='all-code')
item.value['ENG'] = '\t{0} | RMS={1:.5f} km/s sig={2:.5f} m/s n={3}'
item.arguments = 'None'
item.comment = 'prints the stats for the triplet fit'
langlist.add(item)

# =============================================================================
# 40-017-00010 
# =============================================================================
item = langlist.create('40-017-00010', kind='all-code')
item.value['ENG'] = 'Generating resolution map and calculating line spread function'
item.arguments = 'None'
item.comment = 'prints that we are generating resolution map and line spread function'
langlist.add(item)

# =============================================================================
# 40-017-00011 
# =============================================================================
item = langlist.create('40-017-00011', kind='all-code')
item.value['ENG'] = '\t Orders {0} = {1}: nlines={2} xpos={3} resolution={4:.5f} km/s R={5:.5f}'
item.arguments = 'None'
item.comment = 'prints the stats for the resolution map'
langlist.add(item)

# =============================================================================
# 40-017-00012 
# =============================================================================
item = langlist.create('40-017-00012', kind='all-code')
item.value['ENG'] = 'Mean resolution: {0:.3f} \nMedian resolution: {1:.3f}\nStdDev resolution: {2:.3f}'
item.arguments = 'None'
item.comment = 'prints overall resolution stats'
langlist.add(item)

# =============================================================================
# 40-017-00013 
# =============================================================================
item = langlist.create('40-017-00013', kind='all-code')
item.value['ENG'] = 'Littrow check at X={0} \n\t mean:{1:.3f}[m/s] rms:{2:.3f}[m/s] \n\t min/max:{3:.3f}/{4:.3f} (frac:{5:.3f}/{6:.3f})'
item.arguments = 'None'
item.comment = 'prints the littrow check stats'
langlist.add(item)

# =============================================================================
# 40-017-00014 
# =============================================================================
item = langlist.create('40-017-00014', kind='all-code')
item.value['ENG'] = 'Now running the HC solution, mode = {0}'
item.arguments = 'None'
item.comment = 'prints that we are running HC wave solution and the mode running in'
langlist.add(item)

# =============================================================================
# 40-017-00015 
# =============================================================================
item = langlist.create('40-017-00015', kind='all-code')
item.value['ENG'] = 'Sigma too high ({0:.5f} > {1:.5f})'
item.arguments = 'None'
item.comment = 'the text for the sigma quality control'
langlist.add(item)

# =============================================================================
# 40-017-00016 
# =============================================================================
item = langlist.create('40-017-00016', kind='all-code')
item.value['ENG'] = 'Negative wavelength difference between orders'
item.arguments = 'None'
item.comment = 'the text for the wavelength difference between orders quality control'
langlist.add(item)

# =============================================================================
# 40-017-00017 
# =============================================================================
item = langlist.create('40-017-00017', kind='all-code')
item.value['ENG'] = 'Negative wavelength difference along an order'
item.arguments = 'None'
item.comment = 'the text for the wavelength difference along order quality control'
langlist.add(item)

# =============================================================================
# 40-017-00018 
# =============================================================================
item = langlist.create('40-017-00018', kind='all-code')
item.value['ENG'] = 'On fiber {0} HC fit line statistics: \n\t mean={1:.3f}[m/s] rms={2:.1f} {3} HC lines (error on mean value:{4:.4f}[m/s])'
item.arguments = 'None'
item.comment = 'prints the global hc stats'
langlist.add(item)

# =============================================================================
# 40-017-00019 
# =============================================================================
item = langlist.create('40-017-00019', kind='all-code')
item.value['ENG'] = 'Saving wave solution for fiber {0} (HC) file: {1}'
item.arguments = 'None'
item.comment = 'print that we are saving the wavelength hc file'
langlist.add(item)

# =============================================================================
# 40-017-00020 
# =============================================================================
item = langlist.create('40-017-00020', kind='all-code')
item.value['ENG'] = 'Saving resolution map for fiber {0} (HC) file: {1}'
item.arguments = 'None'
item.comment = 'print that we are saving the resolution map file'
langlist.add(item)

# =============================================================================
# 40-017-00021 
# =============================================================================
item = langlist.create('40-017-00021', kind='all-code')
item.value['ENG'] = 'Now running the FP+HC solution, mode = {0} ({1})'
item.arguments = 'None'
item.comment = 'prints that we are running the wave solution for FP+HC using mode {0}'
langlist.add(item)

# =============================================================================
# 40-017-00022 
# =============================================================================
item = langlist.create('40-017-00022', kind='all-code')
item.value['ENG'] = 'Identification of lines in reference file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are using FP file to calculate FP+HC solution'
langlist.add(item)

# =============================================================================
# 40-017-00023 
# =============================================================================
item = langlist.create('40-017-00023', kind='all-code')
item.value['ENG'] = 'Fit wave. Sol. Order: {0:3d} ({1:2d}) [{2:.1f}-{3:.1f}] \n\t mean: {4:.4f}[mpix] rms={5:.5f} [mpix] ({6:2d} it.) [{7} → {8} lines]'
item.arguments = 'None'
item.comment = 'prints the fp fitted wave solution stats'
langlist.add(item)

# =============================================================================
# 40-017-00024 
# =============================================================================
item = langlist.create('40-017-00024', kind='all-code')
item.value['ENG'] = 'On fiber {0} FP+HC fit line statistic: \n\t mean={1:.3f}[m/s] rms={2:.1f} {3} lines (error on mean value:{4:.2f}[m/s])'
item.arguments = 'None'
item.comment = 'prints the fit line statistics for whole fiber'
langlist.add(item)

# =============================================================================
# 40-017-00025 
# =============================================================================
item = langlist.create('40-017-00025', kind='all-code')
item.value['ENG'] = 'Inversion noise ==> mean={0:.3f}[m/s] rms={1:.1f} (error on mean value:{2:.2f}[m/s])'
item.arguments = 'None'
item.comment = 'prints the inversion stats'
langlist.add(item)

# =============================================================================
# 40-017-00026 
# =============================================================================
item = langlist.create('40-017-00026', kind='all-code')
item.value['ENG'] = 'On fiber {0} mean pixel scale at center: {1:.4f} [km/s/pixel]'
item.arguments = 'None'
item.comment = 'prints the mean pixel scale for fiber after fp fit'
langlist.add(item)

# =============================================================================
# 40-017-00027 
# =============================================================================
item = langlist.create('40-017-00027', kind='all-code')
item.value['ENG'] = 'Mode number span: {0} - {1}'
item.arguments = 'None'
item.comment = 'prints the mode number span'
langlist.add(item)

# =============================================================================
# 40-017-00028 
# =============================================================================
item = langlist.create('40-017-00028', kind='all-code')
item.value['ENG'] = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f}'
item.arguments = 'None'
item.comment = 'prints the fp ccf rv uncertainty'
langlist.add(item)

# =============================================================================
# 40-017-00029 
# =============================================================================
item = langlist.create('40-017-00029', kind='all-code')
item.value['ENG'] = 'FP Correlation: C={0:1f}[%] DRIFT={1:.5f}[km/s] FWHM={2:.4f}[km/s]'
item.arguments = 'None'
item.comment = 'prints the fp correlation stats'
langlist.add(item)

# =============================================================================
# 40-017-00030 
# =============================================================================
item = langlist.create('40-017-00030', kind='all-code')
item.value['ENG'] = 'Negative wavelength difference between orders'
item.arguments = 'None'
item.comment = 'quality control - negative wavelength difference text'
langlist.add(item)

# =============================================================================
# 40-017-00031 
# =============================================================================
item = langlist.create('40-017-00031', kind='all-code')
item.value['ENG'] = 'NaN or Inf in X_MEAN_2'
item.arguments = 'None'
item.comment = 'quality control - nan or inf in x mean 2'
langlist.add(item)

# =============================================================================
# 40-017-00032 
# =============================================================================
item = langlist.create('40-017-00032', kind='all-code')
item.value['ENG'] = 'Littrow test (x={0}) failed (sig littrow = {1:.2f} > {2:.2f})'
item.arguments = 'None'
item.comment = 'Littrow quality control text (sig littrow)'
langlist.add(item)

# =============================================================================
# 40-017-00033 
# =============================================================================
item = langlist.create('40-017-00033', kind='all-code')
item.value['ENG'] = 'Littrow test (x={0}) failed (min|max dev = {1:.2f}|{2:.2f} > {3:.2f} for order {4}|{5})'
item.arguments = 'None'
item.comment = 'Littrow quality control min/max out of bounds'
langlist.add(item)

# =============================================================================
# 40-017-00034 
# =============================================================================
item = langlist.create('40-017-00034', kind='all-code')
item.value['ENG'] = 'Global result summary saved in {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving global wave results'
langlist.add(item)

# =============================================================================
# 40-017-00035 
# =============================================================================
item = langlist.create('40-017-00035', kind='all-code')
item.value['ENG'] = 'List of lines used saved in {0}'
item.arguments = 'None'
item.comment = 'Prints that we are saving hc line list to file'
langlist.add(item)

# =============================================================================
# 40-017-00036 
# =============================================================================
item = langlist.create('40-017-00036', kind='all-code')
item.value['ENG'] = 'Wavelength solution read from {0}.\n\t Wave file = {1}'
item.arguments = 'None'
item.comment = 'Prints the wave file that has been used (and where it came from)'
langlist.add(item)

# =============================================================================
# 40-017-00037 
# =============================================================================
item = langlist.create('40-017-00037', kind='all-code')
item.value['ENG'] = 'Saving wave solution for fiber {0} (FP) file: {1}'
item.arguments = 'None'
item.comment = 'print that we are saving the wavelength fp file'
langlist.add(item)

# =============================================================================
# 40-017-00038 
# =============================================================================
item = langlist.create('40-017-00038', kind='all-code')
item.value['ENG'] = 'Updating {0} file with new wave solution parameters. \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'prints that we are updating file with wave parameters'
langlist.add(item)

# =============================================================================
# 40-017-00039 
# =============================================================================
item = langlist.create('40-017-00039', kind='all-code')
item.value['ENG'] = 'Saving {0} line file: {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving the hc or fp line file'
langlist.add(item)

# =============================================================================
# 40-017-00040 
# =============================================================================
item = langlist.create('40-017-00040', kind='all-code')
item.value['ENG'] = 'Loading reference wave HC/FP line files'
item.arguments = 'None'
item.comment = 'prints that we are loading reference wave line files'
langlist.add(item)

# =============================================================================
# 40-017-00041 
# =============================================================================
item = langlist.create('40-017-00041', kind='all-code')
item.value['ENG'] = 'Order {0}: Median absolute dev: {1:.3f} m/s'
item.arguments = 'None'
item.comment = 'prints the median absolute deviation for order after refitting lines'
langlist.add(item)

# =============================================================================
# 40-017-00042 
# =============================================================================
item = langlist.create('40-017-00042', kind='all-code')
item.value['ENG'] = 'reference wavelenth solution achromatic cavity length change by {0:.4f} nm'
item.arguments = 'None'
item.comment = 'prints the achromatic cavity length change'
langlist.add(item)

# =============================================================================
# 40-017-00043 
# =============================================================================
item = langlist.create('40-017-00043', kind='all-code')
item.value['ENG'] = 'Calculating wavelength solution for fiber \'{0}\' (reference={1})'
item.arguments = 'None'
item.comment = 'prints that we are calculating wave solution for fiber using reference fiber'
langlist.add(item)

# =============================================================================
# 40-017-00044 
# =============================================================================
item = langlist.create('40-017-00044', kind='all-code')
item.value['ENG'] = 'Updating measured wavelength (reference)'
item.arguments = 'None'
item.comment = 'prints that we are updating reference wave list'
langlist.add(item)

# =============================================================================
# 40-017-00045 
# =============================================================================
item = langlist.create('40-017-00045', kind='all-code')
item.value['ENG'] = 'Constructing night line list (night)'
item.arguments = 'None'
item.comment = 'prints that we are constructing night line list'
langlist.add(item)

# =============================================================================
# 40-017-00046 
# =============================================================================
item = langlist.create('40-017-00046', kind='all-code')
item.value['ENG'] = 'Updating measured wavelength (night)'
item.arguments = 'None'
item.comment = 'prints that we are updating wavelength for the night'
langlist.add(item)

# =============================================================================
# 40-017-00047 
# =============================================================================
item = langlist.create('40-017-00047', kind='all-code')
item.value['ENG'] = 'Night wave fit iteration {0} of {1} ({2})'
item.arguments = 'None'
item.comment = 'prints that we are doing wave fit iteration '
langlist.add(item)

# =============================================================================
# 40-017-00048 
# =============================================================================
item = langlist.create('40-017-00048', kind='all-code')
item.value['ENG'] = '\tHC Remove lines: Kept {0}/{1} lines'
item.arguments = 'None'
item.comment = 'prints that we are keep a certain amount of lines'
langlist.add(item)

# =============================================================================
# 40-017-00049 
# =============================================================================
item = langlist.create('40-017-00049', kind='all-code')
item.value['ENG'] = 'Running get reference lines for HC (iteration = {0})'
item.arguments = 'None'
item.comment = 'prints that we are running get ref lines for type HC'
langlist.add(item)

# =============================================================================
# 40-017-00050 
# =============================================================================
item = langlist.create('40-017-00050', kind='all-code')
item.value['ENG'] = 'running get reference lines for FP (iteration = {0})'
item.arguments = 'None'
item.comment = 'prints that we are running get ref lines for type FP'
langlist.add(item)

# =============================================================================
# 40-017-00051 
# =============================================================================
item = langlist.create('40-017-00051', kind='all-code')
item.value['ENG'] = 'Order {0}/{1} Fiber {2} Valid lines: {3}/{4} (type={5})'
item.arguments = 'None'
item.comment = 'prints the number of valid lines found'
langlist.add(item)

# =============================================================================
# 40-017-00052 
# =============================================================================
item = langlist.create('40-017-00052', kind='all-code')
item.value['ENG'] = '\td_cavity = {0:.5f} m/s\tdd_cavity = {1:.5e} m/s'
item.arguments = 'None'
item.comment = 'prints the d_cavity and dd_cavity after iteration'
langlist.add(item)

# =============================================================================
# 40-017-00053 
# =============================================================================
item = langlist.create('40-017-00053', kind='all-code')
item.value['ENG'] = 'Updating smart FP mask file: {0}'
item.arguments = 'None'
item.comment = 'prints that we have updated the smart fp mask'
langlist.add(item)

# =============================================================================
# 40-017-00054 
# =============================================================================
item = langlist.create('40-017-00054', kind='all-code')
item.value['ENG'] = 'Saving wave cavity file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the wave cavity file'
langlist.add(item)

# =============================================================================
# 40-017-00055 
# =============================================================================
item = langlist.create('40-017-00055', kind='all-code')
item.value['ENG'] = 'Negative wavelength difference across orders'
item.arguments = 'None'
item.comment = 'quality control - negative wavelength difference text'
langlist.add(item)

# =============================================================================
# 40-017-00056 
# =============================================================================
item = langlist.create('40-017-00056', kind='all-code')
item.value['ENG'] = 'Measuring the wavelength in order {0}'
item.arguments = 'None'
item.comment = 'print that we are measuring wavelength for this order'
langlist.add(item)

# =============================================================================
# 40-017-00057 
# =============================================================================
item = langlist.create('40-017-00057', kind='all-code')
item.value['ENG'] = 'Iteration {0}: Mean HC position {1:6.2f}+-{2:.2f} m/s'
item.arguments = 'None'
item.comment = 'print the current iteration for getting mean hc position'
langlist.add(item)

# =============================================================================
# 40-017-00058 
# =============================================================================
item = langlist.create('40-017-00058', kind='all-code')
item.value['ENG'] = 'Change in cavity length: {0:6.2f} nm'
item.arguments = 'None'
item.comment = 'print the change in cavity length'
langlist.add(item)

# =============================================================================
# 40-017-00059 
# =============================================================================
item = langlist.create('40-017-00059', kind='all-code')
item.value['ENG'] = 'Processing order bin {0} spectral bin {1}  Number lines: {2} \n\t Orders {3} to {4} Pixels {5} to {6}'
item.arguments = 'None'
item.comment = 'print which order we are processing when generating resolution map'
langlist.add(item)

# =============================================================================
# 40-017-00060 
# =============================================================================
item = langlist.create('40-017-00060', kind='all-code')
item.value['ENG'] = 'FWHM={0:.2f} km/s, effective resolution={1:.2f}, expo={2:.2f}'
item.arguments = 'None'
item.comment = 'print the res map stats'
langlist.add(item)

# =============================================================================
# 40-017-00061 
# =============================================================================
item = langlist.create('40-017-00061', kind='all-code')
item.value['ENG'] = 'Getting reference lines from inputs for HC (iteration = {0})'
item.arguments = 'None'
item.comment = 'prints that we are getting ref HC lines from input'
langlist.add(item)

# =============================================================================
# 40-017-00062 
# =============================================================================
item = langlist.create('40-017-00062', kind='all-code')
item.value['ENG'] = 'Getting reference lines from inputs for FP (iteration = {0})'
item.arguments = 'None'
item.comment = 'prints that we are getting ref FP lines from input'
langlist.add(item)

# =============================================================================
# 40-017-00063 
# =============================================================================
item = langlist.create('40-017-00063', kind='all-code')
item.value['ENG'] = 'Skipped Order {0}'
item.arguments = 'None'
item.comment = 'prints that we are skipping order'
langlist.add(item)

# =============================================================================
# 40-017-00064 
# =============================================================================
item = langlist.create('40-017-00064', kind='all-code')
item.value['ENG'] = 'Applying global fractional offset of wavemap: {0}'
item.arguments = 'None'
item.comment = 'prints that we are applying globale fractino offset of wave map'
langlist.add(item)

# =============================================================================
# 40-017-00065 
# =============================================================================
item = langlist.create('40-017-00065', kind='all-code')
item.value['ENG'] = '\tSkipped Order {0} (too few {1} lines: {2} < {3})'
item.arguments = 'None'
item.comment = 'prints that we are skipping order too few lines'
langlist.add(item)

# =============================================================================
# 40-017-00066 
# =============================================================================
item = langlist.create('40-017-00066', kind='all-code')
item.value['ENG'] = '\tSkipped Order {0} (in removed orders)'
item.arguments = 'None'
item.comment = 'prints that we are skipping order as this is a removed order'
langlist.add(item)

# =============================================================================
# 40-017-00067 
# =============================================================================
item = langlist.create('40-017-00067', kind='all-code')
item.value['ENG'] = 'DV({0} - {1}): {2:.4f} m/s'
item.arguments = 'None'
item.comment = 'prints the dv from wave meas between fibers'
langlist.add(item)

# =============================================================================
# 40-017-00068 
# =============================================================================
item = langlist.create('40-017-00068', kind='all/warning_6-code')
item.value['ENG'] = 'CCFRV[{0} ]- CCFRV[{1}] : {2:.4f} m/s'
item.arguments = 'None'
item.comment = 'prints the ccf rv from wave meas with smart fp mask'
langlist.add(item)

# =============================================================================
# 40-017-00069 
# =============================================================================
item = langlist.create('40-017-00069', kind='all-code')
item.value['ENG'] = '\tVelocity RMS of HC lines relative to catalog: {0:.3f} km/s'
item.arguments = 'None'
item.comment = 'prints the velocity RMS of HC lines relative to catalog'
langlist.add(item)

# =============================================================================
# 40-017-00070 
# =============================================================================
item = langlist.create('40-017-00070', kind='all-code')
item.value['ENG'] = 'Skipping order {0} (velocity RMS of HC lines too high)'
item.arguments = 'None'
item.comment = 'prints that we are skipping order due to high RMS of hc lines'
langlist.add(item)

# =============================================================================
# 40-018-00001 
# =============================================================================
item = langlist.create('40-018-00001', kind='all-code')
item.value['ENG'] = 'Order {0}: {1} peak(s) found, {2} peak(s) rejected'
item.arguments = 'None'
item.comment = 'log how many Fps were found and how many were rejected'
langlist.add(item)

# =============================================================================
# 40-018-00002 
# =============================================================================
item = langlist.create('40-018-00002', kind='all-code')
item.value['ENG'] = 'Total number of FP lines found = {0}'
item.arguments = 'None'
item.comment = 'log the total number of FP lines found'
langlist.add(item)

# =============================================================================
# 40-018-00003 
# =============================================================================
item = langlist.create('40-018-00003', kind='all-code')
item.value['ENG'] = 'Number of lines removed due to suspicious width = {0}'
item.arguments = 'None'
item.comment = 'log the number of lines removed due to suspicious width'
langlist.add(item)

# =============================================================================
# 40-018-00004 
# =============================================================================
item = langlist.create('40-018-00004', kind='all-code')
item.value['ENG'] = 'Number of double-fitted lines remove = {0}'
item.arguments = 'None'
item.comment = 'log the number of lines removed as double-fitted'
langlist.add(item)

# =============================================================================
# 40-018-00005 
# =============================================================================
item = langlist.create('40-018-00005', kind='all-code')
item.value['ENG'] = 'Searching observation directory: ‘{0}’'
item.arguments = 'None'
item.comment = 'print that we are searching spefiic observation directory'
langlist.add(item)

# =============================================================================
# 40-018-00006 
# =============================================================================
item = langlist.create('40-018-00006', kind='all-code')
item.value['ENG'] = 'Processing fiber {0} ({1} of {2})'
item.arguments = 'None'
item.comment = 'prints that we are processing fiber'
langlist.add(item)

# =============================================================================
# 40-018-00007 
# =============================================================================
item = langlist.create('40-018-00007', kind='all-code')
item.value['ENG'] = 'Processing file {0} o f{1}'
item.arguments = 'None'
item.comment = 'prints that we are processing file'
langlist.add(item)

# =============================================================================
# 40-018-00008 
# =============================================================================
item = langlist.create('40-018-00008', kind='all-code')
item.value['ENG'] = 'Writing drift file: {0}'
item.arguments = 'None'
item.comment = 'prints we are writing drift file'
langlist.add(item)

# =============================================================================
# 40-019-00001 
# =============================================================================
item = langlist.create('40-019-00001', kind='all-code')
item.value['ENG'] = 'Loading Tapas convolve file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading the tapas convolve file from file'
langlist.add(item)

# =============================================================================
# 40-019-00002 
# =============================================================================
item = langlist.create('40-019-00002', kind='all-code')
item.value['ENG'] = 'Saving Tapas convolve file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the tapas convolve file for later use'
langlist.add(item)

# =============================================================================
# 40-019-00003 
# =============================================================================
item = langlist.create('40-019-00003', kind='all-code')
item.value['ENG'] = 'No template found in telluric database'
item.arguments = 'None'
item.comment = 'prints that no template was found in database'
langlist.add(item)

# =============================================================================
# 40-019-00004 
# =============================================================================
item = langlist.create('40-019-00004', kind='all-code')
item.value['ENG'] = 'No template found with {0} =’{1}’ in database'
item.arguments = 'None'
item.comment = 'prints that no template was found with objname '
langlist.add(item)

# =============================================================================
# 40-019-00005 
# =============================================================================
item = langlist.create('40-019-00005', kind='all-code')
item.value['ENG'] = 'Using template: {0}'
item.arguments = 'None'
item.comment = 'prints that we found a template and will use it'
langlist.add(item)

# =============================================================================
# 40-019-00006 
# =============================================================================
item = langlist.create('40-019-00006', kind='all-code')
item.value['ENG'] = 'transmission map is all NaNs'
item.arguments = 'None'
item.comment = 'message for quality control that transmission map is all NaNs'
langlist.add(item)

# =============================================================================
# 40-019-00007 
# =============================================================================
item = langlist.create('40-019-00007', kind='all-code')
item.value['ENG'] = 'low SNR in order {0}: ({1:.2f} < {2:.2f})'
item.arguments = 'None'
item.comment = 'message for quality control that low SNR in selected order '
langlist.add(item)

# =============================================================================
# 40-019-00008 
# =============================================================================
item = langlist.create('40-019-00008', kind='all-code')
item.value['ENG'] = 'File {0} did not converge on a solution in telluric absorption calculation'
item.arguments = 'None'
item.comment = 'message for quality control that file did not converge on a solution'
langlist.add(item)

# =============================================================================
# 40-019-00009 
# =============================================================================
item = langlist.create('40-019-00009', kind='all-code')
item.value['ENG'] = 'Recovered airmass too dissimilar to input airmass. \n\t Recovered airmass = {0:.3f}  input: {1:.3f}   qc limit = {2}'
item.arguments = 'None'
item.comment = 'message for quality control that recovered airmass to de-similar'
langlist.add(item)

# =============================================================================
# 40-019-00010 
# =============================================================================
item = langlist.create('40-019-00010', kind='all-code')
item.value['ENG'] = 'Recovered water vapor optical depth not between {0:.3f} and {1:.3f} \n\t Value = {2:.3f}'
item.arguments = 'None'
item.comment = 'message for quality control that recovered water vapor not between limits'
langlist.add(item)

# =============================================================================
# 40-019-00011 
# =============================================================================
item = langlist.create('40-019-00011', kind='all-code')
item.value['ENG'] = 'Saving transmission file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving transmission map to file'
langlist.add(item)

# =============================================================================
# 40-019-00012 
# =============================================================================
item = langlist.create('40-019-00012', kind='all-code')
item.value['ENG'] = 'Loading abso from file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading abso from file'
langlist.add(item)

# =============================================================================
# 40-019-00013 
# =============================================================================
item = langlist.create('40-019-00013', kind='all-code')
item.value['ENG'] = 'Saving abso (npy) file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving abso npy file'
langlist.add(item)

# =============================================================================
# 40-019-00014 
# =============================================================================
item = langlist.create('40-019-00014', kind='all-code')
item.value['ENG'] = 'Skipping trans file due to all NaNs. File = {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing a trans file (due to all NaNs)'
langlist.add(item)

# =============================================================================
# 40-019-00015 
# =============================================================================
item = langlist.create('40-019-00015', kind='all-code')
item.value['ENG'] = 'Fraction of valid pixels (not NaNs) for PCA construction = {0:.3f}'
item.arguments = 'None'
item.comment = 'print the fractino of valid pixels (not NaN) for PCA construction'
langlist.add(item)

# =============================================================================
# 40-019-00016 
# =============================================================================
item = langlist.create('40-019-00016', kind='all-code')
item.value['ENG'] = 'Fraction of valid pixels with residual transmission > exp(-1) = {0:.3f}'
item.arguments = 'None'
item.comment = 'print the fraction of valid pixels with transmission > 1 - 1/e'
langlist.add(item)

# =============================================================================
# 40-019-00017 
# =============================================================================
item = langlist.create('40-019-00017', kind='all-code')
item.value['ENG'] = 'Shifting template to stellar frame (using BERV)'
item.arguments = 'None'
item.comment = 'prints that we are shifting the template to reference grid'
langlist.add(item)

# =============================================================================
# 40-019-00018 
# =============================================================================
item = langlist.create('40-019-00018', kind='all-code')
item.value['ENG'] = 'Shifting PCA components in wave grid \n\t in wave grid = {0} \n\t out wave grid = {1}'
item.arguments = 'None'
item.comment = 'prints that we are shifting the pca components'
langlist.add(item)

# =============================================================================
# 40-019-00019 
# =============================================================================
item = langlist.create('40-019-00019', kind='all-code')
item.value['ENG'] = 'Shifting TAPAS spectrum in wave grid \n\t in wave grid = {0} \n\t out wave grid = {1}'
item.arguments = 'None'
item.comment = 'prints that we are shifting the tapas spectrum'
langlist.add(item)

# =============================================================================
# 40-019-00020 
# =============================================================================
item = langlist.create('40-019-00020', kind='all-code')
item.value['ENG'] = 'Recon calculation iteration {0} of {1}'
item.arguments = 'None'
item.comment = 'print the iteration number we are currently processing when calculating recon'
langlist.add(item)

# =============================================================================
# 40-019-00021 
# =============================================================================
item = langlist.create('40-019-00021', kind='all-code')
item.value['ENG'] = 'Shifting template spectrum in wave grid \n\t in wave grid = {0} \n\t out wave grid = {1}'
item.arguments = 'None'
item.comment = 'print that we are shifting the template'
langlist.add(item)

# =============================================================================
# 40-019-00022 
# =============================================================================
item = langlist.create('40-019-00022', kind='all-code')
item.value['ENG'] = 'Number of pixels to keep in PC fit total = {0}'
item.arguments = 'None'
item.comment = 'prints the number of pixel to keep in the PC fit'
langlist.add(item)

# =============================================================================
# 40-019-00023 
# =============================================================================
item = langlist.create('40-019-00023', kind='all-code')
item.value['ENG'] = 'Saving corrected E2DS file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the corrected e2ds file'
langlist.add(item)

# =============================================================================
# 40-019-00024 
# =============================================================================
item = langlist.create('40-019-00024', kind='all-code')
item.value['ENG'] = 'Saving corrected s1d ({0}) file: {1}'
item.arguments = 'None'
item.comment = 'print that we are saving the s1d corrected file'
langlist.add(item)

# =============================================================================
# 40-019-00025 
# =============================================================================
item = langlist.create('40-019-00025', kind='all-code')
item.value['ENG'] = 'Saving recon E2DS file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the e2ds recon file'
langlist.add(item)

# =============================================================================
# 40-019-00026 
# =============================================================================
item = langlist.create('40-019-00026', kind='all-code')
item.value['ENG'] = 'Saving recon s1d ({0}) file: {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving the s1d recon file'
langlist.add(item)

# =============================================================================
# 40-019-00027 
# =============================================================================
item = langlist.create('40-019-00027', kind='all-code')
item.value['ENG'] = 'Constructing data cubes'
item.arguments = 'None'
item.comment = 'prints that we are constructing cudes'
langlist.add(item)

# =============================================================================
# 40-019-00028 
# =============================================================================
item = langlist.create('40-019-00028', kind='all-code')
item.value['ENG'] = 'Processing {0} file {1} of {2} (bin={3} of {4})'
item.arguments = 'None'
item.comment = 'prints that we are processing template file iteration number'
langlist.add(item)

# =============================================================================
# 40-019-00029 
# =============================================================================
item = langlist.create('40-019-00029', kind='all-code')
item.value['ENG'] = 'Saving median template file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the template file'
langlist.add(item)

# =============================================================================
# 40-019-00030 
# =============================================================================
item = langlist.create('40-019-00030', kind='all-code')
item.value['ENG'] = 'Saving Big Cube: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the big cube file'
langlist.add(item)

# =============================================================================
# 40-019-00031 
# =============================================================================
item = langlist.create('40-019-00031', kind='all-code')
item.value['ENG'] = 'Saving Big Cube 0: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the big cube 0 file'
langlist.add(item)

# =============================================================================
# 40-019-00032 
# =============================================================================
item = langlist.create('40-019-00032', kind='all-code')
item.value['ENG'] = 'Iteration {0}/{1} H20 depth: {2:.4f} Other gases depth: {3:.4f} Airmass: {4:.4f}'
item.arguments = 'None'
item.comment = 'prints the iteration number for calculate_telluric_absorption and some stats'
langlist.add(item)

# =============================================================================
# 40-019-00033 
# =============================================================================
item = langlist.create('40-019-00033', kind='all-code')
item.value['ENG'] = '\tReading file: {0}'
item.arguments = 'None'
item.comment = 'prints the file that we are reading'
langlist.add(item)

# =============================================================================
# 40-019-00034 
# =============================================================================
item = langlist.create('40-019-00034', kind='all-code')
item.value['ENG'] = 'E2DS low f filter iteration {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are looping through low f iterations on e2ds big cube'
langlist.add(item)

# =============================================================================
# 40-019-00035 
# =============================================================================
item = langlist.create('40-019-00035', kind='all-code')
item.value['ENG'] = 'S1D low f filter iteration {0} of {1}'
item.arguments = 'None'
item.comment = 'prints that we are looping through low f iterations on s1d big cube'
langlist.add(item)

# =============================================================================
# 40-019-00036 
# =============================================================================
item = langlist.create('40-019-00036', kind='all-code')
item.value['ENG'] = 'Saving median s1d template file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the s1d template file'
langlist.add(item)

# =============================================================================
# 40-019-00037 
# =============================================================================
item = langlist.create('40-019-00037', kind='all-code')
item.value['ENG'] = 'Saving s1d big cube file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the s1dbig cube file'
langlist.add(item)

# =============================================================================
# 40-019-00038 
# =============================================================================
item = langlist.create('40-019-00038', kind='all-code')
item.value['ENG'] = 'Building {0} template.'
item.arguments = 'None'
item.comment = 'prints which s1d format we are processing'
langlist.add(item)

# =============================================================================
# 40-019-00039 
# =============================================================================
item = langlist.create('40-019-00039', kind='all-code')
item.value['ENG'] = 'Found {0} files of type {1}'
item.arguments = 'None'
item.comment = 'prints how many files were found from the tellu db for key/objnames'
langlist.add(item)

# =============================================================================
# 40-019-00040 
# =============================================================================
item = langlist.create('40-019-00040', kind='all-code')
item.value['ENG'] = 'Pre-cleaning data'
item.arguments = 'None'
item.comment = 'prints that we are doing pre-cleaning'
langlist.add(item)

# =============================================================================
# 40-019-00041 
# =============================================================================
item = langlist.create('40-019-00041', kind='all-code')
item.value['ENG'] = '\titeration={0} dexpo={1:.3e} dv_abso={4:.3f} [m/s]\n\t\texpo_water={2:.3f} expo_others={3:.3f}'
item.arguments = 'None'
item.comment = 'prints the pre-clean iteration loop text'
langlist.add(item)

# =============================================================================
# 40-019-00042 
# =============================================================================
item = langlist.create('40-019-00042', kind='all-code')
item.value['ENG'] = 'Cleaning OH lines'
item.arguments = 'None'
item.comment = 'prints that we are cleaning up OH lines'
langlist.add(item)

# =============================================================================
# 40-019-00043 
# =============================================================================
item = langlist.create('40-019-00043', kind='all-code')
item.value['ENG'] = 'Reading pre-cleaned file from: {0}'
item.arguments = 'None'
item.comment = 'prints that we are reading pre-cleaned file from disk'
langlist.add(item)

# =============================================================================
# 40-019-00044 
# =============================================================================
item = langlist.create('40-019-00044', kind='all-code')
item.value['ENG'] = 'Writing pre-cleaned file to: {0}'
item.arguments = 'None'
item.comment = 'prints that we are writing pre-cleaned file to disk'
langlist.add(item)

# =============================================================================
# 40-019-00045 
# =============================================================================
item = langlist.create('40-019-00045', kind='all-code')
item.value['ENG'] = 'Loading {0} files'
item.arguments = 'None'
item.comment = 'prints that we are loading templates'
langlist.add(item)

# =============================================================================
# 40-019-00046 
# =============================================================================
item = langlist.create('40-019-00046', kind='all-code')
item.value['ENG'] = 'Loading {0} files'
item.arguments = 'None'
item.comment = 'prints that we are loading tramission files'
langlist.add(item)

# =============================================================================
# 40-019-00047 
# =============================================================================
item = langlist.create('40-019-00047', kind='all-code')
item.value['ENG'] = 'Writing tapas file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are writing tapas file'
langlist.add(item)

# =============================================================================
# 40-019-00048 
# =============================================================================
item = langlist.create('40-019-00048', kind='all-code')
item.value['ENG'] = 'File validated: OBJECT={0} DPRTYPE={1}'
item.arguments = 'None'
item.comment = 'prints that we validated file'
langlist.add(item)

# =============================================================================
# 40-019-00049 
# =============================================================================
item = langlist.create('40-019-00049', kind='all-code')
item.value['ENG'] = 'Correcting fiber {0}'
item.arguments = 'None'
item.comment = 'prints that we are telluric correcting fiber'
langlist.add(item)

# =============================================================================
# 40-019-00050 
# =============================================================================
item = langlist.create('40-019-00050', kind='all-code')
item.value['ENG'] = 'Skipping trans file (Header does not contain \'{0}\') \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'prints that trans file is missing required header key'
langlist.add(item)

# =============================================================================
# 40-019-00051 
# =============================================================================
item = langlist.create('40-019-00051', kind='all-code')
item.value['ENG'] = 'Calculated BERV coverage: {0} km/s'
item.arguments = 'None'
item.comment = 'print that the berv coverage is this value'
langlist.add(item)

# =============================================================================
# 40-019-00052 
# =============================================================================
item = langlist.create('40-019-00052', kind='all-code')
item.value['ENG'] = 'OH Cleaning: Num of masked lines = {0}'
item.arguments = 'None'
item.comment = 'prints that we have masked this many oh lines in oh cleaning'
langlist.add(item)

# =============================================================================
# 40-019-00053 
# =============================================================================
item = langlist.create('40-019-00053', kind='all-code')
item.value['ENG'] = 'Saving mk tellu model file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving the mk tellu model file'
langlist.add(item)

# =============================================================================
# 40-019-00054 
# =============================================================================
item = langlist.create('40-019-00054', kind='all-code')
item.value['ENG'] = 'Making transmission cube'
item.arguments = 'None'
item.comment = 'prints that we are making the transmission cube'
langlist.add(item)

# =============================================================================
# 40-019-00055 
# =============================================================================
item = langlist.create('40-019-00055', kind='all-code')
item.value['ENG'] = 'Calculating transmission model'
item.arguments = 'None'
item.comment = 'prints that we are calculating the transmission model'
langlist.add(item)

# =============================================================================
# 40-019-00056 
# =============================================================================
item = langlist.create('40-019-00056', kind='all-code')
item.value['ENG'] = '\tProcessing order {0} / {1}'
item.arguments = 'None'
item.comment = 'prints the order we are processing'
langlist.add(item)

# =============================================================================
# 40-020-00001 
# =============================================================================
item = langlist.create('40-020-00001', kind='all-code')
item.value['ENG'] = 'Computing CCF at Rv={0:6.1f} [km/s]'
item.arguments = 'None'
item.comment = 'prints theat we are computing the ccf'
langlist.add(item)

# =============================================================================
# 40-020-00002 
# =============================================================================
item = langlist.create('40-020-00002', kind='all-code')
item.value['ENG'] = 'Template used for CCF computation: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are loading the CCF file'
langlist.add(item)

# =============================================================================
# 40-020-00003 
# =============================================================================
item = langlist.create('40-020-00003', kind='all-code')
item.value['ENG'] = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f}'
item.arguments = 'None'
item.comment = 'prints the ccf rv uncertainty'
langlist.add(item)

# =============================================================================
# 40-020-00004 
# =============================================================================
item = langlist.create('40-020-00004', kind='all-code')
item.value['ENG'] = 'Correlation: C={0:1f}[%] SYSRV={1:.5f}[km/s] RV_NOISE={2:.5f}[km/s] FWHM={3:.4f}[km/s]'
item.arguments = 'None'
item.comment = 'prints the fp correlation stats'
langlist.add(item)

# =============================================================================
# 40-020-00005 
# =============================================================================
item = langlist.create('40-020-00005', kind='all-code')
item.value['ENG'] = 'Processing CCF fiber {0} for Order {1}'
item.arguments = 'None'
item.comment = 'prints which order we are processing the ccf for'
langlist.add(item)

# =============================================================================
# 40-020-00006 
# =============================================================================
item = langlist.create('40-020-00006', kind='all-code')
item.value['ENG'] = 'Saving CCF {0} file: {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving the ccf fits file to file'
langlist.add(item)

# =============================================================================
# 40-020-00007 
# =============================================================================
item = langlist.create('40-020-00007', kind='all-code')
item.value['ENG'] = 'Computing CCF on fiber {0}'
item.arguments = 'None'
item.comment = 'prints that we are computing CCF on fiber'
langlist.add(item)

# =============================================================================
# 40-020-00008 
# =============================================================================
item = langlist.create('40-020-00008', kind='all-code')
item.value['ENG'] = 'Using object temperature = {0} K for mask identification'
item.arguments = 'None'
item.comment = 'prints that we are using this teff for mask identification'
langlist.add(item)

# =============================================================================
# 40-021-00001 
# =============================================================================
item = langlist.create('40-021-00001', kind='all-code')
item.value['ENG'] = 'Loading polar file {0} \n\t Fiber={1} Stokes={2} Exposure={3} ({4} of {5})'
item.arguments = 'None'
item.comment = 'Prints that we are loading a polar file'
langlist.add(item)

# =============================================================================
# 40-021-00002 
# =============================================================================
item = langlist.create('40-021-00002', kind='all-code')
item.value['ENG'] = 'Running {0} function to calculate polarization'
item.arguments = 'None'
item.comment = 'Prints the function we are using to calculate polarization'
langlist.add(item)

# =============================================================================
# 40-021-00003 
# =============================================================================
item = langlist.create('40-021-00003', kind='all-code')
item.value['ENG'] = 'Calculating Stokes I total flux'
item.arguments = 'None'
item.comment = 'Prints that we are running stokes I total flux calculation'
langlist.add(item)

# =============================================================================
# 40-021-00004 
# =============================================================================
item = langlist.create('40-021-00004', kind='all-code')
item.value['ENG'] = 'Running LSD analysis'
item.arguments = 'None'
item.comment = 'prints that we are running LSD calculation'
langlist.add(item)

# =============================================================================
# 40-021-00005 
# =============================================================================
item = langlist.create('40-021-00005', kind='all-code')
item.value['ENG'] = 'Saving POL file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving pol file'
langlist.add(item)

# =============================================================================
# 40-021-00006 
# =============================================================================
item = langlist.create('40-021-00006', kind='all-code')
item.value['ENG'] = 'Saving NULL1 file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving null1 file'
langlist.add(item)

# =============================================================================
# 40-021-00007 
# =============================================================================
item = langlist.create('40-021-00007', kind='all-code')
item.value['ENG'] = 'Saving NULL2 file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving null2 file'
langlist.add(item)

# =============================================================================
# 40-021-00008 
# =============================================================================
item = langlist.create('40-021-00008', kind='all-code')
item.value['ENG'] = 'Saving Stokes I file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving stokes I file'
langlist.add(item)

# =============================================================================
# 40-021-00009 
# =============================================================================
item = langlist.create('40-021-00009', kind='all-code')
item.value['ENG'] = 'Saving LSD file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving lsd file'
langlist.add(item)

# =============================================================================
# 40-021-00010 
# =============================================================================
item = langlist.create('40-021-00010', kind='all-code')
item.value['ENG'] = 'Saving S1D {0} to file: {1}'
item.arguments = 'None'
item.comment = 'prints that we are saving the s1d to file'
langlist.add(item)

# =============================================================================
# 40-021-00011 
# =============================================================================
item = langlist.create('40-021-00011', kind='all-code')
item.value['ENG'] = 'Mask used for LSD computation: {0}'
item.arguments = 'None'
item.comment = 'prints the mask used for LSD calculation'
langlist.add(item)

# =============================================================================
# 40-021-00012 
# =============================================================================
item = langlist.create('40-021-00012', kind='all-code')
item.value['ENG'] = 'Part 1: loading input data'
item.arguments = 'None'
item.comment = 'prints part 1 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00013 
# =============================================================================
item = langlist.create('40-021-00013', kind='all-code')
item.value['ENG'] = 'Part 2: Run polar analysis'
item.arguments = 'None'
item.comment = 'prints part 2 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00014 
# =============================================================================
item = langlist.create('40-021-00014', kind='all-code')
item.value['ENG'] = 'Part 3: Run continuum analysis'
item.arguments = 'None'
item.comment = 'prints part 3 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00015 
# =============================================================================
item = langlist.create('40-021-00015', kind='all-code')
item.value['ENG'] = 'Part 4: Run LSD Analysis'
item.arguments = 'None'
item.comment = 'prints part 4 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00016 
# =============================================================================
item = langlist.create('40-021-00016', kind='all-code')
item.value['ENG'] = 'Part 5: Quality Control'
item.arguments = 'None'
item.comment = 'prints part 5 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00017 
# =============================================================================
item = langlist.create('40-021-00017', kind='all-code')
item.value['ENG'] = 'Part 6: Making S1D tables'
item.arguments = 'None'
item.comment = 'prints part 6 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00018 
# =============================================================================
item = langlist.create('40-021-00018', kind='all-code')
item.value['ENG'] = 'Part 7: Writing files'
item.arguments = 'None'
item.comment = 'prints part 7 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00019 
# =============================================================================
item = langlist.create('40-021-00019', kind='all-code')
item.value['ENG'] = 'Part 8: plots'
item.arguments = 'None'
item.comment = 'prints part 8 of polar code'
langlist.add(item)

# =============================================================================
# 40-021-00020 
# =============================================================================
item = langlist.create('40-021-00020', kind='all-code')
item.value['ENG'] = 'Exposure {0} in polarimetric mode, setting exposure number {1}'
item.arguments = 'None'
item.comment = 'Print we are setting exposure'
langlist.add(item)

# =============================================================================
# 40-021-00021 
# =============================================================================
item = langlist.create('40-021-00021', kind='all-code')
item.value['ENG'] = 'Setting exposure 1 in polarimetry sequence to {0}'
item.arguments = 'None'
item.comment = 'print that we are setting exposure 1'
langlist.add(item)

# =============================================================================
# 40-021-00022 
# =============================================================================
item = langlist.create('40-021-00022', kind='all-code')
item.value['ENG'] = 'Loading data for {0}'
item.arguments = 'None'
item.comment = 'prints that we are loading data for file'
langlist.add(item)

# =============================================================================
# 40-021-00023 
# =============================================================================
item = langlist.create('40-021-00023', kind='all-code')
item.value['ENG'] = 'Routine {0} ran successfully'
item.arguments = 'None'
item.comment = 'print that polar calculation ran successfully'
langlist.add(item)

# =============================================================================
# 40-021-00024 
# =============================================================================
item = langlist.create('40-021-00024', kind='all-code')
item.value['ENG'] = 'Calculating polarization using {0}'
item.arguments = 'None'
item.comment = 'prints we are calculating polarization using a spefiic method'
langlist.add(item)

# =============================================================================
# 40-021-00025 
# =============================================================================
item = langlist.create('40-021-00025', kind='all-code')
item.value['ENG'] = 'Creating {0} file'
item.arguments = 'None'
item.comment = 'print that we are creating a s1d file'
langlist.add(item)

# =============================================================================
# 40-021-00026 
# =============================================================================
item = langlist.create('40-021-00026', kind='all-code')
item.value['ENG'] = '\tnfit={0}/{1}\n\tfit RMS={2:.3e}'
item.arguments = 'None'
item.comment = 'prints the fit continuum stats'
langlist.add(item)

# =============================================================================
# 40-021-00027 
# =============================================================================
item = langlist.create('40-021-00027', kind='all-code')
item.value['ENG'] = '\tUnfiltered RMS={0:.3e}'
item.arguments = 'None'
item.comment = 'print unfiltered rms value'
langlist.add(item)

# =============================================================================
# 40-021-00028 
# =============================================================================
item = langlist.create('40-021-00028', kind='all-code')
item.value['ENG'] = 'Selected input LSD mask: {0}'
item.arguments = 'None'
item.comment = 'print the selected LSD mask '
langlist.add(item)

# =============================================================================
# 40-021-00029 
# =============================================================================
item = langlist.create('40-021-00029', kind='all-code')
item.value['ENG'] = 'Number of lines in the original mask = {0}'
item.arguments = 'None'
item.comment = 'print the number of lines in original mask'
langlist.add(item)

# =============================================================================
# 40-021-00030 
# =============================================================================
item = langlist.create('40-021-00030', kind='all-code')
item.value['ENG'] = 'Number of lines after filtering = {0}'
item.arguments = 'None'
item.comment = 'print the number of lines after filtering'
langlist.add(item)

# =============================================================================
# 40-021-00031 
# =============================================================================
item = langlist.create('40-021-00031', kind='all-code')
item.value['ENG'] = 'Saving POL_CALIB file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are saving pol_calib file'
langlist.add(item)

# =============================================================================
# 40-090-00001 
# =============================================================================
item = langlist.create('40-090-00001', kind='all-code')
item.value['ENG'] = 'Processing {0}'
item.arguments = 'None'
item.comment = 'prints with post file we are currently generating'
langlist.add(item)

# =============================================================================
# 40-090-00002 
# =============================================================================
item = langlist.create('40-090-00002', kind='all-code')
item.value['ENG'] = 'Writing to file: {0}'
item.arguments = 'None'
item.comment = 'prints we are writing post file'
langlist.add(item)

# =============================================================================
# 40-090-00003 
# =============================================================================
item = langlist.create('40-090-00003', kind='all-code')
item.value['ENG'] = 'Loading full database. OBS_DIR={0}. Please wait...'
item.arguments = 'None'
item.comment = 'prints that we are loading the full database'
langlist.add(item)

# =============================================================================
# 40-090-00004 
# =============================================================================
item = langlist.create('40-090-00004', kind='all-code')
item.value['ENG'] = 'Full database loaded in {0:.4f} s'
item.arguments = 'None'
item.comment = 'prints that the full database was loaded in this amount of time'
langlist.add(item)

# =============================================================================
# 40-090-00005 
# =============================================================================
item = langlist.create('40-090-00005', kind='all-code')
item.value['ENG'] = '\tAdding EXT={0} ({1}) [Header only] mode={2}'
item.arguments = 'None'
item.comment = 'prints that we are adding extension but only the header'
langlist.add(item)

# =============================================================================
# 40-090-00006 
# =============================================================================
item = langlist.create('40-090-00006', kind='all-code')
item.value['ENG'] = '\tAdding EXT={0} ({1}) mode={2}'
item.arguments = 'None'
item.comment = 'prints that we are adding extension'
langlist.add(item)

# =============================================================================
# 40-090-00007 
# =============================================================================
item = langlist.create('40-090-00007', kind='all-code')
item.value['ENG'] = '\t\tFile: {0}'
item.arguments = 'None'
item.comment = 'prints the file we are adding'
langlist.add(item)

# =============================================================================
# 40-090-00008 
# =============================================================================
item = langlist.create('40-090-00008', kind='all-code')
item.value['ENG'] = '\tAdding EXT-{0} ({1}) [TABLE] mode={2}'
item.arguments = 'None'
item.comment = 'prints that we are adding extension (table mode)'
langlist.add(item)

# =============================================================================
# 40-090-00009 
# =============================================================================
item = langlist.create('40-090-00009', kind='all-code')
item.value['ENG'] = 'No errors occurred during recipe run'
item.arguments = 'None'
item.comment = 'report no errors were found'
langlist.add(item)

# =============================================================================
# 40-100-00001 
# =============================================================================
item = langlist.create('40-100-00001', kind='all-code')
item.value['ENG'] = 'Plot loop navigation: Go to \n\t [P]revious plot \n\t [N]ext plot \n\t [E]nd plotting \n\t Number from [0 to {0}]: \t'
item.arguments = 'None'
item.comment = 'The plot loop text'
langlist.add(item)

# =============================================================================
# 40-100-00002 
# =============================================================================
item = langlist.create('40-100-00002', kind='all-code')
item.value['ENG'] = 'Plotting debug plot: {0}'
item.arguments = 'None'
item.comment = 'Plotting debug plot'
langlist.add(item)

# =============================================================================
# 40-100-00003 
# =============================================================================
item = langlist.create('40-100-00003', kind='all-code')
item.value['ENG'] = 'Plotting summary plot: {0}'
item.arguments = 'None'
item.comment = 'Plotting summary plot'
langlist.add(item)

# =============================================================================
# 40-100-00004 
# =============================================================================
item = langlist.create('40-100-00004', kind='all-code')
item.value['ENG'] = 'Creating summary latex document'
item.arguments = 'None'
item.comment = 'Creating summary latex document'
langlist.add(item)

# =============================================================================
# 40-100-00005 
# =============================================================================
item = langlist.create('40-100-00005', kind='all-code')
item.value['ENG'] = 'Creating summary html document'
item.arguments = 'None'
item.comment = 'Creating summary html document'
langlist.add(item)

# =============================================================================
# 40-100-00006 
# =============================================================================
item = langlist.create('40-100-00006', kind='all-code')
item.value['ENG'] = 'Plotting: Must close other plots before a loop debug plot.'
item.arguments = 'None'
item.comment = 'Close plots for loop debug plot'
langlist.add(item)

# =============================================================================
# 40-100-00007 
# =============================================================================
item = langlist.create('40-100-00007', kind='all-code')
item.value['ENG'] = 'Plotting plot: {0}'
item.arguments = 'None'
item.comment = 'Plotting plot'
langlist.add(item)

# =============================================================================
# 40-100-00008 
# =============================================================================
item = langlist.create('40-100-00008', kind='all-code')
item.value['ENG'] = 'Skipping latex compile (DRS_PDFLATEX_PATH not set)'
item.arguments = 'None'
item.comment = 'Means that we are skipping latex plot due to pdflatex path being None'
langlist.add(item)

# =============================================================================
# 40-100-00009 
# =============================================================================
item = langlist.create('40-100-00009', kind='all-code')
item.value['ENG'] = 'Plot loop navigation: \n[L]ist options \nGo to \n\t [P]revious plot \n\t [N]ext plot \n\t [E]nd plotting \n\t Number from [0 to {0}]: \t '
item.arguments = 'None'
item.comment = 'alternate plot loop text (for string lists)'
langlist.add(item)

# =============================================================================
# 40-100-01000 
# =============================================================================
item = langlist.create('40-100-01000', kind='all-code')
item.value['ENG'] = 'Graphs'
item.arguments = 'None'
item.comment = 'text for graph section title'
langlist.add(item)

# =============================================================================
# 40-100-01001 
# =============================================================================
item = langlist.create('40-100-01001', kind='all-code')
item.value['ENG'] = 'This section contains the summary graphs for recipe {0}'
item.arguments = 'None'
item.comment = 'text for graph section text'
langlist.add(item)

# =============================================================================
# 40-100-01002 
# =============================================================================
item = langlist.create('40-100-01002', kind='all-code')
item.value['ENG'] = 'Command used: {0}'
item.arguments = 'None'
item.comment = 'text for quality control command print out'
langlist.add(item)

# =============================================================================
# 40-100-01003 
# =============================================================================
item = langlist.create('40-100-01003', kind='all-code')
item.value['ENG'] = 'Quality Control'
item.arguments = 'None'
item.comment = 'text for quality control section title'
langlist.add(item)

# =============================================================================
# 40-100-01004 
# =============================================================================
item = langlist.create('40-100-01004', kind='all-code')
item.value['ENG'] = 'This section contains a summary of the quality control for recipe {0}. In the table green elements passed the quality control and red failed.'
item.arguments = 'None'
item.comment = 'text for quality control section text'
langlist.add(item)

# =============================================================================
# 40-100-01005 
# =============================================================================
item = langlist.create('40-100-01005', kind='all-code')
item.value['ENG'] = 'Quality control criteria for {0}. Green = PASS, Red = Failed.'
item.arguments = 'None'
item.comment = 'text for quality control caption'
langlist.add(item)

# =============================================================================
# 40-100-01006 
# =============================================================================
item = langlist.create('40-100-01006', kind='all-code')
item.value['ENG'] = 'Summary for {0}: {1}'
item.arguments = 'None'
item.comment = 'text for summary pdf title'
langlist.add(item)

# =============================================================================
# 40-100-01007 
# =============================================================================
item = langlist.create('40-100-01007', kind='all-code')
item.value['ENG'] = 'Figure {0}: {1}'
item.arguments = 'None'
item.comment = 'text for graph mention'
langlist.add(item)

# =============================================================================
# 40-100-01008 
# =============================================================================
item = langlist.create('40-100-01008', kind='all-code')
item.value['ENG'] = 'Statistics and Numbers'
item.arguments = 'None'
item.comment = 'text for stats section title'
langlist.add(item)

# =============================================================================
# 40-100-01009 
# =============================================================================
item = langlist.create('40-100-01009', kind='all-code')
item.value['ENG'] = 'This section contains any important statistics and numbers for recipe {0}.'
item.arguments = 'None'
item.comment = 'text for stats section text'
langlist.add(item)

# =============================================================================
# 40-100-01010 
# =============================================================================
item = langlist.create('40-100-01010', kind='all-code')
item.value['ENG'] = 'Statistics and numbers for {0}'
item.arguments = 'None'
item.comment = 'text for stats caption'
langlist.add(item)

# =============================================================================
# 40-100-01011 
# =============================================================================
item = langlist.create('40-100-01011', kind='all-code')
item.value['ENG'] = 'Warnings'
item.arguments = 'None'
item.comment = 'text for warning section title'
langlist.add(item)

# =============================================================================
# 40-100-01012 
# =============================================================================
item = langlist.create('40-100-01012', kind='all-code')
item.value['ENG'] = 'No quality control parameters defined.'
item.arguments = 'None'
item.comment = 'text for no quality controls'
langlist.add(item)

# =============================================================================
# 40-101-00001 
# =============================================================================
item = langlist.create('40-101-00001', kind='all-code')
item.value['ENG'] = 'Lock: Activated {0}'
item.arguments = 'None'
item.comment = 'Notify user that lock is activated'
langlist.add(item)

# =============================================================================
# 40-101-00002 
# =============================================================================
item = langlist.create('40-101-00002', kind='all-code')
item.value['ENG'] = 'Lock: File added to queue: {0}'
item.arguments = 'None'
item.comment = 'Notify user that lock file added to queue'
langlist.add(item)

# =============================================================================
# 40-101-00003 
# =============================================================================
item = langlist.create('40-101-00003', kind='all-code')
item.value['ENG'] = 'Lock: File unlocked: {0}'
item.arguments = 'None'
item.comment = 'Notify user that lock file is unlocked'
langlist.add(item)

# =============================================================================
# 40-101-00004 
# =============================================================================
item = langlist.create('40-101-00004', kind='all-code')
item.value['ENG'] = 'Lock: File removed from queue: {0}'
item.arguments = 'None'
item.comment = 'Notify user that lock file removed from queue'
langlist.add(item)

# =============================================================================
# 40-101-00005 
# =============================================================================
item = langlist.create('40-101-00005', kind='all-code')
item.value['ENG'] = 'Lock: Deactivated {0}'
item.arguments = 'None'
item.comment = 'Notify user that lock is deactivated'
langlist.add(item)

# =============================================================================
# 40-501-00001 
# =============================================================================
item = langlist.create('40-501-00001', kind='all-code')
item.value['ENG'] = 'Current version is \'{0}\''
item.arguments = 'None'
item.comment = 'print current version'
langlist.add(item)

# =============================================================================
# 40-501-00002 
# =============================================================================
item = langlist.create('40-501-00002', kind='all-code')
item.value['ENG'] = 'New version required?'
item.arguments = 'None'
item.comment = 'ask whether new version required'
langlist.add(item)

# =============================================================================
# 40-501-00003 
# =============================================================================
item = langlist.create('40-501-00003', kind='all-code')
item.value['ENG'] = '\n\tPlease Enter new version:\t'
item.arguments = 'None'
item.comment = 'enter new version'
langlist.add(item)

# =============================================================================
# 40-501-00004 
# =============================================================================
item = langlist.create('40-501-00004', kind='all-code')
item.value['ENG'] = '\n\tPlease Re-Enter new version:\t'
item.arguments = 'None'
item.comment = 'Re-enter new version'
langlist.add(item)

# =============================================================================
# 40-501-00005 
# =============================================================================
item = langlist.create('40-501-00005', kind='all-code')
item.value['ENG'] = 'Versions do not match'
item.arguments = 'None'
item.comment = 'print that versions do not match'
langlist.add(item)

# =============================================================================
# 40-501-00006 
# =============================================================================
item = langlist.create('40-501-00006', kind='all-code')
item.value['ENG'] = 'New version is \'{0}\''
item.arguments = 'None'
item.comment = 'print the new version'
langlist.add(item)

# =============================================================================
# 40-501-00007 
# =============================================================================
item = langlist.create('40-501-00007', kind='all-code')
item.value['ENG'] = '\t\tIs this correct?'
item.arguments = 'None'
item.comment = 'Asks for confirmation about new version'
langlist.add(item)

# =============================================================================
# 40-501-00008 
# =============================================================================
item = langlist.create('40-501-00008', kind='all-code')
item.value['ENG'] = 'Running in preview mode'
item.arguments = 'None'
item.comment = 'prints that we are reading drs version'
langlist.add(item)

# =============================================================================
# 40-501-00009 
# =============================================================================
item = langlist.create('40-501-00009', kind='all-code')
item.value['ENG'] = 'Reading DRS version'
item.arguments = 'None'
item.comment = 'informs user if we are running in preview mode'
langlist.add(item)

# =============================================================================
# 40-501-00010 
# =============================================================================
item = langlist.create('40-501-00010', kind='all-code')
item.value['ENG'] = 'Updating changelog'
item.arguments = 'None'
item.comment = 'prints that we are updating changelog'
langlist.add(item)

# =============================================================================
# 40-501-00011 
# =============================================================================
item = langlist.create('40-501-00011', kind='all-code')
item.value['ENG'] = 'Keep changes?'
item.arguments = 'None'
item.comment = 'If in preview mode asks if we want to keep changes'
langlist.add(item)

# =============================================================================
# 40-502-00001 
# =============================================================================
item = langlist.create('40-502-00001', kind='all-code')
item.value['ENG'] = '\t Are you sure you wish to reset the {0} directory? \t If you are sure you want to reset type \'yes\''
item.arguments = 'None'
item.comment = 'prints a reset confirmation for specific directory'
langlist.add(item)

# =============================================================================
# 40-502-00002 
# =============================================================================
item = langlist.create('40-502-00002', kind='all-code')
item.value['ENG'] = '\t Reset the {0} directory?\t'
item.arguments = 'None'
item.comment = 'prints the message to prompt user input to reset'
langlist.add(item)

# =============================================================================
# 40-502-00003 
# =============================================================================
item = langlist.create('40-502-00003', kind='all-code')
item.value['ENG'] = '\t Resetting {0} directory'
item.arguments = 'None'
item.comment = 'prints that we are resetting the “directory name” directory'
langlist.add(item)

# =============================================================================
# 40-502-00004 
# =============================================================================
item = langlist.create('40-502-00004', kind='all-code')
item.value['ENG'] = '\t Removing file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing files (if log needed)'
langlist.add(item)

# =============================================================================
# 40-502-00005 
# =============================================================================
item = langlist.create('40-502-00005', kind='warning_2-code')
item.value['ENG'] = '\t Directory {0} does not exist. Should we create it?'
item.arguments = 'None'
item.comment = 'Means that directory does not exist and asks user whether we should create it'
langlist.add(item)

# =============================================================================
# 40-502-00006 
# =============================================================================
item = langlist.create('40-502-00006', kind='all-code')
item.value['ENG'] = '\t Create directory {0}?\t'
item.arguments = 'None'
item.comment = 'prints the message to prompt user to create directory'
langlist.add(item)

# =============================================================================
# 40-502-00007 
# =============================================================================
item = langlist.create('40-502-00007', kind='all-code')
item.value['ENG'] = '\t Adding file: {0} to {1}'
item.arguments = 'None'
item.comment = 'prints that we are adding file to directory (for reset)'
langlist.add(item)

# =============================================================================
# 40-502-00008 
# =============================================================================
item = langlist.create('40-502-00008', kind='all-code')
item.value['ENG'] = '\t Skipping link: {0}'
item.arguments = 'None'
item.comment = 'prints that we are skipping link (subdirs)'
langlist.add(item)

# =============================================================================
# 40-502-00009 
# =============================================================================
item = langlist.create('40-502-00009', kind='all-code')
item.value['ENG'] = '\t Removing file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing file (subdirs)'
langlist.add(item)

# =============================================================================
# 40-502-00010 
# =============================================================================
item = langlist.create('40-502-00010', kind='all-code')
item.value['ENG'] = '\t Removing directory: {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing directory (subdirs)'
langlist.add(item)

# =============================================================================
# 40-502-00011 
# =============================================================================
item = langlist.create('40-502-00011', kind='all-code')
item.value['ENG'] = '\t Empty directory found.'
item.arguments = 'None'
item.comment = 'prints that empty directory was found'
langlist.add(item)

# =============================================================================
# 40-502-00012 
# =============================================================================
item = langlist.create('40-502-00012', kind='all-code')
item.value['ENG'] = '{0} directory:'
item.arguments = 'None'
item.comment = 'prints reset title'
langlist.add(item)

# =============================================================================
# 40-502-00013 
# =============================================================================
item = langlist.create('40-502-00013', kind='all-code')
item.value['ENG'] = '\t Not resetting {0} directory.'
item.arguments = 'None'
item.comment = 'prints that we are not reseting directory'
langlist.add(item)

# =============================================================================
# 40-503-00001 
# =============================================================================
item = langlist.create('40-503-00001', kind='all-code')
item.value['ENG'] = '[{0}] {1} has started (PID = {2})'
item.arguments = 'None'
item.comment = 'Text message to send via email when started'
langlist.add(item)

# =============================================================================
# 40-503-00002 
# =============================================================================
item = langlist.create('40-503-00002', kind='all-code')
item.value['ENG'] = '[{0}] {1} has finished (PID = {2})'
item.arguments = 'None'
item.comment = 'Text message to send via email when finished'
langlist.add(item)

# =============================================================================
# 40-503-00003 
# =============================================================================
item = langlist.create('40-503-00003', kind='all-code')
item.value['ENG'] = '\tScanning directory: {0}'
item.arguments = 'None'
item.comment = 'Logs that we are scanning this nightname directory for raw files'
langlist.add(item)

# =============================================================================
# 40-503-00004 
# =============================================================================
item = langlist.create('40-503-00004', kind='all-code')
item.value['ENG'] = '\nValidating run {0} ({1} of {2})'
item.arguments = 'None'
item.comment = 'Logs that we are checking run'
langlist.add(item)

# =============================================================================
# 40-503-00005 
# =============================================================================
item = langlist.create('40-503-00005', kind='all-code')
item.value['ENG'] = '\t run {0} validated'
item.arguments = 'None'
item.comment = 'Logs that we have validated run'
langlist.add(item)

# =============================================================================
# 40-503-00006 
# =============================================================================
item = langlist.create('40-503-00006', kind='all-code')
item.value['ENG'] = 'Skipped run {0} \n\t {1}'
item.arguments = 'None'
item.comment = 'Logs that we have skipped run'
langlist.add(item)

# =============================================================================
# 40-503-00007 
# =============================================================================
item = langlist.create('40-503-00007', kind='all-code')
item.value['ENG'] = 'User set run to \'False\''
item.arguments = 'None'
item.comment = 'Reason 1 for skip: user set RUN_{0} to False'
langlist.add(item)

# =============================================================================
# 40-503-00008 
# =============================================================================
item = langlist.create('40-503-00008', kind='all-code')
item.value['ENG'] = 'User set skip to \'True\' and file(s) were found \n\t Filename = {0}'
item.arguments = 'None'
item.comment = 'Reason 2 for skip: user set SKIP_{0} to True and files were found'
langlist.add(item)

# =============================================================================
# 40-503-00009 
# =============================================================================
item = langlist.create('40-503-00009', kind='all-code')
item.value['ENG'] = 'Processing sequence \'{0}\''
item.arguments = 'None'
item.comment = 'prints that sequence found'
langlist.add(item)

# =============================================================================
# 40-503-00010 
# =============================================================================
item = langlist.create('40-503-00010', kind='all-code')
item.value['ENG'] = 'Locating raw files'
item.arguments = 'None'
item.comment = 'prints that we are finding raw files'
langlist.add(item)

# =============================================================================
# 40-503-00011 
# =============================================================================
item = langlist.create('40-503-00011', kind='all-code')
item.value['ENG'] = 'Generating run list'
item.arguments = 'None'
item.comment = 'prints that we are generating run list'
langlist.add(item)

# =============================================================================
# 40-503-00012 
# =============================================================================
item = langlist.create('40-503-00012', kind='all-code')
item.value['ENG'] = '\t processing recipe \'{0}\' ({1})'
item.arguments = 'None'
item.comment = 'prints which recipe we are processing'
langlist.add(item)

# =============================================================================
# 40-503-00013 
# =============================================================================
item = langlist.create('40-503-00013', kind='all-code')
item.value['ENG'] = '\t {0}'
item.arguments = 'None'
item.comment = 'prints the run item string'
langlist.add(item)

# =============================================================================
# 40-503-00014 
# =============================================================================
item = langlist.create('40-503-00014', kind='all-code')
item.value['ENG'] = '\t Loading recipe module files...'
item.arguments = 'None'
item.comment = 'prints that we are loading the recipe module files'
langlist.add(item)

# =============================================================================
# 40-503-00015 
# =============================================================================
item = langlist.create('40-503-00015', kind='all-code')
item.value['ENG'] = 'Validating all runs ({0} run ids found)'
item.arguments = 'None'
item.comment = 'prints that we are validating run ids'
langlist.add(item)

# =============================================================================
# 40-503-00016 
# =============================================================================
item = langlist.create('40-503-00016', kind='all-code')
item.value['ENG'] = 'Running with 1 core'
item.arguments = 'None'
item.comment = 'prints that we are running with a single core'
langlist.add(item)

# =============================================================================
# 40-503-00017 
# =============================================================================
item = langlist.create('40-503-00017', kind='all-code')
item.value['ENG'] = 'Running with {0} cores'
item.arguments = 'None'
item.comment = 'prints that we are running with multiple cores'
langlist.add(item)

# =============================================================================
# 40-503-00018 
# =============================================================================
item = langlist.create('40-503-00018', kind='all-code')
item.value['ENG'] = '{0} GROUP {1}/{2} ({3})'
item.arguments = 'None'
item.comment = 'prints that we are handling group N of M'
langlist.add(item)

# =============================================================================
# 40-503-00019 
# =============================================================================
item = langlist.create('40-503-00019', kind='warning_8-code')
item.value['ENG'] = 'Error found for ID=\'{0}\''
item.arguments = 'None'
item.comment = 'prints that we found an error for this ID and we are now printing it'
langlist.add(item)

# =============================================================================
# 40-503-00020 
# =============================================================================
item = langlist.create('40-503-00020', kind='all-code')
item.value['ENG'] = 'ID = {0} \tTime = {1:.3f}'
item.arguments = 'None'
item.comment = 'prints the id and time for a run id'
langlist.add(item)

# =============================================================================
# 40-503-00021 
# =============================================================================
item = langlist.create('40-503-00021', kind='all-code')
item.value['ENG'] = '\t skipping recipe \'{0}\' (RUN_{1}=False)'
item.arguments = 'None'
item.comment = 'prints that we are skipping group due to run=False'
langlist.add(item)

# =============================================================================
# 40-503-00022 
# =============================================================================
item = langlist.create('40-503-00022', kind='all-code')
item.value['ENG'] = 'Continue? [Y]es or [N]o: \t'
item.arguments = 'None'
item.comment = 'the prompt when a warning happens (before processing)'
langlist.add(item)

# =============================================================================
# 40-503-00023 
# =============================================================================
item = langlist.create('40-503-00023', kind='all-code')
item.value['ENG'] = 'Y'
item.arguments = 'None'
item.comment = 'prompt “True” answer (Upper case string)'
langlist.add(item)

# =============================================================================
# 40-503-00024 
# =============================================================================
item = langlist.create('40-503-00024', kind='all-code')
item.value['ENG'] = 'N'
item.arguments = 'None'
item.comment = 'prompt “False” answer (Upper case string)'
langlist.add(item)

# =============================================================================
# 40-503-00025 
# =============================================================================
item = langlist.create('40-503-00025', kind='all-code')
item.value['ENG'] = 'Cumulative time taken = {0:.3f}'
item.arguments = 'None'
item.comment = 'prints total time'
langlist.add(item)

# =============================================================================
# 40-503-00026 
# =============================================================================
item = langlist.create('40-503-00026', kind='all-code')
item.value['ENG'] = '\t\tBlack listing directories: {0}'
item.arguments = 'None'
item.comment = 'prints that we black listed some nights'
langlist.add(item)

# =============================================================================
# 40-503-00027 
# =============================================================================
item = langlist.create('40-503-00027', kind='all-code')
item.value['ENG'] = '\t\tWhite listing directories: {0}'
item.arguments = 'None'
item.comment = 'prints that we white listed somenights'
langlist.add(item)

# =============================================================================
# 40-503-00028 
# =============================================================================
item = langlist.create('40-503-00028', kind='all-code')
item.value['ENG'] = 'Trigger mode: Not enough files to continue. Stopping at recipe = {0}'
item.arguments = 'None'
item.comment = 'prints that we are in trigger mode and have reached the point where we don\'t have enough files to continue'
langlist.add(item)

# =============================================================================
# 40-503-00029 
# =============================================================================
item = langlist.create('40-503-00029', kind='all-code')
item.value['ENG'] = '\t\tPI Names kept: {0}'
item.arguments = 'None'
item.comment = 'prints that we have restricted to certain pi names'
langlist.add(item)

# =============================================================================
# 40-503-00030 
# =============================================================================
item = langlist.create('40-503-00030', kind='all-code')
item.value['ENG'] = 'Whitelisted: {0}'
item.arguments = 'None'
item.comment = 'prints that we white listed a night'
langlist.add(item)

# =============================================================================
# 40-503-00031 
# =============================================================================
item = langlist.create('40-503-00031', kind='all-code')
item.value['ENG'] = 'Blacklisted: {0}'
item.arguments = 'None'
item.comment = 'prints that we black listed a night'
langlist.add(item)

# =============================================================================
# 40-503-00032 
# =============================================================================
item = langlist.create('40-503-00032', kind='all-code')
item.value['ENG'] = 'User set skip to \'True\' and argument previously used'
item.arguments = 'None'
item.comment = 'Reason 3 for skip: user set SKIP_{0} to True and argument was found'
langlist.add(item)

# =============================================================================
# 40-503-00033 
# =============================================================================
item = langlist.create('40-503-00033', kind='all-code')
item.value['ENG'] = 'Actual time taken = {0:.3f}'
item.arguments = 'None'
item.comment = 'prints the actual time taken'
langlist.add(item)

# =============================================================================
# 40-503-00034 
# =============================================================================
item = langlist.create('40-503-00034', kind='all-code')
item.value['ENG'] = 'Speed up: {0:.3f}   (Number of cores = {1})'
item.arguments = 'None'
item.comment = 'prints the speed up (cumulative time / actual time)'
langlist.add(item)

# =============================================================================
# 40-503-00035 
# =============================================================================
item = langlist.create('40-503-00035', kind='all-code')
item.value['ENG'] = 'Calculating which nights have no object files'
item.arguments = 'None'
item.comment = 'prints that we are checking engineering nights'
langlist.add(item)

# =============================================================================
# 40-503-00036 
# =============================================================================
item = langlist.create('40-503-00036', kind='all-code')
item.value['ENG'] = 'Adding condition for rejected odometer codes'
item.arguments = 'None'
item.comment = 'prints that we are adding odometer code check'
langlist.add(item)

# =============================================================================
# 40-503-00037 
# =============================================================================
item = langlist.create('40-503-00037', kind='all-code')
item.value['ENG'] = 'processing recipes for {0} raw data entries'
item.arguments = 'None'
item.comment = 'prints that we are processing recipes for N rows of raw data'
langlist.add(item)

# =============================================================================
# 40-503-00038 
# =============================================================================
item = langlist.create('40-503-00038', kind='all-code')
item.value['ENG'] = '\tAdding recipe {0} to sequence'
item.arguments = 'None'
item.comment = 'prints that we are adding recipe to sequence'
langlist.add(item)

# =============================================================================
# 40-503-00039 
# =============================================================================
item = langlist.create('40-503-00039', kind='all-code')
item.value['ENG'] = 'Updating object database (from google sheets)'
item.arguments = 'None'
item.comment = 'prints that we are updating object database'
langlist.add(item)

# =============================================================================
# 40-503-00040 
# =============================================================================
item = langlist.create('40-503-00040', kind='all-code')
item.value['ENG'] = '\t Adding object: {0}  (gaia id: {1})'
item.arguments = 'None'
item.comment = 'prints the object we are adding to object database'
langlist.add(item)

# =============================================================================
# 40-503-00041 
# =============================================================================
item = langlist.create('40-503-00041', kind='all-code')
item.value['ENG'] = 'Sending {0} mail to {1}'
item.arguments = 'None'
item.comment = 'prints that we are sending mail'
langlist.add(item)

# =============================================================================
# 40-503-00042 
# =============================================================================
item = langlist.create('40-503-00042', kind='all-code')
item.value['ENG'] = '\t\tAdded {0} runs'
item.arguments = 'None'
item.comment = 'print how many runs we are adding'
langlist.add(item)

# =============================================================================
# 40-503-00043 
# =============================================================================
item = langlist.create('40-503-00043', kind='all-code')
item.value['ENG'] = 'Updating database with header fixes'
item.arguments = 'None'
item.comment = 'print that we are updating database with header fixes'
langlist.add(item)

# =============================================================================
# 40-503-00044 
# =============================================================================
item = langlist.create('40-503-00044', kind='all-code')
item.value['ENG'] = 'Updating index database with new {0} files'
item.arguments = 'None'
item.comment = 'print that we are updating index database with block kind'
langlist.add(item)

# =============================================================================
# 40-503-00045 
# =============================================================================
item = langlist.create('40-503-00045', kind='all-code')
item.value['ENG'] = '\t skipping recipe \'{0}\' (RUN_{1} missing from ini file)'
item.arguments = 'None'
item.comment = 'prints that we are skipping group due to run=False'
langlist.add(item)

# =============================================================================
# 40-503-00046 
# =============================================================================
item = langlist.create('40-503-00046', kind='all-code')
item.value['ENG'] = 'Updating reject database (from google sheets)'
item.arguments = 'None'
item.comment = 'prints that we are updating reject database'
langlist.add(item)

# =============================================================================
# 40-503-00047 
# =============================================================================
item = langlist.create('40-503-00047', kind='all-code')
item.value['ENG'] = 'Analysing calibration raw files on disk'
item.arguments = 'None'
item.comment = 'prints that we are analysing calibration raw files on disk'
langlist.add(item)

# =============================================================================
# 40-503-00048 
# =============================================================================
item = langlist.create('40-503-00048', kind='all-code')
item.value['ENG'] = 'Processing observation directory: {0}'
item.arguments = 'None'
item.comment = 'prints that we are processing specific observation directory'
langlist.add(item)

# =============================================================================
# 40-503-00049 
# =============================================================================
item = langlist.create('40-503-00049', kind='all-code')
item.value['ENG'] = 'Minimum number of calibrations found'
item.arguments = 'None'
item.comment = 'prints that minimum number of calibrations were found'
langlist.add(item)

# =============================================================================
# 40-503-00050 
# =============================================================================
item = langlist.create('40-503-00050', kind='all-code')
item.value['ENG'] = 'Analysing telluric and science raw files on disk'
item.arguments = 'None'
item.comment = 'prints that we are analysing telluric and science raw files on disk'
langlist.add(item)

# =============================================================================
# 40-503-00051 
# =============================================================================
item = langlist.create('40-503-00051', kind='all-code')
item.value['ENG'] = '\tFound {0} {1} telluric files'
item.arguments = 'None'
item.comment = 'prints that we found a specific number of a specific telluric file'
langlist.add(item)

# =============================================================================
# 40-503-00052 
# =============================================================================
item = langlist.create('40-503-00052', kind='all-code')
item.value['ENG'] = '\t Found {0} {1} science files'
item.arguments = 'None'
item.comment = 'prints that we found a specific number of a specific science file'
langlist.add(item)

# =============================================================================
# 40-503-00053 
# =============================================================================
item = langlist.create('40-503-00053', kind='all-code')
item.value['ENG'] = 'File check summary'
item.arguments = 'None'
item.comment = 'prints the file check summary title'
langlist.add(item)

# =============================================================================
# 40-503-00054 
# =============================================================================
item = langlist.create('40-503-00054', kind='all-code')
item.value['ENG'] = 'All observation directories passed prechecks.'
item.arguments = 'None'
item.comment = 'prints that all observations directories passed prechecks'
langlist.add(item)

# =============================================================================
# 40-503-00055 
# =============================================================================
item = langlist.create('40-503-00055', kind='all-code')
item.value['ENG'] = 'All other observation directories passed prechecks'
item.arguments = 'None'
item.comment = 'prints that all other observation directories passed prechecks'
langlist.add(item)

# =============================================================================
# 40-503-00056 
# =============================================================================
item = langlist.create('40-503-00056', kind='all-code')
item.value['ENG'] = 'Getting file types for sequence={0}'
item.arguments = 'None'
item.comment = 'prints that we are getting file types for specific sequence'
langlist.add(item)

# =============================================================================
# 40-503-00057 
# =============================================================================
item = langlist.create('40-503-00057', kind='all-code')
item.value['ENG'] = 'Preparing list of unique objects from file index database (N={0})'
item.arguments = 'None'
item.comment = 'prints that we are preparing the list of unique objects from file index database'
langlist.add(item)

# =============================================================================
# 40-503-00058 
# =============================================================================
item = langlist.create('40-503-00058', kind='all-code')
item.value['ENG'] = 'Finding all original names for each unfound object'
item.arguments = 'None'
item.comment = 'prints that we are finding all original names for each unfound object'
langlist.add(item)

# =============================================================================
# 40-503-00059 
# =============================================================================
item = langlist.create('40-503-00059', kind='all-code')
item.value['ENG'] = 'Objects that will use header for astrometrics are:'
item.arguments = 'None'
item.comment = 'prints objects that weren’t found and thus will use headers for astrometrics'
langlist.add(item)

# =============================================================================
# 40-503-00060 
# =============================================================================
item = langlist.create('40-503-00060', kind='all-code')
item.value['ENG'] = '\t All objects found (or in ignore list)!'
item.arguments = 'None'
item.comment = 'prints that all objects were found or in the ignore list'
langlist.add(item)

# =============================================================================
# 40-503-00061 
# =============================================================================
item = langlist.create('40-503-00061', kind='all-code')
item.value['ENG'] = 'Note {0} objects are in the ignore list / ignore aliases'
item.arguments = 'None'
item.comment = 'prints that a certain number of objects were in the ignore list'
langlist.add(item)

# =============================================================================
# 40-503-00062 
# =============================================================================
item = langlist.create('40-503-00062', kind='all-code')
item.value['ENG'] = 'Iteration {0} (Ctrl+C to cancel)'
item.arguments = 'None'
item.comment = 'prints the trigger iteration '
langlist.add(item)

# =============================================================================
# 40-504-00001 
# =============================================================================
item = langlist.create('40-504-00001', kind='all-code')
item.value['ENG'] = 'Removing index file: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are removing an index file'
langlist.add(item)

# =============================================================================
# 40-504-00002 
# =============================================================================
item = langlist.create('40-504-00002', kind='all-code')
item.value['ENG'] = '\tScanning directory: {0}'
item.arguments = 'None'
item.comment = 'Logs that we are scanning this nightname directory for files'
langlist.add(item)

# =============================================================================
# 40-504-00003 
# =============================================================================
item = langlist.create('40-504-00003', kind='all-code')
item.value['ENG'] = 'Reading headers for indexing'
item.arguments = 'None'
item.comment = 'Reading headers'
langlist.add(item)

# =============================================================================
# 40-504-00004 
# =============================================================================
item = langlist.create('40-504-00004', kind='all-code')
item.value['ENG'] = '\tProcessing file {0} of {1}'
item.arguments = 'None'
item.comment = 'Prints the file we are reading (for indexing)'
langlist.add(item)

# =============================================================================
# 40-504-00005 
# =============================================================================
item = langlist.create('40-504-00005', kind='all-code')
item.value['ENG'] = 'Processing night: {0}'
item.arguments = 'None'
item.comment = 'Prints the night name we are processing'
langlist.add(item)

# =============================================================================
# 40-505-00001 
# =============================================================================
item = langlist.create('40-505-00001', kind='all-code')
item.value['ENG'] = 'Processing file {0} of {1}: {2}'
item.arguments = 'None'
item.comment = 'prints the progress sorting through db files'
langlist.add(item)

# =============================================================================
# 40-505-00002 
# =============================================================================
item = langlist.create('40-505-00002', kind='all-code')
item.value['ENG'] = '\t File identified as \'{0}\''
item.arguments = 'None'
item.comment = 'prints that we have identified file as specific type'
langlist.add(item)

# =============================================================================
# 40-505-00003 
# =============================================================================
item = langlist.create('40-505-00003', kind='all-code')
item.value['ENG'] = '\t File skipped (reference prefix=\'{0}\')'
item.arguments = 'None'
item.comment = 'prints that we have skipped a file due to reference prefix'
langlist.add(item)

# =============================================================================
# 40-505-00004 
# =============================================================================
item = langlist.create('40-505-00004', kind='all-code')
item.value['ENG'] = 'Note: reference switch (1 or 0) must be added manually! \n\t Press enter to continue:\t'
item.arguments = 'None'
item.comment = 'prints that references must be added manually'
langlist.add(item)

# =============================================================================
# 40-506-00001 
# =============================================================================
item = langlist.create('40-506-00001', kind='all-code')
item.value['ENG'] = 'Cleaning build directories'
item.arguments = 'None'
item.comment = 'prints that we are cleaning directories'
langlist.add(item)

# =============================================================================
# 40-506-00002 
# =============================================================================
item = langlist.create('40-506-00002', kind='all-code')
item.value['ENG'] = 'Compiling HTML'
item.arguments = 'None'
item.comment = 'prints that we are compling html'
langlist.add(item)

# =============================================================================
# 40-506-00003 
# =============================================================================
item = langlist.create('40-506-00003', kind='all-code')
item.value['ENG'] = '\tRunning make HTML'
item.arguments = 'None'
item.comment = 'prints that we are running make html'
langlist.add(item)

# =============================================================================
# 40-506-00004 
# =============================================================================
item = langlist.create('40-506-00004', kind='all-code')
item.value['ENG'] = 'Compling Latex'
item.arguments = 'None'
item.comment = 'prints that we are compling latex'
langlist.add(item)

# =============================================================================
# 40-506-00005 
# =============================================================================
item = langlist.create('40-506-00005', kind='all-code')
item.value['ENG'] = '\tRunning make latexpdf'
item.arguments = 'None'
item.comment = 'prints that we are running make latex'
langlist.add(item)

# =============================================================================
# 40-506-00006 
# =============================================================================
item = langlist.create('40-506-00006', kind='all-code')
item.value['ENG'] = '\tRunning pdflatex'
item.arguments = 'None'
item.comment = 'prints that we are running pdflatex'
langlist.add(item)

# =============================================================================
# 40-506-00007 
# =============================================================================
item = langlist.create('40-506-00007', kind='all-code')
item.value['ENG'] = 'Removing content of {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing output directory'
langlist.add(item)

# =============================================================================
# 40-506-00008 
# =============================================================================
item = langlist.create('40-506-00008', kind='all-code')
item.value['ENG'] = 'Copying HTML files'
item.arguments = 'None'
item.comment = 'prints that we are copying HTML files'
langlist.add(item)

# =============================================================================
# 40-506-00009 
# =============================================================================
item = langlist.create('40-506-00009', kind='all-code')
item.value['ENG'] = 'Copying PDF'
item.arguments = 'None'
item.comment = 'prints that we are copying PDF'
langlist.add(item)

# =============================================================================
# 40-507-00001 
# =============================================================================
item = langlist.create('40-507-00001', kind='all-code')
item.value['ENG'] = 'csv file saved to: {0}'
item.arguments = 'None'
item.comment = 'print that we are exporting to this file'
langlist.add(item)

# =============================================================================
# 40-507-00002 
# =============================================================================
item = langlist.create('40-507-00002', kind='all-code')
item.value['ENG'] = 'Reading csv file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are reading csv file'
langlist.add(item)

# =============================================================================
# 40-507-00003 
# =============================================================================
item = langlist.create('40-507-00003', kind='all-code')
item.value['ENG'] = 'Deleting database and replacing with csv data'
item.arguments = 'None'
item.comment = 'Prints that we are using join mode = replace'
langlist.add(item)

# =============================================================================
# 40-507-00004 
# =============================================================================
item = langlist.create('40-507-00004', kind='all-code')
item.value['ENG'] = 'Appending csv data to end of database'
item.arguments = 'None'
item.comment = 'Prints that we are using join mode = append'
langlist.add(item)

# =============================================================================
# 40-508-00001 
# =============================================================================
item = langlist.create('40-508-00001', kind='all-code')
item.value['ENG'] = 'Finding observation directories for {0}'
item.arguments = 'None'
item.comment = 'prints that we are finding observation directories'
langlist.add(item)

# =============================================================================
# 40-508-00002 
# =============================================================================
item = langlist.create('40-508-00002', kind='all-code')
item.value['ENG'] = 'Found {0} observation directories'
item.arguments = 'None'
item.comment = 'prints that we found N observation directories'
langlist.add(item)

# =============================================================================
# 40-508-00003 
# =============================================================================
item = langlist.create('40-508-00003', kind='all-code')
item.value['ENG'] = 'Loading log files'
item.arguments = 'None'
item.comment = 'prints that we are loading log files'
langlist.add(item)

# =============================================================================
# 40-508-00004 
# =============================================================================
item = langlist.create('40-508-00004', kind='all-code')
item.value['ENG'] = '\t - Loading {0}'
item.arguments = 'None'
item.comment = 'prints specific log file we are loading'
langlist.add(item)

# =============================================================================
# 40-508-00005 
# =============================================================================
item = langlist.create('40-508-00005', kind='all-code')
item.value['ENG'] = 'Saving reference log to: {0}'
item.arguments = 'None'
item.comment = 'prints saving reference log file'
langlist.add(item)

# =============================================================================
# 40-508-00006 
# =============================================================================
item = langlist.create('40-508-00006', kind='all-code')
item.value['ENG'] = 'Found and filtering by recipe=’{0}’'
item.arguments = 'None'
item.comment = 'prints we found and filter by specific recipe'
langlist.add(item)

# =============================================================================
# 40-508-00007 
# =============================================================================
item = langlist.create('40-508-00007', kind='all-code')
item.value['ENG'] = 'Obtaining individual log files'
item.arguments = 'None'
item.comment = 'prints that we are obtaining individual log files'
langlist.add(item)

# =============================================================================
# 40-508-00008 
# =============================================================================
item = langlist.create('40-508-00008', kind='all-code')
item.value['ENG'] = 'Unique error messages: '
item.arguments = 'None'
item.comment = 'prints unique error messages'
langlist.add(item)

# =============================================================================
# 40-508-00009 
# =============================================================================
item = langlist.create('40-508-00009', kind='all-code')
item.value['ENG'] = 'Unique warning messages:'
item.arguments = 'None'
item.comment = 'prints unique warning messages'
langlist.add(item)

# =============================================================================
# 40-508-00010 
# =============================================================================
item = langlist.create('40-508-00010', kind='all-code')
item.value['ENG'] = '\'Recipe = {0}\''
item.arguments = 'None'
item.comment = 'prints stats (recipe name)'
langlist.add(item)

# =============================================================================
# 40-508-00011 
# =============================================================================
item = langlist.create('40-508-00011', kind='all-code')
item.value['ENG'] = '\t Started  ={0:4d}'
item.arguments = 'None'
item.comment = 'prints stats (started)'
langlist.add(item)

# =============================================================================
# 40-508-00012 
# =============================================================================
item = langlist.create('40-508-00012', kind='all-code')
item.value['ENG'] = '\t passed qc={0:4d}\t failed qc ={1:4d}\t ({2:.2f} %)'
item.arguments = 'None'
item.comment = 'prints stats (qc)'
langlist.add(item)

# =============================================================================
# 40-508-00013 
# =============================================================================
item = langlist.create('40-508-00013', kind='all-code')
item.value['ENG'] = '\t finished ={0:4d}\t unfinished={1:4d}\t ({2:.2f} %)'
item.arguments = 'None'
item.comment = 'prints stats (finished)'
langlist.add(item)

# =============================================================================
# 40-509-00001 
# =============================================================================
item = langlist.create('40-509-00001', kind='all-code')
item.value['ENG'] = 'Loading {0} database…'
item.arguments = 'None'
item.comment = 'prints that we are loading specific database'
langlist.add(item)

# =============================================================================
# 40-509-00002 
# =============================================================================
item = langlist.create('40-509-00002', kind='all-code')
item.value['ENG'] = 'Processing KW_OBJNAME={0}'
item.arguments = 'None'
item.comment = 'prints that we are processing specific object'
langlist.add(item)

# =============================================================================
# 40-509-00003 
# =============================================================================
item = langlist.create('40-509-00003', kind='all-code')
item.value['ENG'] = '\tFound {0} entries'
item.arguments = 'None'
item.comment = 'prints that we found entries'
langlist.add(item)

# =============================================================================
# 40-509-00004 
# =============================================================================
item = langlist.create('40-509-00004', kind='all-code')
item.value['ENG'] = '\tFound no entries'
item.arguments = 'None'
item.comment = 'prints that we found no entries'
langlist.add(item)

# =============================================================================
# 40-509-00005 
# =============================================================================
item = langlist.create('40-509-00005', kind='all-code')
item.value['ENG'] = '\tExcluded {0} files for failing QC'
item.arguments = 'None'
item.comment = 'prints that we excluded this number of files for failing qc'
langlist.add(item)

# =============================================================================
# 40-509-00006 
# =============================================================================
item = langlist.create('40-509-00006', kind='all-code')
item.value['ENG'] = 'Adding outpaths for KW_OBJNAME={0}'
item.arguments = 'None'
item.comment = 'prints that we are adding outputs'
langlist.add(item)

# =============================================================================
# 40-509-00007 
# =============================================================================
item = langlist.create('40-509-00007', kind='all-code')
item.value['ENG'] = '\tAdded {0} outpaths'
item.arguments = 'None'
item.comment = 'prints that we added this many outpaths'
langlist.add(item)

# =============================================================================
# 40-509-00008 
# =============================================================================
item = langlist.create('40-509-00008', kind='all-code')
item.value['ENG'] = 'COPY KW_OBJNAME={0}'
item.arguments = 'None'
item.comment = 'prints that we are copying object'
langlist.add(item)

# =============================================================================
# 40-999-00001 
# =============================================================================
item = langlist.create('40-999-00001', kind='all-code')
item.value['ENG'] = 'Read cavity file from {0}'
item.arguments = 'None'
item.comment = 'Print that we are loading the cavity file'
langlist.add(item)

# =============================================================================
# 40-999-00002 
# =============================================================================
item = langlist.create('40-999-00002', kind='all-code')
item.value['ENG'] = 'Read tapas file from {0}'
item.arguments = 'None'
item.comment = 'Prints that we are loading the tapas file'
langlist.add(item)

# =============================================================================
# 40-999-00003 
# =============================================================================
item = langlist.create('40-999-00003', kind='all-code')
item.value['ENG'] = 'Read gaia lookup table from {0}'
item.arguments = 'None'
item.comment = 'Prints that we are loading the obj list file'
langlist.add(item)

# =============================================================================
# 40-999-00004 
# =============================================================================
item = langlist.create('40-999-00004', kind='all-code')
item.value['ENG'] = 'Combining files. Math = \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are combining files with math'
langlist.add(item)

# =============================================================================
# 90-000-00000 
# =============================================================================
item = langlist.create('90-000-00000', kind='debug-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Debug messages'
langlist.add(item)

# =============================================================================
# 90-000-00001 
# =============================================================================
item = langlist.create('90-000-00001', kind='debug-code')
item.value['ENG'] = 'No recipe name defined starting with empty recipe.'
item.arguments = 'None'
item.comment = 'Prints that we are using an empty recipe'
langlist.add(item)

# =============================================================================
# 90-000-00002 
# =============================================================================
item = langlist.create('90-000-00002', kind='debug-code')
item.value['ENG'] = 'LOCAL COPY key ‘{0}’ = {1}'
item.arguments = 'None'
item.comment = 'Prints the local copy of variables (as debug)'
langlist.add(item)

# =============================================================================
# 90-000-00003 
# =============================================================================
item = langlist.create('90-000-00003', kind='debug-code')
item.value['ENG'] = '\t local variable not copied \n\t Error {0}: {1}'
item.arguments = 'None'
item.comment = 'Prints that we could not copy local variable'
langlist.add(item)

# =============================================================================
# 90-000-00004 
# =============================================================================
item = langlist.create('90-000-00004', kind='debug-code')
item.value['ENG'] = 'In Func: {0}'
item.arguments = 'None'
item.comment = 'Prints the function we are in'
langlist.add(item)

# =============================================================================
# 90-000-00005 
# =============================================================================
item = langlist.create('90-000-00005', kind='debug-code')
item.value['ENG'] = '\t Entered {0} times'
item.arguments = 'None'
item.comment = 'Prints that we have executed a function N times'
langlist.add(item)

# =============================================================================
# 90-001-00000 
# =============================================================================
item = langlist.create('90-001-00000', kind='debug-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Debug Argument messages'
langlist.add(item)

# =============================================================================
# 90-001-00001 
# =============================================================================
item = langlist.create('90-001-00001', kind='debug-code')
item.value['ENG'] = 'Directory found (absolute path): \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we have found the directory via an absolute path'
langlist.add(item)

# =============================================================================
# 90-001-00002 
# =============================================================================
item = langlist.create('90-001-00002', kind='debug-code')
item.value['ENG'] = 'Checking file locations for \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are checking file locations for \'filename\''
langlist.add(item)

# =============================================================================
# 90-001-00003 
# =============================================================================
item = langlist.create('90-001-00003', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File not found=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that Argument file was not found'
langlist.add(item)

# =============================================================================
# 90-001-00004 
# =============================================================================
item = langlist.create('90-001-00004', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File found (full file path)=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that Argument file was found via full filepath'
langlist.add(item)

# =============================================================================
# 90-001-00005 
# =============================================================================
item = langlist.create('90-001-00005', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File found (input file path)=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that Argument file was found via input file path'
langlist.add(item)

# =============================================================================
# 90-001-00006 
# =============================================================================
item = langlist.create('90-001-00006', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File found (full file path + \'.fits\')=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that Argument file was found via full file path + \'.fits\''
langlist.add(item)

# =============================================================================
# 90-001-00007 
# =============================================================================
item = langlist.create('90-001-00007', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File found (input file path + \'.fits\')=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that Argument file was found via input file path + \'.fits\''
langlist.add(item)

# =============================================================================
# 90-001-00008 
# =============================================================================
item = langlist.create('90-001-00008', kind='debug-code')
item.value['ENG'] = 'Checking DrsFile=\'{0}\' filename=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we are checking a specific DrsFile type'
langlist.add(item)

# =============================================================================
# 90-001-00009 
# =============================================================================
item = langlist.create('90-001-00009', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Valid file extension for file=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we have a valid file extension'
langlist.add(item)

# =============================================================================
# 90-001-00010 
# =============================================================================
item = langlist.create('90-001-00010', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Header key \'{1}\' found for file=\'{2}\''
item.arguments = 'None'
item.comment = 'Prints that we found Argument file header key'
langlist.add(item)

# =============================================================================
# 90-001-00011 
# =============================================================================
item = langlist.create('90-001-00011', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Header key \'{1}\' value is incorrect (value=\'{2}\')'
item.arguments = 'None'
item.comment = 'Prints that Argument file header key value is incorrect (defined by file definition)'
langlist.add(item)

# =============================================================================
# 90-001-00012 
# =============================================================================
item = langlist.create('90-001-00012', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Header key \'{1}\' valid for recipe (value=\'{2}\')'
item.arguments = 'None'
item.comment = 'Prints that Argument file header key value is correct (defined by file definition)'
langlist.add(item)

# =============================================================================
# 90-001-00013 
# =============================================================================
item = langlist.create('90-001-00013', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Exclusivity check skipped for first file (type=\'{1}\')'
item.arguments = 'None'
item.comment = 'Prints that Argument exclusivity check was skipped for first file'
langlist.add(item)

# =============================================================================
# 90-001-00014 
# =============================================================================
item = langlist.create('90-001-00014', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File exclusivity maintained. (type=\'{1}\')'
item.arguments = 'None'
item.comment = 'Prints that Argument exclusivity was maintained'
langlist.add(item)

# =============================================================================
# 90-001-00015 
# =============================================================================
item = langlist.create('90-001-00015', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File logic is \'inclusive\' - skipping check.'
item.arguments = 'None'
item.comment = 'Prints that Argument exclusivity logic was \'inclusive\' so we skip check'
langlist.add(item)

# =============================================================================
# 90-001-00016 
# =============================================================================
item = langlist.create('90-001-00016', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': File=\'{1}\' passes all criteria (type=\'{2}\')\n'
item.arguments = 'None'
item.comment = 'Prints that Argument file passes all criteria. Note we want a new line after this debug message (to destinguish arguments/files)'
langlist.add(item)

# =============================================================================
# 90-001-00017 
# =============================================================================
item = langlist.create('90-001-00017', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Directory found (inputdir + path): \'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we have found the directory via an input directory + path'
langlist.add(item)

# =============================================================================
# 90-001-00018 
# =============================================================================
item = langlist.create('90-001-00018', kind='debug-code')
item.value['ENG'] = 'Checking Directory for argument: \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we have entered CheckDirectory action'
langlist.add(item)

# =============================================================================
# 90-001-00019 
# =============================================================================
item = langlist.create('90-001-00019', kind='debug-code')
item.value['ENG'] = 'Checking Files for argument: \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we have entered CheckFiles action'
langlist.add(item)

# =============================================================================
# 90-001-00020 
# =============================================================================
item = langlist.create('90-001-00020', kind='debug-code')
item.value['ENG'] = 'Checking Bools for argument: \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we have entered CheckBool'
langlist.add(item)

# =============================================================================
# 90-001-00021 
# =============================================================================
item = langlist.create('90-001-00021', kind='debug-code')
item.value['ENG'] = 'Argument \'{0}\': Value entered=\'{1}\' value assigned=\'{2}\''
item.arguments = 'None'
item.comment = 'Prints the value CheckBool gave to argument'
langlist.add(item)

# =============================================================================
# 90-001-00022 
# =============================================================================
item = langlist.create('90-001-00022', kind='debug-code')
item.value['ENG'] = 'No matching files for index file = \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that there were no matching files from \'filelist\' in the index file'
langlist.add(item)

# =============================================================================
# 90-001-00023 
# =============================================================================
item = langlist.create('90-001-00023', kind='debug-code')
item.value['ENG'] = 'Found {0} files for index file = \'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we found a number of files in the index file name'
langlist.add(item)

# =============================================================================
# 90-001-00024 
# =============================================================================
item = langlist.create('90-001-00024', kind='debug-code')
item.value['ENG'] = '\t - Found {0} valid files for DrsFileType \'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we found X valid files for DrsFileType Y'
langlist.add(item)

# =============================================================================
# 90-001-00025 
# =============================================================================
item = langlist.create('90-001-00025', kind='debug-code')
item.value['ENG'] = 'Found index file at \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that index file was found'
langlist.add(item)

# =============================================================================
# 90-001-00026 
# =============================================================================
item = langlist.create('90-001-00026', kind='debug-code')
item.value['ENG'] = 'Index file not found at \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that index file was not found'
langlist.add(item)

# =============================================================================
# 90-001-00027 
# =============================================================================
item = langlist.create('90-001-00027', kind='debug-code')
item.value['ENG'] = 'Filtering by key=\'{0}\' for values \'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we are filtering by key for value1 or value2 or value3...'
langlist.add(item)

# =============================================================================
# 90-001-00028 
# =============================================================================
item = langlist.create('90-001-00028', kind='debug-code')
item.value['ENG'] = 'Only using last entry'
item.arguments = 'None'
item.comment = 'Prints that we are only using the last entry'
langlist.add(item)

# =============================================================================
# 90-001-00029 
# =============================================================================
item = langlist.create('90-001-00029', kind='debug-code')
item.value['ENG'] = 'Adding {0} files to group (\'{0}\')'
item.arguments = 'None'
item.comment = 'Prints that we are adding X number of files to the group and the dir/type/exposure number'
langlist.add(item)

# =============================================================================
# 90-001-00030 
# =============================================================================
item = langlist.create('90-001-00030', kind='debug-code')
item.value['ENG'] = 'Cannot identify closest file (no directory match) \n\tTarget=\'{0}\'\tChoices=\'{1}\''
item.arguments = 'None'
item.comment = 'Prints that we could not id closest file (when matching multiple files in trigger)'
langlist.add(item)

# =============================================================================
# 90-001-00031 
# =============================================================================
item = langlist.create('90-001-00031', kind='debug-code')
item.value['ENG'] = 'Setting program name to: \'{0}\''
item.arguments = 'None'
item.comment = 'Prints that we are setting the program name'
langlist.add(item)

# =============================================================================
# 90-001-00032 
# =============================================================================
item = langlist.create('90-001-00032', kind='debug-code')
item.value['ENG'] = 'Setting ipython_return to True'
item.arguments = 'None'
item.comment = 'Prints that we are setting ipython return mode'
langlist.add(item)

# =============================================================================
# 90-001-00033 
# =============================================================================
item = langlist.create('90-001-00033', kind='debug-code')
item.value['ENG'] = 'Setting allow_breakpoints to True'
item.arguments = 'None'
item.comment = 'Prints that we are setting break points mode'
langlist.add(item)

# =============================================================================
# 90-001-00034 
# =============================================================================
item = langlist.create('90-001-00034', kind='debug-code')
item.value['ENG'] = 'Setting mode to quiet'
item.arguments = 'None'
item.comment = 'Prints that we are setting quiet mode'
langlist.add(item)

# =============================================================================
# 90-001-00035 
# =============================================================================
item = langlist.create('90-001-00035', kind='debug-code')
item.value['ENG'] = 'Directory found is not consistent with input path in recipe defintions: {0}'
item.arguments = 'None'
item.comment = 'Prints that directory was found but that it does not conform to input path set in recipe definitions'
langlist.add(item)

# =============================================================================
# 90-002-00000 
# =============================================================================
item = langlist.create('90-002-00000', kind='debug-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Debug Database messages'
langlist.add(item)

# =============================================================================
# 90-002-00001 
# =============================================================================
item = langlist.create('90-002-00001', kind='debug-code')
item.value['ENG'] = 'Copying {0} database file {1} to {2}'
item.arguments = 'None'
item.comment = 'Prints that we are copying database file from input to output'
langlist.add(item)

# =============================================================================
# 90-002-00002 
# =============================================================================
item = langlist.create('90-002-00002', kind='debug-code')
item.value['ENG'] = 'Mode = {0} for function {1}'
item.arguments = 'None'
item.comment = 'Prints which mode we are using for get_key_from_db'
langlist.add(item)

# =============================================================================
# 90-008-00000 
# =============================================================================
item = langlist.create('90-008-00000', kind='debug-code')
item.value['ENG'] = 'Dev Error: File Definition Error'
item.arguments = 'None'
item.comment = 'Debug: File'
langlist.add(item)

# =============================================================================
# 90-008-00001 
# =============================================================================
item = langlist.create('90-008-00001', kind='debug-code')
item.value['ENG'] = 'Get from header: In=\'{0}\' Out=\'{1}\' ({2})'
item.arguments = 'None'
item.comment = 'Prints that we are reading a 2d key and the input/output key used'
langlist.add(item)

# =============================================================================
# 90-008-00002 
# =============================================================================
item = langlist.create('90-008-00002', kind='warning_2-code')
item.value['ENG'] = 'Check table keys. Key={0} not found in filedict.  \n\t file = {1} \n\t Available keys: {2}'
item.arguments = 'None'
item.comment = 'Prints that we checked for a key and could not find it in filedict'
langlist.add(item)

# =============================================================================
# 90-008-00003 
# =============================================================================
item = langlist.create('90-008-00003', kind='debug-code')
item.value['ENG'] = 'Check table keys. Key={0} was found and file valid = {1} \n\t file = {2} \n\t values = {3}'
item.arguments = 'None'
item.comment = 'Prints that we checked for a key and it was found'
langlist.add(item)

# =============================================================================
# 90-008-00004 
# =============================================================================
item = langlist.create('90-008-00004', kind='debug-code')
item.value['ENG'] = 'Check table Filename. Extension= {0} invalid \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'Prints that in check table filename extensions was invalid'
langlist.add(item)

# =============================================================================
# 90-008-00005 
# =============================================================================
item = langlist.create('90-008-00005', kind='debug-code')
item.value['ENG'] = 'Check table Filename. Suffix = {0} invalid \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'Prints that in check table filename suffix was invalid'
langlist.add(item)

# =============================================================================
# 90-008-00006 
# =============================================================================
item = langlist.create('90-008-00006', kind='debug-code')
item.value['ENG'] = 'Check table Filename. No fiber found. Fibers = {0} \n\t Filename = {1}'
item.arguments = 'None'
item.comment = 'Prints that in check table filename fibers were not found'
langlist.add(item)

# =============================================================================
# 90-008-00007 
# =============================================================================
item = langlist.create('90-008-00007', kind='debug-code')
item.value['ENG'] = '\t rvalue={0}\t\tfound={1}'
item.arguments = 'None'
item.comment = 'Prints that we are checking key and the whether found or not'
langlist.add(item)

# =============================================================================
# 90-008-00008 
# =============================================================================
item = langlist.create('90-008-00008', kind='debug-code')
item.value['ENG'] = 'Lock file {0} found. Waiting {1}. Function = {2}'
item.arguments = 'None'
item.comment = 'Prints that we checked lock file and are waiting for it to close'
langlist.add(item)

# =============================================================================
# 90-008-00009 
# =============================================================================
item = langlist.create('90-008-00009', kind='debug-code')
item.value['ENG'] = 'Lock file {0} found. Waiting {1}. \n\t Error {2}: {3} \n\t Function = {4}'
item.arguments = 'None'
item.comment = 'Prints that we checked lock file and exception happened'
langlist.add(item)

# =============================================================================
# 90-008-00010 
# =============================================================================
item = langlist.create('90-008-00010', kind='debug-code')
item.value['ENG'] = 'Reading file {0} \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Prints that we read drs file in function'
langlist.add(item)

# =============================================================================
# 90-008-00011 
# =============================================================================
item = langlist.create('90-008-00011', kind='debug-code')
item.value['ENG'] = 'RecipeLog: Writing file: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are writing recipe log file'
langlist.add(item)

# =============================================================================
# 90-008-00012 
# =============================================================================
item = langlist.create('90-008-00012', kind='debug-code')
item.value['ENG'] = 'RecipeLog: Reading file: {0}'
item.arguments = 'None'
item.comment = 'Prints that we are reading recipe log file'
langlist.add(item)

# =============================================================================
# 90-008-00013 
# =============================================================================
item = langlist.create('90-008-00013', kind='debug-code')
item.value['ENG'] = 'Setting {0}={1} from sys.argv[{2}] ({3})'
item.arguments = 'None'
item.comment = 'Prints that we are setting input dir from sys.argv'
langlist.add(item)

# =============================================================================
# 90-008-00014 
# =============================================================================
item = langlist.create('90-008-00014', kind='debug-code')
item.value['ENG'] = 'Setting {0}={1} from fkwargs[{2}]'
item.arguments = 'None'
item.comment = 'Prints we are setting input dir from fkwarsg (main function call)'
langlist.add(item)

# =============================================================================
# 90-008-00015 
# =============================================================================
item = langlist.create('90-008-00015', kind='debug-code')
item.value['ENG'] = 'Lock is removing empty folder: {0}'
item.arguments = 'None'
item.comment = 'Prints that drs lock is removing empty folder'
langlist.add(item)

# =============================================================================
# 90-010-00000 
# =============================================================================
item = langlist.create('90-010-00000', kind='debug-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Preprocessing messages'
langlist.add(item)

# =============================================================================
# 90-010-00001 
# =============================================================================
item = langlist.create('90-010-00001', kind='debug-code')
item.value['ENG'] = 'ID: Checking {0}'
item.arguments = 'None'
item.comment = 'Prints which drs file we are looking at currently'
langlist.add(item)

# =============================================================================
# 90-011-00000 
# =============================================================================
item = langlist.create('90-011-00000', kind='debug-code')
item.value['ENG'] = '\t'
item.arguments = 'None'
item.comment = 'Dark messages'
langlist.add(item)

# =============================================================================
# 90-016-00001 
# =============================================================================
item = langlist.create('90-016-00001', kind='debug-code')
item.value['ENG'] = 'Gaia crossmatch: parameter \'{0}\' unset. Setting to zero \n\t Function = {1}'
item.arguments = 'None'
item.comment = 'Prints that parameter was unset (in gaia crossmatch) and will be set to zero'
langlist.add(item)

# =============================================================================
# 90-016-00002 
# =============================================================================
item = langlist.create('90-016-00002', kind='debug-code')
item.value['ENG'] = 'Final BERV input parameters: '
item.arguments = 'None'
item.comment = 'prints the final berv input parameters'
langlist.add(item)

# =============================================================================
# 90-016-00003 
# =============================================================================
item = langlist.create('90-016-00003', kind='debug-code')
item.value['ENG'] = 'Skipping FPLINES (Fiber = \'{0}\')'
item.arguments = 'None'
item.comment = 'prints that we are skipping reference fiber FPLINES'
langlist.add(item)

# =============================================================================
# 90-016-00004 
# =============================================================================
item = langlist.create('90-016-00004', kind='debug-code')
item.value['ENG'] = 'Skipping FPLINES (DPRTYPE=\'{0}\')'
item.arguments = 'None'
item.comment = 'prints that we are skipping FPLINES due to DPRTYPE'
langlist.add(item)

# =============================================================================
# 90-017-00001 
# =============================================================================
item = langlist.create('90-017-00001', kind='debug-code')
item.value['ENG'] = 'M difference for order {0}: {1}'
item.arguments = 'None'
item.comment = 'Prints the M difference for order'
langlist.add(item)

# =============================================================================
# 90-019-00001 
# =============================================================================
item = langlist.create('90-019-00001', kind='debug-code')
item.value['ENG'] = 'Can not load abso from file: {0} \n\t Error {1}: {2}'
item.arguments = 'None'
item.comment = 'prints that we could not load abso from file and the reason for this (the error)'
langlist.add(item)

# =============================================================================
# 90-019-00002 
# =============================================================================
item = langlist.create('90-019-00002', kind='debug-code')
item.value['ENG'] = 'Removing old abso (npy) file: {0}'
item.arguments = 'None'
item.comment = 'prints that we are removing an old abso npy file'
langlist.add(item)

# =============================================================================
# 90-100-00001 
# =============================================================================
item = langlist.create('90-100-00001', kind='debug-code')
item.value['ENG'] = 'Plotting: maplotlib backend used = {0}'
item.arguments = 'None'
item.comment = 'Displays the backend that was chosen for plotting'
langlist.add(item)

# =============================================================================
# 90-100-00002 
# =============================================================================
item = langlist.create('90-100-00002', kind='debug-code')
item.value['ENG'] = 'Plotting: plotting skipped (DRS_PLOT = 0)'
item.arguments = 'None'
item.comment = 'Means that plotting was skipped due to drs_plot = 0'
langlist.add(item)

# =============================================================================
# 90-100-00003 
# =============================================================================
item = langlist.create('90-100-00003', kind='debug-code')
item.value['ENG'] = 'Plotting: plotting skipped (PLOT_{0} = False)'
item.arguments = 'None'
item.comment = 'Means that plotting was skipped due to plot switch set to False'
langlist.add(item)

# =============================================================================
# 90-100-00004 
# =============================================================================
item = langlist.create('90-100-00004', kind='debug-code')
item.value['ENG'] = 'Closing plots manually'
item.arguments = 'None'
item.comment = 'Means we are closing plots manually'
langlist.add(item)

# =============================================================================
# 90-100-00005 
# =============================================================================
item = langlist.create('90-100-00005', kind='debug-code')
item.value['ENG'] = 'Closing plots'
item.arguments = 'None'
item.comment = 'Means we are closing plots'
langlist.add(item)

# =============================================================================
# 90-503-00001 
# =============================================================================
item = langlist.create('90-503-00001', kind='debug-code')
item.value['ENG'] = 'Skip Check: Could not find file {0}'
item.arguments = 'None'
item.comment = 'Prints which files were searched for when trying to skip files'
langlist.add(item)

# =============================================================================
# 90-503-00002 
# =============================================================================
item = langlist.create('90-503-00002', kind='debug-code')
item.value['ENG'] = 'Skip Check: \'directory\' argument not found cannot skip'
item.arguments = 'None'
item.comment = 'Prints that we skipped as directory was not found'
langlist.add(item)

# =============================================================================
# 90-503-00003 
# =============================================================================
item = langlist.create('90-503-00003', kind='debug-code')
item.value['ENG'] = 'Skip Check: not skipping as \'REF\' in {0}'
item.arguments = 'None'
item.comment = 'prints that we didn\'t skip as reference was in the skipname'
langlist.add(item)

# =============================================================================
# 90-503-00004 
# =============================================================================
item = langlist.create('90-503-00004', kind='debug-code')
item.value['ENG'] = 'Skip Check: not skipping as {0} = False'
item.arguments = 'None'
item.comment = 'prints that we did not skip as user set skip to False'
langlist.add(item)

# =============================================================================
# 90-503-00005 
# =============================================================================
item = langlist.create('90-503-00005', kind='debug-code')
item.value['ENG'] = 'Skip Check: not skipping as {0} not in params (unset)'
item.arguments = 'None'
item.comment = 'prints that we did not skip as skipname was not in params'
langlist.add(item)

# =============================================================================
# 90-503-00006 
# =============================================================================
item = langlist.create('90-503-00006', kind='debug-code')
item.value['ENG'] = 'Skip Check: keyword \'skip\' found so skipping internally using skip=True'
item.arguments = 'None'
item.comment = 'prints that we found argument \'skip\' and user wanted to skip so we are adding argument skip'
langlist.add(item)

# =============================================================================
# 90-503-00007 
# =============================================================================
item = langlist.create('90-503-00007', kind='debug-code')
item.value['ENG'] = 'Skip Check: keyword \'skip\' found and \'skip\' already set'
item.arguments = 'None'
item.comment = 'prints that we found argument \'skip\' but skip was already set so we are ignoring skipping'
langlist.add(item)

# =============================================================================
# 90-503-00008 
# =============================================================================
item = langlist.create('90-503-00008', kind='debug-code')
item.value['ENG'] = 'Stop at Exception triggered for recipe: {0}'
item.arguments = 'None'
item.comment = 'prints that an exception was found and we are stopping'
langlist.add(item)

# =============================================================================
# 90-503-00009 
# =============================================================================
item = langlist.create('90-503-00009', kind='debug-code')
item.value['ENG'] = 'Stop at Exception skipping group {0}'
item.arguments = 'None'
item.comment = 'prints that we are skipping further jobs due to exception'
langlist.add(item)

# =============================================================================
# 90-503-00010 
# =============================================================================
item = langlist.create('90-503-00010', kind='debug-code')
item.value['ENG'] = 'Skip Check: \n\t recipe = {0} \n\t short name = {1} \n\t run name = {2} \n\t skip name = {3}'
item.arguments = 'None'
item.comment = 'prints the naming info for run object'
langlist.add(item)

# =============================================================================
# 90-503-00011 
# =============================================================================
item = langlist.create('90-503-00011', kind='debug-code')
item.value['ENG'] = 'For {0} using {1} file(s)'
item.arguments = 'None'
item.comment = 'prints the number of files used for find_run_files'
langlist.add(item)

# =============================================================================
# 90-503-00012 
# =============================================================================
item = langlist.create('90-503-00012', kind='debug-code')
item.value['ENG'] = '\tProcessing argument = {0}'
item.arguments = 'None'
item.comment = 'prints the argument we are scanning for files'
langlist.add(item)

# =============================================================================
# 90-503-00013 
# =============================================================================
item = langlist.create('90-503-00013', kind='debug-code')
item.value['ENG'] = '\t\t DrsFile = {0}'
item.arguments = 'None'
item.comment = 'prints the drs file being tested'
langlist.add(item)

# =============================================================================
# 90-503-00014 
# =============================================================================
item = langlist.create('90-503-00014', kind='debug-code')
item.value['ENG'] = '\t\t\t Number of valid files = {0}'
item.arguments = 'None'
item.comment = 'prints the number of valid files left'
langlist.add(item)

# =============================================================================
# 90-503-00015 
# =============================================================================
item = langlist.create('90-503-00015', kind='debug-code')
item.value['ENG'] = 'Finding all non-telluric star objects'
item.arguments = 'None'
item.comment = 'prints that we are finding non-telluric star objects'
langlist.add(item)

# =============================================================================
# 90-503-00016 
# =============================================================================
item = langlist.create('90-503-00016', kind='debug-code')
item.value['ENG'] = '\tFound {0} objects'
item.arguments = 'None'
item.comment = 'prints that we found X non-tellu star objects'
langlist.add(item)

# =============================================================================
# 90-503-00017 
# =============================================================================
item = langlist.create('90-503-00017', kind='debug-code')
item.value['ENG'] = 'Generating skip table'
item.arguments = 'None'
item.comment = 'prints that we are generating skip table'
langlist.add(item)

# =============================================================================
# 90-503-00018 
# =============================================================================
item = langlist.create('90-503-00018', kind='debug-code')
item.value['ENG'] = '\tFound {0} previous recipe runs'
item.arguments = 'None'
item.comment = 'prints that we found X recipe entries'
langlist.add(item)

# =============================================================================
# 90-503-00019 
# =============================================================================
item = langlist.create('90-503-00019', kind='debug-code')
item.value['ENG'] = 'Loaded log file with {0} entries \n\t Filename: {1}'
item.arguments = 'None'
item.comment = 'prints that we loaded a log.fits file with X entries'
langlist.add(item)

# =============================================================================
# 90-503-00020 
# =============================================================================
item = langlist.create('90-503-00020', kind='debug-code')
item.value['ENG'] = '\t Kept {0} entries that successfully finished'
item.arguments = 'None'
item.comment = 'prints how many of the loaded entries in log.fits finished (and can be used)'
langlist.add(item)

# =============================================================================
# 90-503-00021 
# =============================================================================
item = langlist.create('90-503-00021', kind='debug-code')
item.value['ENG'] = 'MULTIPROCESS - joining job {0}'
item.arguments = 'None'
item.comment = 'prints that we are joining multiprocess'
langlist.add(item)

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
