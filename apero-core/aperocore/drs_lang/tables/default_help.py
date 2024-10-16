
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 09:10

@author: cook
"""
from aperocore.base import base
from aperocore.drs_lang import drs_lang_list


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.tables.default_help.py'
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
# DRS_DESCRIPTION 
# =============================================================================
item = langlist.create('DRS_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'This is the default DRS description message'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# KEYERROR 
# =============================================================================
item = langlist.create('KEYERROR', kind='HELP')
item.value['ENG'] = 'Key {0} not found. Function = {1}'
item.value['FR'] = 'Clé {0} introuvable. Fonction = {1}'
item.arguments = 'None'
item.comment = 'This is the default key error'
langlist.add(item)

# =============================================================================
# ADD_CAL_HELP 
# =============================================================================
item = langlist.create('ADD_CAL_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to add outputs to calibration database'
item.value['FR'] = '[BOOLEAN] S\'il faut ajouter des sorties à la base de données d\'étalonnage '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ALLLISTING_HELP 
# =============================================================================
item = langlist.create('ALLLISTING_HELP', kind='HELP')
item.value['ENG'] = 'Lists ALL the night name directories in the input directory if used without a \'directory\' argument or lists the files in the given \'directory\' (if defined)'
item.value['FR'] = 'Répertorie TOUS les répertoires de noms de nuit du répertoire d\'entrée s\'il est utilisé sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# AND_TEXT 
# =============================================================================
item = langlist.create('AND_TEXT', kind='TEXT')
item.value['ENG'] = 'and'
item.value['FR'] = 'et'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_DESCRIPTION 
# =============================================================================
item = langlist.create('ASTROMETRIC_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run this recipe to check, find and/or add targets to the online astrometric database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_OBJ_HELP 
# =============================================================================
item = langlist.create('ASTROMETRIC_OBJ_HELP', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to check, find and/or add to the online database. Should be comma separated without white spaces'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BREAKFUNC_HELP 
# =============================================================================
item = langlist.create('BREAKFUNC_HELP', kind='HELP')
item.value['ENG'] = 'Given a function name will break when this function is found (only if function contains display_func)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BREAKPOINTS_HELP 
# =============================================================================
item = langlist.create('BREAKPOINTS_HELP', kind='HELP')
item.value['ENG'] = 'If set then any breakpoints in the code are executed'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# C_OR 
# =============================================================================
item = langlist.create('C_OR', kind='TEXT')
item.value['ENG'] = 'or'
item.arguments = 'None'
item.comment = 'text for \"or\" logical condition'
langlist.add(item)

# =============================================================================
# C_AND 
# =============================================================================
item = langlist.create('C_AND', kind='TEXT')
item.value['ENG'] = 'and'
item.arguments = 'None'
item.comment = 'text for \"and\" logical condition'
langlist.add(item)

# =============================================================================
# C_NO 
# =============================================================================
item = langlist.create('C_NO', kind='TEXT')
item.value['ENG'] = 'N'
item.value['FR'] = 'N'
item.arguments = 'None'
item.comment = 'character for no'
langlist.add(item)

# =============================================================================
# C_YES 
# =============================================================================
item = langlist.create('C_YES', kind='TEXT')
item.value['ENG'] = 'Y'
item.value['FR'] = 'O'
item.arguments = 'None'
item.comment = 'character for yes'
langlist.add(item)

# =============================================================================
# C_YES_OR_NO 
# =============================================================================
item = langlist.create('C_YES_OR_NO', kind='TEXT')
item.value['ENG'] = '[Y]es or [N]o'
item.value['FR'] = '[O]ui ou [N[on'
item.arguments = 'None'
item.comment = 'question for yes or no characters'
langlist.add(item)

# =============================================================================
# C_OPTIONS_ARE 
# =============================================================================
item = langlist.create('C_OPTIONS_ARE', kind='TEXT')
item.value['ENG'] = 'Options are'
item.arguments = 'None'
item.comment = 'options are text'
langlist.add(item)

# =============================================================================
# C_DEFAULT_IS 
# =============================================================================
item = langlist.create('C_DEFAULT_IS', kind='TEXT')
item.value['ENG'] = 'Default is'
item.arguments = 'None'
item.comment = 'default is text'
langlist.add(item)

# =============================================================================
# CHANGELOG_DESCRIPTION 
# =============================================================================
item = langlist.create('CHANGELOG_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Produces a nicely formatted change log (using git). Requires gitchangelog to be installed via \'pip install gitchangelog\''
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_CSVARG_HELP 
# =============================================================================
item = langlist.create('DBMGR_CSVARG_HELP', kind='TEXT')
item.value['ENG'] = 'Path to csv file. For --importdb this is the csv file you wish to add. For --exportdb this is the csv file that will be saved.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_DESCRIPTION 
# =============================================================================
item = langlist.create('DBMGR_DESCRIPTION', kind='TEXT')
item.value['ENG'] = 'APERO database manager functionality'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_EXPORTDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_EXPORTDB_HELP', kind='TEXT')
item.value['ENG'] = 'Export a database to a csv file'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_IMPORTDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_IMPORTDB_HELP', kind='TEXT')
item.value['ENG'] = 'Import a csv file into a database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_JOIN_HELP 
# =============================================================================
item = langlist.create('DBMGR_JOIN_HELP', kind='TEXT')
item.value['ENG'] = 'How to add the csv file to database: append adds all lines to the end of current database, replace removes all previous lines from database. Default is ‘replace’.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_KILLARG_HELP 
# =============================================================================
item = langlist.create('DBMGR_KILLARG_HELP', kind='TEXT')
item.value['ENG'] = 'Use this when database is stuck and you have no other opens (mysql only)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_UPDATE_HELP 
# =============================================================================
item = langlist.create('DBMGR_UPDATE_HELP', kind='TEXT')
item.value['ENG'] = 'Use this to update the database based on files on disk in the correct directories (Currently updates calib/tellu/log and index databases)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DEBUG_HELP 
# =============================================================================
item = langlist.create('DEBUG_HELP', kind='HELP')
item.value['ENG'] = 'Activates debug mode (Advanced mode [INTEGER] value must be an integer greater than 0, setting the debug level)'
item.value['FR'] = 'Active le mode débogage (la valeur en mode avancé [INTEGER] doit être un entier supérieur à 0, définissant le niveau de débogage)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DEPENDENCIES_DESCRIPTION 
# =============================================================================
item = langlist.create('DEPENDENCIES_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run a dependency check on the DRS (Will display all modules required and some stats)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DESCRIPTION_TEXT 
# =============================================================================
item = langlist.create('DESCRIPTION_TEXT', kind='TEXT')
item.value['ENG'] = ' Description:'
item.value['FR'] = ' La description: '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DIRECTORY_HELP 
# =============================================================================
item = langlist.create('DIRECTORY_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'night_name\' or absolute path of the directory'
item.value['FR'] = '[STRING] Le \'night_name\' ou chemin absolu du répertoire '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXAMPLES_TEXT 
# =============================================================================
item = langlist.create('EXAMPLES_TEXT', kind='TEXT')
item.value['ENG'] = ' Example uses:'
item.value['FR'] = ' Exemple d\'utilisation: '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_DESCRIPTION 
# =============================================================================
item = langlist.create('EXPLORER_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Opens a GUI browser to help one navigate the raw, working and reduced directories. Displays all files and a select set of header keys'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_HASH 
# =============================================================================
item = langlist.create('EXPLORER_HASH', kind='TEXT')
item.value['ENG'] = 'Display all hash columns (hidden by default)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_INST_HEPL 
# =============================================================================
item = langlist.create('EXPLORER_INST_HEPL', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to nagivate'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FILE_HELP 
# =============================================================================
item = langlist.create('FILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] A single fits files. '
item.value['FR'] = '[STRING] Un seul correspond à des fichiers. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FILES_HELP 
# =============================================================================
item = langlist.create('FILES_HELP', kind='HELP')
item.value['ENG'] = '[STRING/STRINGS] A list of fits files to use separated by spaces. '
item.value['FR'] = '[STRING / STRINGS] Liste des fichiers de correspondance à utiliser séparés par des espaces. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FPMODE_HELP 
# =============================================================================
item = langlist.create('FPMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] the mode to calculate the fp+hc wave solution. 0 = following Bauer et al 15 (previously WAVE_E2DS_EA), 1 = following C Lovis (previously WAVE_NEW)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# HCMODE_HELP 
# =============================================================================
item = langlist.create('HCMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] the mode to calculate the hc wave solution. 0 = Etienne method'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INFO_HELP 
# =============================================================================
item = langlist.create('INFO_HELP', kind='HELP')
item.value['ENG'] = 'Displays the short version of the help menu'
item.value['FR'] = 'Affiche la version courte du menu d\'aide'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INTERACTIVE_HELP 
# =============================================================================
item = langlist.create('INTERACTIVE_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to run in interactive mode – 0 to be in non-interactive mode'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# IS_REFERENCE_HELP 
# =============================================================================
item = langlist.create('IS_REFERENCE_HELP', kind='HELP')
item.value['ENG'] = 'If set then recipe is a reference recipe (e.g. reference recipes write to calibration database as reference calibrations)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_DESC 
# =============================================================================
item = langlist.create('LISTING_DESC', kind='HELP')
item.value['ENG'] = 'Rebuilds index files'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP 
# =============================================================================
item = langlist.create('LISTING_HELP', kind='HELP')
item.value['ENG'] = 'Lists the night name directories in the input directory if used without a \'directory\' argument or lists the files in the given \'directory\' (if defined). Only lists up to {0} files/directories'
item.value['FR'] = 'Répertorie les répertoires de noms de nuit dans le répertoire d\'entrée s\'ils sont utilisés sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini). Ne répertorie que jusqu\'à {0} fichiers / répertoires'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_INSTRUMENT 
# =============================================================================
item = langlist.create('LISTING_HELP_INSTRUMENT', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to rebuild for'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_KIND 
# =============================================================================
item = langlist.create('LISTING_HELP_KIND', kind='HELP')
item.value['ENG'] = '[STRING] The kind of indexs to rebuild (i.e. raw, tmp or reduced)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_NIGHTNAME 
# =============================================================================
item = langlist.create('LISTING_HELP_NIGHTNAME', kind='HELP')
item.value['ENG'] = '[STRING] The directory/nightname to rebuild for (default is to do all directories)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_DESC 
# =============================================================================
item = langlist.create('LOGSTAT_DESC', kind='HELP')
item.value['ENG'] = 'Performs a log analysis on the log.fits files generated by recipes'
item.value['FR'] = 'Répertorie les répertoires de noms de nuit dans le répertoire d\'entrée s\'ils sont utilisés sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini). Ne répertorie que jusqu\'à {0} fichiers / répertoires'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# NO_TEXT 
# =============================================================================
item = langlist.create('NO_TEXT', kind='TEXT')
item.value['ENG'] = 'no'
item.value['FR'] = 'non'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OPTIONS_TEXT 
# =============================================================================
item = langlist.create('OPTIONS_TEXT', kind='TEXT')
item.value['ENG'] = ' options'
item.value['FR'] = ' les options '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OR_TEXT 
# =============================================================================
item = langlist.create('OR_TEXT', kind='TEXT')
item.value['ENG'] = 'or'
item.value['FR'] = 'ou'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PLOT_HELP 
# =============================================================================
item = langlist.create('PLOT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file'
item.value['FR'] = '[BOOLEAN] Niveau de graphique. 0 = désactivé, 1 = interactivement, 2 = enregistrer dans un fichier'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# POS_ARG_TEXT 
# =============================================================================
item = langlist.create('POS_ARG_TEXT', kind='TEXT')
item.value['ENG'] = ' positional arguments'
item.value['FR'] = ' arguments de position'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PPSKIP_HELP 
# =============================================================================
item = langlist.create('PPSKIP_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True skips preprocessed files that are already found'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PREVIEW_HELP 
# =============================================================================
item = langlist.create('PREVIEW_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True previews the changelog before making any changes if False makes changes without preview'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_BNIGHTNAMES_HELP 
# =============================================================================
item = langlist.create('PROCESS_BNIGHTNAMES_HELP', kind='HELP')
item.value['ENG'] = '[STRING] List of \'night_name\'s or directories to black list (will not process these directories)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_CORES_HELP 
# =============================================================================
item = langlist.create('PROCESS_CORES_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Number of cores to use in processing'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_DESCRIPTION 
# =============================================================================
item = langlist.create('PROCESS_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Process a night or a set of nights or all nights given some options and a run file'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_FILENAME_HELP 
# =============================================================================
item = langlist.create('PROCESS_FILENAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'filename\' to reprocess (default is None for all files)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_INST_HELP 
# =============================================================================
item = langlist.create('PROCESS_INST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to reprocess'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_NIGHTNAME_HELP 
# =============================================================================
item = langlist.create('PROCESS_NIGHTNAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'night_name\' or directory to reprocess (default is None for all directories)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_RUNFILE_HELP 
# =============================================================================
item = langlist.create('PROCESS_RUNFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run file to use in reprocessing'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_SCI_TARGETS 
# =============================================================================
item = langlist.create('PROCESS_SCI_TARGETS', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to process as science targets (if unsets default to the run.in file) must be separated by a comma and surrounded with speech-marks i.e. \'target1,target2,target3\''
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TELLU_TARGETS 
# =============================================================================
item = langlist.create('PROCESS_TELLU_TARGETS', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to process as telluric targets (if unsets default to the run.in file) must be separated by a commas and surrounded with speech-marks i.e. \'target1,target2,target3\''
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TEST_HELP 
# =============================================================================
item = langlist.create('PROCESS_TEST_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True does not process any files just prints an output of what recipes would be run'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TRIGGER_HELP 
# =============================================================================
item = langlist.create('PROCESS_TRIGGER_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True activates trigger mode (i.e. will stop processing at the first point we do not find required files). Note one must define --night in trigger mode'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_UPDATE_OBJDB 
# =============================================================================
item = langlist.create('PROCESS_UPDATE_OBJDB', kind='HELP')
item.value['ENG'] = 'Update the object database - only recommended if doing a full reprocess with all data.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_WNIGHTNAMES_HELP 
# =============================================================================
item = langlist.create('PROCESS_WNIGHTNAMES_HELP', kind='HELP')
item.value['ENG'] = '[STRING] List of \'night_name\'s or directories to white list (will only process these directories)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# Q_NO 
# =============================================================================
item = langlist.create('Q_NO', kind='TEXT')
item.value['ENG'] = '[N]o'
item.value['FR'] = '[N]on'
item.arguments = 'None'
item.comment = 'Used for input of no'
langlist.add(item)

# =============================================================================
# Q_YES 
# =============================================================================
item = langlist.create('Q_YES', kind='TEXT')
item.value['ENG'] = '[Y]es'
item.value['FR'] = '[O]ui'
item.arguments = 'None'
item.comment = 'Used for input of yes'
langlist.add(item)

# =============================================================================
# QUIET_HELP 
# =============================================================================
item = langlist.create('QUIET_HELP', kind='HELP')
item.value['ENG'] = 'Run recipe without start up text'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DESC 
# =============================================================================
item = langlist.create('REMAKE_DESC', kind='HELP')
item.value['ENG'] = 'Remake a database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_DESCRIPTION 
# =============================================================================
item = langlist.create('REMAKE_DOC_DESCRIPTION', kind='TEXT')
item.value['ENG'] = 'Re-make the apero documentation'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_UPLOADARG_HELP 
# =============================================================================
item = langlist.create('REMAKE_DOC_UPLOADARG_HELP', kind='TEXT')
item.value['ENG'] = '[Bool] If True upload documentation to defined server (for web access)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_COMPILE_HELP 
# =============================================================================
item = langlist.create('REMAKE_DOC_COMPILE_HELP', kind='HELP')
item.value['ENG'] = 'Compile all rst pages'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_FILEDEF_HELP 
# =============================================================================
item = langlist.create('REMAKE_DOC_FILEDEF_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for file definitions'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_RECIPEDEF_HELP 
# =============================================================================
item = langlist.create('REMAKE_DOC_RECIPEDEF_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for recipe definitions'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_RECIPESEQ_HELP 
# =============================================================================
item = langlist.create('REMAKE_DOC_RECIPESEQ_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for recipe sequences'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_HELP_INSTRUMENT 
# =============================================================================
item = langlist.create('REMAKE_HELP_INSTRUMENT', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to remake the database for'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_HELP_KIND 
# =============================================================================
item = langlist.create('REMAKE_HELP_KIND', kind='HELP')
item.value['ENG'] = '[STRING] The kind of database to remake (i.e. calibration or telluric)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_DESCRIPTION 
# =============================================================================
item = langlist.create('RESET_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Resets the DRS raw/tmp/db/reduced files based on user input'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_INST_HELP 
# =============================================================================
item = langlist.create('RESET_INST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to reset'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_LOG_HELP 
# =============================================================================
item = langlist.create('RESET_LOG_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True logs the reset else is quite'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_WARN_HELP 
# =============================================================================
item = langlist.create('RESET_WARN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True asks for user to type \'YES\' before each reset'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_DATABASE_TIMEOUT_HELP 
# =============================================================================
item = langlist.create('RESET_DATABASE_TIMEOUT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Set the database timeout number of tries'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_INPUT_DIR_HELP 
# =============================================================================
item = langlist.create('SET_INPUT_DIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Force the default input directory (Normally set by recipe)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_IPYTHON_RETURN_HELP 
# =============================================================================
item = langlist.create('SET_IPYTHON_RETURN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True always returns to ipython (or python) at end (via ipdb or pdb)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_OUTPUT_DIR_HELP 
# =============================================================================
item = langlist.create('SET_OUTPUT_DIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Force the default output directory (Normally set by recipe)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_PARALLEL_HELP 
# =============================================================================
item = langlist.create('SET_PARALLEL_HELP', kind='TEXT')
item.value['ENG'] = '[BOOL] If True this is a run in parellel - disable some features (normally only used in apero_processing.py)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_PROGRAM_HELP 
# =============================================================================
item = langlist.create('SET_PROGRAM_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The name of the program to display and use (mostly for logging purpose) log becomes date | {THIS STRING} | Message'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_RECIPE_KIND_HELP 
# =============================================================================
item = langlist.create('SET_RECIPE_KIND_HELP', kind='TEXT')
item.value['ENG'] = '[STRING] The recipe kind for this recipe run (normally only used in apero_processing.py)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_SHORTNAME_HELP 
# =============================================================================
item = langlist.create('SET_SHORTNAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Set a shortname for a recipe to distinguish it from other runs - this is mainly for use with apero processing but will appear in the log database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_DESC 
# =============================================================================
item = langlist.create('TEST_DESC', kind='HELP')
item.value['ENG'] = 'Test recipe - used to test the argument parser of the DRS'
item.value['FR'] = 'Test recipe - utilisé pour tester l\'analyseur d\'arguments du DRS '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_DESCRIPTION 
# =============================================================================
item = langlist.create('TEST_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'This is the top level test recipe'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_EXAMPLE 
# =============================================================================
item = langlist.create('TEST_EXAMPLE', kind='HELP')
item.value['ENG'] = ' test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT] \n test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 *f_pp *d_pp'
item.value['FR'] = ' test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT] \n test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 *f_pp *d_pp'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_FILELIST1_HELP 
# =============================================================================
item = langlist.create('TEST_FILELIST1_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed types: -DARK_DARK -FLAT_FLAT'
item.value['FR'] = 'Types actuellement autorisés: -DARK_DARK -FLAT_FLAT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_FILELIST2_HELP 
# =============================================================================
item = langlist.create('TEST_FILELIST2_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed types: -FP_FP'
item.value['FR'] = 'Types actuellement autorisés: -FP_FP '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# USAGE_TEXT 
# =============================================================================
item = langlist.create('USAGE_TEXT', kind='TEXT')
item.value['ENG'] = ' Usage:'
item.value['FR'] = ' L\'utilisation:'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VALIDATE_DESCRIPTION 
# =============================================================================
item = langlist.create('VALIDATE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Runs the DRS validate script (If this script runs the APERO frame work has been installed successfully)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VERSION_HELP 
# =============================================================================
item = langlist.create('VERSION_HELP', kind='HELP')
item.value['ENG'] = 'Displays the current version of this recipe.'
item.value['FR'] = 'Affiche la version actuelle de cette recette.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# YES_TEXT 
# =============================================================================
item = langlist.create('YES_TEXT', kind='TEXT')
item.value['ENG'] = 'yes'
item.value['FR'] = 'oui'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_GUI_HELP 
# =============================================================================
item = langlist.create('GET_GUI_HELP', kind='HELP')
item.value['ENG'] = 'Use a gui to filter files (Currently not ready)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OBJNAME_HELP 
# =============================================================================
item = langlist.create('GET_OBJNAME_HELP', kind='HELP')
item.value['ENG'] = 'The object names separated by a comma. Use \'\' for objects with whitespaces i.e \'obj1,obj2,obj 3\''
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_DPRTYPES_HELP 
# =============================================================================
item = langlist.create('GET_DPRTYPES_HELP', kind='HELP')
item.value['ENG'] = 'The DPRTYPES to use (multiple dprtypes combined with OR logic) separate dprtypes with commas. Leaving blank will not use DPRTYPE to filter files.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OUTTYPES_HELP 
# =============================================================================
item = langlist.create('GET_OUTTYPES_HELP', kind='HELP')
item.value['ENG'] = 'The drs output file types to use (multiple output type combined  with OR logic) separate output types with commas. Leaving blank will not use output type to filter files.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FIBERS_HELP 
# =============================================================================
item = langlist.create('GET_FIBERS_HELP', kind='HELP')
item.value['ENG'] = 'The fibres to use (multiple output type combined  with OR logic) separate fibers with commas. Leaving blank will not use fiber to filter files.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OUTPATH_HELP 
# =============================================================================
item = langlist.create('GET_OUTPATH_HELP', kind='HELP')
item.value['ENG'] = 'This is the directory where copied files will be placed. Must be a valid path and must have permission be able to write.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_SYMLINKS_HELP 
# =============================================================================
item = langlist.create('GET_SYMLINKS_HELP', kind='HELP')
item.value['ENG'] = 'Create symlinks to the file instead of copying'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_TEST_HELP 
# =============================================================================
item = langlist.create('GET_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Does not copy files - prints copy as a debug test. Recommended for first time use.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_RAW_DESC 
# =============================================================================
item = langlist.create('DATA_RAW_DESC', kind='TEXT')
item.value['ENG'] = 'Raw data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_TMP_DESC 
# =============================================================================
item = langlist.create('DATA_TMP_DESC', kind='TEXT')
item.value['ENG'] = 'Temporary data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_REDUC_DESC 
# =============================================================================
item = langlist.create('DATA_REDUC_DESC', kind='TEXT')
item.value['ENG'] = 'Reduced data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_OUT_DESC 
# =============================================================================
item = langlist.create('DATA_OUT_DESC', kind='TEXT')
item.value['ENG'] = 'Post process directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_CALIB_DESC 
# =============================================================================
item = langlist.create('DATA_CALIB_DESC', kind='TEXT')
item.value['ENG'] = 'Calibration DB data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_TELLU_DESC 
# =============================================================================
item = langlist.create('DATA_TELLU_DESC', kind='TEXT')
item.value['ENG'] = 'Telluric DB data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_PLOT_DESC 
# =============================================================================
item = langlist.create('DATA_PLOT_DESC', kind='TEXT')
item.value['ENG'] = 'Plotting directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_RUN_DESC 
# =============================================================================
item = langlist.create('DATA_RUN_DESC', kind='TEXT')
item.value['ENG'] = 'Run directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_ASSETS_DESC 
# =============================================================================
item = langlist.create('DATA_ASSETS_DESC', kind='TEXT')
item.value['ENG'] = 'Assets directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_LOG_DESC 
# =============================================================================
item = langlist.create('DATA_LOG_DESC', kind='TEXT')
item.value['ENG'] = 'Log directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PROFILE_MSG 
# =============================================================================
item = langlist.create('INSTALL_PROFILE_MSG', kind='TEXT')
item.value['ENG'] = 'APERO profile name:      \n\nThis is the profile name to associate with this installation\nDo not include spaces or wildcards (alpha-numeric only)\nNote you can create multiple profiles for different instruments\nso the name should be logical and unique'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CONFIG_PATH_MSG 
# =============================================================================
item = langlist.create('INSTALL_CONFIG_PATH_MSG', kind='TEXT')
item.value['ENG'] = 'User config path:      \n\nThis is the path where your user configuration will be saved.     \nIf it doesn\'t exist you will be prompted to create it.      \nNote please make sure directory is EMPTY.      \nNote the \"profile name\" sub-directory will be created under this path.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DATA_PATH_MSG 
# =============================================================================
item = langlist.create('INSTALL_DATA_PATH_MSG', kind='TEXT')
item.value['ENG'] = 'Setup paths invidiually? [Y]es or [N]o        \n\nIf [Y]es it will allow you to set each path separately      \n(i.e. for raw, tmp, reduced, calibDB etc).      \nIf [N]o you will just set one path and all folders      \n(raw, tmp, reduced, calibDB etc) will be created under this      \ndirectory.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_MSG 
# =============================================================================
item = langlist.create('INSTALL_CLEAN_MSG', kind='TEXT')
item.value['ENG'] = 'Clean install? [Y]es or [N]o      \n\nWARNING: If you type [Y]es you will be prompted (later) to reset     \nthe directories this means any previous data in these directories     \nwill be removed.  \n\nNote you can always say later to individual cases.  \n\nNote if you have given empty directories you MUST run a clean install to copy the required files to the given directories.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ALIAS_MSG 
# =============================================================================
item = langlist.create('INSTALL_ALIAS_MSG', kind='TEXT')
item.value['ENG'] = 'Add an alias in your ~/.bashrc or ~/.bash_profile or ~/.tcshrc or ~/.profile or ~/.zshrc or ~/.zprofile         \nand then type \"{NAME}\" every time you wish to run apero.          \n\ni.e. for bash              \nalias {NAME}=\"source {DRS_UCONFIG}{NAME}.bash.setup\"          \n\ni.e. for sh             \nalias {NAME} \"source {DRS_UCONFIG}{NAME}.sh.setup\"         \n\ni.e. for zsh              \nalias {NAME} \"source {DRS_UCONFIG}{NAME}.zsh.setup\"'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_MSG 
# =============================================================================
item = langlist.create('INSTALL_DB_MSG', kind='TEXT')
item.value['ENG'] = 'For MySQL you must define some parameters, these will take the form:\n\n    >> mysql -h {HOSTNAME} -n {USERNAME} -p {PASSWORD}\n\n- Note the password will be stored as plain text.\n\nYou will also need a database name (within mysql) \n- if it does not exist we will attempt to create it (but may not have permissions to do so)\n\nYou may also link the database to a specific apero profile\nby default this is the profile name you set up here\nhowever you may want to link this database to another apero profile'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_UPDATE_HELP 
# =============================================================================
item = langlist.create('INSTALL_UPDATE_HELP', kind='HELP')
item.value['ENG'] = 'updates installation (not clean install) and checks for updates to your current config files'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_SKIP_HELP 
# =============================================================================
item = langlist.create('INSTALL_SKIP_HELP', kind='HELP')
item.value['ENG'] = 'skip the python module checks (Not recommended for first time installation)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DEV_HELP 
# =============================================================================
item = langlist.create('INSTALL_DEV_HELP', kind='HELP')
item.value['ENG'] = 'activate developer mode (prompts for all config/constant groups and add them to your config/constant files)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_GUI_HELP 
# =============================================================================
item = langlist.create('INSTALL_GUI_HELP', kind='HELP')
item.value['ENG'] = 'use GUI to install (Not yet supported) '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_NAME_HELP 
# =============================================================================
item = langlist.create('INSTALL_NAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The name for this specific installation (Allows the creation of multiple profiles with different settings)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DESCRIPTION 
# =============================================================================
item = langlist.create('INSTALL_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Install {0} software for reducing observational data'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ROOT_HELP 
# =============================================================================
item = langlist.create('INSTALL_ROOT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The installation directory (if not given tries to find the path and if not found prompts the user)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CONFIG_HELP 
# =============================================================================
item = langlist.create('INSTALL_CONFIG_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The user configuration path (if not given prompts the user)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_INSTRUMENT_HELP 
# =============================================================================
item = langlist.create('INSTALL_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to install (if not given prompts the user for each available instrument). THIS ARGUMENT IS REQUIRED TO SET --datadir, --rawdir, --tmpdir, --reddir, --calibdir, --telludir, --plotdir, --rundir, --assetdir, --logdir'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DATADIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_DATADIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The data directory (if given overrides all sub-data directories - i.e. raw/tmp/red/plot) if not given and other paths not given prompts the user for input.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_RAWDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_RAWDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The raw directory where input files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TMPDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_TMPDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The tmp directory where preprocessed files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_REDDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_REDDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The reduced directory where output files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_OUTDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_OUTDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The post process directory where output files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CALIBDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_CALIBDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The calibration database directory where calibrations used in the database files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TELLUDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_TELLUDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The telluric database directory where telluric database files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PLOTDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_PLOTDIR_HELP', kind='HELP')
item.value['ENG'] = 'The plot directory where plots/summary documents are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_RUNDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_RUNDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run directory where run/batch files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ASSETDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_ASSETDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The assets directory where assets files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LOGDIR_HELP 
# =============================================================================
item = langlist.create('INSTALL_LOGDIR_HELP', kind='HELP')
item.value['ENG'] = 'The log directory where log and lock files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install  each directory separately)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PLOTMODE_HELP 
# =============================================================================
item = langlist.create('INSTALL_PLOTMODE_HELP', kind='HELP')
item.value['ENG'] = '[INT] The plot mode. 0=Summary plots only 1=Plot at end of run 2=Plot at creation (pauses code). If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_HELP 
# =============================================================================
item = langlist.create('INSTALL_CLEAN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to run from clean directories -  RECOMMENDED - clears out old files and copies over all required default data files. If unset user is prompted for  choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_NO_WARNING_HELP 
# =============================================================================
item = langlist.create('INSTALL_CLEAN_NO_WARNING_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to warn about cleaning populated directories - WARNING if set to True will delete all tmp/reduced/calibDB etc. data without prompt'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DBMODE_HELP 
# =============================================================================
item = langlist.create('INSTALL_DBMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Database mode (1: sqlite, 2: mysql). If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_HOST_HELP 
# =============================================================================
item = langlist.create('INSTALL_DB_HOST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database hostname (Only required if --databasemode=2. If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_USER_HELP 
# =============================================================================
item = langlist.create('INSTALL_DB_USER_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database username (Only required if --databasemode=2. If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_PASS_HELP 
# =============================================================================
item = langlist.create('INSTALL_DB_PASS_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database password (Only required if --databasemode=2. If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_NAME_HELP 
# =============================================================================
item = langlist.create('INSTALL_DB_NAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database name (Only required if --databasemode=2. If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CALIBTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_CALIBTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the calibration database (default is the APERO profile name). If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TELLUTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_TELLUTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the telluric database (default is the APERO profile name). If unset user is prompted for choice.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_INDEXTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_INDEXTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the index database (default is the APERO profile name).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LOGTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_LOGTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the log database (default is the APERO profile name).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_OBJTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_OBJTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the object database (default is the APERO profile name).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LANGTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_LANGTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the language database (default is the APERO profile name).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ALL_TEXT 
# =============================================================================
item = langlist.create('ALL_TEXT', kind='TEXT')
item.value['ENG'] = 'all'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_DESCRIPTION 
# =============================================================================
item = langlist.create('GO_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Use this tool to find current paths set by current profile'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_DATA_HELP 
# =============================================================================
item = langlist.create('GO_DATA_HELP', kind='HELP')
item.value['ENG'] = 'Find the current data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_BLOCK_HELP 
# =============================================================================
item = langlist.create('GO_BLOCK_HELP', kind='HELP')
item.value['ENG'] = 'Find the current {0} data directory'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_DESC 
# =============================================================================
item = langlist.create('LANGDB_DESC', kind='HELP')
item.value['ENG'] = 'Language database tools'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_FIND_HELP 
# =============================================================================
item = langlist.create('LANGDB_FIND_HELP', kind='HELP')
item.value['ENG'] = 'Displays the message locator GUI'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_UPDATE_HELP 
# =============================================================================
item = langlist.create('LANGDB_UPDATE_HELP', kind='HELP')
item.value['ENG'] = 'Updates local language database and local text files with any changes'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_RELOAD_HELP 
# =============================================================================
item = langlist.create('LANGDB_RELOAD_HELP', kind='HELP')
item.value['ENG'] = 'Reloads the local language database (with text file changes)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_REJECTTABLE_HELP 
# =============================================================================
item = langlist.create('INSTALL_REJECTTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the reject database (default is the APERO profile name).'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTENDED_HELP 
# =============================================================================
item = langlist.create('EXTENDED_HELP', kind='HELP')
item.value['ENG'] = 'Extended help menu (with all advanced arguments)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_DESCREIPTION 
# =============================================================================
item = langlist.create('PRECHECK_DESCREIPTION', kind='HELP')
item.value['ENG'] = 'Run a check before running apero processing to check on the number of calibrations, number of telluric and science raw files and/or check if any objects astrometric data are coming from the header'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_NOFILECHECK_HELP 
# =============================================================================
item = langlist.create('PRECHECK_NOFILECHECK_HELP', kind='HELP')
item.value['ENG'] = 'Don’t check the number of files on disk and don’t flag these errors'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_NOOBJCHECK_HELP 
# =============================================================================
item = langlist.create('PRECHECK_NOOBJCHECK_HELP', kind='HELP')
item.value['ENG'] = 'Don’t check object database with current set of raw files and don’t flag these errors'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_DESCRIPTION 
# =============================================================================
item = langlist.create('TRIGGER_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Basic (brute force) trigger for APERO'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_INDIR_HELP 
# =============================================================================
item = langlist.create('TRIGGER_INDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The input directory to scan for new data. (This is not the apero defined raw directory)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_RESET_HELP 
# =============================================================================
item = langlist.create('TRIGGER_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Reset the trigger (default is False and thus we use cached files to speed up trigger). This means after nights are marked done (calib/sci) they will not be reprocessed. Thus --reset to avoid this.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_IGNORE_HELP 
# =============================================================================
item = langlist.create('TRIGGER_IGNORE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Ignore certain obs_dir (observation directories) by default all directories in --indir are reduced. Using ignore will ignore certain directories and not add them to the the sym-linked (DRS_DATA_RAW) directory.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_WAIT_HELP 
# =============================================================================
item = langlist.create('TRIGGER_WAIT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Number of second to wait between processing runs. Should not be too low (below 10s its too fast) unless testing, or too high (above 3600s)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_CALIB_HELP 
# =============================================================================
item = langlist.create('TRIGGER_CALIB_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run.ini file to use for calibration trigger run'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_SCI_HELP 
# =============================================================================
item = langlist.create('TRIGGER_SCI_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run.ini file to use for science trigger run'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_TEST_HELP 
# =============================================================================
item = langlist.create('TRIGGER_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Active test mode (does not run recipes)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_MODE_HELP 
# =============================================================================
item = langlist.create('LOGSTAT_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Stats mode. Any combination of the following (separated by a comma, no white spaces). For all use “all”. For timing statistics use \"timing\". For quality control statistics use \"qc\". For error statistics use \"error\". For memory statistics use \"memory\". For file index use “findex”.  I.e. --mode=qc,memory  runs the qc and memory stats.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_PLOG_HELP 
# =============================================================================
item = langlist.create('LOGSTAT_PLOG_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Specify a certain log file (full path)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_SQL_HELP 
# =============================================================================
item = langlist.create('LOGSTAT_SQL_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Specify a SQL WHERE clause to narrow the stats'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RUN_INI_DESCRIPTION 
# =============================================================================
item = langlist.create('RUN_INI_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Create default run.ini files for APERO instrument(s)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RUN_INI_INSTRUMENT_HELP 
# =============================================================================
item = langlist.create('RUN_INI_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Instrument or instruments to create run.ini files for'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# STATIC_DESCRIPTION 
# =============================================================================
item = langlist.create('STATIC_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Create static files for APERO instrument(s)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# STATIC_MODE_HELP 
# =============================================================================
item = langlist.create('STATIC_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Chooses the static file to create'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISU_DESCRIPTION 
# =============================================================================
item = langlist.create('VISU_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'APERO visualizer'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISU_MODE_HELP 
# =============================================================================
item = langlist.create('VISU_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which type of graph to plot'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FAILEDQC_HELP 
# =============================================================================
item = langlist.create('GET_FAILEDQC_HELP', kind='HELP')
item.value['ENG'] = 'Include files that failed QC. Highly unrecommended.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_DESCRIPTION 
# =============================================================================
item = langlist.create('GET_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Use database to search and copy any files quickly'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_RECIPE 
# =============================================================================
item = langlist.create('EXPLORER_RECIPE', kind='HELP')
item.value['ENG'] = '[STRING] Recipe or shortname for recipe (must be used in combination with –flagnum)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_FLAGNUM 
# =============================================================================
item = langlist.create('EXPLORER_FLAGNUM', kind='HELP')
item.value['ENG'] = '[INTEGER] Instead of running explorer converts a binary flagg to a set of binary flags for a recipe (must be used in combination with –recipe)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_MODE_HELP 
# =============================================================================
item = langlist.create('REMAKE_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which mode to output in \"html\", \"latex\" or \"both\". Default is \"both\".'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_INSTRUMENT_HELP 
# =============================================================================
item = langlist.create('REMAKE_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which instrument(s) to run this for (default is current instrument) can also write ALL to get all instruments or list instruments separated by a comma'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_DELETE_HELP 
# =============================================================================
item = langlist.create('DBMGR_DELETE_HELP', kind='HELP')
item.value['ENG'] = 'Load up the delete table GUI (MySQL only)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_RESET_HELP 
# =============================================================================
item = langlist.create('DBMGR_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Reset current databases'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_CALIBDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_CALIBDB_HELP', kind='HELP')
item.value['ENG'] = 'Update calibration database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_TELLUDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_TELLUDB_HELP', kind='HELP')
item.value['ENG'] = 'Update telluric database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_LOGDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_LOGDB_HELP', kind='HELP')
item.value['ENG'] = 'Update log database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_FINDEXDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_FINDEXDB_HELP', kind='HELP')
item.value['ENG'] = 'Update file index database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_ASTROMDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_ASTROMDB_HELP', kind='HELP')
item.value['ENG'] = 'Update astrometric database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_REJECTDB_HELP 
# =============================================================================
item = langlist.create('DBMGR_REJECTDB_HELP', kind='HELP')
item.value['ENG'] = 'Update rejection database'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_OVERWRITE_HELP 
# =============================================================================
item = langlist.create('ASTROMETRIC_OVERWRITE_HELP', kind='HELP')
item.value['ENG'] = 'Do not check if object is currently in database. Overwrite old value.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_GETTEFF_HELP 
# =============================================================================
item = langlist.create('ASTROMETRIC_GETTEFF_HELP', kind='HELP')
item.value['ENG'] = 'Attempt to get Teff from header value. Requires a raw file of this object and the index database to be up-to-date'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_NOPM_REQ_HELP 
# =============================================================================
item = langlist.create('ASTROMETRIC_NOPM_REQ_HELP', kind='HELP')
item.value['ENG'] = 'Do not require proper motion (not recommended)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_TEST_HELP 
# =============================================================================
item = langlist.create('ASTROMETRIC_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Run in test mode (do not add to database)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_RUNFILE_HELP 
# =============================================================================
item = langlist.create('SET_RUNFILE_HELP', kind='HELP')
item.value['ENG'] = 'Set a run file to override default arguments'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_NOSAVE_HELP 
# =============================================================================
item = langlist.create('SET_NOSAVE_HELP', kind='HELP')
item.value['ENG'] = 'Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once.'
item.arguments = 'None'
item.comment = ''
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
